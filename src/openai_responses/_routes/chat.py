import json
from typing import Any

import httpx
import respx

from openai.types.chat.chat_completion import ChatCompletion, Choice
from openai.types.chat.completion_create_params import CompletionCreateParams

from .base import Route

from .._types.partials.chat import PartialChatCompletion

from .._utils.faker import faker
from .._utils.filter import remove_none
from .._utils.serde import model_dict, model_parse
from .._utils.time import utcnow_unix_timestamp_s
from .._utils.token import add_token_usage_for_completion

__all__ = ["ChatCompletionsCreateRoute"]


class ChatCompletionsCreateRoute(Route[ChatCompletion, PartialChatCompletion]):
    def __init__(self, router: respx.MockRouter) -> None:
        super().__init__(
            route=router.post(url__regex="/v1/chat/completions"),
            status_code=201,
        )

    def _handler(
        self,
        request: httpx.Request,
        route: respx.Route,
        **kwargs: Any,
    ) -> httpx.Response:
        self._route = route
        completion = self._build({}, request)
        return httpx.Response(
            status_code=self._status_code,
            json=model_dict(completion),
        )

    @staticmethod
    def _build(
        partial: PartialChatCompletion,
        request: httpx.Request,
    ) -> ChatCompletion:
        content: CompletionCreateParams = json.loads(request.content)
        choices = partial.get("choices", [])
        completion = ChatCompletion(
            id=partial.get("id", faker.chat.completion.id()),
            choices=remove_none([model_parse(Choice, c) for c in choices]),
            created=partial.get("created", utcnow_unix_timestamp_s()),
            model=content["model"],
            system_fingerprint=partial.get("system_fingerprint", ""),
            object="chat.completion",
        )

        add_token_usage_for_completion(completion, content)

        return completion
