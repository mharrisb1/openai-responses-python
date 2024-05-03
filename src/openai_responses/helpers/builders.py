from typing import Optional, Type

import httpx

from openai.types.chat.chat_completion import ChatCompletion
from openai.types.create_embedding_response import CreateEmbeddingResponse

from openai.types.beta.assistant import Assistant

from .._routes._base import Route
from .._routes.assistants import AssistantCreateRoute
from .._routes.chat import ChatCompletionsCreateRoute
from .._routes.embeddings import EmbeddingsCreateRoute

from .._types.generics import M, P

from .._types.partials.assistants import PartialAssistant
from .._types.partials.chat import PartialChatCompletion
from .._types.partials.embeddings import PartialCreateEmbeddingResponse

__all__ = [
    "chat_completion_from_create_request",
    "embedding_create_response_from_create_request",
]


def _abstract_builder(
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
    return _abstract_builder(ChatCompletionsCreateRoute, request, extra)


def embedding_create_response_from_create_request(
    request: httpx.Request,
    *,
    extra: Optional[PartialCreateEmbeddingResponse] = None,
) -> CreateEmbeddingResponse:
    return _abstract_builder(EmbeddingsCreateRoute, request, extra)


def assistant_from_create_request(
    request: httpx.Request,
    *,
    extra: Optional[PartialAssistant] = None,
) -> Assistant:
    return _abstract_builder(AssistantCreateRoute, request, extra)
