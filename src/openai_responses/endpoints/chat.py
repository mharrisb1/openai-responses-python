import json
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
from ..tokens import count_tokens


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
        super().__init__(
            name="chat_completion_mock",
            endpoint="/v1/chat/completions",
            route_registrations=[
                {
                    "name": "create",
                    "method": respx.post,
                    "pattern": None,
                    "side_effect": self._create,
                }
            ],
        )
        self.create = CallContainer()

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

        return self._make_decorator(getter)

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
        )

        generated = ""
        for choice in completion.choices:
            if choice.message.content:
                generated += choice.message.content
            elif choice.message.tool_calls:
                for tool_call in choice.message.tool_calls:
                    generated += tool_call.function.arguments

        prompt = ""
        for message in content["messages"]:
            prompt += str(message.get("content"))

        completion_tokens = count_tokens(completion.model, generated)
        prompt_tokens = count_tokens(completion.model, prompt)
        total_tokens = completion_tokens + prompt_tokens

        completion.usage = CompletionUsage(
            completion_tokens=completion_tokens,
            prompt_tokens=prompt_tokens,
            total_tokens=total_tokens,
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
                return calls

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
