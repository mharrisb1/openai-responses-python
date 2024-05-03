from typing import Any, Optional, Type

from openai import BaseModel
from pydantic import ValidationError

from .._types.generics import M


def model_dict(m: BaseModel) -> dict[str, Any]:
    if hasattr(m, "model_dump"):
        return getattr(m, "model_dump")()
    else:
        return getattr(m, "dict")()


def model_parse(m: Type[M], d: Optional[object]) -> Optional[M]:
    if not d:
        return None
    try:
        if hasattr(m, "model_validate"):
            return getattr(m, "model_validate")(d)
        else:
            return getattr(m, "parse_obj")(d)
    except ValidationError:
        return None
