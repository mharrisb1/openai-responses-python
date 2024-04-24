import json
from functools import partial
from typing import Any, Iterable, List, Literal, Optional, Sequence, TypedDict, Union

import httpx

from openai.types.beta.assistant_tool_choice import AssistantToolChoice
from openai.types.beta.assistant_tool_choice_option import AssistantToolChoiceOption
from openai.types.beta.assistant_tool_choice_option_param import (
    AssistantToolChoiceOptionParam,
)
from openai.types.beta.code_interpreter_tool import CodeInterpreterTool
from openai.types.beta.file_search_tool import FileSearchTool
import respx

from openai.pagination import SyncCursorPage
from openai.types.beta.assistant import Assistant

from openai.types.beta.thread import Thread, ToolResources
from openai.types.beta.thread_deleted import ThreadDeleted
from openai.types.beta.thread_update_params import ThreadUpdateParams
from openai.types.beta.thread_create_params import (
    ThreadCreateParams,
    Message as ThreadMessageCreateParams,
    MessageAttachment as ThreadMessageCreateAttachmentParams,
)

from openai.types.beta.threads.text import Text
from openai.types.beta.threads.text_content_block import TextContentBlock

from openai.types.beta.threads.message import Message, Attachment as MessageAttachment
from openai.types.beta.threads.message_create_params import (
    MessageCreateParams,
    Attachment as MessageCreateAttachmentParams,
)
from openai.types.beta.threads.message_update_params import MessageUpdateParams

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

from openai.types.beta.threads.runs.run_step import (
    RunStep,
    LastError as RunStepLastError,
)
from openai.types.beta.threads.runs.tool_calls_step_details import ToolCallsStepDetails
from openai.types.beta.threads.runs.message_creation_step_details import (
    MessageCreationStepDetails,
)

from ._base import StatefulMock, CallContainer
from ._partial_schemas import PartialRun, PartialRunStep
from .assistants import AssistantsMock
from ..decorators import side_effect
from ..state import StateStore
from ..utils import model_dict, model_parse, remove_none, utcnow_unix_timestamp_s

__all__ = ["ThreadsMock", "MessagesMock", "RunsMock"]


class ThreadsMock(StatefulMock):
    def __init__(self) -> None:
        super().__init__()
        self.url = self.BASE_URL + "/threads"
        self.create = CallContainer()
        self.retrieve = CallContainer()
        self.update = CallContainer()
        self.delete = CallContainer()

        self.messages = MessagesMock()
        self.runs = RunsMock()

    def _register_routes(self, **common: Any) -> None:
        self.create.route = respx.post(url__regex=self.url).mock(
            side_effect=partial(self._create, **common)
        )
        self.retrieve.route = respx.get(url__regex=self.url + r"/(?P<id>\w+)").mock(
            side_effect=partial(self._retrieve, **common)
        )
        self.update.route = respx.post(url__regex=self.url + r"/(?P<id>\w+)").mock(
            side_effect=partial(self._update, **common)
        )
        self.delete.route = respx.delete(url__regex=self.url + r"/(?P<id>\w+)").mock(
            side_effect=partial(self._delete, **common)
        )

    def __call__(
        self,
        *,
        latency: Optional[float] = None,
        failures: Optional[int] = None,
        state_store: Optional[StateStore] = None,
    ):
        def getter(*args: Any, **kwargs: Any):
            return dict(
                latency=latency or 0,
                failures=failures or 0,
                state_store=kwargs["used_state"],
            )

        return self._make_decorator("threads_mock", getter, state_store or StateStore())

    @side_effect
    def _create(
        self,
        request: httpx.Request,
        route: respx.Route,
        state_store: StateStore,
        **kwargs: Any,
    ) -> httpx.Response:
        self.create.route = route

        content: ThreadCreateParams = json.loads(request.content)

        thread = Thread(
            id=self._faker.beta.thread.id(),
            created_at=utcnow_unix_timestamp_s(),
            tool_resources=model_parse(ToolResources, content.get("tool_resources")),
            metadata=content.get("metadata"),
            object="thread",
        )
        messages = [
            self.messages._parse_message_create_params(thread.id, m)
            for m in content.get("messages", [])
        ]

        state_store.beta.threads.put(thread)
        for message in messages:
            state_store.beta.threads.messages.put(message)

        return httpx.Response(status_code=201, json=model_dict(thread))

    @side_effect
    def _retrieve(
        self,
        request: httpx.Request,
        route: respx.Route,
        id: str,
        state_store: StateStore,
        **kwargs: Any,
    ) -> httpx.Response:
        self.retrieve.route = route

        *_, id = request.url.path.split("/")
        thread = state_store.beta.threads.get(id)

        if not thread:
            return httpx.Response(status_code=404)

        else:
            return httpx.Response(status_code=200, json=model_dict(thread))

    @side_effect
    def _update(
        self,
        request: httpx.Request,
        route: respx.Route,
        id: str,
        state_store: StateStore,
        **kwargs: Any,
    ) -> httpx.Response:
        self.update.route = route

        *_, id = request.url.path.split("/")
        content: ThreadUpdateParams = json.loads(request.content)

        thread = state_store.beta.threads.get(id)

        if not thread:
            return httpx.Response(status_code=404)

        thread.tool_resources = (
            model_parse(ToolResources, content.get("tool_resources"))
            or thread.tool_resources
        )
        thread.metadata = content.get("metadata", thread.metadata)

        state_store.beta.threads.put(thread)

        return httpx.Response(status_code=200, json=model_dict(thread))

    @side_effect
    def _delete(
        self,
        request: httpx.Request,
        route: respx.Route,
        id: str,
        state_store: StateStore,
        **kwargs: Any,
    ) -> httpx.Response:
        self.delete.route = route

        *_, id = request.url.path.split("/")
        deleted = state_store.beta.threads.delete(id)

        return httpx.Response(
            status_code=200,
            json=model_dict(
                ThreadDeleted(id=id, deleted=deleted, object="thread.deleted")
            ),
        )


