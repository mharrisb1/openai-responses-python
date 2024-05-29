from typing import Any, Literal
from typing_extensions import override

import httpx
import respx

from openai.pagination import SyncCursorPage
from openai.types.beta.vector_stores.vector_store_file import VectorStoreFile
from openai.types.beta.vector_stores.vector_store_file_deleted import (
    VectorStoreFileDeleted,
)

from ._base import StatefulRoute

from ..stores import StateStore
from .._types.partials.deleted import PartialResourceDeleted
from .._types.partials.sync_cursor_page import PartialSyncCursorPage
from .._types.partials.vector_store_files import PartialVectorStoreFile

from .._utils.serde import json_loads, model_dict, model_parse
from .._utils.time import utcnow_unix_timestamp_s

__all__ = [
    "VectorStoreFileCreateRoute",
    "VectorStoreFileListRoute",
    "VectorStoreFileRetrieveRoute",
    "VectorStoreFileDeleteRoute",
]


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


class VectorStoreFileListRoute(
    StatefulRoute[
        SyncCursorPage[VectorStoreFile], PartialSyncCursorPage[PartialVectorStoreFile]
    ]
):
    def __init__(self, router: respx.MockRouter, state: StateStore) -> None:
        super().__init__(
            route=router.get(
                url__regex=r"/vector_stores/(?P<vector_store_id>[a-zA-Z0-9\_]+)/files"
            ),
            status_code=200,
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

        limit = request.url.params.get("limit")
        order = request.url.params.get("order")
        after = request.url.params.get("after")
        before = request.url.params.get("before")
        filter = request.url.params.get("filter")

        data = self._state.beta.vector_stores.files.list(
            vector_store_id,
            limit,
            order,
            after,
            before,
            filter,
        )
        result_count = len(data)
        total_count = len(self._state.beta.vector_stores.files.list(vector_store_id))
        has_data = bool(result_count)
        has_more = total_count != result_count
        first_id = data[0].id if has_data else None
        last_id = data[-1].id if has_data else None
        model = SyncCursorPage[VectorStoreFile](data=data)
        return httpx.Response(
            status_code=200,
            json=model_dict(model)
            | {"first_id": first_id, "last_id": last_id, "has_more": has_more},
        )

    @staticmethod
    def _build(
        partial: PartialSyncCursorPage[PartialVectorStoreFile],
        request: httpx.Request,
    ) -> SyncCursorPage[VectorStoreFile]:
        raise NotImplementedError


class VectorStoreFileRetrieveRoute(
    StatefulRoute[VectorStoreFile, PartialVectorStoreFile]
):
    def __init__(self, router: respx.MockRouter, state: StateStore) -> None:
        super().__init__(
            route=router.get(
                url__regex=r"/vector_stores/(?P<vector_store_id>[a-zA-Z0-9\_]+)/files/(?P<file_id>[a-zA-Z0-9\-]+)"
            ),
            status_code=200,
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

        file_id = kwargs["file_id"]
        found = self._state.beta.vector_stores.files.get(file_id)
        if not found:
            return httpx.Response(404)

        return httpx.Response(status_code=self._status_code, json=model_dict(found))

    @staticmethod
    def _build(
        partial: PartialVectorStoreFile,
        request: httpx.Request,
    ) -> VectorStoreFile:
        raise NotImplementedError


class VectorStoreFileDeleteRoute(
    StatefulRoute[
        VectorStoreFileDeleted,
        PartialResourceDeleted[Literal["vector_store.file.deleted"]],
    ]
):
    def __init__(self, router: respx.MockRouter, state: StateStore) -> None:
        super().__init__(
            route=router.delete(
                url__regex=r"/vector_stores/(?P<vector_store_id>[a-zA-Z0-9\_]+)/files/(?P<file_id>[a-zA-Z0-9\-]+)"
            ),
            status_code=200,
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

        file_id = kwargs["file_id"]
        found = self._state.beta.vector_stores.files.get(file_id)
        if not found:
            return httpx.Response(404)

        deleted = self._state.beta.vector_stores.files.delete(file_id)

        return httpx.Response(
            status_code=200,
            json=model_dict(
                VectorStoreFileDeleted(
                    id=file_id,
                    deleted=deleted,
                    object="vector_store.file.deleted",
                )
            ),
        )

    @staticmethod
    def _build(
        partial: PartialResourceDeleted[Literal["vector_store.file.deleted"]],
        request: httpx.Request,
    ) -> VectorStoreFileDeleted:
        raise NotImplementedError
