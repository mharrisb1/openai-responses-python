from typing import Optional

import httpx

from openai.types.beta.assistant import Assistant

from ._base import _generic_builder
from ..._routes.assistants import AssistantCreateRoute
from ..._types.partials.assistants import PartialAssistant

__all__ = ["assistant_from_create_request"]


def assistant_from_create_request(
    request: httpx.Request,
    *,
    extra: Optional[PartialAssistant] = None,
) -> Assistant:
    return _generic_builder(AssistantCreateRoute, request, extra)
