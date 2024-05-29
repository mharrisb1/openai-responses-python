from typing import Any
from typing_extensions import override

import httpx
import respx

from openai.pagination import SyncCursorPage
from openai.types.beta.threads.runs.run_step import RunStep

from ._base import StatefulRoute

from ..stores import StateStore
from .._types.partials.run_steps import PartialRunStep
from .._types.partials.sync_cursor_page import PartialSyncCursorPage

from .._utils.serde import model_dict


__all__ = ["RunStepListRoute", "RunStepRetrieveRoute"]


class RunStepListRoute(
    StatefulRoute[SyncCursorPage[RunStep], PartialSyncCursorPage[PartialRunStep]]
):
    def __init__(self, router: respx.MockRouter, state: StateStore) -> None:
        super().__init__(
            route=router.get(
                url__regex=r"/threads/(?P<thread_id>[a-zA-Z0-9\_]+)/runs/(?P<run_id>[a-zA-Z0-9\_]+)/steps"
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

        limit = request.url.params.get("limit")
        order = request.url.params.get("order")
        after = request.url.params.get("after")
        before = request.url.params.get("before")

        data = self._state.beta.threads.runs.steps.list(
            thread_id,
            run_id,
            limit,
            order,
            after,
            before,
        )
        result_count = len(data)
        total_count = len(self._state.beta.threads.runs.steps.list(thread_id, run_id))
        has_data = bool(result_count)
        has_more = total_count != result_count
        first_id = data[0].id if has_data else None
        last_id = data[-1].id if has_data else None
        model = SyncCursorPage[RunStep](data=data)
        return httpx.Response(
            status_code=200,
            json=model_dict(model)
            | {"first_id": first_id, "last_id": last_id, "has_more": has_more},
        )

    @staticmethod
    def _build(
        partial: PartialSyncCursorPage[PartialRunStep],
        request: httpx.Request,
    ) -> SyncCursorPage[RunStep]:
        raise NotImplementedError


class RunStepRetrieveRoute(StatefulRoute[RunStep, PartialRunStep]):
    def __init__(self, router: respx.MockRouter, state: StateStore) -> None:
        super().__init__(
            route=router.get(
                url__regex=r"/threads/(?P<thread_id>[a-zA-Z0-9\_]+)/runs/(?P<run_id>[a-zA-Z0-9\_]+)/steps/(?P<step_id>[a-zA-Z0-9\_]+)"
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

        step_id = kwargs["step_id"]
        found_run_step = self._state.beta.threads.runs.steps.get(step_id)
        if not found_run_step:
            return httpx.Response(404)

        return httpx.Response(status_code=200, json=model_dict(found_run_step))

    @staticmethod
    def _build(partial: PartialRunStep, request: httpx.Request) -> RunStep:
        raise NotImplementedError
