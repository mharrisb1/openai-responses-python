from typing import Any, Dict, List, Literal, TypedDict
from typing_extensions import NotRequired

__all__ = ["PartialChatCompletion", "PartialParsedChatCompletion"]


class PartialFunctionCall(TypedDict):
    arguments: str
    name: str


class PartialToolCall(TypedDict):
    id: str
    function: PartialFunctionCall
    type: Literal["function"]


class PartialChatCompletionMessage(TypedDict):
    content: NotRequired[str]
    refusal: NotRequired[str]
    role: Literal["assistant"]
    function_call: NotRequired[PartialFunctionCall]
    tool_calls: NotRequired[List[PartialToolCall]]


class PartialTopLogprob(TypedDict):
    token: str
    bytes: NotRequired[List[int]]
    logprob: float


class PartialChatCompletionTokenLogprob(TypedDict):
    token: str
    bytes: NotRequired[List[int]]
    logprob: float
    top_logprobs: List[PartialTopLogprob]


class PartialChoiceLogprobs(TypedDict):
    content: NotRequired[List[PartialChatCompletionTokenLogprob]]


class PartialChoice(TypedDict):
    finish_reason: Literal[
        "stop",
        "length",
        "tool_calls",
        "content_filter",
        "function_call",
    ]
    index: int
    logprops: NotRequired[PartialChatCompletionTokenLogprob]
    message: PartialChatCompletionMessage


class PartialCompletionUsage(TypedDict):
    completion_tokens: int
    prompt_tokens: int
    total_tokens: int


class PartialChatCompletion(TypedDict):
    id: NotRequired[str]
    choices: NotRequired[List[PartialChoice]]
    created: NotRequired[int]
    model: NotRequired[str]
    object: NotRequired[Literal["chat.completion"]]
    service_tier: NotRequired[Literal["scale", "default"]]
    system_fingerprint: NotRequired[str]
    usage: NotRequired[PartialCompletionUsage]


class PartialParsedChatCompletionMessage(PartialChatCompletionMessage):
    parsed: NotRequired[Dict[str, Any]]


class PartialParsedChoice(PartialChoice):
    message: PartialParsedChatCompletionMessage  # type: ignore


class PartialParsedChatCompletion(PartialChatCompletion):
    choices: NotRequired[List[PartialParsedChoice]]  # type: ignore
