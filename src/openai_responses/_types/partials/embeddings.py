from typing import List, Literal, TypedDict
from typing_extensions import NotRequired

__all__ = ["PartialCreateEmbeddingResponse"]


class PartialEmbedding(TypedDict):
    embedding: List[float]
    index: int
    object: Literal["embedding"]


class PartialUsage(TypedDict):
    prompt_tokens: int
    total_tokens: int


class PartialCreateEmbeddingResponse(TypedDict):
    data: NotRequired[List[PartialEmbedding]]
    model: NotRequired[str]
    object: NotRequired[Literal["list"]]
    usage: NotRequired[PartialUsage]
