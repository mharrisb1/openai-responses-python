import pytest
from openai import OpenAI, AsyncOpenAI, NotFoundError

import openai_responses
from openai_responses import ThreadsMock, MessagesMock, RunsMock
from openai_responses.state import StateStore


@openai_responses.mock.beta.threads()
def test_create_empty_thread(threads_mock: ThreadsMock):
    client = OpenAI(api_key="fakeKey")
    empty_thread = client.beta.threads.create()
    assert empty_thread.id
    assert threads_mock.create.route.calls.call_count == 1


@pytest.mark.asyncio
@openai_responses.mock.beta.threads()
async def test_async_create_empty_thread(threads_mock: ThreadsMock):
    client = AsyncOpenAI(api_key="fakeKey")
    empty_thread = await client.beta.threads.create()
    assert empty_thread.id
    assert threads_mock.create.route.calls.call_count == 1


@openai_responses.mock.beta.threads()
def test_create_thread_with_messages(threads_mock: ThreadsMock):
    client = OpenAI(api_key="fakeKey")
    message_thread = client.beta.threads.create(
        messages=[
            {
                "role": "user",
                "content": "Hello, what is AI?",
            },
            {
                "role": "user",
                "content": "How does AI work? Explain it in simple terms.",
            },
        ]
    )
    assert message_thread.id
    assert threads_mock.create.route.calls.call_count == 1


@openai_responses.mock.beta.threads()
def test_retrieve_tread(threads_mock: ThreadsMock):
    client = OpenAI(api_key="fakeKey")

    with pytest.raises(NotFoundError):
        client.beta.threads.retrieve("invalid-id")

    thread = client.beta.threads.create()
    found = client.beta.threads.retrieve(thread.id)

    assert found.id == thread.id

    assert threads_mock.retrieve.route.calls.call_count == 2


@openai_responses.mock.beta.threads()
def test_update_thread(threads_mock: ThreadsMock):
    client = OpenAI(api_key="fakeKey")

    with pytest.raises(NotFoundError):
        client.beta.threads.update("invalid-id")

    thread = client.beta.threads.create()
    updated = client.beta.threads.update(thread.id, metadata={"modified": "true"})
    assert updated.id == thread.id
    assert updated.metadata == {"modified": "true"}

    assert threads_mock.update.route.calls.call_count == 2


@openai_responses.mock.beta.threads()
def test_delete_thread(threads_mock: ThreadsMock):
    client = OpenAI(api_key="fakeKey")

    assert not client.beta.threads.delete("invalid-id").deleted

    thread = client.beta.threads.create()
    assert client.beta.threads.delete(thread.id).deleted

    assert threads_mock.delete.route.calls.call_count == 2


@openai_responses.mock.beta.threads.messages()
def test_create_thread_message(messages_mock: MessagesMock):
    client = OpenAI(api_key="fakeKey")

    thread_message = client.beta.threads.messages.create(
        "thread_abc123",
        role="user",
        content="How does AI work? Explain it in simple terms.",
    )

    assert thread_message.id
    assert messages_mock.create.route.calls.call_count == 1


@pytest.mark.asyncio
@openai_responses.mock.beta.threads.messages()
async def test_async_create_thread_message(messages_mock: MessagesMock):
    client = AsyncOpenAI(api_key="fakeKey")

    thread_message = await client.beta.threads.messages.create(
        "thread_abc123",
        role="user",
        content="How does AI work? Explain it in simple terms.",
    )

    assert thread_message.id
    assert messages_mock.create.route.calls.call_count == 1


@openai_responses.mock.beta.threads.messages(validate_thread_exists=True)
def test_create_thread_message_with_thread_exists_validation(
    messages_mock: MessagesMock,
):
    client = OpenAI(api_key="fakeKey")

    with pytest.raises(NotFoundError):
        client.beta.threads.messages.create(
            "thread_abc123",
            role="user",
            content="How does AI work? Explain it in simple terms.",
        )

    assert messages_mock.create.route.calls.call_count == 1


@openai_responses.mock.beta.threads.messages()
def test_list_thread_messages(messages_mock: MessagesMock):
    client = OpenAI(api_key="fakeKey")

    for _ in range(20):
        client.beta.threads.messages.create(
            "thread_abc123",
            role="user",
            content="How does AI work? Explain it in simple terms.",
        )

    messages = client.beta.threads.messages.list("thread_abc123")
    assert len(messages.data) == 20
    assert messages_mock.create.route.calls.call_count == 20
    assert messages_mock.list.route.calls.call_count == 1


@openai_responses.mock.beta.threads.messages()
def test_retrieve_thread_message(messages_mock: MessagesMock):
    client = OpenAI(api_key="fakeKey")

    with pytest.raises(NotFoundError):
        client.beta.threads.messages.retrieve("invalid_id", thread_id="thread_abc123")

    thread_message = client.beta.threads.messages.create(
        "thread_abc123",
        role="user",
        content="How does AI work? Explain it in simple terms.",
    )
    found = client.beta.threads.messages.retrieve(
        thread_message.id, thread_id="thread_abc123"
    )

    assert thread_message.id == found.id
    assert messages_mock.retrieve.route.calls.call_count == 2


