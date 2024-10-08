import httpx
import respx

from openai.types.moderation import (
    Moderation,
    Categories,
    CategoryScores,
    CategoryAppliedInputTypes,
)
from openai.types.moderation_create_response import ModerationCreateResponse

from ._base import StatelessRoute

from .._types.partials.moderation import (
    PartialModerationCreateResponse,
    PartialCategories,
    PartialCategoryScores,
    PartialCategoryAppliedInputTypes,
)

from .._utils.serde import model_parse
from .._utils.faker import faker

__all__ = ["ModerationCreateRoute"]

_default_categories: PartialCategories = {
    "harassment": False,
    "harassment/threatening": False,
    "hate": False,
    "hate/threatening": False,
    "illicit": False,
    "illicit/violent": False,
    "self-harm": False,
    "self-harm/instructions": False,
    "self-harm/intent": False,
    "sexual": False,
    "sexual/minors": False,
    "violence": False,
    "violence/graphic": False,
}

_default_category_scores: PartialCategoryScores = {
    "harassment": 0.0,
    "harassment/threatening": 0.0,
    "hate": 0.0,
    "hate/threatening": 0.0,
    "illicit": 0.0,
    "illicit/violent": 0.0,
    "self-harm": 0.0,
    "self-harm/instructions": 0.0,
    "self-harm/intent": 0.0,
    "sexual": 0.0,
    "sexual/minors": 0.0,
    "violence": 0.0,
    "violence/graphic": 0.0,
}

_default_category_applied_input_types: PartialCategoryAppliedInputTypes = {
    "harassment": [],
    "harassment/threatening": [],
    "hate": [],
    "hate/threatening": [],
    "illicit": [],
    "illicit/violent": [],
    "self-harm": [],
    "self-harm/instructions": [],
    "self-harm/intent": [],
    "sexual": [],
    "sexual/minors": [],
    "violence": [],
    "violence/graphic": [],
}


class ModerationCreateRoute(
    StatelessRoute[ModerationCreateResponse, PartialModerationCreateResponse]
):
    def __init__(self, router: respx.MockRouter) -> None:
        super().__init__(route=router.post(url__regex="/moderations"), status_code=200)

    @staticmethod
    def _build(
        partial: PartialModerationCreateResponse, request: httpx.Request
    ) -> ModerationCreateResponse:
        partial_results = partial.get("results", [])
        moderation_results = [
            Moderation(
                categories=model_parse(
                    Categories,
                    _default_categories
                    | partial_result.get("categories", _default_categories),
                ),
                category_applied_input_types=model_parse(
                    CategoryAppliedInputTypes,
                    _default_category_applied_input_types,
                ),
                category_scores=model_parse(
                    CategoryScores,
                    _default_category_scores
                    | partial_result.get("category_scores", _default_category_scores),
                ),
                flagged=partial_result.get("flagged", False),
            )
            for partial_result in partial_results
        ]

        return ModerationCreateResponse(
            id=partial.get("id", faker.moderation.id()),
            model=partial.get("model", "text-moderation-007"),
            results=moderation_results,
        )
