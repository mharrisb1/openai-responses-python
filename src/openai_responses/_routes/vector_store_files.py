from typing import Any
from typing_extensions import override

import httpx
import respx

from openai.pagination import SyncCursorPage
from openai.types.beta.vector_stores.vector_store_file import VectorStoreFile

from ._base import StatefulRoute

from ..stores import StateStore
from .._types.partials.vector_store_files import PartialVectorStoreFile

from .._utils.serde import json_loads, model_dict, model_parse
from .._utils.time import utcnow_unix_timestamp_s

__all__ = ["VectorStoreFileCreateRoute"]


class VectorStoreFileCreateRoute(
    StatefulRoute[VectorStoreFile, PartialVectorStoreFile]
):
    def __init__(self, router: respx.MockRouter, state: StateStore) -> None:
        super().__init__(
            route=router.post(
                url__regex=r"/vector_stores/(?P<vector_store_id>[a-zA-Z0-9\_]+)/files"
            ),
            status_code=201,
            state=state,
        )

    @override
    def _handler(
        self,
        request: httpx.Request,
        route: respx.Route,
        **kwargs: Any,
    ) -> httpx.Response:
        self._route = route

        vector_store_id = kwargs["vector_store_id"]
        found_vector_store = self._state.beta.vector_stores.get(vector_store_id)
        if not found_vector_store:
            return httpx.Response(404)

        model = self._build({"vector_store_id": vector_store_id}, request)
        found_file = self._state.files.get(model.id)
        if not found_file:
            return httpx.Response(404)

        self._state.beta.vector_stores.files.put(model)
        return httpx.Response(status_code=self._status_code, json=model_dict(model))

    @staticmethod
    def _build(
        partial: PartialVectorStoreFile,
        request: httpx.Request,
    ) -> VectorStoreFile:
        content = json_loads(request.content)
        defaults: PartialVectorStoreFile = {
            "id": content["file_id"],
            "created_at": utcnow_unix_timestamp_s(),
            "object": "vector_store.file",
            "status": "completed",
            "usage_bytes": 0,
        }
        return model_parse(VectorStoreFile, defaults | partial)
