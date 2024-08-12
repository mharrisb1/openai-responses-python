from typing import Any, Dict

import httpx
import respx

from openai.types.chat.parsed_chat_completion import ParsedChatCompletion

from .._base import StatelessRoute

from ..._types.partials.chat import PartialParsedChatCompletion

from ..._utils.faker import faker
from ..._utils.serde import json_loads, model_parse
from ..._utils.time import utcnow_unix_timestamp_s

__all__ = ["ParsedChatCompletionsCreateRoute"]


class ParsedChatCompletionsCreateRoute(
    StatelessRoute[ParsedChatCompletion[Dict[str, Any]], PartialParsedChatCompletion]
):
    def __init__(self, router: respx.MockRouter) -> None:
        super().__init__(
            route=router.post(url__regex="/chat/completions"),
            status_code=201,
        )

    @staticmethod
    def _build(
        partial: PartialParsedChatCompletion,
        request: httpx.Request,
    ) -> ParsedChatCompletion[Dict[str, Any]]:
        content = json_loads(request.content)
        defaults: PartialParsedChatCompletion = {
            "id": partial.get("id", faker.chat.completion.id()),
            "created": partial.get("created", utcnow_unix_timestamp_s()),
            "object": "chat.completion",
        }
        return model_parse(ParsedChatCompletion[Any], defaults | partial | content)
