# 🧪🤖 openai-responses

Pytest plugin for automatically mocking OpenAI requests. Powered by [RESPX](https://github.com/lundberg/respx).

[![sdk support](https://img.shields.io/badge/SDK_Support-v1.66+-white?logo=openai&logoColor=black&labelColor=white)](https://github.com/openai/openai-python)

> [!NOTE]
> This project is in maintenance mode unless I see an appetite for more community contributions. I built this because we at [Definite](https://definite.app) needed a way to easily and quickly test the integration between [openai-python](https://github.com/openai/openai-python) and our codebase but we have [moved on to other frameworks/SDKs](https://pydantic.dev/articles/building-data-team-with-pydanticai). With that, my need and desire to work on this library has dropped significantly.
> 
> I will be encouraging community contributions to fill in the gap for some of the new features released since the last major update to this library such as [evals](https://platform.openai.com/docs/api-reference/evals), [graders](https://platform.openai.com/docs/api-reference/graders), [containers](https://platform.openai.com/docs/api-reference/containers), and all of the new [administration](https://platform.openai.com/docs/api-reference/administration) endpoints.
>
> Absent community contributions, if the work required just for maintenance mode becomes too much (>2 hours a month) then this project will be fully deprecated and archived.

## Supported Endpoints

- [Chat](https://github.com/mharrisb1/openai-responses-python/blob/main/examples/test_chat_completion.py)
- [Embeddings](https://github.com/mharrisb1/openai-responses-python/blob/main/examples/test_embeddings.py)
- [Files](https://github.com/mharrisb1/openai-responses-python/blob/main/examples/test_files.py)
- [Models](https://github.com/mharrisb1/openai-responses-python/blob/main/examples/test_models.py)
- [Moderations](https://github.com/mharrisb1/openai-responses-python/blob/main/examples/test_moderations.py)
- [Assistants](https://github.com/mharrisb1/openai-responses-python/blob/main/examples/test_assistants.py)
- [Threads](https://github.com/mharrisb1/openai-responses-python/blob/main/examples/test_threads.py)
- [Messages](https://github.com/mharrisb1/openai-responses-python/blob/main/examples/test_messages.py)
- [Runs](https://github.com/mharrisb1/openai-responses-python/blob/main/examples/test_runs.py)
- [Run Steps](https://github.com/mharrisb1/openai-responses-python/blob/main/examples/test_run_steps.py)
- [Vector Stores](https://github.com/mharrisb1/openai-responses-python/blob/main/examples/test_vector_stores.py)
- [Vector Store Files](https://github.com/mharrisb1/openai-responses-python/blob/main/examples/test_vector_store_files.py)
- [Vector Store File Batches](https://github.com/mharrisb1/openai-responses-python/blob/main/examples/test_vector_store_file_batches.py)

View full support coverage [here](https://mharrisb1.github.io/openai-responses-python/coverage).

> [!TIP]
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
