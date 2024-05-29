from typing import Generic, TypeVar
from typing_extensions import NotRequired, TypedDict

S = TypeVar("S")

__all__ = ["PartialResourceDeleted"]


class PartialResourceDeleted(TypedDict, Generic[S]):
    id: NotRequired[str]
    object: NotRequired[S]
    deleted: NotRequired[bool]
