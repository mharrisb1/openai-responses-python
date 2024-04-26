from openai_responses.endpoints.assistants import AssistantsMock
from openai_responses.endpoints.chat import ChatMock, ChatCompletionMock
from openai_responses.endpoints.embeddings import EmbeddingsMock
from openai_responses.endpoints.files import FilesMock
from openai_responses.endpoints.threads import ThreadsMock
from openai_responses.endpoints.messages import MessagesMock
from openai_responses.endpoints.runs import RunsMock
from openai_responses.endpoints.run_steps import RunStepsMock

__all__ = [
    # main API
    "mock",
    # mockers
    "AssistantsMock",
    "ChatCompletionMock",
    "EmbeddingsMock",
    "FilesMock",
    "ThreadsMock",
    "MessagesMock",
    "RunsMock",
    "RunStepsMock",
]


class Api:
    def __init__(self) -> None:
        self.files = FilesMock()
        self.embeddings = EmbeddingsMock()
        self.chat = ChatMock()
        self.beta = Beta()


class Beta:
    def __init__(self) -> None:
        self.assistants = AssistantsMock()
        self.threads = ThreadsMock()


mock = Api()
