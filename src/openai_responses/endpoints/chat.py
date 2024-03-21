import json
from functools import partial
from typing import Any, List, Literal, Optional, TypedDict

import httpx
import respx

from openai.types.chat.chat_completion import ChatCompletion, Choice
from openai.types.completion_usage import CompletionUsage
from openai.types.chat.chat_completion_message import (
    ChatCompletionMessage,
    FunctionCall,
)
from openai.types.chat.chat_completion_message_tool_call import (
    ChatCompletionMessageToolCall,
    Function,
)
from openai.types.chat.completion_create_params import CompletionCreateParams

from ._base import StatelessMock, CallContainer
from ..decorators import side_effect
from ..utils import model_dict, utcnow_unix_timestamp_s


class ChatMock:
    def __init__(self) -> None:
        self.completions = ChatCompletionMock()


class PartialFunctionCall(TypedDict, total=False):
    arguments: str
    name: str


class PartialToolCall(TypedDict, total=False):
    function: PartialFunctionCall


class PartialMessage(TypedDict, total=False):
    content: str
    function_call: PartialFunctionCall
    tool_calls: List[PartialToolCall]


class PartialChoice(TypedDict, total=False):
    finish_reason: Literal[
        "stop",
        "length",
        "tool_calls",
        "content_filter",
        "function_call",
    ]
    message: PartialMessage


class ChatCompletionMock(StatelessMock):
    def __init__(self) -> None:
        super().__init__()
        self.url = self.BASE_URL + "/chat/completions"
        self.create = CallContainer()

    def _register_routes(self, **common: Any) -> None:
        self.create.route = respx.post(url__regex=self.url).mock(
            side_effect=partial(self._create, **common)
        )

    def __call__(
        self,
        *,
        choices: Optional[List[PartialChoice]] = None,
        latency: Optional[float] = None,
        failures: Optional[int] = None,
    ):
        def getter(*args: Any, **kwargs: Any):
            return dict(
                choices=choices or [],
                latency=latency or 0,
                failures=failures or 0,
            )

        return self._make_decorator("chat_completion_mock", getter)

    @side_effect
    def _create(
        self,
        request: httpx.Request,
        route: respx.Route,
        choices: List[PartialChoice],
        **kwargs: Any,
    ) -> httpx.Response:
        self.create.route = route

        content: CompletionCreateParams = json.loads(request.content)

        completion = ChatCompletion(
            id=self._faker.chat.completion.id(),
            choices=[
                self._choice_partial_to_model(i, p) for i, p in enumerate(choices)
            ],
            model=content["model"],
            created=utcnow_unix_timestamp_s(),
            system_fingerprint="",
            object="chat.completion",
            usage=CompletionUsage(completion_tokens=0, prompt_tokens=0, total_tokens=0),
        )

        return httpx.Response(status_code=201, json=model_dict(completion))

    def _choice_partial_to_model(self, i: int, p: PartialChoice) -> Choice:

        def fn_call_partial_to_model(p: Optional[PartialFunctionCall]):
            if p is None:
                return None
            else:
                return FunctionCall(
                    arguments=p.get("arguments", ""),
                    name=p.get("name", ""),
                )

        def tool_calls_partial_to_model(p: Optional[List[PartialToolCall]]):
            if p is None:
                return None
            else:
                calls: List[ChatCompletionMessageToolCall] = []
                for partial_call in p:
                    call_function = partial_call.get("function", {})
                    calls.append(
                        ChatCompletionMessageToolCall(
                            id=self._faker.beta.thread.run.step.step_details.tool_call.id(),
                            function=Function(
                                arguments=call_function.get("arguments", ""),
                                name=call_function.get("name", ""),
                            ),
                            type="function",
                        )
                    )

        message = ChatCompletionMessage(
            content=p.get("message", {}).get("content"),
            role="assistant",
            function_call=fn_call_partial_to_model(
                p.get("message", {}).get("function_call")
            ),
            tool_calls=tool_calls_partial_to_model(
                p.get("message", {}).get("tool_calls")
            ),
        )

        return Choice(
            finish_reason=p.get("finish_reason", "stop"),
            message=message,
            index=i,
        )
