from typing import Dict, List, Literal, TypedDict
from typing_extensions import NotRequired

__all__ = ["PartialThread"]


class PartialToolResourcesCodeInterpreter(TypedDict):
    file_ids: NotRequired[List[str]]


class PartialToolResourcesFileSearch(TypedDict):
    vector_store_ids: NotRequired[List[str]]


class PartialToolResources(TypedDict):
    code_interpreter: NotRequired[PartialToolResourcesCodeInterpreter]
    file_search: NotRequired[PartialToolResourcesFileSearch]


class PartialThread(TypedDict):
    id: NotRequired[str]
    created_at: NotRequired[int]
    tool_resources: NotRequired[PartialToolResources]
    metadata: NotRequired[Dict[str, str]]
    object: NotRequired[Literal["thread"]]
