from typing import Generic, List, Literal, TypedDict, TypeVar
from typing_extensions import NotRequired

M = TypeVar("M")

__all__ = ["PartialSyncCursorPage"]


class PartialSyncCursorPage(TypedDict, Generic[M]):
    object: NotRequired[Literal["list"]]
    data: NotRequired[List[M]]
    first_id: NotRequired[str]
    last_id: NotRequired[str]
    has_more: NotRequired[bool]
