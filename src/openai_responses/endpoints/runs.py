import json
from typing import Any, Literal, Optional, Sequence, TypedDict

import httpx

from openai.types.beta.assistant_tool_choice import AssistantToolChoice
from openai.types.beta.assistant_tool_choice_option import AssistantToolChoiceOption
from openai.types.beta.assistant_tool_choice_option_param import (
    AssistantToolChoiceOptionParam,
)
import respx

from openai.pagination import SyncCursorPage
from openai.types.beta.assistant import Assistant


from openai.types.beta.threads.run import (
    IncompleteDetails,
    Run,
    LastError,
    RequiredAction,
    TruncationStrategy,
    Usage,
)
from openai.types.beta.threads.run_create_params import RunCreateParams
from openai.types.beta.threads.run_update_params import RunUpdateParams

from openai_responses.endpoints.messages import MessagesMock


from ._base import StatefulMock, CallContainer
from ._partial_schemas import PartialRun
from .assistants import AssistantsMock
from .run_steps import RunStepsMock

from ..decorators import side_effect
from ..state import StateStore
from ..utils import model_dict, model_parse, utcnow_unix_timestamp_s

__all__ = ["RunsMock"]


class MultiMethodSequence(TypedDict, total=False):
    create: Sequence[PartialRun]
    retrieve: Sequence[PartialRun]


