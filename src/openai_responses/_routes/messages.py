import json
from typing import Any
from typing_extensions import override

import httpx
import respx

from openai.types.beta.threads.message import Message

from ._base import StatefulRoute

from .._stores import StateStore
from .._types.partials.messages import PartialMessage

from .._utils.faker import faker
from .._utils.serde import model_dict, model_parse
from .._utils.time import utcnow_unix_timestamp_s

__all__ = ["MessageCreateRoute"]


class MessageCreateRoute(StatefulRoute[Message, PartialMessage]):
    def __init__(self, router: respx.MockRouter, state: StateStore) -> None:
        super().__init__(
            route=router.post(
                url__regex=r"/v1/threads/(?P<thread_id>[a-zA-Z0-9\_]+)/messages"
            ),
            status_code=201,
            state=state,
        )

    @override
    def _handler(
        self,
        request: httpx.Request,
        route: respx.Route,
        **kwargs: Any,
    ) -> httpx.Response:
        self._route = route
        thread_id = kwargs["thread_id"]
        found = self._state.beta.threads.get(thread_id)
        if not found:
            return httpx.Response(404)

        model = self._build({"thread_id": thread_id}, request)
        self._state.beta.threads.messages.put(model)
        return httpx.Response(
            status_code=self._status_code,
            json=model_dict(model),
        )

    @staticmethod
    def _build(partial: PartialMessage, request: httpx.Request) -> Message:
        content = json.loads(request.content)
        defaults: PartialMessage = {
            "id": faker.beta.thread.message.id(),
            "content": [],
            "created_at": utcnow_unix_timestamp_s(),
            "object": "thread.message",
            "role": "user",
            "status": "completed",
            "thread_id": faker.beta.thread.id(),
        }
        return model_parse(Message, content | partial | defaults)
