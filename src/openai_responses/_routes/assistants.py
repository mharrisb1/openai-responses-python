import json
from typing import Any, List, Literal
from typing_extensions import override

import httpx
import respx

from openai.pagination import SyncCursorPage
from openai.types.beta.assistant import Assistant
from openai.types.beta.assistant_deleted import AssistantDeleted
from openai.types.beta.assistant_create_params import AssistantCreateParams
from openai.types.beta.assistant_update_params import AssistantUpdateParams

from ._base import StatefulRoute

from ..helpers.builders.vector_stores import vector_store_from_create_request
from ..helpers.builders.vector_store_files import vector_store_file_from_create_request
from ..helpers.mergers.assistants import merge_assistant_with_partial

from ..stores import StateStore

from .._types.partials.deleted import PartialResourceDeleted
from .._types.partials.sync_cursor_page import PartialSyncCursorPage
from .._types.partials.assistants import PartialAssistant

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
            route=router.post(url__regex="/assistants"),
            status_code=201,
            state=state,
        )

    @override
    def _handler(self, request: httpx.Request, route: respx.Route) -> httpx.Response:
        self._route = route
        model = self._build({}, request)
        content: AssistantCreateParams = json_loads(request.content)

        tool_resources = content.get("tool_resources")
        if tool_resources:
            file_search = tool_resources.get("file_search")
            if file_search:
                vector_stores = file_search.get("vector_stores")
                if vector_stores:
                    vector_store_ids: List[str] = []
                    for vector_store_create_params in vector_stores:
                        encoded = json.dumps(vector_store_create_params)
                        create_req = httpx.Request("", "", content=encoded)
                        vector_store = vector_store_from_create_request(create_req)
                        vector_store_ids.append(vector_store.id)
                        self._state.beta.vector_stores.put(vector_store)
                        for file_id in vector_store_create_params.get("file_ids", []):
                            found_file = self._state.files.get(file_id)
                            if not found_file:
                                return httpx.Response(404)
                            encoded = json.dumps({"file_id": found_file.id})
                            create_file_req = httpx.Request("", "", content=encoded)
                            vector_store_file = vector_store_file_from_create_request(
                                create_file_req,
                                extra={"vector_store_id": vector_store.id},
                            )
                            self._state.beta.vector_stores.files.put(vector_store_file)

                    model = merge_assistant_with_partial(
                        model,
                        {
                            "tool_resources": {
                                "file_search": {
                                    "vector_store_ids": vector_store_ids,
                                }
                            }
                        },
                    )

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
    StatefulRoute[SyncCursorPage[Assistant], PartialSyncCursorPage[PartialAssistant]]
):
    def __init__(self, router: respx.MockRouter, state: StateStore) -> None:
        super().__init__(
            route=router.get(url__regex="/assistants"),
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
        partial: PartialSyncCursorPage[PartialAssistant],
        request: httpx.Request,
    ) -> SyncCursorPage[Assistant]:
        raise NotImplementedError


class AssistantRetrieveRoute(StatefulRoute[Assistant, PartialAssistant]):
    def __init__(self, router: respx.MockRouter, state: StateStore) -> None:
        super().__init__(
            route=router.get(
                url__regex=r"/assistants/(?P<assistant_id>[a-zA-Z0-9\_]+)"
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
        assistant_id = kwargs["assistant_id"]
        found = self._state.beta.assistants.get(assistant_id)
        if not found:
            return httpx.Response(404)

        return httpx.Response(status_code=200, json=model_dict(found))

    @staticmethod
    def _build(partial: PartialAssistant, request: httpx.Request) -> Assistant:
        raise NotImplementedError


class AssistantUpdateRoute(StatefulRoute[Assistant, PartialAssistant]):
    def __init__(self, router: respx.MockRouter, state: StateStore) -> None:
        super().__init__(
            route=router.post(
                url__regex=r"/assistants/(?P<assistant_id>[a-zA-Z0-9\_]+)"
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
        assistant_id = kwargs["assistant_id"]
        found = self._state.beta.assistants.get(assistant_id)
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


class AssistantDeleteRoute(
    StatefulRoute[
        AssistantDeleted, PartialResourceDeleted[Literal["assistant.deleted"]]
    ]
):
    def __init__(self, router: respx.MockRouter, state: StateStore) -> None:
        super().__init__(
            route=router.delete(
                url__regex=r"/assistants/(?P<assistant_id>[a-zA-Z0-9\_]+)"
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
        assistant_id = kwargs["assistant_id"]
        deleted = self._state.beta.assistants.delete(assistant_id)
        return httpx.Response(
            status_code=200,
            json=model_dict(
                AssistantDeleted(
                    id=assistant_id, deleted=deleted, object="assistant.deleted"
                )
            ),
        )

    @staticmethod
    def _build(
        partial: PartialResourceDeleted[Literal["assistant.deleted"]],
        request: httpx.Request,
    ) -> AssistantDeleted:
        raise NotImplementedError
