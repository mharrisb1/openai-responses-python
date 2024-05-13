from typing import Optional

import httpx

from openai.types.beta.threads.message import Message

from ._base import _generic_builder
from ..._routes.messages import MessageCreateRoute
from ..._types.partials.messages import PartialMessage

from ..._utils.faker import faker
from ..._utils.serde import model_parse
from ..._utils.time import utcnow_unix_timestamp_s

__all__ = ["message_from_create_request", "build_message"]


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


def build_message(partial: PartialMessage) -> Message:
    default: PartialMessage = {
        "id": faker.beta.thread.message.id(),
        "created_at": utcnow_unix_timestamp_s(),
        "object": "thread.message",
    }
    return model_parse(Message, default | partial)
