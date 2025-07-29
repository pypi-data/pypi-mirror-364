import asyncio
import time
from threading import Thread
from typing import List, Optional

from analytics_ingest.internal.schemas.message_schema import MessageSchema
from analytics_ingest.internal.schemas.signal_schema import SignalSchema
from analytics_ingest.internal.utils.batching import Batcher
from analytics_ingest.internal.utils.graphql_executor import GraphQLExecutor
from analytics_ingest.internal.utils.message import (
    create_message,
    get_cached_message_id,
    generate_message_cache_key,
)
from analytics_ingest.internal.utils.mutations import GraphQLMutations


class SignalBufferManager:
    def __init__(
        self,
        executor: GraphQLExecutor,
        configuration_id: int,
        batch_size: int,
        max_signal_count: int,
        batch_interval_seconds: int = 10,
    ):
        self.executor = executor
        self.configuration_id = configuration_id
        self.batch_size = batch_size
        self.max_signal_count = max_signal_count
        self.batch_interval_seconds = batch_interval_seconds

        self.buffer: List[dict] = []
        self.last_flush_time = time.time()

        self.loop = asyncio.get_event_loop()
        self._start_background_flush()

    def _start_background_flush(self):
        thread = Thread(target=self._background_flush_loop, daemon=True)
        thread.start()

    def _background_flush_loop(self):
        while True:
            time.sleep(1)
            if self.buffer and (
                time.time() - self.last_flush_time >= self.batch_interval_seconds
            ):
                print("[BackgroundFlush] Time-based flush triggered")
                try:
                    asyncio.run(self.flush(force=True))
                except Exception as e:
                    print(f"[SignalBufferManager] Flush error: {e}")

    def add_signal(self, signals: List[dict]):
        if not signals:
            print("[add_signal] No signals received")
            return

        print(f"[add_signal] Received {len(signals)} signals")

        try:
            print("[add_signal] Creating messages...")
            create_message(self.executor, signals)
            print("[add_signal] Messages created")
        except Exception as e:
            print(f"[add_signal] Failed to create messages: {e}")
            return

        self.buffer.extend(signals)
        print(f"[add_signal] Buffer size after add: {len(self.buffer)}")

        if len(self.buffer) >= self.max_signal_count:
            print("[add_signal] Buffer size exceeded max_signal_count, flushing")
            self.flush()

    def flush(self, force=False):
        if not self.buffer:
            print("[flush] No signals to flush")
            return

        print(f"[flush] Flushing {len(self.buffer)} signals (force={force})")

        signals_to_flush = self.buffer
        self.buffer = []
        self.last_flush_time = time.time()

        batches = Batcher.create_batches(signals_to_flush, self.batch_size)
        print(f"[flush] Created {len(batches)} batches")

        for idx, batch in enumerate(batches):
            print(f"[flush] Processing batch {idx + 1} with {len(batch)} signals")

            signal_inputs = []
            for signal in batch:
                message_key = generate_message_cache_key(signal)
                message_id = get_cached_message_id(message_key)
                print(f"[flush] message_key={message_key}, message_id={message_id}")

                if message_id is None:
                    print(f"[flush] ERROR: Message ID not found for key: {message_key}")
                    continue

                signal_input = SignalSchema.from_variables(
                    self.configuration_id, int(message_id), signal["data"], signal
                )
                signal_inputs.append(signal_input.model_dump())

            if signal_inputs:
                payload = {"input": {"signals": signal_inputs}}
                print(f"[flush] Sending {len(signal_inputs)} signals to GraphQL")
                self.executor.execute(GraphQLMutations.upsert_signal_data(), payload)

    def _chunk_signals(self, signals: List[dict]) -> List[List[dict]]:
        return [
            signals[i : i + self.max_signal_count]
            for i in range(0, len(signals), self.max_signal_count)
        ]
