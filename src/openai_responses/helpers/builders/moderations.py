from typing import Optional

import httpx

from openai.types.moderation_create_response import ModerationCreateResponse

from ._base import _generic_builder
from ..._routes.moderation import ModerationCreateRoute
from ..._types.partials.moderation import PartialModerationCreateResponse

__all__ = ["moderation_create_response_from_create_request"]


def moderation_create_response_from_create_request(
    request: httpx.Request,
    *,
    extra: Optional[PartialModerationCreateResponse] = None,
) -> ModerationCreateResponse:
    return _generic_builder(ModerationCreateRoute, request, extra)
