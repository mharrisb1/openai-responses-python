import json
from typing import Any, Optional

import httpx
import respx

from openai.types.beta.thread import Thread, ToolResources
from openai.types.beta.thread_deleted import ThreadDeleted
from openai.types.beta.thread_update_params import ThreadUpdateParams
from openai.types.beta.thread_create_params import ThreadCreateParams

from ._base import StatefulMock, CallContainer
from .messages import MessagesMock
from .runs import RunsMock

from ..decorators import side_effect
from ..state import StateStore
from ..utils import model_dict, model_parse, utcnow_unix_timestamp_s

__all__ = ["ThreadsMock"]


class ThreadsMock(StatefulMock):
    def __init__(self) -> None:
        super().__init__(
            name="threads_mock",
            endpoint="/v1/threads",
            route_registrations=[
                {
                    "name": "create",
                    "method": respx.post,
                    "pattern": None,
                    "side_effect": self._create,
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
                    "name": "delete",
                    "method": respx.delete,
                    "pattern": r"/(?P<id>\w+)",
                    "side_effect": self._delete,
                },
            ],
        )

        # NOTE: these are explicitly defined to help with autocomplete and type hints
        self.create = CallContainer()
        self.retrieve = CallContainer()
        self.update = CallContainer()
        self.delete = CallContainer()

        self.messages = MessagesMock()
        self.runs = RunsMock()

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

        return self._make_decorator(getter, state_store or StateStore())

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
