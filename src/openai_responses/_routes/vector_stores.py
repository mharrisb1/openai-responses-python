from typing_extensions import override

import httpx
import respx

from openai.types.beta.vector_store import VectorStore

from ._base import StatefulRoute

from ..stores import StateStore
from .._types.partials.vector_stores import PartialVectorStore

from .._utils.faker import faker
from .._utils.serde import json_loads, model_dict, model_parse
from .._utils.time import utcnow_unix_timestamp_s

__all__ = ["VectorStoreCreateRoute"]


class VectorStoreCreateRoute(StatefulRoute[VectorStore, PartialVectorStore]):
    def __init__(self, router: respx.MockRouter, state: StateStore) -> None:
        super().__init__(
            route=router.post(url__regex="/vector_stores"),
            status_code=201,
            state=state,
        )

    @override
    def _handler(self, request: httpx.Request, route: respx.Route) -> httpx.Response:
        self._route = route
        model = self._build({}, request)
        self._state.beta.vector_stores.put(model)
        return httpx.Response(status_code=self._status_code, json=model_dict(model))

    @staticmethod
    def _build(partial: PartialVectorStore, request: httpx.Request) -> VectorStore:
        content = json_loads(request.content)
        defaults: PartialVectorStore = {
            "id": faker.beta.vector_store.id(),
            "created_at": utcnow_unix_timestamp_s(),
            "file_counts": {
                "cancelled": 0,
                "completed": 0,
                "failed": 0,
                "in_progress": 0,
                "total": 0,
            },
            "name": "",
            "object": "vector_store",
            "status": "completed",
            "usage_bytes": 0,
        }
        return model_parse(VectorStore, defaults | partial | content)
