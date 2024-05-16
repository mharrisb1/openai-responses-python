from typing import Any
from typing_extensions import override

import httpx
import respx

from openai.pagination import SyncCursorPage
from openai.types.beta.assistant import Assistant
from openai.types.beta.assistant_deleted import AssistantDeleted
from openai.types.beta.assistant_update_params import AssistantUpdateParams

from ._base import StatefulRoute

from .._stores import StateStore
from .._types.partials.assistants import (
    PartialAssistant,
    PartialAssistantList,
    PartialAssistantDeleted,
)

from .._utils.faker import faker
from .._utils.serde import json_loads, model_dict, model_parse
from .._utils.time import utcnow_unix_timestamp_s

__all__ = [
    "AssistantCreateRoute",
    "AssistantListRoute",
    "AssistantRetrieveRoute",
    "AssistantUpdateRoute",
    "AssistantDeleteRoute",
]


class AssistantCreateRoute(StatefulRoute[Assistant, PartialAssistant]):
    def __init__(self, router: respx.MockRouter, state: StateStore) -> None:
        super().__init__(
            route=router.post(url__regex="/v1/assistants"),
            status_code=201,
            state=state,
        )

    @override
    def _handler(self, request: httpx.Request, route: respx.Route) -> httpx.Response:
        self._route = route
        model = self._build({}, request)
        self._state.beta.assistants.put(model)
        return httpx.Response(
            status_code=self._status_code,
            json=model_dict(model),
        )

    @staticmethod
    def _build(partial: PartialAssistant, request: httpx.Request) -> Assistant:
        content = json_loads(request.content)
        defaults: PartialAssistant = {
            "id": faker.beta.assistant.id(),
            "created_at": utcnow_unix_timestamp_s(),
            "tools": [],
            "object": "assistant",
        }
        return model_parse(Assistant, defaults | partial | content)


class AssistantListRoute(
    StatefulRoute[SyncCursorPage[Assistant], PartialAssistantList]
):
    def __init__(self, router: respx.MockRouter, state: StateStore) -> None:
        super().__init__(
            route=router.get(url__regex="/v1/assistants"),
            status_code=200,
            state=state,
        )

    @override
    def _handler(self, request: httpx.Request, route: respx.Route) -> httpx.Response:
        self._route = route

        limit = request.url.params.get("limit")
        order = request.url.params.get("order")
        after = request.url.params.get("after")
        before = request.url.params.get("before")

        data = self._state.beta.assistants.list(limit, order, after, before)
        result_count = len(data)
        total_count = len(self._state.beta.assistants.list())
        has_data = bool(result_count)
        has_more = total_count != result_count
        first_id = data[0].id if has_data else None
        last_id = data[-1].id if has_data else None
        model = SyncCursorPage[Assistant](data=data)
        return httpx.Response(
            status_code=200,
            json=model_dict(model)
            | {"first_id": first_id, "last_id": last_id, "has_more": has_more},
        )

    @staticmethod
    def _build(
        partial: PartialAssistantList,
        request: httpx.Request,
    ) -> SyncCursorPage[Assistant]:
        raise NotImplementedError


class AssistantRetrieveRoute(StatefulRoute[Assistant, PartialAssistant]):
    def __init__(self, router: respx.MockRouter, state: StateStore) -> None:
        super().__init__(
            route=router.get(url__regex=r"/v1/assistants/(?P<id>[a-zA-Z0-9\_]+)"),
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
        found = self._state.beta.assistants.get(id)
        if not found:
            return httpx.Response(404)

        return httpx.Response(status_code=200, json=model_dict(found))

    @staticmethod
    def _build(partial: PartialAssistant, request: httpx.Request) -> Assistant:
        raise NotImplementedError


class AssistantUpdateRoute(StatefulRoute[Assistant, PartialAssistant]):
    def __init__(self, router: respx.MockRouter, state: StateStore) -> None:
        super().__init__(
            route=router.post(url__regex=r"/v1/assistants/(?P<id>[a-zA-Z0-9\_]+)"),
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
        found = self._state.beta.assistants.get(id)
        if not found:
            return httpx.Response(404)

        content: AssistantUpdateParams = json_loads(request.content)
        deserialized = model_dict(found)
        updated = model_parse(Assistant, deserialized | content)
        self._state.beta.assistants.put(updated)

        return httpx.Response(status_code=200, json=model_dict(updated))

    @staticmethod
    def _build(partial: PartialAssistant, request: httpx.Request) -> Assistant:
        raise NotImplementedError


class AssistantDeleteRoute(StatefulRoute[AssistantDeleted, PartialAssistantDeleted]):
    def __init__(self, router: respx.MockRouter, state: StateStore) -> None:
        super().__init__(
            route=router.delete(url__regex=r"/v1/assistants/(?P<id>[a-zA-Z0-9\_]+)"),
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
        deleted = self._state.beta.assistants.delete(id)
        return httpx.Response(
            status_code=200,
            json=model_dict(
                AssistantDeleted(id=id, deleted=deleted, object="assistant.deleted")
            ),
        )

    @staticmethod
    def _build(
        partial: PartialAssistantDeleted,
        request: httpx.Request,
    ) -> AssistantDeleted:
        raise NotImplementedError
