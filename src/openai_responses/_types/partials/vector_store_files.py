from typing import Literal, TypedDict

from typing_extensions import NotRequired

__all__ = ["PartialVectorStoreFile"]


class PartialLastError(TypedDict):
    code: Literal[
        "internal_error",
        "file_not_found",
        "parsing_error",
        "unhandled_mime_type",
    ]
    message: str


class PartialVectorStoreFile(TypedDict):
    id: NotRequired[str]
    created_at: NotRequired[int]
    last_error: NotRequired[PartialLastError]
    object: NotRequired[Literal["vector_store.file"]]
    status: NotRequired[Literal["in_progress", "completed", "cancelled", "failed"]]
    usage_bytes: NotRequired[int]
    vector_store_id: NotRequired[str]
