from typing import Optional

from openai_responses._utils.faker import faker


def assert_is_functional_id(
    id: Optional[str],
    expected_prefix: str,
    sep: str = "_",
) -> None:
    assert id is not None
    prefix, suffix = id.split(sep)
    assert prefix == expected_prefix
    assert len(suffix) == 24


def test_fake_chat_completion_id():
    chat_completion_id = faker.chat.completion.id()
    assert_is_functional_id(chat_completion_id, "chatcmpl")


def test_fake_file_id():
    file_id = faker.file.id()
    assert_is_functional_id(file_id, "file", "-")


def test_fake_assistant_id():
    assistant_id = faker.beta.assistant.id()
    assert_is_functional_id(assistant_id, "asst")


def test_fake_thread_id():
    thread_id = faker.beta.thread.id()
    assert_is_functional_id(thread_id, "thread")


def test_fake_message_id():
    message_id = faker.beta.thread.message.id()
    assert_is_functional_id(message_id, "msg")


def test_fake_run_id():
    run_id = faker.beta.thread.run.id()
    assert_is_functional_id(run_id, "run")


def test_fake_run_step_id():
    run_step_id = faker.beta.thread.run.step.id()
    assert_is_functional_id(run_step_id, "step")


def test_fake_run_step_step_details_tool_call_id():
    tool_call_id = faker.beta.thread.run.step.step_details.tool_call.id()
    assert_is_functional_id(tool_call_id, "call")


def test_fake_vector_store_id():
    vector_store_id = faker.beta.vector_store.id()
    assert_is_functional_id(vector_store_id, "vs")


def test_fake_vector_store_file_batch_id():
    vector_store_file_batch_id = faker.beta.vector_store.file_batch.id()
    assert_is_functional_id(vector_store_file_batch_id, "vsfb")
