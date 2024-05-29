from typing import Annotated, Dict, List, Literal, TypedDict, Union
from typing_extensions import NotRequired

from openai._utils import PropertyInfo

__all__ = ["PartialMessage", "PartialMessageDeleted"]


class PartialFileSearchTool(TypedDict):
    type: Literal["file_search"]


class PartialCodeInterpreterTool(TypedDict):
    type: Literal["code_interpreter"]


class PartialAttachment(TypedDict):
    file_id: NotRequired[str]
    tools: NotRequired[List[Union[PartialCodeInterpreterTool, PartialFileSearchTool]]]


class PartialImageFile(TypedDict):
    file_id: str


class PartialImageFileContentBlock(TypedDict):
    type: Literal["image_file"]
    image_file: PartialImageFile


class PartialFileCitation(TypedDict):
    file_id: str
    quote: str


class PartialFileCitationAnnotation(TypedDict):
    end_index: int
    file_citation: PartialFileCitation
    start_index: int
    text: str
    type: Literal["file_citation"]


class PartialFilePath(TypedDict):
    file_id: str


class PartialFilePathAnnotation(TypedDict):
    end_index: int
    file_path: PartialFilePath
    start_index: int
    text: str
    type: Literal["file_path"]


class PartialText(TypedDict):
    annotations: List[
        Annotated[
            Union[PartialFileCitationAnnotation, PartialFilePathAnnotation],
            PropertyInfo(discriminator="type"),
        ]
    ]
    value: str


class PartialTextContentBlock(TypedDict):
    type: Literal["text"]
    text: PartialText


class PartialMessage(TypedDict):
    id: NotRequired[str]
    assistant_id: NotRequired[str]
    attachments: NotRequired[List[PartialAttachment]]
    completed_at: NotRequired[int]
    content: NotRequired[
        List[
            Annotated[
                Union[PartialImageFileContentBlock, PartialTextContentBlock],
                PropertyInfo(discriminator="type"),
            ]
        ]
    ]
    created_at: NotRequired[int]
    incomplete_at: NotRequired[int]
    metadata: NotRequired[Dict[str, str]]
    object: NotRequired[Literal["thread.message"]]
    role: NotRequired[Literal["user", "assistant"]]
    run_id: NotRequired[str]
    status: NotRequired[Literal["in_progress", "incomplete", "completed"]]
    thread_id: NotRequired[str]


class PartialMessageDeleted(TypedDict):
    id: NotRequired[str]
    object: NotRequired[Literal["thread.message.deleted"]]
    deleted: NotRequired[bool]
