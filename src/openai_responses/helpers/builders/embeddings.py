from typing import Optional

import httpx

from openai.types.create_embedding_response import CreateEmbeddingResponse

from ._base import _generic_builder
from ..._routes.embeddings import EmbeddingsCreateRoute
from ..._types.partials.embeddings import PartialCreateEmbeddingResponse

__all__ = ["embedding_create_response_from_create_request"]


def embedding_create_response_from_create_request(
    request: httpx.Request,
    *,
    extra: Optional[PartialCreateEmbeddingResponse] = None,
) -> CreateEmbeddingResponse:
    return _generic_builder(EmbeddingsCreateRoute, request, extra)
