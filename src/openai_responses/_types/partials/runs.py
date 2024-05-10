from typing import Annotated, Any, Dict, List, Literal, TypedDict, Union
from typing_extensions import NotRequired

from openai._utils import PropertyInfo

__all__ = ["PartialRun"]


class PartialIncompleteDetails(TypedDict):
    reason: NotRequired[Literal["max_completion_tokens", "max_prompt_tokens"]]


class PartialLastError(TypedDict):
    code: Literal["server_error", "rate_limit_exceeded", "invalid_prompt"]
    message: str


class PartialFunction(TypedDict):
    arguments: str
    name: str


class PartialRequiredActionFunctionToolCall(TypedDict):
    id: str
    function: PartialFunction
    type: Literal["function"]


class PartialRequiredActionSubmitToolOutputs(TypedDict):
    tool_calls: List[PartialRequiredActionFunctionToolCall]


class PartialRequiredAction(TypedDict):
    submit_tool_outputs: PartialRequiredActionSubmitToolOutputs
    type: Literal["submit_tool_outputs"]


class PartialAssistantResponseFormat(TypedDict):
    type: NotRequired[Literal["text", "json_object"]]


class PartialAssistantToolChoiceFunction(TypedDict):
    name: str


class PartialAssistantToolChoice(TypedDict):
    type: Literal["function", "code_interpreter", "file_search"]
    function: NotRequired[PartialAssistantToolChoiceFunction]


class PartialCodeInterpreterTool(TypedDict):
    type: Literal["code_interpreter"]


class PartialFileSearchTool(TypedDict):
    type: Literal["file_search"]


class PartialFunctionDefinition(TypedDict):
    name: str
    description: NotRequired[str]
    parameters: NotRequired[Dict[str, Any]]


class PartialFunctionTool(TypedDict):
    function: PartialFunctionDefinition
    type: Literal["function"]


class PartialTruncationStrategy(TypedDict):
    type: Literal["auto", "last_messages"]
    last_messages: NotRequired[int]


class PartialUsage(TypedDict):
    completion_tokens: int
    prompt_tokens: int
    total_tokens: int


class PartialRun(TypedDict):
    id: NotRequired[str]
    assistant_id: NotRequired[str]
    cancelled_at: NotRequired[int]
    completed_at: NotRequired[int]
    created_at: NotRequired[int]
    expires_at: NotRequired[int]
    failed_at: NotRequired[int]
    incomplete_details: NotRequired[PartialIncompleteDetails]
    instructions: NotRequired[str]
    last_error: NotRequired[PartialLastError]
    max_completion_tokens: NotRequired[int]
    max_prompt_tokens: NotRequired[int]
    metadata: NotRequired[Dict[str, str]]
    model: NotRequired[str]
    object: NotRequired[Literal["thread.run"]]
    required_action: NotRequired[PartialRequiredAction]
    response_format: NotRequired[
        Union[Literal["none", "auto"], PartialAssistantResponseFormat]
    ]
    started_at: NotRequired[int]
    status: NotRequired[
        Literal[
            "queued",
            "in_progress",
            "requires_action",
            "cancelling",
            "cancelled",
            "failed",
            "completed",
            "expired",
        ]
    ]
    thread_id: NotRequired[str]
    tool_choice: NotRequired[
        Union[Literal["none", "auto", "required"], PartialAssistantToolChoice]
    ]
    tools: NotRequired[
        List[
            Annotated[
                Union[
                    PartialCodeInterpreterTool,
                    PartialFileSearchTool,
                    PartialFunctionTool,
                ],
                PropertyInfo(discriminator="type"),
            ]
        ]
    ]
    truncation_strategy: NotRequired[PartialTruncationStrategy]
    usage: NotRequired[PartialUsage]
    temperature: NotRequired[float]
    top_p: NotRequired[float]
