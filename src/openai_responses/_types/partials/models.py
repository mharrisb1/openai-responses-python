from typing import List, Literal, TypedDict
from typing_extensions import NotRequired


class PartialModel(TypedDict):
    id: NotRequired[str]
    created: NotRequired[int]
    object: NotRequired[Literal["model"]]
    owned_by: NotRequired[str]


class PartialModelList(TypedDict):
    object: NotRequired[Literal["list"]]
    data: List[PartialModel]
