from typing import Any
from typing_extensions import override

import httpx
import respx

from openai.pagination import SyncCursorPage
from openai.types.beta.threads.message import Message
from openai.types.beta.threads.message_deleted import MessageDeleted
from openai.types.beta.threads.message_update_params import MessageUpdateParams

from ._base import StatefulRoute

from ..stores import StateStore
from .._types.partials.sync_cursor_page import PartialSyncCursorPage
from .._types.partials.messages import PartialMessage, PartialMessageDeleted

from .._utils.faker import faker
from .._utils.serde import json_loads, model_dict, model_parse
from .._utils.time import utcnow_unix_timestamp_s

__all__ = [
    "MessageCreateRoute",
    "MessageListRoute",
    "MessageRetrieveRoute",
    "MessageUpdateRoute",
    "MessageDeleteRoute",
]


class MessageCreateRoute(StatefulRoute[Message, PartialMessage]):
    def __init__(self, router: respx.MockRouter, state: StateStore) -> None:
        super().__init__(
            route=router.post(
                url__regex=r"/threads/(?P<thread_id>[a-zA-Z0-9\_]+)/messages"
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
        content = json_loads(request.content)
        defaults: PartialMessage = {
            "id": faker.beta.thread.message.id(),
            "content": [],
            "created_at": utcnow_unix_timestamp_s(),
            "object": "thread.message",
            "role": "user",
            "status": "completed",
        }
        if content.get("content"):
            value = content.get("content")
            if isinstance(value, str):
                defaults["content"].append(
                    {
                        "type": "text",
                        "text": {"annotations": [], "value": value},
                    }
                )
            else:
                for block in value:
                    if block.get("type") == "text":
                        defaults["content"].append(
                            {
                                "type": "text",
                                "text": {
                                    "annotations": [],
                                    "value": block.get("text"),
                                },
                            }
                        )

            del content["content"]

        return model_parse(Message, defaults | partial | content)


class MessageListRoute(
    StatefulRoute[SyncCursorPage[Message], PartialSyncCursorPage[PartialMessage]]
):
    def __init__(self, router: respx.MockRouter, state: StateStore) -> None:
        super().__init__(
            route=router.get(
                url__regex=r"/threads/(?P<thread_id>[a-zA-Z0-9\_]+)/messages"
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
        partial: PartialSyncCursorPage[PartialMessage],
        request: httpx.Request,
    ) -> SyncCursorPage[Message]:
        raise NotImplementedError


class MessageRetrieveRoute(StatefulRoute[Message, PartialMessage]):
    def __init__(self, router: respx.MockRouter, state: StateStore) -> None:
        super().__init__(
            route=router.get(
                url__regex=r"/threads/(?P<thread_id>[a-zA-Z0-9\_]+)/messages/(?P<message_id>[a-zA-Z0-9\_]+)"
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
        found_thread = self._state.beta.threads.get(thread_id)
        if not found_thread:
            return httpx.Response(404)

        message_id = kwargs["message_id"]
        found_message = self._state.beta.threads.messages.get(message_id)
        if not found_message:
            return httpx.Response(404)

        return httpx.Response(status_code=200, json=model_dict(found_message))

    @staticmethod
    def _build(partial: PartialMessage, request: httpx.Request) -> Message:
        raise NotImplementedError


class MessageUpdateRoute(StatefulRoute[Message, PartialMessage]):
    def __init__(self, router: respx.MockRouter, state: StateStore) -> None:
        super().__init__(
            route=router.post(
                url__regex=r"/threads/(?P<thread_id>[a-zA-Z0-9\_]+)/messages/(?P<message_id>[a-zA-Z0-9\_]+)"
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
        found_thread = self._state.beta.threads.get(thread_id)
        if not found_thread:
            return httpx.Response(404)

        message_id = kwargs["message_id"]
        found_message = self._state.beta.threads.messages.get(message_id)
        if not found_message:
            return httpx.Response(404)

        content: MessageUpdateParams = json_loads(request.content)
        deserialized = model_dict(found_message)
        updated = model_parse(Message, deserialized | content)
        self._state.beta.threads.messages.put(updated)

        return httpx.Response(status_code=200, json=model_dict(updated))

    @staticmethod
    def _build(partial: PartialMessage, request: httpx.Request) -> Message:
        raise NotImplementedError


class MessageDeleteRoute(StatefulRoute[MessageDeleted, PartialMessageDeleted]):
    def __init__(self, router: respx.MockRouter, state: StateStore) -> None:
        super().__init__(
            route=router.delete(
                url__regex=r"/threads/(?P<thread_id>[a-zA-Z0-9\_]+)/messages/(?P<message_id>[a-zA-Z0-9\_]+)"
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
        found_thread = self._state.beta.threads.get(thread_id)
        if not found_thread:
            return httpx.Response(404)

        message_id = kwargs["message_id"]
        deleted = self._state.beta.threads.messages.delete(message_id)
        return httpx.Response(
            status_code=200,
            json=model_dict(
                MessageDeleted(
                    id=message_id, deleted=deleted, object="thread.message.deleted"
                )
            ),
        )

    @staticmethod
    def _build(
        partial: PartialMessageDeleted,
        request: httpx.Request,
    ) -> MessageDeleted:
        raise NotImplementedError
