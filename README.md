# openai-responses

[![PyPI version](https://badge.fury.io/py/openai-responses.svg)](https://badge.fury.io/py/openai-responses)
[![PyPI - License](https://img.shields.io/pypi/l/openai-responses)](https://opensource.org/blog/license/mit)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/openai-responses.svg)](https://pypi.org/project/openai-responses/)
[![PyPI - Downloads](https://img.shields.io/pypi/dm/openai-responses)](https://pypi.org/project/openai-responses/)
[![Open Issues](https://img.shields.io/github/issues/mharrisb1/openai-responses-python)](https://github.com/mharrisb1/openai-responses-python/issues)
[![Stargazers](https://img.shields.io/github/stars/mharrisb1/openai-responses-python?style)](https://pypistats.org/packages/openai-responses)


Pytest plugin for automatically mocking OpenAI requests. Simply decorate any test function that contains code that calls an OpenAI endpoint (either using the SDK or HTTPX).

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

## Installation

Available on [PyPi](https://pypi.org/project/openai-responses/)

```bash
pip install openai-responses
```

## Usage

See the [documentation site](https://mharrisb1.github.io/openai-responses-python) for more info.

## License

See [LICENSE](https://github.com/mharrisb1/openai-responses-python/blob/main/LICENSE) for more info.

## Contributing

See [CONTRIBUTING.md](https://github.com/mharrisb1/openai-responses-python/blob/main/CONTRIBUTING.md) for more info.

## Changelog

See [CHANGELOG.md](https://github.com/mharrisb1/openai-responses-python/blob/main/CHANGELOG.md) for more info.
