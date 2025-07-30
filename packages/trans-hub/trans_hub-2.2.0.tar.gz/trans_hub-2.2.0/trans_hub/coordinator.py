# trans_hub/coordinator.py
"""
本模块包含 Trans-Hub 引擎的主协调器 (Coordinator)。
它负责动态加载、验证引擎配置，并编排所有核心工作流。
"""

import asyncio
import json
from collections.abc import AsyncGenerator
from itertools import groupby
from typing import Any, Optional, Union

import structlog

from trans_hub.cache import TranslationCache
from trans_hub.config import TransHubConfig
from trans_hub.engine_registry import ENGINE_REGISTRY, discover_engines
from trans_hub.engines.base import BaseContextModel, BaseTranslationEngine
from trans_hub.engines.meta import ENGINE_CONFIG_REGISTRY
from trans_hub.interfaces import PersistenceHandler
from trans_hub.rate_limiter import RateLimiter
from trans_hub.types import (
    ContentItem,
    EngineError,
    EngineSuccess,
    TranslationRequest,
    TranslationResult,
    TranslationStatus,
)
from trans_hub.utils import get_context_hash, validate_lang_codes

logger = structlog.get_logger(__name__)


class Coordinator:
    """异步主协调器。"""

    def __init__(
        self,
        config: TransHubConfig,
        persistence_handler: PersistenceHandler,
        rate_limiter: Optional[RateLimiter] = None,
    ) -> None:
        """初始化协调器实例，并动态完成引擎配置的加载和验证。"""
        discover_engines()

        self.config = config
        self.handler = persistence_handler
        self.cache = TranslationCache(self.config.cache_config)
        self.rate_limiter = rate_limiter
        self.active_engine_name = config.active_engine
        self.initialized = False

        logger.info(
            "协调器初始化开始...", available_engines=list(ENGINE_REGISTRY.keys())
        )

        if self.active_engine_name not in ENGINE_REGISTRY:
            raise ValueError(f"指定的活动引擎 '{self.active_engine_name}' 不可用。")

        # [核心修复] 只确保 active_engine 的配置存在
        self._ensure_engine_config(self.active_engine_name)

        self.active_engine: BaseTranslationEngine[Any] = self._create_engine_instance(
            self.active_engine_name
        )

        if self.active_engine.REQUIRES_SOURCE_LANG and not self.config.source_lang:
            raise ValueError(f"活动引擎 '{self.active_engine_name}' 需要提供源语言。")

        logger.info("协调器初始化完成。", active_engine=self.active_engine_name)

    def _ensure_engine_config(self, engine_name: str) -> None:
        """如果指定引擎的配置不存在，则动态创建它。"""
        if getattr(self.config.engine_configs, engine_name, None) is None:
            config_class = ENGINE_CONFIG_REGISTRY.get(engine_name)
            if not config_class:
                raise ValueError(f"引擎 '{engine_name}' 的配置模型未在元数据中注册。")

            # BaseSettings 会自动从 .env 加载
            instance = config_class()
            setattr(self.config.engine_configs, engine_name, instance)

    def _create_engine_instance(self, engine_name: str) -> BaseTranslationEngine[Any]:
        engine_class = ENGINE_REGISTRY[engine_name]
        engine_config_instance = getattr(self.config.engine_configs, engine_name, None)

        if not engine_config_instance:
            raise ValueError(f"未能为引擎 '{engine_name}' 创建或找到配置实例。")

        return engine_class(config=engine_config_instance)

    def switch_engine(self, engine_name: str) -> None:
        if engine_name == self.active_engine_name:
            return

        logger.info("正在切换活动引擎...", new_engine=engine_name)
        if engine_name not in ENGINE_REGISTRY:
            raise ValueError(f"尝试切换至一个不可用的引擎: '{engine_name}'")

        # [核心修复] 在切换时，也确保目标引擎的配置存在
        self._ensure_engine_config(engine_name)

        self.active_engine = self._create_engine_instance(engine_name)
        self.active_engine_name = engine_name
        self.config.active_engine = engine_name
        logger.info(f"成功切换活动引擎至: '{self.active_engine_name}'。")

    async def initialize(self) -> None:
        if self.initialized:
            return
        logger.info("正在连接持久化存储...")
        await self.handler.connect()
        self.initialized = True
        logger.info("持久化存储连接成功。")

    async def process_pending_translations(
        self,
        target_lang: str,
        batch_size: Optional[int] = None,
        limit: Optional[int] = None,
        max_retries: Optional[int] = None,
        initial_backoff: Optional[float] = None,
    ) -> AsyncGenerator[TranslationResult, None]:
        validate_lang_codes([target_lang])
        batch_policy = getattr(
            self.active_engine.config, "max_batch_size", self.config.batch_size
        )
        final_batch_size = min(batch_size or self.config.batch_size, batch_policy)
        final_max_retries = max_retries or self.config.retry_policy.max_attempts
        final_initial_backoff = (
            initial_backoff or self.config.retry_policy.initial_backoff
        )

        logger.info(
            "开始处理待翻译任务。", target_lang=target_lang, batch_size=final_batch_size
        )
        content_batches = self.handler.stream_translatable_items(
            lang_code=target_lang,
            statuses=[TranslationStatus.PENDING, TranslationStatus.FAILED],
            batch_size=final_batch_size,
            limit=limit,
        )

        async for batch in content_batches:
            if not batch:
                continue

            batch.sort(key=lambda item: item.context_hash)
            for context_hash, items_group_iter in groupby(
                batch, key=lambda item: item.context_hash
            ):
                items_group = list(items_group_iter)
                logger.debug(
                    "正在处理上下文一致的小组",
                    context_hash=context_hash,
                    item_count=len(items_group),
                )

                batch_results = await self._process_batch_with_retry_logic(
                    items_group, target_lang, final_max_retries, final_initial_backoff
                )

                await self.handler.save_translations(batch_results)
                for result in batch_results:
                    if (
                        result.status == TranslationStatus.TRANSLATED
                        and result.business_id
                    ):
                        await self.handler.touch_source(result.business_id)
                    yield result

    async def _process_batch_with_retry_logic(
        self,
        batch: list[ContentItem],
        target_lang: str,
        max_retries: int,
        initial_backoff: float,
    ) -> list[TranslationResult]:
        business_id_map = await self._get_business_id_map(batch)

        validated_context = self.active_engine.validate_and_parse_context(
            batch[0].context if batch else None
        )

        if isinstance(validated_context, EngineError):
            logger.warning("批次上下文验证失败", error=validated_context.error_message)
            return [
                self._build_translation_result(
                    item, target_lang, business_id_map, error_override=validated_context
                )
                for item in batch
            ]

        items_to_process = list(batch)
        final_results: list[TranslationResult] = []

        for attempt in range(max_retries + 1):
            (
                processed_results,
                retryable_items,
            ) = await self._process_single_translation_attempt(
                items_to_process, target_lang, business_id_map, validated_context
            )
            final_results.extend(processed_results)

            if not retryable_items:
                return final_results

            if attempt >= max_retries:
                logger.error(
                    "小组达到最大重试次数", retry_item_count=len(retryable_items)
                )
                error = EngineError(
                    error_message="达到最大重试次数", is_retryable=False
                )
                failed_results = [
                    self._build_translation_result(
                        item, target_lang, business_id_map, error_override=error
                    )
                    for item in retryable_items
                ]
                final_results.extend(failed_results)
                return final_results

            items_to_process = retryable_items
            backoff_time = initial_backoff * (2**attempt)
            logger.warning(
                f"小组中包含可重试错误，将在 {backoff_time:.2f}s 后重试。",
                retry_count=len(items_to_process),
            )
            await asyncio.sleep(backoff_time)
        return final_results

    async def _process_single_translation_attempt(
        self,
        batch: list[ContentItem],
        target_lang: str,
        business_id_map: dict[tuple[int, str], Optional[str]],
        context: Optional[BaseContextModel],
    ) -> tuple[list[TranslationResult], list[ContentItem]]:
        cached_results, uncached_items = await self._separate_cached_items(
            batch, target_lang, business_id_map
        )
        if not uncached_items:
            return cached_results, []

        engine_outputs = await self._translate_uncached_items(
            uncached_items, target_lang, context
        )
        processed_results: list[TranslationResult] = list(cached_results)
        retryable_items: list[ContentItem] = []

        for item, output in zip(uncached_items, engine_outputs):
            if isinstance(output, EngineError) and output.is_retryable:
                retryable_items.append(item)
            else:
                result = self._build_translation_result(
                    item, target_lang, business_id_map, engine_output=output
                )
                processed_results.append(result)

        await self._cache_new_results(processed_results, target_lang)
        return processed_results, retryable_items

    async def _get_business_id_map(
        self, batch: list[ContentItem]
    ) -> dict[tuple[int, str], Optional[str]]:
        if not batch:
            return {}
        tasks = [
            self.handler.get_business_id_for_content(item.content_id, item.context_hash)
            for item in batch
        ]
        return {
            (item.content_id, item.context_hash): biz_id
            for item, biz_id in zip(batch, await asyncio.gather(*tasks))
        }

    async def _separate_cached_items(
        self,
        batch: list[ContentItem],
        target_lang: str,
        business_id_map: dict,
    ) -> tuple[list[TranslationResult], list[ContentItem]]:
        cached_results: list[TranslationResult] = []
        uncached_items: list[ContentItem] = []
        for item in batch:
            request = TranslationRequest(
                source_text=item.value,
                source_lang=self.config.source_lang,
                target_lang=target_lang,
                context_hash=item.context_hash,
            )
            cached_text = await self.cache.get_cached_result(request)
            if cached_text:
                result = self._build_translation_result(
                    item, target_lang, business_id_map, cached_text=cached_text
                )
                cached_results.append(result)
            else:
                uncached_items.append(item)
        return cached_results, uncached_items

    async def _translate_uncached_items(
        self,
        items: list[ContentItem],
        target_lang: str,
        context: Optional[BaseContextModel],
    ) -> list[Union[EngineSuccess, EngineError]]:
        if self.rate_limiter:
            await self.rate_limiter.acquire(len(items))
        try:
            return await self.active_engine.atranslate_batch(
                texts=[item.value for item in items],
                target_lang=target_lang,
                source_lang=self.config.source_lang,
                context=context,
            )
        except Exception as e:
            logger.error("引擎调用失败", error=str(e), exc_info=True)
            return [EngineError(error_message=str(e), is_retryable=True)] * len(items)

    async def _cache_new_results(
        self, results: list[TranslationResult], target_lang: str
    ) -> None:
        tasks = [
            self.cache.cache_translation_result(
                TranslationRequest(
                    source_text=res.original_content,
                    source_lang=self.config.source_lang,
                    target_lang=target_lang,
                    context_hash=res.context_hash,
                ),
                res.translated_content or "",
            )
            for res in results
            if res.status == TranslationStatus.TRANSLATED and not res.from_cache
        ]
        if tasks:
            await asyncio.gather(*tasks)

    def _build_translation_result(
        self,
        item: ContentItem,
        target_lang: str,
        business_id_map: dict[tuple[int, str], Optional[str]],
        *,
        engine_output: Optional[Union[EngineSuccess, EngineError]] = None,
        cached_text: Optional[str] = None,
        error_override: Optional[EngineError] = None,
    ) -> TranslationResult:
        biz_id = business_id_map.get((item.content_id, item.context_hash))
        final_error = error_override or (
            engine_output if isinstance(engine_output, EngineError) else None
        )
        if final_error:
            return TranslationResult(
                original_content=item.value,
                translated_content=None,
                target_lang=target_lang,
                status=TranslationStatus.FAILED,
                engine=self.active_engine_name,
                error=final_error.error_message,
                from_cache=False,
                context_hash=item.context_hash,
                business_id=biz_id,
            )
        if cached_text is not None:
            return TranslationResult(
                original_content=item.value,
                translated_content=cached_text,
                target_lang=target_lang,
                status=TranslationStatus.TRANSLATED,
                from_cache=True,
                engine=f"{self.active_engine_name} (mem-cached)",
                context_hash=item.context_hash,
                business_id=biz_id,
            )
        if isinstance(engine_output, EngineSuccess):
            return TranslationResult(
                original_content=item.value,
                translated_content=engine_output.translated_text,
                target_lang=target_lang,
                status=TranslationStatus.TRANSLATED,
                engine=self.active_engine_name,
                from_cache=engine_output.from_cache,
                context_hash=item.context_hash,
                business_id=biz_id,
            )
        raise TypeError("无法为项目构建 TranslationResult：输入参数无效。")

    async def request(
        self,
        target_langs: list[str],
        text_content: str,
        business_id: Optional[str] = None,
        context: Optional[dict[str, Any]] = None,
        source_lang: Optional[str] = None,
    ) -> None:
        validate_lang_codes(target_langs)
        context_hash = get_context_hash(context)
        context_json = json.dumps(context) if context else None

        await self.handler.ensure_pending_translations(
            text_content=text_content,
            target_langs=target_langs,
            business_id=business_id,
            context_hash=context_hash,
            context_json=context_json,
            source_lang=(source_lang or self.config.source_lang),
            engine_version=self.active_engine.VERSION,
        )
        logger.info(
            "翻译任务已成功入队。", business_id=business_id, num_langs=len(target_langs)
        )

    async def get_translation(
        self,
        text_content: str,
        target_lang: str,
        context: Optional[dict[str, Any]] = None,
    ) -> Optional[TranslationResult]:
        validate_lang_codes([target_lang])
        context_hash = get_context_hash(context)
        request = TranslationRequest(
            source_text=text_content,
            source_lang=self.config.source_lang,
            target_lang=target_lang,
            context_hash=context_hash,
        )
        cached_text = await self.cache.get_cached_result(request)
        if cached_text:
            return TranslationResult(
                original_content=text_content,
                translated_content=cached_text,
                target_lang=target_lang,
                status=TranslationStatus.TRANSLATED,
                from_cache=True,
                engine=f"{self.active_engine_name} (mem-cached)",
                context_hash=context_hash,
                business_id=None,
            )
        db_result = await self.handler.get_translation(
            text_content, target_lang, context
        )
        if db_result and db_result.translated_content:
            await self.cache.cache_translation_result(
                request, db_result.translated_content
            )
        return db_result

    async def run_garbage_collection(
        self, expiration_days: Optional[int] = None, dry_run: bool = False
    ) -> dict[str, int]:
        days = expiration_days or self.config.gc_retention_days
        logger.info("开始执行垃圾回收。", expiration_days=days, dry_run=dry_run)
        deleted_counts = await self.handler.garbage_collect(
            retention_days=days, dry_run=dry_run
        )
        logger.info("垃圾回收执行完毕。", deleted_counts=deleted_counts)
        return deleted_counts

    async def close(self) -> None:
        if self.initialized:
            logger.info("正在关闭协调器...")
            await self.handler.close()
            self.initialized = False
            logger.info("协调器已成功关闭。")