class MessagesMock(StatefulMock):
    def __init__(self) -> None:
        super().__init__()
        self.url = self.BASE_URL + r"/threads/(?P<thread_id>\w+)/messages"
        self.create = CallContainer()
        self.list = CallContainer()
        self.retrieve = CallContainer()
        self.update = CallContainer()

    def _register_routes(self, **common: Any) -> None:
        self.retrieve.route = respx.get(url__regex=self.url + r"/(?P<id>\w+)").mock(
            side_effect=partial(self._retrieve, **common)
        )
        self.update.route = respx.post(url__regex=self.url + r"/(?P<id>\w+)").mock(
            side_effect=partial(self._update, **common)
        )
        self.create.route = respx.post(url__regex=self.url).mock(
            side_effect=partial(self._create, **common)
        )
        self.list.route = respx.get(url__regex=self.url).mock(
            side_effect=partial(self._list, **common)
        )

    def __call__(
        self,
        *,
        latency: Optional[float] = None,
        failures: Optional[int] = None,
        state_store: Optional[StateStore] = None,
        validate_thread_exists: Optional[bool] = None,
    ):
        def getter(*args: Any, **kwargs: Any):
            return dict(
                latency=latency or 0,
                failures=failures or 0,
                state_store=kwargs["used_state"],
                validate_thread_exists=validate_thread_exists or False,
            )

        return self._make_decorator(
            "messages_mock", getter, state_store or StateStore()
        )

    @side_effect
    def _create(
        self,
        request: httpx.Request,
        route: respx.Route,
        thread_id: str,
        state_store: StateStore,
        validate_thread_exists: bool,
        **kwargs: Any,
    ) -> httpx.Response:
        self.create.route = route

        if validate_thread_exists:
            thread = state_store.beta.threads.get(thread_id)

            if not thread:
                return httpx.Response(status_code=404)

        content: MessageCreateParams = json.loads(request.content)
        message = self._parse_message_create_params(thread_id, content)

        state_store.beta.threads.messages.put(message)

        return httpx.Response(status_code=201, json=model_dict(message))

    @side_effect
    def _list(
        self,
        request: httpx.Request,
        route: respx.Route,
        thread_id: str,
        state_store: StateStore,
        validate_thread_exists: bool,
        **kwargs: Any,
    ) -> httpx.Response:
        self.list.route = route

        if validate_thread_exists:
            thread = state_store.beta.threads.get(thread_id)

            if not thread:
                return httpx.Response(status_code=404)

        limit = request.url.params.get("limit")
        order = request.url.params.get("order")
        after = request.url.params.get("after")
        before = request.url.params.get("before")

        messages = SyncCursorPage[Message](
            data=state_store.beta.threads.messages.list(
                thread_id,
                limit,
                order,
                after,
                before,
            )
        )

        return httpx.Response(status_code=200, json=model_dict(messages))

    @side_effect
    def _retrieve(
        self,
        request: httpx.Request,
        route: respx.Route,
        thread_id: str,
        id: str,
        state_store: StateStore,
        validate_thread_exists: bool,
        **kwargs: Any,
    ) -> httpx.Response:
        self.retrieve.route = route

        if validate_thread_exists:
            thread = state_store.beta.threads.get(thread_id)

            if not thread:
                return httpx.Response(status_code=404)

        *_, id = request.url.path.split("/")
        message = state_store.beta.threads.messages.get(id)

        if not message:
            return httpx.Response(status_code=404)

        else:
            return httpx.Response(status_code=200, json=model_dict(message))

    @side_effect
    def _update(
        self,
        request: httpx.Request,
        route: respx.Route,
        thread_id: str,
        id: str,
        state_store: StateStore,
        validate_thread_exists: bool,
        **kwargs: Any,
    ) -> httpx.Response:
        self.update.route = route

        if validate_thread_exists:
            thread = state_store.beta.threads.get(thread_id)

            if not thread:
                return httpx.Response(status_code=404)

        *_, id = request.url.path.split("/")
        content: MessageUpdateParams = json.loads(request.content)

        message = state_store.beta.threads.messages.get(id)

        if not message:
            return httpx.Response(status_code=404)

        message.metadata = content.get("metadata", message.metadata)

        state_store.beta.threads.messages.put(message)

        return httpx.Response(status_code=200, json=model_dict(message))

    def _parse_message_create_params(
        self,
        thread_id: str,
        params: Union[ThreadMessageCreateParams, MessageCreateParams],
    ) -> Message:
        return Message(
            id=self._faker.beta.thread.message.id(),
            attachments=self._parse_attachments_params(params.get("attachments")),
            content=[
                TextContentBlock(
                    text=Text(annotations=[], value=params["content"]),
                    type="text",
                )
            ],
            created_at=utcnow_unix_timestamp_s(),
            metadata=params.get("metadata"),
            object="thread.message",
            role=params["role"],
            status="completed",
            thread_id=thread_id,
        )

    @staticmethod
    def _parse_attachments_params(
        params: Optional[
            Union[
                Iterable[MessageCreateAttachmentParams],
                Iterable[ThreadMessageCreateAttachmentParams],
            ]
        ],
    ) -> Optional[List[MessageAttachment]]:
        m = {"code_interpreter": CodeInterpreterTool, "file_search": FileSearchTool}
        return (
            remove_none(
                [
                    model_parse(
                        MessageAttachment,
                        {
                            "file_id": attachment.get("file_id"),
                            "tools": [
                                model_parse(m[t["type"]], t)
                                for t in attachment.get("tools", [])
                            ],
                        },
                    )
                    for attachment in params
                ]
            )
            if params
            else None
        )


