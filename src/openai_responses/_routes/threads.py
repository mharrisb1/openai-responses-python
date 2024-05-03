import json
from typing import Any
from typing_extensions import override

import httpx
import respx

from openai.types.beta.thread import Thread

from ._base import StatefulRoute

from .._stores import StateStore
from .._types.partials.threads import PartialThread

from .._utils.faker import faker
from .._utils.serde import model_dict, model_parse
from .._utils.time import utcnow_unix_timestamp_s


__all__ = ["ThreadCreateRoute", "ThreadRetrieveRoute"]


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
        model = self._build({}, request)
        self._state.beta.threads.put(model)
        return httpx.Response(
            status_code=self._status_code,
            json=model_dict(model),
        )

    @staticmethod
    def _build(partial: PartialThread, request: httpx.Request) -> Thread:
        content = json.loads(request.content)
        defaults: PartialThread = {
            "id": faker.beta.thread.id(),
            "created_at": utcnow_unix_timestamp_s(),
            "object": "thread",
        }
        return model_parse(Thread, content | partial | defaults)


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
