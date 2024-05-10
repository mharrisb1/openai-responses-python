from .._types.generics import M


def model_copy(m: M) -> M:
    if hasattr(m, "model_validate"):
        return getattr(m, "model_copy")()
    else:
        return getattr(m, "copy")()
