import openai

import openai_responses
from openai_responses import OpenAIMock


@openai_responses.mock()
def test_create_file(openai_mock: OpenAIMock):
    client = openai.Client(api_key="sk-fake123")

    file_obj = client.files.create(
        file=open("examples/example.json", "rb"),
        purpose="fine-tune",
    )

    assert file_obj.filename == "example.json"
    assert openai_mock.files.create.calls.call_count == 1


@openai_responses.mock()
def test_list_files(openai_mock: OpenAIMock):
    client = openai.Client(api_key="sk-fake123")

    for _ in range(10):
        client.files.create(
            file=open("examples/example.json", "rb"),
            purpose="fine-tune",
        )

    files = client.files.list()

    assert len(files.data) == 10
    assert openai_mock.files.create.calls.call_count == 10
    assert openai_mock.files.list.calls.call_count == 1
