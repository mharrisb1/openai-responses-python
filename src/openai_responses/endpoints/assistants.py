import json
from functools import partial
from typing import Any, Iterable, List, Optional

import httpx
import respx

from openai.types import FunctionDefinition
from openai.pagination import SyncCursorPage
from openai.types.beta.assistant import Assistant
from openai.types.beta.function_tool import FunctionTool
from openai.types.beta.retrieval_tool import RetrievalTool
from openai.types.beta.assistant_tool import AssistantTool
from openai.types.beta.assistant_deleted import AssistantDeleted
from openai.types.beta.code_interpreter_tool import CodeInterpreterTool
from openai.types.beta.assistant_tool_param import AssistantToolParam
from openai.types.beta.assistant_create_params import AssistantCreateParams
from openai.types.beta.assistant_update_params import AssistantUpdateParams

from ._base import StatefulMock, CallContainer
from ..decorators import side_effect
from ..state import StateStore
from ..utils import model_dict, utcnow_unix_timestamp_s


class AssistantsMock(StatefulMock):
    def __init__(self) -> None:
        super().__init__()
        self.url = self.BASE_URL + "/assistants"
        self.create = CallContainer()
        self.list = CallContainer()
        self.retrieve = CallContainer()
        self.update = CallContainer()
        self.delete = CallContainer()

    def _register_routes(self, **common: Any) -> None:
        self.create.route = respx.post(url__regex=self.url).mock(
            side_effect=partial(self._create, **common)
        )
        self.list.route = respx.get(url__regex=self.url).mock(
            side_effect=partial(self._list, **common)
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

        return self._make_decorator(
            "assistants_mock", getter, state_store or StateStore()
        )

    @side_effect
    def _create(
        self,
        request: httpx.Request,
        route: respx.Route,
        state_store: StateStore,
        **kwargs: Any,
    ) -> httpx.Response:
        self.create.route = route

        content: AssistantCreateParams = json.loads(request.content)

        content_tools = content.get("tools", [])

        asst = Assistant(
            id=self._faker.beta.assistant.id(),
            created_at=utcnow_unix_timestamp_s(),
            description=content.get("description"),
            file_ids=content.get("file_ids", []),
            instructions=content.get("instructions"),
            metadata=content.get("metadata"),
            model=content["model"],
            name=content.get("name"),
            object="assistant",
            tools=self._parse_tool_params(content_tools),
        )
        state_store.beta.assistants.put(asst)

        return httpx.Response(status_code=201, json=model_dict(asst))

    @side_effect
    def _list(
        self,
        request: httpx.Request,
        route: respx.Route,
        state_store: StateStore,
        **kwargs: Any,
    ) -> httpx.Response:
        self.list.route = route

        limit = request.url.params.get("limit")
        order = request.url.params.get("order")
        after = request.url.params.get("after")
        before = request.url.params.get("before")

        assts = SyncCursorPage[Assistant](
            data=state_store.beta.assistants.list(limit, order, after, before)
        )

        return httpx.Response(status_code=200, json=model_dict(assts))

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
        asst = state_store.beta.assistants.get(id)

        if not asst:
            return httpx.Response(status_code=404)

        else:
            return httpx.Response(status_code=200, json=model_dict(asst))

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
        content: AssistantUpdateParams = json.loads(request.content)

        asst = state_store.beta.assistants.get(id)

        if not asst:
            return httpx.Response(status_code=404)

        asst.description = content.get("description", asst.description)
        asst.file_ids = content.get("file_ids", asst.file_ids)
        asst.instructions = content.get("instructions", asst.instructions)
        asst.metadata = content.get("metadata", asst.metadata)
        asst.model = content.get("model", asst.model)
        asst.name = content.get("name", asst.name)

        update_tools = content.get("tools")
        if update_tools:
            asst.tools = self._parse_tool_params(update_tools)

        state_store.beta.assistants.put(asst)

        return httpx.Response(status_code=200, json=model_dict(asst))

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
        deleted = state_store.beta.assistants.delete(id)

        return httpx.Response(
            status_code=200,
            json=model_dict(
                AssistantDeleted(id=id, deleted=deleted, object="assistant.deleted")
            ),
        )

    @staticmethod
    def _parse_tool_params(
        tool_params: Iterable[AssistantToolParam],
    ) -> List[AssistantTool]:
        tools: List[AssistantTool] = []

        for tool in tool_params:
            if tool["type"] == "code_interpreter":
                tools.append(CodeInterpreterTool(type=tool["type"]))
            elif tool["type"] == "retrieval":
                tools.append(RetrievalTool(type=tool["type"]))
            else:
                tools.append(
                    FunctionTool(
                        type=tool["type"],
                        function=FunctionDefinition(
                            name=tool["function"]["name"],
                            description=tool["function"].get("description"),
                            parameters=tool["function"].get("parameters"),
                        ),
                    )
                )

        return tools
