import time
import unittest
from unittest.mock import MagicMock, patch

from analytics_ingest.ingest_client import IcsAnalytics
from analytics_ingest.internal.utils.batching import Batcher
from analytics_ingest.internal.utils.mutations import GraphQLMutations
from factories import configuration_factory, message_factory, signal_factory


class TestAnalyticsIngestClient(unittest.TestCase):
    def setUp(self):
        self.config = configuration_factory()
        with patch(
            "analytics_ingest.ingest_client.SignalBufferManager"
        ) as MockBufferManager:
            self.mock_buffer_manager = MockBufferManager.return_value
            self.client = IcsAnalytics(
                device_id=self.config['device_id'],
                vehicle_id=self.config['vehicle_id'],
                fleet_id=self.config['fleet_id'],
                org_id=self.config['organization_id'],
                graphql_endpoint="http://0.0.0.0:8092/graphql",
                batch_size=5,
                batch_interval_seconds=2,
            )

    @patch("analytics_ingest.internal.utils.message.create_message")
    def test_add_signal_valid_and_flushed(self, mock_create_message):
        signals = [
            s
            for _ in range(10)
            for s in signal_factory(vehicle_id=self.config["vehicle_id"])
        ]

        self.client.add_signal(signals)

        self.client.signal_buffer_manager.flush()

        self.mock_buffer_manager.add_signal.assert_called_with(signals)
        self.mock_buffer_manager.flush.assert_called()

    def test_buffer_flush_on_time(self):
        signals = [
            signal_factory(vehicle_id=self.config["vehicle_id"])[0] for _ in range(3)
        ]
        self.client.add_signal(signals)

        self.client.signal_buffer_manager.flush()

        self.mock_buffer_manager.flush.assert_called()


if __name__ == "__main__":
    unittest.main()
