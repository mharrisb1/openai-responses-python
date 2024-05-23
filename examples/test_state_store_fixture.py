import pytest

import openai

import openai_responses
from openai_responses import OpenAIMock
from openai_responses.stores import StateStore


@pytest.fixture(scope="module")
def shared_state():
    return StateStore()


@openai_responses.mock()
def test_create_assistant(openai_mock: OpenAIMock, shared_state: StateStore):
    openai_mock.state = shared_state

    client = openai.Client(api_key="sk-fake123")
    client.beta.assistants.create(model="gpt-4o")


@openai_responses.mock()
def test_retrieve_assistant(openai_mock: OpenAIMock, shared_state: StateStore):
    openai_mock.state = shared_state

    client = openai.Client(api_key="sk-fake123")
    assistants = client.beta.assistants.list()
    assert len(assistants.data) == 1
