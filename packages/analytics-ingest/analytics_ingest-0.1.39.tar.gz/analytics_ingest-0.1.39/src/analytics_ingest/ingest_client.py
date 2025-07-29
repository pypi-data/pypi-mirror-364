import asyncio
import time
from collections import deque
from threading import Thread
from typing import Optional

from more_itertools import chunked

from analytics_ingest.internal.schemas.ingest_config_schema import IngestConfigSchema
from analytics_ingest.internal.schemas.message_schema import MessageSchema
from analytics_ingest.internal.schemas.signal_schema import SignalSchema
from analytics_ingest.internal.utils.configuration import ConfigurationService
from analytics_ingest.internal.utils.dtc import create_dtc
from analytics_ingest.internal.utils.gps import create_gps
from analytics_ingest.internal.utils.graphql_executor import GraphQLExecutor
from analytics_ingest.internal.utils.message import (
    create_message,
    get_cached_message_id,
)
from analytics_ingest.internal.utils.mutations import GraphQLMutations
from analytics_ingest.internal.utils.network import create_network
from analytics_ingest.internal.utils.batching import Batcher
from analytics_ingest.internal.utils.signal_buffer_manager import SignalBufferManager


class IcsAnalytics:
    def __init__(self, **kwargs):
        self.config = IngestConfigSchema(**kwargs)
        self.executor = GraphQLExecutor(self.config.graphql_endpoint)

        self.configuration_id = ConfigurationService(self.executor).create(
            self.config.model_dump()
        )["data"]["createConfiguration"]["id"]

        self.signal_buffer_manager = SignalBufferManager(
            executor=self.executor,
            configuration_id=self.configuration_id,
            batch_size=self.config.batch_size,
            max_signal_count=self.config.max_signal_count,
            batch_interval_seconds=self.config.batch_interval_seconds,
        )

    def add_signal(self, signals: Optional[list] = None):
        if not isinstance(signals, list):
            raise ValueError("'signals' should be a list of dicts")
        if not signals:
            raise ValueError("Missing 'signals' list")

        try:
            self.signal_buffer_manager.add_signal(signals)
        except Exception as e:
            logger.error(f"Failed to add signals: {e}")

    def add_dtc(self, variables_list: Optional[list] = None):
        if not variables_list:
            raise ValueError("Missing 'dtc' list")
        try:
            create_message(self.executor, variables_list)
            create_dtc(
                executor=self.executor,
                config_id=self.configuration_id,
                variables_list=variables_list,
                batch_size=self.config.batch_size,
            )
        except Exception as e:
            raise RuntimeError(f"Failed to add DTC: {e}")

    def add_gps(self, variables: Optional[dict] = None):
        if not variables:
            raise ValueError("Missing 'variables' dictionary")
        try:
            create_gps(
                executor=self.executor,
                config_id=self.configuration_id,
                variables=variables,
                batch_size=self.config.batch_size,
            )
        except Exception as e:
            raise RuntimeError(f"Failed to add GPS: {e}")

    def add_network_stats(self, variables: Optional[dict] = None):
        if not variables:
            raise ValueError("Missing 'variables' dictionary")
        try:
            create_network(
                executor=self.executor,
                config=self.config,
                variables=variables,
            )
        except Exception as e:
            raise RuntimeError(f"Failed to add network stats: {e}")

    def close(self):
        self._shutdown = True

        if self.signal_buffer:
            future = asyncio.run_coroutine_threadsafe(self._flush_buffer(), self.loop)
            try:
                future.result(timeout=10)
            except Exception as e:
                print(f"Final flush failed: {e}")

        if self.loop.is_running():
            self.loop.call_soon_threadsafe(self.loop.stop)

        if hasattr(self, "thread") and self.thread.is_alive():
            self.thread.join(timeout=2)
