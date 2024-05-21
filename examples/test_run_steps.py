import openai

import openai_responses
from openai_responses import OpenAIMock
from openai_responses.helpers.builders.messages import build_message
from openai_responses.helpers.builders.run_steps import build_run_step


@openai_responses.mock()
def test_list_run_steps(openai_mock: OpenAIMock):
    client = openai.Client(api_key="sk-fake123")

    assistant = client.beta.assistants.create(
        instructions="You are a personal math tutor. When asked a question, write and run Python code to answer the question.",
        name="Math Tutor",
        tools=[{"type": "code_interpreter"}],
        model="gpt-4-turbo",
    )

    thread = client.beta.threads.create()

    run = client.beta.threads.runs.create(
        thread.id,
        assistant_id=assistant.id,
    )

    # NOTE: need to manually construct assistant message and run step
    assistant_message = build_message(
        {
            "assistant_id": assistant.id,
            "content": [
                {
                    "type": "text",
                    "text": {
                        "annotations": [],
                        "value": "Hello! Feel free to ask me any questions.",
                    },
                }
            ],
            "role": "assistant",
            "run_id": run.id,
            "status": "completed",
            "thread_id": thread.id,
        }
    )

    run_step = build_run_step(
        {
            "assistant_id": assistant.id,
            "thread_id": thread.id,
            "run_id": run.id,
            "status": "in_progress",
            "type": "message_creation",
            "step_details": {
                "type": "message_creation",
                "message_creation": {
                    "message_id": assistant_message.id,
                },
            },
        }
    )
    openai_mock.state.beta.threads.messages.put(assistant_message)
    openai_mock.state.beta.threads.runs.steps.put(run_step)

    steps = client.beta.threads.runs.steps.list(run.id, thread_id=thread.id)

    assert len(steps.data) == 1