class MultiMethodSequence(TypedDict, total=False):
    create: Sequence[PartialRun]
    retrieve: Sequence[PartialRun]


class RunsMock(StatefulMock):
    def __init__(self) -> None:
        super().__init__()
        self.url = self.BASE_URL + r"/threads/(?P<thread_id>\w+)/runs"
        self.create = CallContainer()
        self.list = CallContainer()
        self.retrieve = CallContainer()
        self.update = CallContainer()
        self.cancel = CallContainer()
        self.submit_tool_outputs = CallContainer()

        self.steps = RunStepsMock()

    def _register_routes(self, **common: Any) -> None:
        self.submit_tool_outputs.route = respx.post(
            url__regex=self.url + r"/(?P<id>\w+)/submit_tool_outputs"
        ).mock(side_effect=partial(self._submit_tool_outputs, **common))
        self.cancel.route = respx.post(
            url__regex=self.url + r"/(?P<id>\w+)/cancel"
        ).mock(side_effect=partial(self._cancel, **common))
        self.update.route = respx.post(url__regex=self.url + r"/(?P<id>\w+)").mock(
            side_effect=partial(self._update, **common)
        )
        self.retrieve.route = respx.get(url__regex=self.url + r"/(?P<id>\w+)").mock(
            side_effect=partial(self._retrieve, **common)
        )
        self.create.route = respx.post(url__regex=self.url).mock(
            side_effect=partial(self._create, **common)
        )
        self.list.route = respx.get(url__regex=self.url).mock(
            side_effect=partial(self._list, **common)
        )

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

        return self._make_decorator("runs_mock", getter, state_store or StateStore())

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

        # TODO: create additional messages

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


class RunStepsMock(StatefulMock):
    def __init__(self) -> None:
        super().__init__()
        self.url = (
            self.BASE_URL + r"/threads/(?P<thread_id>\w+)/runs/(?P<run_id>\w+)/steps"
        )
        self.list = CallContainer()
        self.retrieve = CallContainer()

    def _register_routes(self, **common: Any) -> None:
        self.retrieve.route = respx.get(url__regex=self.url + r"/(?P<id>\w+)").mock(
            side_effect=partial(self._retrieve, **common)
        )
        self.list.route = respx.get(url__regex=self.url).mock(
            side_effect=partial(self._list, **common)
        )

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

        return self._make_decorator(
            "run_steps_mock", getter, state_store or StateStore()
        )

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
