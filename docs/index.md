# Introduction

🧪🤖 Pytest plugin for automatically mocking OpenAI requests. Powered by [RESPX](https://github.com/lundberg/respx).

## Why mock?

Mocking is a common practice in software testing. Instead of sending actual requests over the network, you can patch the requests to return predefined responses.

This has many benefits:

- 💰 **Cost**: Avoiding actual API calls ensures you're not paying for usage during testing
- ⚡️ **Speed**: No round-trip latencies since you completely avoid the network
- 🔒 **Security**: No physical requests to separate servers helps ensure no private information is leaked from your system
- 👩‍🔬 **Reproducibility**: Mocks give you control and predictability of responses allowing you to test more scenarios

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

Simply decorate any test function that makes a call to the OpenAI API (either using the [official Python SDK](https://github.com/openai/openai-python) or with [HTTPX](https://www.python-httpx.org/)).

See [examples](https://github.com/mharrisb1/openai-responses-python/tree/main/examples) for more.

```python
import openai
import openai_responses


@openai_responses.mock()
def test_create_assistant():
    client = openai.Client(api_key="sk-fake123")

    assistant = client.beta.assistants.create(
        instructions="You are a personal math tutor.",
        name="Math Tutor",
        tools=[{"type": "code_interpreter"}],
        model="gpt-4-turbo",
    )

    assert assistant.name == "Math Tutor"
```
