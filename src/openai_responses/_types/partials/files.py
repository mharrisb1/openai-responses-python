from typing import List, Literal, TypedDict
from typing_extensions import NotRequired

__all__ = ["PartialFileObject", "PartialFileList", "PartialFileDeleted"]


class PartialFileObject(TypedDict):
    id: NotRequired[str]
    bytes: NotRequired[int]
    created_at: NotRequired[int]
    filename: NotRequired[str]
    object: NotRequired[Literal["file"]]
    purpose: NotRequired[
        Literal["fine-tune", "fine-tune-results", "assistants", "assistants_output"]
    ]
    status: NotRequired[Literal["uploaded", "processed", "error"]]
    status_details: NotRequired[str]


class PartialFileList(TypedDict):
    data: NotRequired[List[PartialFileObject]]
    object: NotRequired[Literal["list"]]


class PartialFileDeleted(TypedDict):
    id: NotRequired[str]
    object: NotRequired[Literal["file"]]
    deleted: NotRequired[bool]
