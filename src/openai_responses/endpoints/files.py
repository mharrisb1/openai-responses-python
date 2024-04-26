import re
from typing import Any, Optional

import httpx
import respx

from openai.pagination import SyncPage
from openai.types.file_object import FileObject
from openai.types.file_deleted import FileDeleted

from ._base import StatefulMock, CallContainer
from ..decorators import side_effect
from ..state import StateStore
from ..utils import model_dict, utcnow_unix_timestamp_s


class FilesMock(StatefulMock):
    def __init__(self) -> None:
        super().__init__(
            name="files_mock",
            endpoint="/v1/files",
            route_registrations=[
                {
                    "name": "create",
                    "method": respx.post,
                    "pattern": None,
                    "side_effect": self._create,
                },
                {
                    "name": "list",
                    "method": respx.get,
                    "pattern": None,
                    "side_effect": self._list,
                },
                {
                    "name": "retrieve",
                    "method": respx.get,
                    "pattern": r"/(?P<id>\w+)",
                    "side_effect": self._retrieve,
                },
                {
                    "name": "delete",
                    "method": respx.delete,
                    "pattern": r"/(?P<id>\w+)",
                    "side_effect": self._delete,
                },
            ],
        )

        # NOTE: these are explicitly defined to help with autocomplete and type hints
        self.create = CallContainer()
        self.list = CallContainer()
        self.retrieve = CallContainer()
        self.delete = CallContainer()

    def __call__(
        self,
        *,
        latency: Optional[float] = None,
        failures: Optional[int] = None,
        state_store: Optional[StateStore] = None,
    ):
        def getter(*args: Any, **kwargs: Any):
            return dict(
                latency=latency or 0,
                failures=failures or 0,
                state_store=kwargs["used_state"],
            )

        return self._make_decorator(getter, state_store or StateStore())

    @side_effect
    def _create(
        self,
        request: httpx.Request,
        route: respx.Route,
        state_store: StateStore,
        **kwargs: Any,
    ) -> httpx.Response:
        self.create.route = route

        filename = ""
        purpose = "assistants"

        content = request.content.decode("utf-8")

        prog = re.compile(
            r'Content-Disposition: form-data;[^;]+; name="purpose"\r\n\r\n(?P<purpose_value>[^\r\n]+)|filename="(?P<filename>[^"]+)"'
        )
        matches = prog.finditer(content)
        for match in matches:
            if match.group("filename"):
                filename = match.group("filename")
            if match.group("purpose_value"):
                purpose = match.group("purpose_value")

        obj = FileObject(
            id=self._faker.file.id(),
            bytes=0,
            created_at=utcnow_unix_timestamp_s(),
            filename=filename,
            object="file",
            purpose=purpose,  # type: ignore
            status="uploaded",
        )
        state_store.files.put(obj)

        return httpx.Response(status_code=201, json=model_dict(obj))

    @side_effect
    def _list(
        self,
        request: httpx.Request,
        route: respx.Route,
        state_store: StateStore,
        **kwargs: Any,
    ) -> httpx.Response:
        self.list.route = route

        purpose = request.url.params.get("purpose")
        files = SyncPage[FileObject](
            object="list",
            data=state_store.files.list(purpose=purpose),
        )

        return httpx.Response(status_code=200, json=model_dict(files))

    @side_effect
    def _retrieve(
        self,
        request: httpx.Request,
        route: respx.Route,
        id: str,
        state_store: StateStore,
        **kwargs: Any,
    ) -> httpx.Response:
        self.retrieve.route = route

        *_, id = request.url.path.split("/")
        file = state_store.files.get(id)

        if not file:
            return httpx.Response(status_code=404)

        return httpx.Response(status_code=200, json=model_dict(file))

    @side_effect
    def _delete(
        self,
        request: httpx.Request,
        route: respx.Route,
        id: str,
        state_store: StateStore,
        **kwargs: Any,
    ) -> httpx.Response:
        self.delete.route = route

        *_, id = request.url.path.split("/")
        deleted = state_store.files.delete(id)

        return httpx.Response(
            status_code=200,
            json=model_dict(FileDeleted(id=id, deleted=deleted, object="file")),
        )
