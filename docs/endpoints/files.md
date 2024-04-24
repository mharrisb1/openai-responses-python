# Files

!!! warning

    There is currently no support for retrieving file content. Subscribe to [#4: feat: add support for retrieving file content](https://github.com/mharrisb1/openai-responses-python/issues/4) to be updated when this is available.

!!! tip

    See [examples](https://github.com/mharrisb1/openai-responses-python/blob/main/examples/test_files_api.py) for more

## Decorator Arguments

- `latency` - synthetic latency in seconds to introduce to the call(s). Defaults to `0.0`.
- `failures` - number of failures to simulate. Defaults to `0`.
- `state_store` - Optional [state store](../user_guide/state.md) override for custom and shared states.

## Upload file

=== "Sync"

    ```python linenums="1"
    from openai import OpenAI

    import openai_responses


    @openai_responses.mock.files()
    def test_upload_file():
        client = OpenAI(api_key="fakeKey")
        file = client.files.create(
            file=open("examples/example.json", "rb"),
            purpose="assistants",
        )
        assert file.filename == "example.json"
        assert file.purpose == "assistants"
    ```

=== "Async"

    ```python linenums="1"
    import pytest

    from openai import AsyncOpenAI

    import openai_responses


    @pytest.mark.asyncio
    @openai_responses.mock.files()
    async def test_upload_file():
        client = AsyncOpenAI(api_key="fakeKey")
        file = await client.files.create(
            file=open("examples/example.json", "rb"),
            purpose="assistants",
        )
        assert file.filename == "example.json"
        assert file.purpose == "assistants"
    ```

=== "With Mocker Class"

    ```python linenums="1" hl_lines="4 8 16"
    from openai import OpenAI

    import openai_responses
    from openai_responses import FilesMock # (1)


    @openai_responses.mock.files()
    def test_upload_file(files_mock: FilesMock):
        client = OpenAI(api_key="fakeKey")
        file = client.files.create(
            file=open("examples/example.json", "rb"),
            purpose="assistants",
        )
        assert file.filename == "example.json"
        assert file.purpose == "assistants"
        assert files_mock.create.route.calls.call_count == 1
    ```

    1.  See [mockers guide](../user_guide/mockers.md) for more

## List files

=== "Sync"

    ```python linenums="1"
    from openai import OpenAI

    import openai_responses


    @openai_responses.mock.files()
    def test_list_uploaded_files():
        client = OpenAI(api_key="fakeKey")

        files = client.files.list()
        assert len(files.data) == 0

        client.files.create(file=open("file_1.json", "rb"))
        client.files.create(file=open("file_2.json", "rb"))

        files = client.files.list()
        assert len(files.data) == 2
    ```

=== "Async"

    ```python linenums="1"
    import pytest

    from openai import AsyncOpenAI

    import openai_responses


    @pytest.mark.asyncio
    @openai_responses.mock.files()
    async def test_list_uploaded_files():
        client = AsyncOpenAI(api_key="fakeKey")

        files = await client.files.list()
        assert len(files.data) == 0

        await client.files.create(file=open("file_1.json", "rb"))
        await client.files.create(file=open("file_2.json", "rb"))

        files = await client.files.list()
        assert len(files.data) == 2
    ```

=== "With Mocker Class"

    ```python linenums="1" hl_lines="6 11 23 24"
    import pytest

    from openai import AsyncOpenAI

    import openai_responses
    from openai_responses import FilesMock # (1)


    @pytest.mark.asyncio
    @openai_responses.mock.files()
    async def test_list_uploaded_files(files_mock: FilesMock):
        client = AsyncOpenAI(api_key="fakeKey")

        files = await client.files.list()
        assert len(files.data) == 0

        await client.files.create(file=open("file_1.json", "rb"))
        await client.files.create(file=open("file_2.json", "rb"))

        files = await client.files.list()
        assert len(files.data) == 2

        assert files_mock.create.route.calls.call_count == 2
        assert files_mock.list.route.calls.call_count == 2
    ```

    1.  See [mockers guide](../user_guide/mockers.md) for more

## Retrieve file

=== "Sync"

    ```python linenums="1"
    from openai import OpenAI

    import openai_responses


    @openai_responses.mock.files()
    def test_retrieve_file():
        client = OpenAI(api_key="fakeKey")

        file = client.files.create(file=open("my_file.json", "rb"))

        found = client.files.retrieve(file.id)

        assert found
        assert found.id == file.id
    ```

=== "Async"

    ```python linenums="1"
    import pytest

    from openai import AsyncOpenAI

    import openai_responses


    @pytest.mark.asyncio
    @openai_responses.mock.files()
    async def test_retrieve_file():
        client = AsyncOpenAI(api_key="fakeKey")

        file = await client.files.create(file=open("my_file.json", "rb"))

        found = await client.files.retrieve(file.id)

        assert found
        assert found.id == file.id
    ```

=== "With Mocker Class"

    ```python linenums="1" hl_lines="4 8 18 19"
    from openai import OpenAI

    import openai_responses
    from openai_responses import FilesMock # (1)


    @openai_responses.mock.files()
    def test_retrieve_file(files_mock: FilesMock):
        client = OpenAI(api_key="fakeKey")

        file = client.files.create(file=open("my_file.json", "rb"))

        found = client.files.retrieve(file.id)

        assert found
        assert found.id == file.id

        assert files_mock.create.route.calls.call_count == 1
        assert files_mock.retrieve.route.calls.call_count == 1
    ```

    1.  See [mockers guide](../user_guide/mockers.md) for more

## Delete file

=== "Sync"

    ```python linenums="1"
    from openai import OpenAI

    import openai_responses


    @openai_responses.mock.files()
    def test_delete_file():
        client = OpenAI(api_key="fakeKey")

        file = client.files.create(file=open("my_file.json", "rb"))

        deleted = client.files.delete(file.id)

        assert deleted.deleted
    ```

=== "Async"

    ```python linenums="1"
    import pytest

    from openai import AsyncOpenAI

    import openai_responses


    @pytest.mark.asyncio
    @openai_responses.mock.files()
    def test_delete_file():
        client = AsyncOpenAI(api_key="fakeKey")

        file = await client.files.create(file=open("my_file.json", "rb"))

        deleted = await client.files.delete(file.id)

        assert deleted.deleted
    ```

=== "With Mocker Class"

    ```python linenums="1" hl_lines="4 8 17 18"
    from openai import OpenAI

    import openai_responses
    from openai_responses import FilesMock # (1)


    @openai_responses.mock.files()
    def test_delete_file(files_mock: FilesMock):
        client = OpenAI(api_key="fakeKey")

        file = client.files.create(file=open("my_file.json", "rb"))

        deleted = client.files.delete(file.id)

        assert deleted.deleted

        assert files_mock.create.route.calls.call_count = 1
        assert files_mock.delete.route.calls.call_count = 1
    ```

    1.  See [mockers guide](../user_guide/mockers.md) for more
