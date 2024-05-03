import json
from typing_extensions import override

import httpx
import respx

from openai.types.beta.assistant import Assistant
from openai.types.beta.assistant_create_params import AssistantCreateParams

from .base import StatefulRoute

from .._stores import StateStore
from .._types.partials.assistants import PartialAssistant

from .._utils.faker import faker
from .._utils.serde import model_dict, model_parse
from .._utils.time import utcnow_unix_timestamp_s

__all__ = ["AssistantCreateRoute"]


class AssistantCreateRoute(StatefulRoute[Assistant, PartialAssistant]):
    def __init__(self, router: respx.MockRouter, state: StateStore) -> None:
        super().__init__(
            route=router.post(url__regex="/v1/assistants"),
            status_code=201,
            state=state,
        )

    @override
    def _handler(
        self,
        request: httpx.Request,
        route: respx.Route,
    ) -> httpx.Response:
        self._route = route
        model = self._build({}, request)
        self._state.beta.assistants.put(model)
        return httpx.Response(
            status_code=self._status_code,
            json=model_dict(model),
        )

    @staticmethod
    def _build(partial: PartialAssistant, request: httpx.Request) -> Assistant:
        content: AssistantCreateParams = json.loads(request.content)
        assistant = model_parse(
            Assistant,
            {
                "id": partial.get("id", faker.beta.assistant.id()),
                "created_at": partial.get("created_at", utcnow_unix_timestamp_s()),
                "description": content.get("description", partial.get("description")),
                "instructions": content.get(
                    "instructions", partial.get("instructions")
                ),
                "metadata": content.get("metadata", partial.get("metadata")),
                "model": content["model"],
                "name": content.get("name", partial.get("name")),
                "object": "assistant",
                "tools": content.get("tools", partial.get("tools", [])),
                "response_format": content.get(
                    "response_format", partial.get("response_format")
                ),
                "temperature": content.get("temperature", partial.get("temperature")),
                "tool_resources": content.get(
                    "tool_resources", partial.get("tool_resources")
                ),
                "top_p": content.get("top_p", partial.get("top_p")),
            },
        )
        assert assistant, "Parsing failed"
        return assistant
