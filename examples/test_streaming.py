from typing import Generator
from typing_extensions import override

import openai
from openai import AssistantEventHandler
from openai.types.beta import AssistantStreamEvent
from openai.types.beta.threads import Run

import openai_responses
from openai_responses import OpenAIMock
from openai_responses.stores import StateStore
from openai_responses.streaming import EventStream, Event
from openai_responses.helpers.builders.runs import run_from_create_request
from openai_responses.helpers.builders.messages import build_message
from openai_responses.ext.httpx import Request, Response

event_count = 0


class EventHandler(AssistantEventHandler):
    @override
    def on_event(self, event: AssistantStreamEvent) -> None:
        global event_count
        if (
            event.event == "thread.run.created"
            or event.event == "thread.run.in_progress"
            or event.event == "thread.message.created"
            or event.event == "thread.run.completed"
        ):
            event_count += 1


class CreateRunEventStream(EventStream):
    def __init__(self, created_run: Run, state_store: StateStore) -> None:
        self.created_run = created_run
        self.state_store = state_store

    @override
    def generate(self) -> Generator[Event, None, None]:
        self.state_store.beta.threads.runs.put(self.created_run)
        yield self.event("thread.run.created", self.created_run)

        self.created_run.status = "in_progress"
        self.state_store.beta.threads.runs.put(self.created_run)
        yield self.event("thread.run.in_progress", self.created_run)

        assistant_message = build_message(
            {
                "assistant_id": self.created_run.assistant_id,
                "thread_id": self.created_run.thread_id,
                "run_id": self.created_run.id,
                "role": "assistant",
                "status": "completed",
                "content": [
                    {
                        "type": "text",
                        "text": {"annotations": [], "value": "Hello! How can I help?"},
                    }
                ],
            }
        )
        self.state_store.beta.threads.messages.put(assistant_message)
        yield self.event("thread.message.created", assistant_message)

        self.created_run.status = "completed"
        self.state_store.beta.threads.runs.put(self.created_run)
        yield self.event("thread.run.completed", self.created_run)


def create_run_stream_response(
    request: Request,
    *,
    thread_id: str,
    state_store: StateStore,
) -> Response:
    # NOTE: creating run this way does not currently inherit config from assistant
    created_run = run_from_create_request(
        thread_id,
        request,
        extra={"model": "gpt-4-turbo", "tools": [{"type": "code_interpreter"}]},
    )
    stream = CreateRunEventStream(created_run, state_store)
    return Response(201, content=stream)


@openai_responses.mock()
def test_handle_stream(openai_mock: OpenAIMock):
    openai_mock.beta.threads.runs.create.response = create_run_stream_response

    client = openai.Client(api_key="sk-fake123")

    assistant = client.beta.assistants.create(
        instructions="You are a personal math tutor. When asked a question, write and run Python code to answer the question.",
        name="Math Tutor",
        tools=[{"type": "code_interpreter"}],
        model="gpt-4-turbo",
    )

    thread = client.beta.threads.create()

    client.beta.threads.messages.create(
        thread_id=thread.id,
        role="user",
        content=[{"type": "text", "text": "Hello!"}],
    )

    with client.beta.threads.runs.stream(
        thread_id=thread.id,
        assistant_id=assistant.id,
        event_handler=EventHandler(),
    ) as stream:
        stream.until_done()
        run = stream.current_run
        assert run

    messages = client.beta.threads.messages.list(thread.id)

    global event_count
    assert event_count == 4
    assert len(messages.data) == 2

    assert openai_mock.beta.threads.runs.create.route.call_count == 1
