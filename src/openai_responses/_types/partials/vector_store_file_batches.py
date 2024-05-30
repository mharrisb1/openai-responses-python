from typing import Literal, TypedDict
from typing_extensions import NotRequired

__all__ = ["PartialVectorStoreFileBatch"]


class PartialFileCounts(TypedDict):
    cancelled: int
    completed: int
    failed: int
    in_progress: int
    total: int


class PartialVectorStoreFileBatch(TypedDict):
    id: NotRequired[str]
    created_at: NotRequired[int]
    file_counts: NotRequired[PartialFileCounts]
    object: NotRequired[Literal["vector_store.files_batch"]]
    status: NotRequired[Literal["in_progress", "completed", "cancelled", "failed"]]
    vector_store_id: NotRequired[str]
