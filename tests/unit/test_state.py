import pytest
from openai.types import FileObject
from openai.types.beta.assistant import Assistant
from openai.types.beta.thread import Thread
from openai.types.beta.threads.message import Message
from openai.types.beta.threads.run import Run

from openai_responses.state import StateStore


@pytest.fixture
def state_store() -> StateStore:
    return StateStore()


def test_file_store(state_store: StateStore):
    obj = FileObject(
        id="file-abc123",
        bytes=0,
        created_at=0,
        filename="foo.json",
        object="file",
        purpose="assistants",
        status="uploaded",
    )
    state_store.files.put(obj)
    files = state_store.files.list()
    assert len(files) == 1
    files = state_store.files.list(purpose="assistants")
    assert len(files) == 1
    files = state_store.files.list(purpose="fine-tune")
    assert len(files) == 0
    file = state_store.files.get("file-abc123")
    assert file
    file = state_store.files.get("invalid-id")
    assert file is None
    is_deleted = state_store.files.delete("invalid-id")
    assert not is_deleted
    is_deleted = state_store.files.delete("file-abc123")
    assert is_deleted


def test_assistant_store(state_store: StateStore):
    obj = Assistant(
        id="asst_abc123",
        created_at=0,
        file_ids=[],
        model="",
        object="assistant",
        tools=[],
    )
    state_store.beta.assistants.put(obj)
    assts = state_store.beta.assistants.list()
    assert len(assts) == 1
    asst = state_store.beta.assistants.get("asst_abc123")
    assert asst
    deleted = state_store.beta.assistants.delete("invalid_id")
    assert not deleted
    deleted = state_store.beta.assistants.delete("asst_abc123")
    assert deleted

    for i in range(100):
        state_store.beta.assistants.put(
            Assistant(
                id=f"asst_{i}",
                created_at=0,
                file_ids=[],
                model="",
                object="assistant",
                tools=[],
            )
        )

    assts = state_store.beta.assistants.list(
        limit=100,
        order="asc",
        after="asst_19",
        before="asst_30",
    )
    assert len(assts) == 10
    assert assts[0].id == "asst_20"
    assert assts[-1].id == "asst_29"

    assts = state_store.beta.assistants.list(
        limit=100,
        order="desc",
        after="asst_30",
        before="asst_19",
    )
    assert len(assts) == 10
    assert assts[0].id == "asst_29"
    assert assts[-1].id == "asst_20"


def test_thread_store(state_store: StateStore):
    obj = Thread(id="thread_abc123", created_at=0, object="thread")
    state_store.beta.threads.put(obj)
    found = state_store.beta.threads.get("invalid_id")
    assert found is None
    found = state_store.beta.threads.get("thread_abc123")
    assert found
    deleted = state_store.beta.threads.delete("invalid_id")
    assert not deleted
    deleted = state_store.beta.threads.delete("thread_abc123")
    assert deleted


def test_message_store(state_store: StateStore):
    obj = Message(
        id="msg_abc123",
        content=[],
        created_at=0,
        file_ids=[],
        object="thread.message",
        role="user",
        status="completed",
        thread_id="thread_abc123",
    )
    state_store.beta.threads.messages.put(obj)
    messages = state_store.beta.threads.messages.list(thread_id="thread_abc123")
    assert len(messages) == 1
    messages = state_store.beta.threads.messages.list(thread_id="invalid_id")
    assert len(messages) == 0
    deleted = state_store.beta.threads.messages.delete("invalid_id")
    assert not deleted
    deleted = state_store.beta.threads.messages.delete("msg_abc123")
    assert deleted

    for i in range(100):
        state_store.beta.threads.messages.put(
            Message(
                id=f"msg_{i}",
                content=[],
                created_at=0,
                file_ids=[],
                object="thread.message",
                role="user",
                status="completed",
                thread_id="thread_abc123",
            )
        )

    messages = state_store.beta.threads.messages.list(
        thread_id="thread_abc123",
        limit=100,
        order="asc",
        after="msg_19",
        before="msg_30",
    )

    assert len(messages) == 10
    assert messages[0].id == "msg_20"
    assert messages[-1].id == "msg_29"

    messages = state_store.beta.threads.messages.list(
        thread_id="thread_abc123",
        limit=100,
        order="desc",
        after="msg_30",
        before="msg_19",
    )

    assert len(messages) == 10
    assert messages[0].id == "msg_29"
    assert messages[-1].id == "msg_20"


def test_run_store(state_store: StateStore):
    obj = Run(
        id="run_abc123",
        assistant_id="asst_abc123",
        created_at=0,
        file_ids=[],
        instructions="",
        model="",
        object="thread.run",
        status="in_progress",
        thread_id="thread_abc123",
        tools=[],
    )

    state_store.beta.threads.runs.put(obj)
    runs = state_store.beta.threads.runs.list(thread_id="thread_abc123")
    assert len(runs) == 1
    runs = state_store.beta.threads.runs.list(thread_id="invalid_id")
    assert len(runs) == 0
    deleted = state_store.beta.threads.runs.delete("invalid_id")
    assert not deleted
    deleted = state_store.beta.threads.runs.delete("run_abc123")
    assert deleted

    for i in range(100):
        state_store.beta.threads.runs.put(
            Run(
                id=f"run_{i}",
                assistant_id="asst_abc123",
                created_at=0,
                file_ids=[],
                instructions="",
                model="",
                object="thread.run",
                status="in_progress",
                thread_id="thread_abc123",
                tools=[],
            )
        )

    runs = state_store.beta.threads.runs.list(
        thread_id="thread_abc123",
        limit=100,
        order="asc",
        after="run_19",
        before="run_30",
    )

    assert len(runs) == 10
    assert runs[0].id == "run_20"
    assert runs[-1].id == "run_29"

    runs = state_store.beta.threads.runs.list(
        thread_id="thread_abc123",
        limit=100,
        order="desc",
        after="run_30",
        before="run_19",
    )

    assert len(runs) == 10
    assert runs[0].id == "run_29"
    assert runs[-1].id == "run_20"
