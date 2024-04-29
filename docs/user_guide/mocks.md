# Mocks

Each mock decorator also has an accompanying mocker class. These classes are provided as pytest fixtures and are always available. To access them from your test function, just include the mocker class name as snake case (e.g. access `FilesMock` mocker with `files_mock`).

**Mockers**

- `ChatCompletionMock`
- `EmbeddingsMock`
- `FilesMock`
- `AssistantsMock`
- `ThreadsMock`
- `MessagesMock`
- `RunsMock`
- `RunStepsMock`

### Example Access

```python linenums="1" hl_lines="8 19"
from openai import OpenAI

import openai_responses
from openai_responses import FilesMock


@openai_responses.mock.files(failures=2)
def test_upload_files_with_retries(files_mock: FilesMock): # (1)
    client = OpenAI(api_key="fakeKey", max_retries=2, timeout=0)

    file = client.files.create(
        file=open("examples/example.json", "rb"),
        purpose="assistants",
    )

    assert file.filename == "example.json"
    assert file.purpose == "assistants"

    assert files_mock.create.route.calls.call_count == 3 # (2)
```

1. Pass in mocker class name (snake case) with optional type annotation for code completion
2. Access attributes of the mocker class
