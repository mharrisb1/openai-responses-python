from typing import Dict, Literal, TypedDict
from typing_extensions import NotRequired

__all__ = ["PartialVectorStore", "PartialVectorStoreDeleted"]


class PartialFileCount(TypedDict):
    cancelled: int
    completed: int
    failed: int
    in_progress: int
    total: int


class PartialExpiresAfter(TypedDict):
    anchor: Literal["last_active_at"]
    days: int


class PartialVectorStore(TypedDict):
    id: NotRequired[str]
    created_at: NotRequired[int]
    file_counts: NotRequired[PartialFileCount]
    last_active_at: NotRequired[int]
    metadata: NotRequired[Dict[str, str]]
    name: NotRequired[str]
    object: NotRequired[Literal["vector_store"]]
    status: NotRequired[Literal["expired", "in_progress", "completed"]]
    usage_bytes: NotRequired[int]
    expires_after: NotRequired[PartialExpiresAfter]
    expires_at: NotRequired[int]


class PartialVectorStoreDeleted(TypedDict):
    id: NotRequired[str]
    object: NotRequired[Literal["vector_store.deleted"]]
    deleted: NotRequired[bool]
