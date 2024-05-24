import openai

import openai_responses
from openai_responses import OpenAIMock


@openai_responses.mock()
def test_list_models(openai_mock: OpenAIMock):
    client = openai.Client(api_key="sk-fake123")
    models = client.models.list()

    assert len(models.data) > 0
    assert openai_mock.models.list.route.call_count == 1


@openai_responses.mock()
def test_retrieve_model(openai_mock: OpenAIMock):
    client = openai.Client(api_key="sk-fake123")
    model = client.models.retrieve("gpt-3.5-turbo-instruct")

    assert model
    assert openai_mock.models.retrieve.route.call_count == 1