@openai_responses.mock.beta.threads.messages()
def test_update_thread_message(messages_mock: MessagesMock):
    client = OpenAI(api_key="fakeKey")

    with pytest.raises(NotFoundError):
        client.beta.threads.messages.update("invalid_id", thread_id="thread_abc123")

    thread_message = client.beta.threads.messages.create(
        "thread_abc123",
        role="user",
        content="How does AI work? Explain it in simple terms.",
    )
    updated = client.beta.threads.messages.update(
        thread_message.id, thread_id="thread_abc123", metadata={"modified": "true"}
    )
    assert updated.id == thread_message.id
    assert updated.metadata == {"modified": "true"}

    assert messages_mock.update.route.calls.call_count == 2


@openai_responses.mock.beta.threads.runs()
def test_create_thread_run(runs_mock: RunsMock):
    client = OpenAI(api_key="fakeKey")

    run = client.beta.threads.runs.create(
        thread_id="thread_abc123",
        assistant_id="asst_abc123",
    )

    assert run.id
    assert run.status == "queued"
    assert runs_mock.create.route.calls.call_count == 1


shared_state = StateStore()


@openai_responses.mock.beta.threads.messages(state_store=shared_state)
@openai_responses.mock.beta.threads.runs(state_store=shared_state)
def test_create_thread_run_with_additional_messages(
    messages_mock: MessagesMock,
    runs_mock: RunsMock,
):
    client = OpenAI(api_key="fakeKey")

    run = client.beta.threads.runs.create(
        thread_id="thread_abc123",
        assistant_id="asst_abc123",
        additional_messages=[
            {
                "role": "user",
                "content": "Hello, additional messages!",
            }
        ],
    )
    assert run.id
    assert run.status == "queued"

    messages = client.beta.threads.messages.list(thread_id="thread_abc123")
    assert len(messages.data) == 1

    assert messages_mock.list.route.calls.call_count == 1
    assert runs_mock.create.route.calls.call_count == 1


@openai_responses.mock.beta.threads.runs(
    sequence={
        "retrieve": [
            {"status": "in_progress"},
        ]
    }
)
def test_retrieve_thread_run(runs_mock: RunsMock):
    client = OpenAI(api_key="fakeKey")

    run = client.beta.threads.runs.create(
        thread_id="thread_abc123",
        assistant_id="asst_abc123",
    )
    assert run.status == "queued"

    found = client.beta.threads.runs.retrieve(run.id, thread_id="thread_abc123")

    assert found.id == run.id
    assert found.status == "in_progress"

    assert runs_mock.create.route.calls.call_count == 1
    assert runs_mock.retrieve.route.calls.call_count == 1


@openai_responses.mock.beta.threads.runs(
    sequence={
        "create": [
            {"status": "in_progress"},
        ],
        "retrieve": [
            {"status": "in_progress"},
            {"status": "in_progress"},
            {"status": "in_progress"},
            {"status": "in_progress"},
            {"status": "completed"},
        ],
    }
)
def test_polled_get_status(runs_mock: RunsMock):
    client = OpenAI(api_key="fakeKey")

    run = client.beta.threads.runs.create(
        thread_id="thread_abc123",
        assistant_id="asst_abc123",
    )

    while run.status != "completed":
        run = client.beta.threads.runs.retrieve(run.id, thread_id="thread_abc123")

    assert run.status == "completed"
    assert runs_mock.create.route.calls.call_count == 1
    assert runs_mock.retrieve.route.calls.call_count == 5


@openai_responses.mock.beta.threads()
@openai_responses.mock.beta.threads.runs()
def test_list_runs(threads_mock: ThreadsMock, runs_mock: RunsMock):
    client = OpenAI(api_key="fakeKey")
    thread = client.beta.threads.create()

    for _ in range(20):
        client.beta.threads.runs.create(thread.id, assistant_id="asst_abc123")

    runs = client.beta.threads.runs.list(thread.id)

    assert len(runs.data) == 20

    assert threads_mock.create.route.calls.call_count == 1
    assert runs_mock.create.route.calls.call_count == 20
    assert runs_mock.list.route.calls.call_count == 1


@openai_responses.mock.beta.threads.runs()
def test_update_thread_run(runs_mock: RunsMock):
    client = OpenAI(api_key="fakeKey")

    run = client.beta.threads.runs.create(
        thread_id="thread_abc123",
        assistant_id="asst_abc123",
    )
    assert run.status == "queued"

    run = client.beta.threads.runs.update(
        run.id, thread_id="thread_abc123", metadata={"modified": "true"}
    )
    assert run.metadata == {"modified": "true"}

    assert runs_mock.create.route.calls.call_count == 1
    assert runs_mock.update.route.calls.call_count == 1


@openai_responses.mock.beta.threads.runs(
    sequence={
        "retrieve": [
            {"status": "in_progress"},
            {"status": "cancelled"},
        ],
    }
)
def test_cancel_run(runs_mock: RunsMock):
    client = OpenAI(api_key="fakeKey")

    run = client.beta.threads.runs.create(
        thread_id="thread_abc123",
        assistant_id="asst_abc123",
    )

    assert run.status == "queued"

    run = client.beta.threads.runs.retrieve(run.id, thread_id="thread_abc123")
    assert run.status == "in_progress"

    run = client.beta.threads.runs.cancel(run.id, thread_id="thread_abc123")
    assert run.status == "cancelling"

    run = client.beta.threads.runs.retrieve(run.id, thread_id="thread_abc123")
    assert run.status == "cancelled"

    assert runs_mock.create.route.calls.call_count == 1
    assert runs_mock.cancel.route.calls.call_count == 1
    assert runs_mock.retrieve.route.calls.call_count == 2
