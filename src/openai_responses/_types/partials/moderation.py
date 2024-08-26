from typing import List, TypedDict
from typing_extensions import NotRequired

__all__ = [
    "PartialModerationCreateResponse",
    "PartialCategories",
    "PartialCategoryScores",
]

PartialCategories = TypedDict(
    "PartialCategories",
    {
        "harassment": NotRequired[bool],
        "harassment/threatening": NotRequired[bool],
        "hate": NotRequired[bool],
        "hate/threatening": NotRequired[bool],
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
        "self-harm": NotRequired[float],
        "self-harm/instructions": NotRequired[float],
        "self-harm/intent": NotRequired[float],
        "sexual": NotRequired[float],
        "sexual/minors": NotRequired[float],
        "violence": NotRequired[float],
        "violence/graphic": NotRequired[float],
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
