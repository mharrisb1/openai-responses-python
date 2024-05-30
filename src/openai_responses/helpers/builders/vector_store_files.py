from typing import Optional

import httpx
from openai.types.beta.vector_stores.vector_store_file import VectorStoreFile

from ._base import _generic_builder
from ..._routes.vector_store_files import VectorStoreFileCreateRoute
from ..._types.partials.vector_store_files import PartialVectorStoreFile

__all__ = ["vector_store_file_from_create_request"]


def vector_store_file_from_create_request(
    request: httpx.Request,
    *,
    extra: Optional[PartialVectorStoreFile] = None,
) -> VectorStoreFile:
    return _generic_builder(VectorStoreFileCreateRoute, request, extra)
