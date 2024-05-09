import json
from typing import Any
from typing_extensions import override

import httpx
import respx

from openai.pagination import SyncCursorPage
from openai.types.beta.threads.message import Message

from ._base import StatefulRoute

from .._stores import StateStore
from .._types.partials.messages import PartialMessage, PartialMessageList

from .._utils.faker import faker
from .._utils.serde import model_dict, model_parse
from .._utils.time import utcnow_unix_timestamp_s

__all__ = ["MessageCreateRoute", "MessageListRoute"]


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
        }
        if content.get("content"):
            defaults["content"].append(
                {
                    "type": "text",
                    "text": {"annotations": [], "value": content.get("content")},
                }
            )
            del content["content"]
        return model_parse(Message, defaults | partial | content)


class MessageListRoute(StatefulRoute[SyncCursorPage[Message], PartialMessageList]):
    def __init__(self, router: respx.MockRouter, state: StateStore) -> None:
        super().__init__(
            route=router.get(
                url__regex=r"/v1/threads/(?P<thread_id>[a-zA-Z0-9\_]+)/messages"
            ),
            status_code=200,
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

        limit = request.url.params.get("limit")
        order = request.url.params.get("order")
        after = request.url.params.get("after")
        before = request.url.params.get("before")
        run_id = request.url.params.get("run_id")

        data = self._state.beta.threads.messages.list(
            thread_id,
            limit,
            order,
            after,
            before,
            run_id,
        )
        result_count = len(data)
        total_count = len(self._state.beta.threads.messages.list(thread_id))
        has_data = bool(result_count)
        has_more = total_count != result_count
        first_id = data[0].id if has_data else None
        last_id = data[-1].id if has_data else None
        model = SyncCursorPage[Message](data=data)
        return httpx.Response(
            status_code=200,
            json=model_dict(model)
            | {"first_id": first_id, "last_id": last_id, "has_more": has_more},
        )

    @staticmethod
    def _build(
        partial: PartialMessageList,
        request: httpx.Request,
    ) -> SyncCursorPage[Message]:
        raise NotImplementedError
