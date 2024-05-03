import re
from typing_extensions import override

import httpx
import respx

from openai.pagination import SyncPage
from openai.types.file_object import FileObject

from .base import StatefulRoute

from .._stores import StateStore
from .._types.partials.files import PartialFileObject, PartialFileList

from .._utils.faker import faker
from .._utils.serde import model_dict
from .._utils.time import utcnow_unix_timestamp_s

REGEXP_FILE = r'Content-Disposition: form-data;[^;]+; name="purpose"\r\n\r\n(?P<purpose_value>[^\r\n]+)|filename="(?P<filename>[^"]+)"'


class FileCreateRoute(StatefulRoute[FileObject, PartialFileObject]):
    def __init__(self, router: respx.MockRouter, state: StateStore) -> None:
        super().__init__(
            route=router.post(url__regex="/v1/files"),
            status_code=201,
            state=state,
        )

    @override
    def _handler(self, request: httpx.Request, route: respx.Route) -> httpx.Response:
        self._route = route
        model = self._build({}, request)
        self._state.files.put(model)
        return httpx.Response(
            status_code=self._status_code,
            json=model_dict(model),
        )

    @staticmethod
    def _build(partial: PartialFileObject, request: httpx.Request) -> FileObject:
        content = request.content.decode("utf-8")

        filename = ""
        purpose = "assistants"

        # FIXME: hacky
        prog = re.compile(REGEXP_FILE)
        matches = prog.finditer(content)
        for match in matches:
            if match.group("filename"):
                filename = match.group("filename")
            if match.group("purpose_value"):
                purpose = match.group("purpose_value")

        return FileObject(
            id=partial.get("id", faker.file.id()),
            bytes=partial.get("bytes", 0),
            created_at=partial.get("created_at", utcnow_unix_timestamp_s()),
            filename=partial.get("filename", filename),
            object="file",
            purpose=partial.get("purpose", purpose),  # type: ignore
            status=partial.get("status", "uploaded"),
            status_details=partial.get("status_details"),
        )


class FileListRoute(StatefulRoute[SyncPage[FileObject], PartialFileList]):
    def __init__(self, router: respx.MockRouter, state: StateStore) -> None:
        super().__init__(
            route=router.get(url__regex="/v1/files"),
            status_code=200,
            state=state,
        )

    @override
    def _handler(self, request: httpx.Request, route: respx.Route) -> httpx.Response:
        self._route = route
        purpose = request.url.params.get("purpose")
        files = SyncPage[FileObject](
            object="list",
            data=self._state.files.list(purpose=purpose),
        )
        return httpx.Response(status_code=200, json=model_dict(files))

    @staticmethod
    def _build(
        partial: PartialFileList,
        request: httpx.Request,
    ) -> SyncPage[FileObject]:
        raise NotImplementedError
