import pytest
from openai import OpenAI, AsyncOpenAI
from openai import NotFoundError

import openai_responses
from openai_responses import FilesMock


@openai_responses.mock.files()
def test_upload_file():
    client = OpenAI(api_key="fakeKey")
    file = client.files.create(
        file=open("examples/example.json", "rb"),
        purpose="assistants",
    )
    assert file.filename == "example.json"
    assert file.purpose == "assistants"


@pytest.mark.asyncio
@openai_responses.mock.files()
async def test_async_upload_file():
    client = AsyncOpenAI(api_key="fakeKey")
    file = await client.files.create(
        file=open("examples/example.json", "rb"),
        purpose="assistants",
    )
    assert file.filename == "example.json"
    assert file.purpose == "assistants"


@openai_responses.mock.files(failures=2)
def test_upload_files_with_retries(files_mock: FilesMock):
    client = OpenAI(api_key="fakeKey", max_retries=2, timeout=0)
    file = client.files.create(
        file=open("examples/example.json", "rb"),
        purpose="assistants",
    )
    assert file.filename == "example.json"
    assert file.purpose == "assistants"
    assert files_mock.create.route.calls.call_count == 3


@openai_responses.mock.files()
def test_list_uploaded_files():
    client = OpenAI(api_key="fakeKey")

    files = client.files.list()
    assert len(files.data) == 0

    client.files.create(
        file=open("examples/example.json", "rb"),
        purpose="assistants",
    )
    client.files.create(
        file=open("examples/example.json", "rb"),
        purpose="assistants",
    )

    files = client.files.list()
    assert len(files.data) == 2

    files = client.files.list(purpose="fine-tune")
    assert len(files.data) == 0


@openai_responses.mock.files()
def test_retrieve_file():
    client = OpenAI(api_key="fakeKey")

    with pytest.raises(NotFoundError):
        client.files.retrieve("invalid-id")

    file = client.files.create(
        file=open("examples/example.json", "rb"),
        purpose="assistants",
    )

    found = client.files.retrieve(file.id)

    assert found.id == file.id


@openai_responses.mock.files()
def test_delete_file():
    client = OpenAI(api_key="fakeKey")

    assert not client.files.delete("invalid").deleted

    file = client.files.create(
        file=open("examples/example.json", "rb"),
        purpose="assistants",
    )

    assert client.files.delete(file.id).deleted
