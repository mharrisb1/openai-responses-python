import json
from typing import Any, Type

from openai import BaseModel

from .._types.generics import M

__all__ = ["json_loads", "model_dict", "model_parse"]


def json_loads(b: bytes) -> Any:
    d = json.loads(b)
    return {k: v for k, v in d.items() if v is not None}


def model_dict(m: BaseModel, **kwargs: Any) -> dict[str, Any]:
    if hasattr(m, "model_dump"):
        return getattr(m, "model_dump")(**kwargs)
    else:
        return getattr(m, "dict")(**kwargs)


def model_parse(m: Type[M], d: object, **kwargs: Any) -> M:
    if hasattr(m, "model_validate"):
        return getattr(m, "model_validate")(d, **kwargs)
    else:
        return getattr(m, "parse_obj")(d, **kwargs)
