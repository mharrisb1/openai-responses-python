import openai

import openai_responses
from openai_responses import OpenAIMock


@openai_responses.mock()
def test_create_file(openai_mock: OpenAIMock):
    client = openai.Client(api_key="sk-fake123")

    file = client.files.create(
        file=open("examples/example.json", "rb"),
        purpose="fine-tune",
    )

    assert file.filename == "example.json"
    assert openai_mock.files.create.route.call_count == 1


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
    assert openai_mock.files.create.route.call_count == 10
    assert openai_mock.files.list.route.call_count == 1


@openai_responses.mock()
def test_retrieve_file(openai_mock: OpenAIMock):
    client = openai.Client(api_key="sk-fake123")

    file = client.files.create(
        file=open("examples/example.json", "rb"),
        purpose="fine-tune",
    )

    found = client.files.retrieve(file.id)

    assert found.id == file.id
    assert file.filename == "example.json"
    assert found.filename == file.filename
    assert openai_mock.files.create.route.call_count == 1
    assert openai_mock.files.retrieve.route.call_count == 1


@openai_responses.mock()
def test_delete_file(openai_mock: OpenAIMock):
    client = openai.Client(api_key="sk-fake123")

    file = client.files.create(
        file=open("examples/example.json", "rb"),
        purpose="fine-tune",
    )

    assert client.files.delete(file.id).deleted
    assert openai_mock.files.create.route.call_count == 1
    assert openai_mock.files.delete.route.call_count == 1
