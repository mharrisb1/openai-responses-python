# 🧪🤖 openai-responses

Pytest plugin for automatically mocking OpenAI requests. Powered by [RESPX](https://github.com/lundberg/respx).

[![sdk support](https://img.shields.io/badge/SDK_Support-v1.25+-white?logo=openai&logoColor=black&labelColor=white)](https://github.com/openai/openai-python)

## Supported Endpoints

- [Chat](https://platform.openai.com/docs/api-reference/chat)
- [Embeddings](https://platform.openai.com/docs/api-reference/embeddings)
- [Files](https://platform.openai.com/docs/api-reference/files)
- [Models](https://platform.openai.com/docs/api-reference/models)
- [Assistants](https://platform.openai.com/docs/api-reference/assistants)
- [Threads](https://platform.openai.com/docs/api-reference/threads)
- [Messages](https://platform.openai.com/docs/api-reference/messages)
- [Runs](https://platform.openai.com/docs/api-reference/runs)
- [Run Steps](https://platform.openai.com/docs/api-reference/run-steps)
- [Vector Stores](https://platform.openai.com/docs/api-reference/vector-stores)
- [Vector Store Files](https://platform.openai.com/docs/api-reference/vector-stores-files)
- [Vector Store File Batches](https://platform.openai.com/docs/api-reference/vector-stores-file-batches)

View full support coverage [here](https://mharrisb1.github.io/openai-responses-python/coverage).

> [!NOTE]
> ✨ Support for creating [streaming responses](https://mharrisb1.github.io/openai-responses-python/user_guide/streaming/) added in v0.4

## Usage

Just decorate any test function that makes a call to the OpenAI API (either using [openai-python](https://github.com/openai/openai-python) or with [HTTPX](https://www.python-httpx.org/)).

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

See [examples](https://github.com/mharrisb1/openai-responses-python/tree/main/examples) or [docs](https://mharrisb1.github.io/openai-responses-python) for more.

## Installation

[![PyPI version](https://badge.fury.io/py/openai-responses.svg)](https://badge.fury.io/py/openai-responses)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/openai-responses.svg)](https://pypi.org/project/openai-responses/)
[![PyPI - Downloads](https://img.shields.io/pypi/dm/openai-responses)](https://pypi.org/project/openai-responses/)

Available on [PyPI](https://pypi.org/project/openai-responses/)

```bash
pip install openai-responses
```

## Documentation

[![Docs](https://github.com/mharrisb1/openai-responses-python/actions/workflows/docs.yml/badge.svg)](https://mharrisb1.github.io/openai-responses-python)

See the [documentation site](https://mharrisb1.github.io/openai-responses-python) for more info.

## License

[![PyPI - License](https://img.shields.io/pypi/l/openai-responses)](https://opensource.org/blog/license/mit)

See [LICENSE](https://github.com/mharrisb1/openai-responses-python/blob/main/LICENSE) for more info.

## Contributing

[![Open Issues](https://img.shields.io/github/issues/mharrisb1/openai-responses-python)](https://github.com/mharrisb1/openai-responses-python/issues)
[![Stargazers](https://img.shields.io/github/stars/mharrisb1/openai-responses-python?style)](https://pypistats.org/packages/openai-responses)

See [CONTRIBUTING.md](https://github.com/mharrisb1/openai-responses-python/blob/main/CONTRIBUTING.md) for info on PRs, issues, and feature requests.

## Changelog

See [CHANGELOG.md](https://github.com/mharrisb1/openai-responses-python/blob/main/CHANGELOG.md) for summarized notes on changes or view [releases](https://github.com/mharrisb1/openai-responses-python/releases) for more details information on changes.
