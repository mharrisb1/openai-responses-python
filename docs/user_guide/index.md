# User Guide

## First steps

Before getting started, make sure that you've installed [pytest](https://pytest.org/en/7.0.x/contents.html). For async support, you can see more setup instructions [here](async.md).

## Overview

This library will automatically mock any call to the OpenAI API by just decorating the test function. The API call(s) can either come from the [official Python library](https://github.com/openai/openai-python), [HTTPX](https://www.python-httpx.org), or [HTTP Core](https://www.encode.io/httpcore). All documented examples will use the official Python library but can easily be ported.

Let's look at an example:

```python linenums="1" hl_lines="4 7 8 9 20 30"
import openai

import openai_responses
from openai_responses import OpenAIMock # (1)


@openai_responses.mock() # (2)
def test_create_chat_completion(openai_mock: OpenAIMock): # (3)
    openai_mock.chat.completions.create.response = { # (4)
        "choices": [
            {
                "index": 0,
                "finish_reason": "stop",
                "message": {"content": "Hello! How can I help?", "role": "assistant"},
            }
        ]
    }

    client = openai.Client(api_key="sk-fake123")
    completion = client.chat.completions.create( # (5)
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Hello!"},
        ],
    )

    assert len(completion.choices) == 1
    assert completion.choices[0].message.content == "Hello! How can I help?"
    assert openai_mock.chat.completions.create.calls.call_count == 1 # (6)
```

1. Optional import for type annotations
2. Decorate the test function
3. Request mock instance fixture from Pytest
4. Define the response
5. Make the API call as you normally would
6. Use the route call history for assertions

Now, walking through this example, let's focus on the highlighted lines.

- **Lines 4 and 8**: For type inference and autocompletion support in you editor or IDE, it's recommended to import the [mock class](mock.md) and annotate the fixture `openai_mock`.
- **Line 7**: The `mock()` [decorator](decorator.md) wraps a function and will patch any request called within that function.
- **Line 9**: You can define the response of the API call. There are many options for defining a response. See [Responses](responses.md) for more.
- **Line 20**: You can use the SDK or HTTP calls the way you normally would, including [async support](async.md).
- **Line 30**: You can access each route's [call history](mock.md#call-history) for additional assertions like ensuring a route was not called or was called only a certain number of times
