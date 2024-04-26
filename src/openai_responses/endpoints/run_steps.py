from typing import Any, List, Optional

import httpx
import respx

from openai.pagination import SyncCursorPage
from openai.types.beta.threads.runs.run_step import (
    RunStep,
    LastError as RunStepLastError,
)
from openai.types.beta.threads.runs.tool_calls_step_details import ToolCallsStepDetails
from openai.types.beta.threads.runs.message_creation_step_details import (
    MessageCreationStepDetails,
)

from ._base import StatefulMock, CallContainer
from ._partial_schemas import PartialRunStep

from ..decorators import side_effect
from ..state import StateStore
from ..utils import model_dict, model_parse, utcnow_unix_timestamp_s


class RunStepsMock(StatefulMock):
    def __init__(self) -> None:
        super().__init__(
            name="assistants_mock",
            endpoint="/v1/assistants",
            route_registrations=[
                {
                    "name": "list",
                    "method": respx.get,
                    "pattern": None,
                    "side_effect": self._list,
                },
                {
                    "name": "retrieve",
                    "method": respx.get,
                    "pattern": r"/(?P<id>\w+)",
                    "side_effect": self._retrieve,
                },
            ],
        )

        self.list = CallContainer()
        self.retrieve = CallContainer()

    def __call__(
        self,
        *,
        steps: Optional[List[PartialRunStep]] = None,
        latency: Optional[float] = None,
        failures: Optional[int] = None,
        state_store: Optional[StateStore] = None,
        validate_thread_exists: Optional[bool] = None,
        validate_run_exists: Optional[bool] = None,
    ):
        def getter(*args: Any, **kwargs: Any):
            return dict(
                steps=steps or [],
                latency=latency or 0,
                failures=failures or 0,
                state_store=kwargs["used_state"],
                validate_thread_exists=validate_thread_exists or False,
                validate_run_exists=validate_run_exists or False,
            )

        return self._make_decorator(getter, state_store or StateStore())

    @side_effect
    def _list(
        self,
        request: httpx.Request,
        route: respx.Route,
        thread_id: str,
        run_id: str,
        steps: List[PartialRunStep],
        state_store: StateStore,
        validate_thread_exists: bool,
        validate_run_exists: bool,
        **kwargs: Any,
    ) -> httpx.Response:
        self.list.route = route

        if validate_thread_exists:
            thread = state_store.beta.threads.get(thread_id)

            if not thread:
                return httpx.Response(status_code=404)

        assistant_id = ""
        if validate_run_exists:
            run = state_store.beta.threads.runs.get(run_id)

            if not run:
                return httpx.Response(status_code=404)

            assistant_id = run.assistant_id

        self._put_steps_in_store(thread_id, run_id, assistant_id, steps, state_store)

        limit = request.url.params.get("limit")
        order = request.url.params.get("order")
        after = request.url.params.get("after")
        before = request.url.params.get("before")

        return httpx.Response(
            status_code=200,
            json=model_dict(
                SyncCursorPage[RunStep](
                    data=state_store.beta.threads.runs.steps.list(
                        thread_id,
                        run_id,
                        limit,
                        order,
                        after,
                        before,
                    )
                )
            ),
        )

    @side_effect
    def _retrieve(
        self,
        request: httpx.Request,
        route: respx.Route,
        thread_id: str,
        run_id: str,
        id: str,
        steps: List[PartialRunStep],
        state_store: StateStore,
        validate_thread_exists: bool,
        validate_run_exists: bool,
        **kwargs: Any,
    ) -> httpx.Response:
        self.list.route = route

        if validate_thread_exists:
            thread = state_store.beta.threads.get(thread_id)

            if not thread:
                return httpx.Response(status_code=404)

        assistant_id = ""
        if validate_run_exists:
            run = state_store.beta.threads.runs.get(run_id)

            if not run:
                return httpx.Response(status_code=404)

            assistant_id = run.assistant_id

        self._put_steps_in_store(thread_id, run_id, assistant_id, steps, state_store)

        *_, id = request.url.path.split("/")
        step = state_store.beta.threads.runs.steps.get(id)

        if not step:
            return httpx.Response(status_code=404)

        return httpx.Response(status_code=200, json=model_dict(step))

    def _put_steps_in_store(
        self,
        thread_id: str,
        run_id: str,
        assistant_id: str,
        steps: List[PartialRunStep],
        state_store: StateStore,
    ) -> None:
        for step in steps:
            step_details = step.get("step_details")
            if not step_details:
                continue

            step_details_model: Any = None
            if step_details["type"] == "message_creation":
                step_details_model = model_parse(
                    MessageCreationStepDetails, step_details
                )
            elif step_details["type"] == "tool_calls":
                step_details_model = model_parse(ToolCallsStepDetails, step_details)

            if not step_details_model:
                continue

            state_store.beta.threads.runs.steps.put(
                RunStep(
                    id=step.get("id", self._faker.beta.thread.run.step.id()),
                    assistant_id=step.get("assistant_id", assistant_id),
                    cancelled_at=step.get("cancelled_at"),
                    completed_at=step.get("completed_at"),
                    created_at=utcnow_unix_timestamp_s(),
                    expired_at=step.get("expired_at"),
                    failed_at=step.get("failed_at"),
                    last_error=model_parse(
                        RunStepLastError,
                        step.get("last_error"),
                    ),
                    object="thread.run.step",
                    run_id=run_id,
                    status=step.get("status", "in_progress"),
                    thread_id=thread_id,
                    type=step_details["type"],
                    step_details=step_details_model,
                )
            )
