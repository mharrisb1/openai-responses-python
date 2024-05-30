from typing import Annotated, Any, Dict, Literal, List, TypedDict, Union
from typing_extensions import NotRequired

from openai._utils._transform import PropertyInfo

__all__ = ["PartialAssistant"]


class PartialAssistantResponseFormat(TypedDict):
    type: NotRequired[Literal["text", "json_object"]]


class PartialFunctionDefinition(TypedDict):
    name: str
    description: NotRequired[str]
    parameters: NotRequired[Dict[str, Any]]


class PartialCodeInterpreterTool(TypedDict):
    type: Literal["code_interpreter"]


class PartialFileSearchTool(TypedDict):
    type: Literal["file_search"]


class PartialFunctionTool(TypedDict):
    type: Literal["function"]
    function: PartialFunctionDefinition


class PartialToolResourcesCodeInterpreter(TypedDict):
    file_ids: NotRequired[List[str]]


class PartialToolResourcesFileSearch(TypedDict):
    vector_store_ids: NotRequired[List[str]]


class PartialToolResources(TypedDict):
    code_interpreter: NotRequired[PartialToolResourcesCodeInterpreter]
    file_search: NotRequired[PartialToolResourcesFileSearch]


class PartialAssistant(TypedDict):
    id: NotRequired[str]
    created_at: NotRequired[int]
    description: NotRequired[str]
    instructions: NotRequired[str]
    metadata: NotRequired[Dict[str, str]]
    model: NotRequired[str]
    name: NotRequired[str]
    object: NotRequired[Literal["assistant"]]
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
    response_format: NotRequired[
        Union[Literal["none", "auto"], PartialAssistantResponseFormat]
    ]
    temperature: NotRequired[float]
    tool_resources: NotRequired[PartialToolResources]
    top_p: NotRequired[float]
