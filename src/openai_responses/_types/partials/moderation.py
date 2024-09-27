from typing import List, Literal, TypedDict
from typing_extensions import NotRequired

__all__ = [
    "PartialModerationCreateResponse",
    "PartialCategories",
    "PartialCategoryScores",
    "PartialCategoryAppliedInputTypes",
]

PartialCategories = TypedDict(
    "PartialCategories",
    {
        "harassment": NotRequired[bool],
        "harassment/threatening": NotRequired[bool],
        "hate": NotRequired[bool],
        "hate/threatening": NotRequired[bool],
        "illicit": NotRequired[bool],
        "illicit/violent": NotRequired[bool],
        "self-harm": NotRequired[bool],
        "self-harm/instructions": NotRequired[bool],
        "self-harm/intent": NotRequired[bool],
        "sexual": NotRequired[bool],
        "sexual/minors": NotRequired[bool],
        "violence": NotRequired[bool],
        "violence/graphic": NotRequired[bool],
    },
)

PartialCategoryScores = TypedDict(
    "PartialCategoryScores",
    {
        "harassment": NotRequired[float],
        "harassment/threatening": NotRequired[float],
        "hate": NotRequired[float],
        "hate/threatening": NotRequired[float],
        "illicit": NotRequired[float],
        "illicit/violent": NotRequired[float],
        "self-harm": NotRequired[float],
        "self-harm/instructions": NotRequired[float],
        "self-harm/intent": NotRequired[float],
        "sexual": NotRequired[float],
        "sexual/minors": NotRequired[float],
        "violence": NotRequired[float],
        "violence/graphic": NotRequired[float],
    },
)

PartialCategoryAppliedInputTypes = TypedDict(
    "PartialCategoryAppliedInputTypes",
    {
        "harassment": NotRequired[List[Literal["text"]]],
        "harassment/threatening": NotRequired[List[Literal["text"]]],
        "hate": NotRequired[List[Literal["text"]]],
        "hate/threatening": NotRequired[List[Literal["text"]]],
        "illicit": NotRequired[List[Literal["text"]]],
        "illicit/violent": NotRequired[List[Literal["text"]]],
        "self-harm": NotRequired[List[Literal["text", "image"]]],
        "self-harm/instructions": NotRequired[List[Literal["text", "image"]]],
        "self-harm/intent": NotRequired[List[Literal["text", "image"]]],
        "sexual": NotRequired[List[Literal["text", "image"]]],
        "sexual/minors": NotRequired[List[Literal["text"]]],
        "violence": NotRequired[List[Literal["text", "image"]]],
        "violence/graphic": NotRequired[List[Literal["text", "image"]]],
    },
)


class PartialModeration(TypedDict):
    categories: NotRequired[PartialCategories]
    category_scores: NotRequired[PartialCategoryScores]
    flagged: NotRequired[bool]


class PartialModerationCreateResponse(TypedDict):
    id: NotRequired[str]
    model: NotRequired[str]
    results: NotRequired[List[PartialModeration]]
