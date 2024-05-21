import httpx
import respx

from openai.types.chat.chat_completion import ChatCompletion

from ._base import StatelessRoute

from .._types.partials.chat import PartialChatCompletion

from .._utils.faker import faker
from .._utils.serde import json_loads, model_parse
from .._utils.time import utcnow_unix_timestamp_s

__all__ = ["ChatCompletionsCreateRoute"]


class ChatCompletionsCreateRoute(StatelessRoute[ChatCompletion, PartialChatCompletion]):
    def __init__(self, router: respx.MockRouter) -> None:
        super().__init__(
            route=router.post(url__regex="/chat/completions"),
            status_code=201,
        )

    @staticmethod
    def _build(
        partial: PartialChatCompletion,
        request: httpx.Request,
    ) -> ChatCompletion:
        content = json_loads(request.content)
        defaults: PartialChatCompletion = {
            "id": partial.get("id", faker.chat.completion.id()),
            "created": partial.get("created", utcnow_unix_timestamp_s()),
            "object": "chat.completion",
        }
        return model_parse(ChatCompletion, defaults | partial | content)
