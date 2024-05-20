from openai.types.beta.threads.run import Run

from ._base import _generic_merge_with_partial

from ..._types.partials.runs import PartialRun

__all__ = ["merge_run_with_partial"]


def merge_run_with_partial(r: Run, p: PartialRun) -> Run:
    return _generic_merge_with_partial(Run, r, p)
