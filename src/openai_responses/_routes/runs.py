import json
from typing import Any
from typing_extensions import override

import httpx
import respx

from openai.pagination import SyncCursorPage
from openai.types.beta.threads.run import Run
from openai.types.beta.threads.run_create_params import RunCreateParams
from openai.types.beta.threads.run_update_params import RunUpdateParams
from openai.types.beta.thread_create_and_run_params import ThreadCreateAndRunParams

from ._base import StatefulRoute

from ..helpers.builders.messages import message_from_create_request
from ..helpers.builders.threads import thread_from_create_request

from ..stores import StateStore
from .._types.partials.sync_cursor_page import PartialSyncCursorPage
from .._types.partials.runs import PartialRun

from .._utils.copy import model_copy
from .._utils.faker import faker
from .._utils.serde import json_loads, model_dict, model_parse
from .._utils.time import utcnow_unix_timestamp_s


__all__ = [
    "RunCreateRoute",
    "ThreadCreateAndRun",
    "RunListRoute",
    "RunRetrieveRoute",
    "RunUpdateRoute",
    "RunSubmitToolOutputsRoute",
    "RunCancelRoute",
]


class RunCreateRoute(StatefulRoute[Run, PartialRun]):
    def __init__(self, router: respx.MockRouter, state: StateStore) -> None:
        super().__init__(
            route=router.post(
                url__regex=r"/threads/(?P<thread_id>[a-zA-Z0-9\_]+)/runs"
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
        found_thread = self._state.beta.threads.get(thread_id)
        if not found_thread:
            return httpx.Response(404)

        content: RunCreateParams = json_loads(request.content)

        found_asst = self._state.beta.assistants.get(content["assistant_id"])
        if not found_asst:
            return httpx.Response(404)

        model = self._build(
            {
                "thread_id": thread_id,
                "instructions": found_asst.instructions or "",
                "model": found_asst.model,
                "tools": [model_dict(t) for t in (found_asst.tools or [])],  # type: ignore
            },
            request,
        )
        self._state.beta.threads.runs.put(model)
        return httpx.Response(
            status_code=self._status_code,
            json=model_dict(model),
        )

    @staticmethod
    def _build(partial: PartialRun, request: httpx.Request) -> Run:
        content = json_loads(request.content)
        defaults: PartialRun = {
            "id": faker.beta.thread.run.id(),
            "created_at": utcnow_unix_timestamp_s(),
            "instructions": "",
            "object": "thread.run",
            "status": "queued",
        }
        return model_parse(Run, defaults | partial | content)


class ThreadCreateAndRun(StatefulRoute[Run, PartialRun]):
    def __init__(self, router: respx.MockRouter, state: StateStore) -> None:
        super().__init__(
            route=router.post(url__regex="/threads/runs"),
            status_code=201,
            state=state,
        )

    @override
    def _handler(self, request: httpx.Request, route: respx.Route) -> httpx.Response:
        self._route = route

        content: ThreadCreateAndRunParams = json_loads(request.content)

        found_asst = self._state.beta.assistants.get(content["assistant_id"])
        if not found_asst:
            return httpx.Response(404)

        thread_create_params = content.get("thread", {})
        encoded = json.dumps(thread_create_params).encode("utf-8")
        thread_create_req = httpx.Request("", "", content=encoded)
        thread = thread_from_create_request(thread_create_req)
        self._state.beta.threads.put(thread)

        for message_create_params in thread_create_params.get("messages", []):
            encoded = json.dumps(message_create_params).encode("utf-8")
            create_message_req = httpx.Request(method="", url="", content=encoded)
            message = message_from_create_request(thread.id, create_message_req)
            self._state.beta.threads.messages.put(message)

        model = self._build(
            {
                "thread_id": thread.id,
                "instructions": found_asst.instructions or "",
                "model": found_asst.model,
                "tools": [model_dict(t) for t in (found_asst.tools or [])],  # type: ignore
            },
            request,
        )
        self._state.beta.threads.runs.put(model)
        return httpx.Response(
            status_code=self._status_code,
            json=model_dict(model),
        )

    @staticmethod
    def _build(partial: PartialRun, request: httpx.Request) -> Run:
        content = json_loads(request.content)
        if content.get("thread"):
            del content["thread"]

        return RunCreateRoute._build(partial, request)


class RunListRoute(
    StatefulRoute[SyncCursorPage[Run], PartialSyncCursorPage[PartialRun]]
):
    def __init__(self, router: respx.MockRouter, state: StateStore) -> None:
        super().__init__(
            route=router.get(url__regex=r"/threads/(?P<thread_id>[a-zA-Z0-9\_]+)/runs"),
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

        limit = request.url.params.get("limit")
        order = request.url.params.get("order")
        after = request.url.params.get("after")
        before = request.url.params.get("before")

        data = self._state.beta.threads.runs.list(
            thread_id,
            limit,
            order,
            after,
            before,
        )
        result_count = len(data)
        total_count = len(self._state.beta.threads.runs.list(thread_id))
        has_data = bool(result_count)
        has_more = total_count != result_count
        first_id = data[0].id if has_data else None
        last_id = data[-1].id if has_data else None
        model = SyncCursorPage[Run](data=data)
        return httpx.Response(
            status_code=200,
            json=model_dict(model)
            | {"first_id": first_id, "last_id": last_id, "has_more": has_more},
        )

    @staticmethod
    def _build(
        partial: PartialSyncCursorPage[PartialRun],
        request: httpx.Request,
    ) -> SyncCursorPage[Run]:
        raise NotImplementedError


class RunRetrieveRoute(StatefulRoute[Run, PartialRun]):
    def __init__(self, router: respx.MockRouter, state: StateStore) -> None:
        super().__init__(
            route=router.get(
                url__regex=r"/threads/(?P<thread_id>[a-zA-Z0-9\_]+)/runs/(?P<run_id>[a-zA-Z0-9\_]+)"
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

        run_id = kwargs["run_id"]
        found_run = self._state.beta.threads.runs.get(run_id)
        if not found_run:
            return httpx.Response(404)

        return httpx.Response(status_code=200, json=model_dict(found_run))

    @staticmethod
    def _build(partial: PartialRun, request: httpx.Request) -> Run:
        raise NotImplementedError


class RunUpdateRoute(StatefulRoute[Run, PartialRun]):
    def __init__(self, router: respx.MockRouter, state: StateStore) -> None:
        super().__init__(
            route=router.post(
                url__regex=r"/threads/(?P<thread_id>[a-zA-Z0-9\_]+)/runs/(?P<run_id>[a-zA-Z0-9\_]+)"
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

        run_id = kwargs["run_id"]
        found_run = self._state.beta.threads.runs.get(run_id)
        if not found_run:
            return httpx.Response(404)

        content: RunUpdateParams = json_loads(request.content)
        deserialized = model_dict(found_run)
        updated = model_parse(Run, deserialized | content)
        self._state.beta.threads.runs.put(updated)

        return httpx.Response(status_code=200, json=model_dict(updated))

    @staticmethod
    def _build(partial: PartialRun, request: httpx.Request) -> Run:
        raise NotImplementedError


class RunSubmitToolOutputsRoute(StatefulRoute[Run, PartialRun]):
    def __init__(self, router: respx.MockRouter, state: StateStore) -> None:
        super().__init__(
            route=router.post(
                url__regex=r"/threads/(?P<thread_id>[a-zA-Z0-9\_]+)/runs/(?P<run_id>[a-zA-Z0-9\_]+)/submit_tool_outputs"
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
        # TODO: update associated run step in store
        self._route = route

        thread_id = kwargs["thread_id"]
        found_thread = self._state.beta.threads.get(thread_id)
        if not found_thread:
            return httpx.Response(404)

        run_id = kwargs["run_id"]
        found_run = self._state.beta.threads.runs.get(run_id)
        if not found_run:
            return httpx.Response(404)

        return httpx.Response(status_code=200, json=model_dict(found_run))

    @staticmethod
    def _build(partial: PartialRun, request: httpx.Request) -> Run:
        raise NotImplementedError


class RunCancelRoute(StatefulRoute[Run, PartialRun]):
    def __init__(self, router: respx.MockRouter, state: StateStore) -> None:
        super().__init__(
            route=router.post(
                url__regex=r"/threads/(?P<thread_id>[a-zA-Z0-9\_]+)/runs/(?P<run_id>[a-zA-Z0-9\_]+)/cancel"
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
        # TODO: update associated run step in store
        self._route = route

        thread_id = kwargs["thread_id"]
        found_thread = self._state.beta.threads.get(thread_id)
        if not found_thread:
            return httpx.Response(404)

        run_id = kwargs["run_id"]
        found_run = self._state.beta.threads.runs.get(run_id)
        if not found_run:
            return httpx.Response(404)

        found_run.status = "cancelled"
        self._state.beta.threads.runs.put(found_run)
        copy = model_copy(found_run)
        copy.status = "cancelling"

        return httpx.Response(status_code=200, json=model_dict(copy))

    @staticmethod
    def _build(partial: PartialRun, request: httpx.Request) -> Run:
        raise NotImplementedError
