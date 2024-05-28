import sys
from typing import Any, Optional
from typing_extensions import override

import httpx
import respx
from requests_toolbelt.multipart import decoder

from openai.pagination import SyncPage
from openai.types.file_object import FileObject
from openai.types.file_deleted import FileDeleted

from ._base import StatefulRoute

from ..stores import StateStore
from .._types.partials.files import (
    PartialFileObject,
    PartialFileList,
    PartialFileDeleted,
)

from .._utils.faker import faker
from .._utils.serde import model_dict
from .._utils.time import utcnow_unix_timestamp_s


__all__ = ["FileCreateRoute", "FileListRoute", "FileRetrieveRoute", "FileDeleteRoute"]


class FileCreateRoute(StatefulRoute[FileObject, PartialFileObject]):
    def __init__(self, router: respx.MockRouter, state: StateStore) -> None:
        super().__init__(
            route=router.post(url__regex="/files"),
            status_code=201,
            state=state,
        )

    @override
    def _handler(self, request: httpx.Request, route: respx.Route) -> httpx.Response:
        self._route = route

        filename: Optional[str] = None
        purpose: Optional[str] = None
        file_content: Optional[bytes] = None

        multipart_data = decoder.MultipartDecoder(
            request.content, request.headers.get("content-type")
        )
        for part in multipart_data.parts:  # type: ignore
            content_disposition = part.headers.get(b"Content-Disposition", b"").decode()  # type: ignore
            if 'name="purpose"' in content_disposition:
                purpose = part.text  # type: ignore
            elif 'name="file"' in content_disposition:
                filename = (  # type: ignore
                    part.headers.get(b"Content-Disposition", b"")  # type: ignore
                    .decode()
                    .split("filename=")[1]
                    .strip('"')
                )
                file_content = part.content  # type: ignore

        assert filename
        assert purpose
        assert file_content

        model = FileObject(
            id=faker.file.id(),
            bytes=sys.getsizeof(file_content),  # type: ignore
            created_at=utcnow_unix_timestamp_s(),
            filename=filename,  # type: ignore
            object="file",
            purpose=purpose,  # type: ignore
            status="uploaded",
            status_details=None,
        )
        self._state.files.put(model)
        self._state.files.content.put(model.id, file_content)  # type: ignore
        return httpx.Response(
            status_code=self._status_code,
            json=model_dict(model),
        )

    @staticmethod
    def _build(partial: PartialFileObject, request: httpx.Request) -> FileObject:
        raise NotImplementedError


class FileListRoute(StatefulRoute[SyncPage[FileObject], PartialFileList]):
    def __init__(self, router: respx.MockRouter, state: StateStore) -> None:
        super().__init__(
            route=router.get(url__regex="/files"),
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


class FileRetrieveRoute(StatefulRoute[FileObject, PartialFileObject]):
    def __init__(self, router: respx.MockRouter, state: StateStore) -> None:
        super().__init__(
            route=router.get(url__regex=r"/files/(?P<file_id>[a-zA-Z0-9\-]+)"),
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
        fil_id = kwargs["file_id"]
        found = self._state.files.get(fil_id)
        if not found:
            return httpx.Response(404)

        return httpx.Response(status_code=200, json=model_dict(found))

    @staticmethod
    def _build(
        partial: PartialFileObject,
        request: httpx.Request,
    ) -> FileObject:
        raise NotImplementedError


class FileDeleteRoute(StatefulRoute[FileObject, PartialFileDeleted]):
    def __init__(self, router: respx.MockRouter, state: StateStore) -> None:
        super().__init__(
            route=router.delete(url__regex=r"/files/(?P<file_id>[a-zA-Z0-9\-]+)"),
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
        file_id = kwargs["file_id"]
        deleted = self._state.files.delete(file_id)
        return httpx.Response(
            status_code=200,
            json=model_dict(FileDeleted(id=file_id, deleted=deleted, object="file")),
        )

    @staticmethod
    def _build(
        partial: PartialFileDeleted,
        request: httpx.Request,
    ) -> FileObject:
        raise NotImplementedError


class FileRetrieveContentRoute(StatefulRoute[FileObject, PartialFileObject]):
    def __init__(self, router: respx.MockRouter, state: StateStore) -> None:
        super().__init__(
            route=router.get(url__regex=r"/files/(?P<file_id>[a-zA-Z0-9\-]+)/content"),
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
        fil_id = kwargs["file_id"]
        found = self._state.files.get(fil_id)
        if not found:
            return httpx.Response(404)

        content = self._state.files.content.get(found.id)
        assert content
        return httpx.Response(status_code=200, content=content)

    @staticmethod
    def _build(partial: PartialFileObject, request: httpx.Request) -> FileObject:
        raise NotImplementedError
