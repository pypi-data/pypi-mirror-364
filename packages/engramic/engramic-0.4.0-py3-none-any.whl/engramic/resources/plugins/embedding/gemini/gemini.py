# Copyright (c) 2025 Preisz Consulting, LLC.
# This file is part of Engramic, licensed under the Engramic Community License.
# See the LICENSE file in the project root for more details.


import os
from typing import Any, cast

from google import genai
from google.genai import types

from engramic.core.interface.embedding import Embedding
from engramic.infrastructure.system.plugin_specifications import embedding_impl


class Gemini(Embedding):
    def __init__(self) -> None:
        api_key = os.environ.get('GEMINI_API_KEY')
        self._api_client = genai.Client(api_key=api_key)

    @embedding_impl
    def gen_embed(self, strings: list[str], args: dict[str, Any]) -> dict[str, list[list[float]]]:
        result = self._api_client.models.embed_content(
            model=args['model'],
            contents=strings,
            config=types.EmbedContentConfig(task_type='RETRIEVAL_QUERY', output_dimensionality=args['dimensions']),
        )

        if not result.embeddings:
            error = 'Embeddings returned None result'
            raise RuntimeError(error)

        for float_array in result.embeddings:
            if float_array.values is None:
                error = 'Found None in embedding values'
                raise RuntimeError(error)

        # cast to satisfy type checker
        float_ret_array = [cast(list[float], float_array.values) for float_array in result.embeddings]

        return {'embeddings_list': float_ret_array}
