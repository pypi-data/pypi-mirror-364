# Copyright (c) 2025 Preisz Consulting, LLC.
# This file is part of Engramic, licensed under the Engramic Community License.
# See the LICENSE file in the project root for more details.

import logging
import sys
from typing import Any

import pytest

from engramic.application.consolidate.consolidate_service import ConsolidateService
from engramic.application.message.message_service import MessageService
from engramic.core.host import Host
from engramic.infrastructure.system.service import Service

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logging.info('Using Python interpreter:%s', sys.executable)


class MiniService(Service):
    def __init__(self, host) -> None:
        self.callback_ctr = 0
        self.index_create_count = 0
        self.index_complete_count = 0
        self.engram_create_count = 0
        self.engram_complete_count = 0
        super().__init__(host)

    def start(self) -> None:
        super().start()
        self.subscribe(Service.Topic.ENGRAM_COMPLETE, self.on_engrams_complete)
        self.subscribe(Service.Topic.ENGRAMS_CREATED, self.on_engrams_created)
        self.subscribe(Service.Topic.INDICES_COMPLETE, self.on_indices_complete)
        self.subscribe(Service.Topic.INDICES_CREATED, self.on_indices_created)

        self.run_task(self.send_messages())

    async def send_messages(self) -> None:
        observation = self.host.mock_data_collector['CodifyService--output']
        self.send_message_async(Service.Topic.OBSERVATION_COMPLETE, observation)

    def on_engrams_created(self, message_in: dict[str, Any]) -> None:
        self.engram_create_count += len(message_in['engram_id_array'])

        self.tracking_id = message_in['tracking_id']

    def on_engrams_complete(self, generated_response_in) -> None:
        expected_results = self.host.mock_data_collector[f'ConsolidateService-{self.tracking_id}-output'][
            'engram_array'
        ]
        generated_response = generated_response_in['engram_array']

        for msg in generated_response:
            logging.debug(msg['id'])

        assert len(generated_response) == len(expected_results), (
            f'Result count mismatch: ' f'{len(generated_response)} generated vs {len(expected_results)} expected'
        )

        # Created date is expected to be different.
        # Indices don't compare well because of floats.
        def strip_fields(data):
            return [{k: v for k, v in item.items() if k not in {'created_date', 'indices'}} for item in data]

        stripped_generated = strip_fields(generated_response)
        stripped_expected = strip_fields(expected_results)

        gen_str = str(stripped_generated)
        exp_str = str(stripped_expected)

        assert gen_str == exp_str

        if generated_response_in['tracking_id'] == self.tracking_id:
            self.engram_complete_count += len(generated_response)

            if (
                self.engram_create_count == self.engram_complete_count
                and self.index_create_count == self.index_complete_count
            ):
                self.host.shutdown()

    def on_indices_created(self, message_in: dict[str, Any]) -> None:
        self.index_create_count += len(message_in['index_id_array'])

    def on_indices_complete(self, message_in: dict[str, Any]) -> None:
        self.index_complete_count += len(message_in['index'])

        if (
            self.engram_create_count == self.engram_complete_count
            and self.index_create_count == self.index_complete_count
        ):
            self.host.shutdown()


@pytest.mark.timeout(100)  # seconds
def test_consolidate_service_submission() -> None:
    host = Host('mock', [MessageService, ConsolidateService, MiniService])

    host.wait_for_shutdown()
