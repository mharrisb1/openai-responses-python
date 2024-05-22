# Introduction

🧪🤖 Pytest plugin for automatically mocking OpenAI requests. Powered by [RESPX](https://github.com/lundberg/respx).

## Why mock?

Mocking is a common practice in software testing. Instead of sending requests over the network, you can patch the requests to return predefined responses.

This has many benefits:

- 🤑 **Cost**: Don't pay for actual API usage
- 🏎️ **Speed**: Completely avoid the network
- 🔒 **Security**: Nothing actually leaves the machine
- 🎮 **Control**: 100% certainty on what will be received

## Installation

Available on [PyPi](https://pypi.org/project/openai-responses/)

=== "pip"

    ```shell
    pip install openai-responses
    ```

=== "poetry"

    ```shell
    poetry add --group dev openai-responses
    ```

## First steps

Before getting started, make sure that you've installed [pytest](https://pytest.org/en/7.0.x/contents.html). For async support, you can see more setup instructions [here](user_guide/async.md).

## Quickstart

Simply decorate any test function that makes a call to the OpenAI API.

See [examples](https://github.com/mharrisb1/openai-responses-python/tree/main/examples) for more.

!!! tip

     The API call(s) can either come from the [official Python library](https://github.com/openai/openai-python), [HTTPX](https://www.python-httpx.org), or [HTTP Core](https://www.encode.io/httpcore). All documented examples will use the official Python library.

```python linenums="1" hl_lines="7 8 9 20 30"
import openai

import openai_responses
from openai_responses import OpenAIMock


@openai_responses.mock() # (1)
def test_create_chat_completion(openai_mock: OpenAIMock): # (2)
    openai_mock.chat.completions.create.response = { # (3)
        "choices": [
            {
                "index": 0,
                "finish_reason": "stop",
                "message": {"content": "Hello! How can I help?", "role": "assistant"},
            }
        ]
    }

    client = openai.Client(api_key="sk-fake123")
    completion = client.chat.completions.create( # (4)
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Hello!"},
        ],
    )

    assert len(completion.choices) == 1
    assert completion.choices[0].message.content == "Hello! How can I help?"
    assert openai_mock.chat.completions.create.route.call_count == 1 # (5)
```

1. [Decorate](user_guide/overview.md#modalities) the test function
2. Use the test fixture
3. Define the [response](user_guide/responses.md)
4. Call the API the way you normally would (including [async support](user_guide/async.md))
5. Optionally use the [call history](user_guide/overview.md#call-history) to add additional assertions
