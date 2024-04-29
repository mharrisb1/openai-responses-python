# Introduction

Pytest plugin for automatically mocking OpenAI requests.

## Why mock?

Mocking is a common practice in software testing. Instead of sending _actual_ requests over the wire, you can mock the behavior of API and avoid that external call entirely.

This has many benefits:

- 🔒 **Security**: No physical requests to separate servers helps ensure no private information is leaked from your system
- 💰 **Cost**: Calling an API often incurs a cost. If you've set up a robust testing infrastructure then you'd be calling APIs on every PR check, deployment smoke test, local unit test, etc. Simulating the call avoids the actual cost of calling the API
- 👩‍🔬**Reproducibility**: Mocks give you control and predictability of responses allowing you to test more scenarios
- ⚡️**Speed**: Calling an API also often incurs some latency cost. Sending data over the network from machine to machine is one of the most expensive actions a machine can take. Add on top of that fact the latency _within_ the system that is serving the API and one of your test cases can easily take 5+ seconds. Multiply that by every test run and you'll quickly find yourself waiting longer and longer for deployments to succeed.

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

## Quickstart

Simply decorate any test function that makes a call to the OpenAI API (either using the [official library](https://github.com/openai/openai-python) or with [HTTPX](https://www.python-httpx.org/)).

```python
import openai_responses
from openai import OpenAI


@openai_responses.mock.chat.completions(
    choices=[
        {"message": {"content": "Hello, how can I help?"}},
        {"message": {"content": "Hi! I'm here to help!"}},
        {"message": {"content": "How can I help?"}},
    ],
)
def test_create_completion_with_multiple_choices():
    client = OpenAI(api_key="fakeKey")
    completion = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Hello!"},
        ],
        n=3,
    )
    assert len(completion.choices) == 3
```