class RunsMock(StatefulMock):
    def __init__(self) -> None:
        super().__init__(
            name="runs_mock",
            endpoint=r"/v1/threads/(?P<thread_id>\w+)/runs",
            route_registrations=[
                {
                    "name": "create",
                    "method": respx.post,
                    "pattern": None,
                    "side_effect": self._create,
                },
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
                {
                    "name": "update",
                    "method": respx.post,
                    "pattern": r"/(?P<id>\w+)",
                    "side_effect": self._update,
                },
                {
                    "name": "cancel",
                    "method": respx.post,
                    "pattern": r"/(?P<id>\w+)/cancel",
                    "side_effect": self._cancel,
                },
                {
                    "name": "submit_tool_outputs",
                    "method": respx.post,
                    "pattern": r"/(?P<id>\w+)/submit_tool_outputs",
                    "side_effect": self._submit_tool_outputs,
                },
            ],
        )

        self.create = CallContainer()
        self.list = CallContainer()
        self.retrieve = CallContainer()
        self.update = CallContainer()
        self.cancel = CallContainer()
        self.submit_tool_outputs = CallContainer()

        self.steps = RunStepsMock()

    def __call__(
        self,
        *,
        sequence: Optional[MultiMethodSequence] = None,
        latency: Optional[float] = None,
        failures: Optional[int] = None,
        state_store: Optional[StateStore] = None,
        validate_thread_exists: Optional[bool] = None,
        validate_assistant_exists: Optional[bool] = None,
    ):
        def getter(*args: Any, **kwargs: Any):
            return dict(
                sequence=sequence or {},
                latency=latency or 0,
                failures=failures or 0,
                state_store=kwargs["used_state"],
                validate_thread_exists=validate_thread_exists or False,
                validate_assistant_exists=validate_assistant_exists or False,
            )

        return self._make_decorator(getter, state_store or StateStore())

    @side_effect
    def _create(
        self,
        request: httpx.Request,
        route: respx.Route,
        thread_id: str,
        sequence: MultiMethodSequence,
        state_store: StateStore,
        validate_thread_exists: bool,
        validate_assistant_exists: bool,
        **kwargs: Any,
    ) -> httpx.Response:
        self.create.route = route
        failures: int = kwargs.get("failures", 0)

        if validate_thread_exists:
            thread = state_store.beta.threads.get(thread_id)

            if not thread:
                return httpx.Response(status_code=404)

        content: RunCreateParams = json.loads(request.content)

        partial_run = (
            self._next_partial_run(sequence, route.call_count, failures, "create") or {}
        )
        if validate_assistant_exists:
            asst = state_store.beta.assistants.get(content["assistant_id"])

            if not asst:
                return httpx.Response(status_code=404)

            partial_run = self._merge_partial_run_with_assistant(partial_run, asst)

        for additional_message in content.get("additional_messages", []) or []:
            parsed = MessagesMock()._parse_message_create_params(
                thread_id,
                additional_message,
            )
            state_store.beta.threads.messages.put(parsed)

        run = Run(
            id=self._faker.beta.thread.run.id(),
            assistant_id=content["assistant_id"],
            cancelled_at=partial_run.get("cancelled_at"),
            completed_at=partial_run.get("completed_at"),
            created_at=utcnow_unix_timestamp_s(),
            expires_at=partial_run.get("expires_at"),
            failed_at=partial_run.get("failed_at"),
            incomplete_details=model_parse(
                IncompleteDetails,
                partial_run.get("incomplete_details"),
            ),
            instructions="\n".join(
                [
                    partial_run.get("instructions", ""),
                    content.get("additional_instructions", "") or "",
                ]
            ),
            last_error=model_parse(
                LastError,
                partial_run.get("last_error"),
            ),
            max_completion_tokens=content.get("max_completion_tokens"),
            max_prompt_tokens=content.get("max_prompt_tokens"),
            metadata=content.get("metadata"),
            model=partial_run.get("model", "gpt-3.5-turbo"),
            object="thread.run",
            required_action=model_parse(
                RequiredAction,
                partial_run.get("required_action"),
            ),
            response_format=AssistantsMock._parse_response_format_params(
                content.get("response_format")
            ),
            started_at=partial_run.get("started_at"),
            status=partial_run.get("status", "queued"),
            thread_id=thread_id,
            tool_choice=self._parse_tool_choice_params(content.get("tool_choice")),
            tools=AssistantsMock._parse_tool_params(partial_run.get("tools")) or [],
            truncation_strategy=model_parse(
                TruncationStrategy, content.get("truncation_strategy")
            ),
            usage=Usage(
                completion_tokens=0,
                prompt_tokens=0,
                total_tokens=0,
            ),
            temperature=content.get("temperature"),
            top_p=content.get("top_p"),
        )

        state_store.beta.threads.runs.put(run)

        return httpx.Response(status_code=201, json=model_dict(run))

    def _retrieve(
        self,
        request: httpx.Request,
        route: respx.Route,
        thread_id: str,
        id: str,
        sequence: MultiMethodSequence,
        state_store: StateStore,
        validate_thread_exists: bool,
        validate_assistant_exists: bool,
        **kwargs: Any,
    ) -> httpx.Response:
        self.retrieve.route = route
        failures: int = kwargs.get("failures", 0)

        if validate_thread_exists:
            thread = state_store.beta.threads.get(thread_id)

            if not thread:
                return httpx.Response(status_code=404)

        *_, id = request.url.path.split("/")
        run = state_store.beta.threads.runs.get(id)

        if not run:
            return httpx.Response(status_code=404)

        partial_run = (
            self._next_partial_run(sequence, route.call_count, failures, "retrieve")
            or {}
        )

        if validate_assistant_exists:
            asst = state_store.beta.assistants.get(run.assistant_id)
            if asst:
                partial_run = self._merge_partial_run_with_assistant(partial_run, asst)

        run.cancelled_at = partial_run.get("cancelled_at", run.cancelled_at)
        run.completed_at = partial_run.get("completed_at", run.completed_at)
        run.expires_at = partial_run.get("expires_at", run.expires_at)
        run.failed_at = partial_run.get("failed_at", run.failed_at)
        run.incomplete_details = (
            model_parse(
                IncompleteDetails,
                partial_run.get("incomplete_details"),
            )
            or run.incomplete_details
        )
        run.instructions = partial_run.get("instructions", run.instructions)
        run.last_error = (
            model_parse(LastError, partial_run.get("last_error")) or run.last_error
        )
        run.model = partial_run.get("model", run.model)
        run.required_action = (
            model_parse(RequiredAction, partial_run.get("required_action"))
            or run.required_action
        )
        run.started_at = partial_run.get("started_at", run.started_at)
        run.status = partial_run.get("status", run.status)
        run.tools = (
            AssistantsMock._parse_tool_params(partial_run.get("tools")) or run.tools
        )

        state_store.beta.threads.runs.put(run)

        return httpx.Response(status_code=200, json=model_dict(run))

    def _list(
        self,
        request: httpx.Request,
        route: respx.Route,
        thread_id: str,
        sequence: MultiMethodSequence,
        state_store: StateStore,
        validate_thread_exists: bool,
        validate_assistant_exists: bool,
        **kwargs: Any,
    ):
        self.list.route = route

        if validate_thread_exists:
            thread = state_store.beta.threads.get(thread_id)

            if not thread:
                return httpx.Response(status_code=404)

        if validate_assistant_exists:
            # TODO: what should be done here?
            pass

        if sequence:
            # TODO: should there be a method sequence for list?
            pass

        limit = request.url.params.get("limit")
        order = request.url.params.get("order")
        after = request.url.params.get("after")
        before = request.url.params.get("before")

        runs = SyncCursorPage[Run](
            data=state_store.beta.threads.runs.list(
                thread_id, limit, order, after, before
            )
        )

        return httpx.Response(status_code=200, json=model_dict(runs))

    def _update(
        self,
        request: httpx.Request,
        route: respx.Route,
        thread_id: str,
        id: str,
        sequence: MultiMethodSequence,
        state_store: StateStore,
        validate_thread_exists: bool,
        validate_assistant_exists: bool,
        **kwargs: Any,
    ) -> httpx.Response:
        self.update.route = route

        if validate_thread_exists:
            thread = state_store.beta.threads.get(thread_id)

            if not thread:
                return httpx.Response(status_code=404)

        if validate_assistant_exists:
            # TODO: what should be done here?
            pass

        if sequence:
            # TODO: should there be a method sequence for update?
            pass

        *_, id = request.url.path.split("/")
        run = state_store.beta.threads.runs.get(id)

        if not run:
            return httpx.Response(status_code=404)

        content: RunUpdateParams = json.loads(request.content)

        run.metadata = content.get("metadata", run.metadata)

        state_store.beta.threads.runs.put(run)

        return httpx.Response(status_code=200, json=model_dict(run))

    def _cancel(
        self,
        request: httpx.Request,
        route: respx.Route,
        thread_id: str,
        id: str,
        sequence: MultiMethodSequence,
        state_store: StateStore,
        validate_thread_exists: bool,
        validate_assistant_exists: bool,
        **kwargs: Any,
    ) -> httpx.Response:
        self.cancel.route = route

        if validate_thread_exists:
            thread = state_store.beta.threads.get(thread_id)

            if not thread:
                return httpx.Response(status_code=404)

        if validate_assistant_exists:
            # TODO: what should be done here?
            pass

        if sequence:
            # TODO: should there be a method sequence for cancel?
            pass

        *_, id, _ = request.url.path.split("/")
        run = state_store.beta.threads.runs.get(id)

        if not run:
            return httpx.Response(status_code=404)

        run.status = "cancelling"

        state_store.beta.threads.runs.put(run)

        return httpx.Response(status_code=200, json=model_dict(run))

    def _submit_tool_outputs(
        self,
        request: httpx.Request,
        route: respx.Route,
        thread_id: str,
        id: str,
        sequence: MultiMethodSequence,
        state_store: StateStore,
        validate_thread_exists: bool,
        validate_assistant_exists: bool,
        **kwargs: Any,
    ) -> httpx.Response:
        self.submit_tool_outputs.route = route

        if validate_thread_exists:
            thread = state_store.beta.threads.get(thread_id)

            if not thread:
                return httpx.Response(status_code=404)

        if validate_assistant_exists:
            # TODO: what should be done here?
            pass

        if sequence:
            # TODO: should there be a method sequence for submit tools?
            pass

        *_, id, _ = request.url.path.split("/")
        run = state_store.beta.threads.runs.get(id)

        if not run:
            return httpx.Response(status_code=404)

        return httpx.Response(status_code=200, json=model_dict(run))

    @staticmethod
    def _next_partial_run(
        sequence: MultiMethodSequence,
        call_count: int,
        failures: int,
        method: Literal["create", "retrieve"],
    ) -> Optional[PartialRun]:
        used_sequence = sequence.get(method, [])
        net_ix = call_count - failures
        try:
            return used_sequence[net_ix]
        except IndexError:
            return None

    @staticmethod
    def _merge_partial_run_with_assistant(
        run: Optional[PartialRun],
        asst: Assistant,
    ) -> PartialRun:
        if not run:
            return {
                "instructions": asst.instructions or "",
                "model": asst.model,
                "tools": [model_dict(tool) for tool in asst.tools],  # type: ignore
            }
        else:
            return run | {
                "instructions": run.get("instructions", asst.instructions or ""),
                "model": run.get("model", asst.model),
                "tools": run.get("tools", [model_dict(tool) for tool in asst.tools]),  # type: ignore
            }

    @staticmethod
    def _parse_tool_choice_params(
        params: Optional[AssistantToolChoiceOptionParam],
    ) -> Optional[AssistantToolChoiceOption]:
        return (
            model_parse(AssistantToolChoice, params)
            if isinstance(params, dict)
            else params
        )
