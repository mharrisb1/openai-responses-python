import json
from typing import Any
from typing_extensions import override

import httpx
import respx

from openai.types.beta.thread import Thread
from openai.types.beta.thread_create_params import ThreadCreateParams
from openai.types.beta.thread_update_params import ThreadUpdateParams
from openai.types.beta.thread_deleted import ThreadDeleted

from ._base import StatefulRoute

from ..helpers.builders.messages import message_from_create_request

from .._stores import StateStore
from .._types.partials.threads import PartialThread, PartialThreadDeleted

from .._utils.faker import faker
from .._utils.serde import json_loads, model_dict, model_parse
from .._utils.time import utcnow_unix_timestamp_s


__all__ = [
    "ThreadCreateRoute",
    "ThreadRetrieveRoute",
    "ThreadUpdateRoute",
    "ThreadDeleteRoute",
]


class ThreadCreateRoute(StatefulRoute[Thread, PartialThread]):
    def __init__(self, router: respx.MockRouter, state: StateStore) -> None:
        super().__init__(
            route=router.post(url__regex="/v1/threads"),
            status_code=201,
            state=state,
        )

    @override
    def _handler(self, request: httpx.Request, route: respx.Route) -> httpx.Response:
        self._route = route

        content: ThreadCreateParams = json_loads(request.content)
        model = self._build({}, request)
        self._state.beta.threads.put(model)

        for message_create_params in content.get("messages", []):
            encoded = json.dumps(message_create_params).encode("utf-8")
            create_message_req = httpx.Request(method="", url="", content=encoded)
            message = message_from_create_request(model.id, create_message_req)
            self._state.beta.threads.messages.put(message)

        return httpx.Response(
            status_code=self._status_code,
            json=model_dict(model),
        )

    @staticmethod
    def _build(partial: PartialThread, request: httpx.Request) -> Thread:
        content = json.loads(request.content)
        if content.get("messages"):
            del content["messages"]
        if content.get("tool_resources"):
            del content["tool_resources"]
        defaults: PartialThread = {
            "id": faker.beta.thread.id(),
            "created_at": utcnow_unix_timestamp_s(),
            "object": "thread",
        }
        return model_parse(Thread, defaults | partial | content)


class ThreadRetrieveRoute(StatefulRoute[Thread, PartialThread]):
    def __init__(self, router: respx.MockRouter, state: StateStore) -> None:
        super().__init__(
            route=router.get(url__regex=r"/v1/threads/(?P<id>[a-zA-Z0-9\_]+)"),
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
        id = kwargs["id"]
        found = self._state.beta.threads.get(id)
        if not found:
            return httpx.Response(404)

        return httpx.Response(status_code=200, json=model_dict(found))

    @staticmethod
    def _build(partial: PartialThread, request: httpx.Request) -> Thread:
        raise NotImplementedError


class ThreadUpdateRoute(StatefulRoute[Thread, PartialThread]):
    def __init__(self, router: respx.MockRouter, state: StateStore) -> None:
        super().__init__(
            route=router.post(
                url__regex=r"/v1/threads/(?P<id>(?!.*runs)[a-zA-Z0-9_]+)"  # NOTE: avoids match on /threads/runs
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
        id = kwargs["id"]
        found = self._state.beta.threads.get(id)
        if not found:
            return httpx.Response(404)

        content: ThreadUpdateParams = json.loads(request.content)
        deserialized = model_dict(found)
        updated = model_parse(Thread, deserialized | content)
        self._state.beta.threads.put(updated)

        return httpx.Response(status_code=200, json=model_dict(updated))

    @staticmethod
    def _build(partial: PartialThread, request: httpx.Request) -> Thread:
        raise NotImplementedError


class ThreadDeleteRoute(StatefulRoute[ThreadDeleted, PartialThreadDeleted]):
    def __init__(self, router: respx.MockRouter, state: StateStore) -> None:
        super().__init__(
            route=router.delete(url__regex=r"/v1/threads/(?P<id>[a-zA-Z0-9\_]+)"),
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
        id = kwargs["id"]
        deleted = self._state.beta.threads.delete(id)
        return httpx.Response(
            status_code=200,
            json=model_dict(
                ThreadDeleted(id=id, deleted=deleted, object="thread.deleted")
            ),
        )

    @staticmethod
    def _build(partial: PartialThreadDeleted, request: httpx.Request) -> ThreadDeleted:
        raise NotImplementedError
