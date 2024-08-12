from typing import Annotated, Any, Dict, Literal, List, Optional, TypedDict, Union
from typing_extensions import NotRequired

from openai._utils._transform import PropertyInfo

__all__ = ["PartialAssistant"]


class PartialFunctionDefinition(TypedDict):
    name: str
    description: NotRequired[str]
    parameters: NotRequired[Dict[str, Any]]
    strict: NotRequired[bool]


class PartialCodeInterpreterTool(TypedDict):
    type: Literal["code_interpreter"]


class PartialFileSearch(TypedDict):
    max_num_results: NotRequired[int]


class PartialFileSearchTool(TypedDict):
    type: Literal["file_search"]
    file_search: Optional[PartialFileSearch]


class PartialFunctionTool(TypedDict):
    type: Literal["function"]
    function: PartialFunctionDefinition


class PartialResponseFormatText(TypedDict):
    type: Literal["text"]


class PartialResponseFormatJSONObject(TypedDict):
    type: Literal["json_object"]


class PartialJSONSchema(TypedDict):
    name: str
    description: NotRequired[str]
    schema: NotRequired[Dict[str, Any]]
    strict: Optional[bool]


class PartialResponseFormatJSONSchema(TypedDict):
    type: Literal["json_schema"]
    json_schema: PartialJSONSchema


class PartialToolResourcesCodeInterpreter(TypedDict):
    file_ids: NotRequired[List[str]]


class PartialToolResourcesFileSearch(TypedDict):
    vector_store_ids: NotRequired[List[str]]


class PartialToolResources(TypedDict):
    code_interpreter: NotRequired[PartialToolResourcesCodeInterpreter]
    file_search: NotRequired[PartialToolResourcesFileSearch]


PartialAssistantResponseFormat = Union[
    Literal["auto"],
    PartialResponseFormatText,
    PartialResponseFormatJSONObject,
    PartialResponseFormatJSONSchema,
]

PartialAssistantTool = Annotated[
    Union[
        PartialCodeInterpreterTool,
        PartialFileSearchTool,
        PartialFunctionTool,
    ],
    PropertyInfo(discriminator="type"),
]


class PartialAssistant(TypedDict):
    id: NotRequired[str]
    created_at: NotRequired[int]
    description: NotRequired[str]
    instructions: NotRequired[str]
    metadata: NotRequired[Dict[str, str]]
    model: NotRequired[str]
    name: NotRequired[str]
    object: NotRequired[Literal["assistant"]]
    tools: NotRequired[List[PartialAssistantTool]]
    response_format: NotRequired[PartialAssistantResponseFormat]
    temperature: NotRequired[float]
    tool_resources: NotRequired[PartialToolResources]
    top_p: NotRequired[float]
