from typing import Optional

import httpx
from openai.types.beta.vector_store import VectorStore

from ._base import _generic_builder
from ..._routes.vector_stores import VectorStoreCreateRoute
from ..._types.partials.vector_stores import PartialVectorStore

__all__ = ["vector_store_from_create_request"]


def vector_store_from_create_request(
    request: httpx.Request,
    *,
    extra: Optional[PartialVectorStore] = None,
) -> VectorStore:
    return _generic_builder(VectorStoreCreateRoute, request, extra)
