import pytest

from openai_responses import (
    AssistantsMock,
    ChatCompletionMock,
    EmbeddingsMock,
    FilesMock,
    ThreadsMock,
    MessagesMock,
    RunsMock,
    RunStepsMock,
)


def pytest_configure(config: pytest.Config):
    config.addinivalue_line(
        "markers",
        "assistants_mock: OpenAI assistants API mocker",
    )

    config.addinivalue_line(
        "markers",
        "chat_completion_mock: OpenAI chat completion API mocker",
    )

    config.addinivalue_line(
        "markers",
        "embeddings_mock: OpenAI embeddings API mocker",
    )

    config.addinivalue_line(
        "markers",
        "files_mock: OpenAI files API mocker",
    )

    config.addinivalue_line(
        "markers",
        "threads_mock: OpenAI threads API mocker",
    )

    config.addinivalue_line(
        "markers",
        "messages_mock: OpenAI messages API mocker",
    )

    config.addinivalue_line(
        "markers",
        "runs_mock: OpenAI runs API mocker",
    )

    config.addinivalue_line(
        "markers",
        "run_steps_mock: OpenAI runs steps API mocker",
    )


@pytest.fixture()
def assistants_mock() -> AssistantsMock:
    return AssistantsMock()


@pytest.fixture()
def chat_completion_mock() -> ChatCompletionMock:
    return ChatCompletionMock()


@pytest.fixture()
def embeddings_mock() -> EmbeddingsMock:
    return EmbeddingsMock()


@pytest.fixture()
def files_mock() -> FilesMock:
    return FilesMock()


@pytest.fixture()
def threads_mock() -> ThreadsMock:
    return ThreadsMock()


@pytest.fixture()
def messages_mock() -> MessagesMock:
    return MessagesMock()


@pytest.fixture()
def runs_mock() -> RunsMock:
    return RunsMock()


@pytest.fixture()
def run_steps_mock() -> RunStepsMock:
    return RunStepsMock()
