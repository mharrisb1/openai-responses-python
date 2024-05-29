from typing import Annotated, Dict, List, Literal, TypedDict, Union
from typing_extensions import NotRequired

from openai._utils import PropertyInfo

__all__ = ["PartialRunStep"]


class PartialLastError(TypedDict):
    code: Literal["server_error", "rate_limit_exceeded"]
    message: str


class PartialMessageCreation(TypedDict):
    message_id: str


class PartialMessageCreationStepDetails(TypedDict):
    message_creation: PartialMessageCreation
    type: Literal["message_creation"]


class PartialCodeInterpreterOutputLogs(TypedDict):
    logs: str
    type: Literal["logs"]


class PartialCodeInterpreterOutputImageImage(TypedDict):
    file_id: str


class PartialCodeInterpreterOutputImage(TypedDict):
    image: PartialCodeInterpreterOutputImageImage
    type: Literal["image"]


class PartialCodeInterpreter(TypedDict):
    input: str
    outputs: List[
        Annotated[
            Union[PartialCodeInterpreterOutputLogs, PartialCodeInterpreterOutputImage],
            PropertyInfo(discriminator="type"),
        ]
    ]


class PartialCodeInterpreterToolCall(TypedDict):
    id: str
    code_interpreter: PartialCodeInterpreter
    type: Literal["code_interpreter"]


class PartialFileSearchToolCall(TypedDict):
    id: str
    file_search: object
    type: Literal["file_search"]


class PartialFunction(TypedDict):
    arguments: str
    name: str
    output: NotRequired[str]


class PartialFunctionToolCall(TypedDict):
    id: str
    function: PartialFunction
    type: Literal["function"]


class PartialToolCallsStepDetails(TypedDict):
    tool_calls: List[
        Annotated[
            Union[
                PartialCodeInterpreterToolCall,
                PartialFileSearchToolCall,
                PartialFunctionToolCall,
            ],
            PropertyInfo(discriminator="type"),
        ]
    ]
    type: Literal["tool_calls"]


class PartialUsage(TypedDict):
    completion_tokens: int
    prompt_tokens: int
    total_tokens: int


PartialStepDetails = Annotated[
    Union[PartialMessageCreationStepDetails, PartialToolCallsStepDetails],
    PropertyInfo(discriminator="type"),
]


class PartialRunStep(TypedDict):
    id: NotRequired[str]
    assistant_id: str
    cancelled_at: NotRequired[int]
    completed_at: NotRequired[int]
    created_at: NotRequired[int]
    expired_at: NotRequired[int]
    failed_at: NotRequired[int]
    last_error: NotRequired[PartialLastError]
    metadata: NotRequired[Dict[str, str]]
    object: NotRequired[Literal["thread.run.step"]]
    run_id: str
    status: Literal["in_progress", "cancelled", "failed", "completed", "expired"]
    step_details: PartialStepDetails
    thread_id: str
    type: Literal["message_creation", "tool_calls"]
    usage: NotRequired[PartialUsage]
