from typing import Annotated, Literal, List, Optional, TypedDict, Union
from typing_extensions import Required

from openai._utils._transform import PropertyInfo
from openai.types.beta.assistant_tool_param import AssistantToolParam
from openai.types.beta.threads.run_status import RunStatus

__all__ = ["PartialRun", "PartialRunStep"]


class PartialFunctionNoOutput(TypedDict):
    name: str
    arguments: str


class PartialRequiredActionFunctionToolCall(TypedDict):
    id: str
    function: PartialFunctionNoOutput
    type: Literal["function"]


class PartialRequiredActionSubmitToolOutputs(TypedDict):
    tool_calls: List[PartialRequiredActionFunctionToolCall]


class PartialRequiredAction(TypedDict):
    submit_tool_outputs: PartialRequiredActionSubmitToolOutputs
    type: Literal["submit_tool_outputs"]


class PartialLastError(TypedDict, total=False):
    code: Literal["server_error", "rate_limit_exceeded", "invalid_prompt"]
    message: str


class PartialRun(TypedDict, total=False):
    status: RunStatus
    required_action: PartialRequiredAction
    last_error: PartialLastError
    expires_at: int
    started_at: int
    cancelled_at: int
    failed_at: int
    completed_at: int
    model: str
    instructions: str
    tools: List[AssistantToolParam]
    file_ids: List[str]


class PartialCodeInterpreterOutputLogs(TypedDict):
    logs: str
    type: Literal["logs"]


class PartialCodeInterpreterOutputImageImage(TypedDict):
    file_id: str


class PartialCodeInterpreterOutputImage(TypedDict):
    type: Literal["image"]
    image: PartialCodeInterpreterOutputImageImage


class PartialCodeInterpreter(TypedDict):
    input: str
    outputs: List[
        Annotated[
            Union[
                PartialCodeInterpreterOutputLogs,
                PartialCodeInterpreterOutputImage,
            ],
            PropertyInfo(discriminator="type"),
        ]
    ]


class PartialCodeInterpreterToolCall(TypedDict):
    type: Literal["code_interpreter"]
    id: str
    code_interpreter: PartialCodeInterpreter


class PartialRetrievalToolCall(TypedDict):
    type: Literal["retrieval"]
    id: str


class PartialFunction(TypedDict, total=False):
    name: Required[str]
    arguments: Required[str]
    output: Optional[str]


class PartialFunctionToolCall(TypedDict):
    type: Literal["function"]
    id: str
    function: PartialFunction


class PartialToolCallsStepDetails(TypedDict):
    type: Literal["tool_calls"]
    tool_calls: List[
        Annotated[
            Union[
                PartialCodeInterpreterToolCall,
                PartialRetrievalToolCall,
                PartialFunctionToolCall,
            ],
            PropertyInfo(discriminator="type"),
        ]
    ]


class PartialMessageCreation(TypedDict):
    message_id: str


class PartialMessageCreationStepDetails(TypedDict):
    type: Literal["message_creation"]
    message_creation: PartialMessageCreation


class PartialRunStep(TypedDict, total=False):
    id: str
    assistant_id: str
    cancelled_at: Optional[int]
    completed_at: Optional[int]
    expired_at: Optional[int]
    failed_at: Optional[int]
    last_error: Optional[PartialLastError]
    status: Literal["in_progress", "cancelled", "failed", "completed", "expired"]
    step_details: Required[
        Annotated[
            Union[PartialMessageCreationStepDetails, PartialToolCallsStepDetails],
            PropertyInfo(discriminator="type"),
        ]
    ]
    type: Literal["message_creation", "tool_calls"]
