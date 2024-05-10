from typing import Optional

import httpx

from openai.types.beta.threads.message import Message

from ._base import _generic_builder
from ..._routes.messages import MessageCreateRoute
from ..._types.partials.messages import PartialMessage

__all__ = ["message_from_create_request"]


def message_from_create_request(
    thread_id: str,
    request: httpx.Request,
    *,
    extra: Optional[PartialMessage] = None,
) -> Message:
    partial: PartialMessage = {"thread_id": thread_id}
    if extra:
        partial |= extra
    return _generic_builder(MessageCreateRoute, request, partial)
