from typing import Optional, Type

import httpx

from openai.types.chat.chat_completion import ChatCompletion
from openai.types.create_embedding_response import CreateEmbeddingResponse

from openai.types.beta.assistant import Assistant
from openai.types.beta.thread import Thread
from openai.types.beta.threads.message import Message

from .._routes._base import Route
from .._routes.assistants import AssistantCreateRoute
from .._routes.chat import ChatCompletionsCreateRoute
from .._routes.embeddings import EmbeddingsCreateRoute
from .._routes.threads import ThreadCreateRoute
from .._routes.messages import MessageCreateRoute

from .._types.generics import M, P

from .._types.partials.assistants import PartialAssistant
from .._types.partials.chat import PartialChatCompletion
from .._types.partials.embeddings import PartialCreateEmbeddingResponse
from .._types.partials.threads import PartialThread
from .._types.partials.messages import PartialMessage

__all__ = [
    "chat_completion_from_create_request",
    "embedding_create_response_from_create_request",
    "assistant_from_create_request",
    "thread_from_create_request",
    "message_from_create_request",
]


def _generic_builder(
    route: Type[Route[M, P]],
    request: httpx.Request,
    extra: Optional[P] = None,
) -> M:
    return getattr(route, "_build")(extra or {}, request)


def chat_completion_from_create_request(
    request: httpx.Request,
    *,
    extra: Optional[PartialChatCompletion] = None,
) -> ChatCompletion:
    return _generic_builder(ChatCompletionsCreateRoute, request, extra)


def embedding_create_response_from_create_request(
    request: httpx.Request,
    *,
    extra: Optional[PartialCreateEmbeddingResponse] = None,
) -> CreateEmbeddingResponse:
    return _generic_builder(EmbeddingsCreateRoute, request, extra)


def assistant_from_create_request(
    request: httpx.Request,
    *,
    extra: Optional[PartialAssistant] = None,
) -> Assistant:
    return _generic_builder(AssistantCreateRoute, request, extra)


def thread_from_create_request(
    request: httpx.Request,
    *,
    extra: Optional[PartialThread] = None,
) -> Thread:
    return _generic_builder(ThreadCreateRoute, request, extra)


def message_from_create_request(
    thread_id: str,
    request: httpx.Request,
    *,
    extra: Optional[PartialMessage] = None,
) -> Message:
    partial: PartialMessage = {"thread_id": thread_id}
    if extra:
        partial |= extra
    return _generic_builder(MessageCreateRoute, request, partial)
