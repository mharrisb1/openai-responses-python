from typing import Optional, Type

import httpx

from openai.types.chat.chat_completion import ChatCompletion

from .._routes.base import Route
from .._routes.chat import ChatCompletionsCreateRoute

from .._types.generics import M, P
from .._types.partials.chat import PartialChatCompletion

__all__ = ["chat_completion_from_create_request"]


def _abstract_builder(
    route: Type[Route[M, P]],
    request: httpx.Request,
    *,
    extra: Optional[P] = None,
) -> M:
    return getattr(route, "_build")(extra or {}, request)


def chat_completion_from_create_request(
    request: httpx.Request,
    *,
    extra: Optional[PartialChatCompletion] = None,
) -> ChatCompletion:
    return _abstract_builder(ChatCompletionsCreateRoute, request, extra=extra)
