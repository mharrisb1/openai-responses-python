from typing import Optional

import httpx

from openai.types.chat.chat_completion import ChatCompletion

from ._base import _generic_builder
from ..._routes.chat import ChatCompletionsCreateRoute
from ..._types.partials.chat import PartialChatCompletion

__all__ = ["chat_completion_from_create_request"]


def chat_completion_from_create_request(
    request: httpx.Request,
    *,
    extra: Optional[PartialChatCompletion] = None,
) -> ChatCompletion:
    return _generic_builder(ChatCompletionsCreateRoute, request, extra)
