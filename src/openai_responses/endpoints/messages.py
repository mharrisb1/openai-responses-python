import json
from functools import partial
from typing import Any, Iterable, List, Optional, Union

import httpx

from openai.types.beta.code_interpreter_tool import CodeInterpreterTool
from openai.types.beta.file_search_tool import FileSearchTool
import respx

from openai.pagination import SyncCursorPage
from openai.types.beta.thread_create_params import (
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
from openai.types.beta.threads.run_create_params import AdditionalMessage


from ._base import StatefulMock, CallContainer
from ..decorators import side_effect
from ..state import StateStore
from ..utils import model_dict, model_parse, remove_none, utcnow_unix_timestamp_s

__all__ = ["MessagesMock"]


class MessagesMock(StatefulMock):
    def __init__(self) -> None:
        super().__init__(
            name="messages_mock",
            endpoint=r"/v1/threads/(?P<thread_id>\w+)/messages",
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
            ],
        )

        # NOTE: these are explicitly defined to help with autocomplete and type hints
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

        return self._make_decorator(getter, state_store or StateStore())

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
        params: Union[
            ThreadMessageCreateParams,
            MessageCreateParams,
            AdditionalMessage,
        ],
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
                                model_parse(m[t["type"]], t)  # type: ignore
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
