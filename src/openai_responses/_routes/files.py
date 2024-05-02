import re

import httpx
import respx

from openai.types.file_object import FileObject

from .base import StatefulRoute

from .._stores import StateStore
from .._types.partials.files import PartialFileObject

from .._utils.faker import faker
from .._utils.time import utcnow_unix_timestamp_s


class FileCreateRoute(StatefulRoute[FileObject, PartialFileObject]):
    def __init__(self, router: respx.MockRouter, state: StateStore) -> None:
        super().__init__(
            route=respx.post(url__regex="/v1/files"),
            status_code=201,
            state=state,
        )

    @staticmethod
    def _build(partial: PartialFileObject, request: httpx.Request) -> FileObject:
        content = request.content.decode("utf-8")

        filename = ""
        purpose = "assistants"

        # FIXME: hacky
        prog = re.compile(
            r'Content-Disposition: form-data;[^;]+; name="purpose"\r\n\r\n(?P<purpose_value>[^\r\n]+)|filename="(?P<filename>[^"]+)"'
        )
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
