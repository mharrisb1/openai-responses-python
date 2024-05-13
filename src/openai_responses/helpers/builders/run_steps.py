from openai.types.beta.threads.runs.run_step import RunStep

from ..._types.partials.run_steps import PartialRunStep

from ..._utils.faker import faker
from ..._utils.serde import model_parse
from ..._utils.time import utcnow_unix_timestamp_s


__all__ = ["build_run_step"]


def build_run_step(partial: PartialRunStep) -> RunStep:
    return model_parse(
        RunStep,
        {
            "id": faker.beta.thread.run.step.id(),
            "created_at": utcnow_unix_timestamp_s(),
            "object": "thread.run.step",
        }
        | partial,
    )
