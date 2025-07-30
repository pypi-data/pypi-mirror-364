# Copyright (c) 2025 Preisz Consulting, LLC.
# This file is part of Engramic, licensed under the Engramic Community License.
# See the LICENSE file in the project root for more details.
import json
from abc import ABC, abstractmethod
from dataclasses import asdict, dataclass
from typing import Any

from engramic.core.prompt import Prompt
from engramic.infrastructure.system.websocket_manager import WebsocketManager


class LLM(ABC):
    """
    An abstract base class that defines an interface for any Large Language Model.
    """

    @dataclass()
    class StreamPacket:
        packet: str
        finish: bool
        finish_reason: str

        def to_json(self) -> str:
            data: dict[str, Any] = asdict(self)
            json_str: str = json.dumps(data)
            return json_str

    @abstractmethod
    def submit(
        self, prompt: Prompt, images: list[str], structured_schema: dict[str, Any], args: dict[str, Any]
    ) -> dict[str, Any]:
        """
        Submits a prompt to the LLM and returns the model-generated text.

        Args:
            prompt (str): The prompt or input text for the LLM.
            **kwargs (Any): Optional keyword arguments for provider-specific settings,
                such as model name, temperature, max tokens, etc.

        Returns:
            str: The model-generated response.
        """

    @abstractmethod
    def submit_streaming(
        self, prompt: Prompt, args: dict[Any, Any], websocket_manager: WebsocketManager
    ) -> dict[str, Any]:
        """
        Submits a prompt to the LLM and returns the model-generated text.

        Args:
            prompt (str): The prompt or input text for the LLM.
            **kwargs (Any): Optional keyword arguments for provider-specific settings,
                such as model name, temperature, max tokens, etc.

        Returns:
            str: The model-generated response.
        """
