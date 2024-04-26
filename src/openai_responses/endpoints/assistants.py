import json
from typing import Any, Iterable, List, Optional

import httpx
import respx

from openai.pagination import SyncCursorPage
from openai.types.beta.assistant import Assistant, ToolResources
from openai.types.beta.function_tool import FunctionTool
from openai.types.beta.file_search_tool import FileSearchTool
from openai.types.beta.assistant_tool import AssistantTool
from openai.types.beta.assistant_deleted import AssistantDeleted
from openai.types.beta.code_interpreter_tool import CodeInterpreterTool
from openai.types.beta.assistant_tool_param import AssistantToolParam
from openai.types.beta.assistant_create_params import AssistantCreateParams
from openai.types.beta.assistant_update_params import AssistantUpdateParams
from openai.types.beta.assistant_response_format import AssistantResponseFormat
from openai.types.beta.assistant_response_format_option import (
    AssistantResponseFormatOption,
)
from openai.types.beta.assistant_response_format_option_param import (
    AssistantResponseFormatOptionParam,
)

from ._base import StatefulMock, CallContainer
from ..decorators import side_effect
from ..state import StateStore
from ..utils import model_dict, model_parse, utcnow_unix_timestamp_s, remove_none


class AssistantsMock(StatefulMock):
    def __init__(self) -> None:
        super().__init__(
            name="assistants_mock",
            endpoint="/v1/assistants",
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
                    "name": "delete",
                    "method": respx.delete,
                    "pattern": r"/(?P<id>\w+)",
                    "side_effect": self._delete,
                },
            ],
        )

        # NOTE: these are explicitly defined to help with autocomplete and type hints
        self.create = CallContainer()
        self.list = CallContainer()
        self.retrieve = CallContainer()
        self.update = CallContainer()
        self.delete = CallContainer()

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

        content: AssistantCreateParams = json.loads(request.content)

        content_tools = content.get("tools", [])

        asst = Assistant(
            id=self._faker.beta.assistant.id(),
            created_at=utcnow_unix_timestamp_s(),
            description=content.get("description"),
            instructions=content.get("instructions"),
            metadata=content.get("metadata"),
            model=content["model"],
            name=content.get("name"),
            object="assistant",
            tools=self._parse_tool_params(content_tools) or [],
            response_format=self._parse_response_format_params(
                content.get("response_format")
            ),
            temperature=content.get("temperature"),
            tool_resources=model_parse(
                ToolResources,
                content.get("tool_resources"),
            ),
            top_p=content.get("top_p"),
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
        asst.instructions = content.get("instructions", asst.instructions)
        asst.metadata = content.get("metadata", asst.metadata)
        asst.model = content.get("model", asst.model)
        asst.name = content.get("name", asst.name)
        asst.response_format = (
            self._parse_response_format_params(content.get("response_format"))
            or asst.response_format
        )
        asst.temperature = content.get("temperature", asst.temperature)
        asst.tool_resources = (
            model_parse(ToolResources, content.get("tool_resources"))
            or asst.tool_resources
        )
        asst.tools = self._parse_tool_params(content.get("tools")) or asst.tools
        asst.top_p = content.get("top_p", asst.top_p)

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
        params: Optional[Iterable[AssistantToolParam]],
    ) -> Optional[List[AssistantTool]]:
        m = {
            "code_interpreter": CodeInterpreterTool,
            "file_search": FileSearchTool,
            "function": FunctionTool,
        }
        return (
            remove_none([model_parse(m[tool["type"]], tool) for tool in params])  # type: ignore
            if params
            else None
        )

    @staticmethod
    def _parse_response_format_params(
        params: Optional[AssistantResponseFormatOptionParam],
    ) -> Optional[AssistantResponseFormatOption]:
        return (
            model_parse(AssistantResponseFormat, params)
            if isinstance(params, dict)
            else params
        )
