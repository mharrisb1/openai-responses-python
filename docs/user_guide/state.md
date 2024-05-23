# State

State is managed for stateful routes by utilizing the `StateStore` object.

This object has simple `get`, `list`, `put`, `delete` operations for different resource types.

!!! warning

    Initially this object was only used internally but is now public. Overtime the API may change as it matures.

To access the state store for an instance of an `OpenAIMock` object you can use the `state` property.

```python linenums="1"
openai_mock.state
```

The interface tries to adhere to the same design as the mock class by following closely to that of the official Python library client.

For example, if you access message routes in the client like this:

```python linenums="1"
client.beta.threads.messages
```

Then accessing the operations for the state store will looke like this:

```python linenums="1"
openai_mock.state.beta.threads.messages
```

## Custom states

By default, the `OpenAIMock` object is constructed with an empty state store. If you'd like to provide a custom initial state you can provide one.

```python linenums="1"
from openai.type.beta import Assistant

import openai_responses
from openai_responses import OpenAIMock
from openai_responses.store import StateStore

my_custom_state = StateStore()
my_custom_state.beta.assistants.put(Assistant(...))

@openai_responses.mock(state=my_custom_state)
def my_test_function(openai_mock: OpenAIMock):
    ...
```

Alternatively, you can use a Pytest fixture to pass around the custom state.

```python linenums="1"
import pytest

import openai

import openai_responses
from openai_responses import OpenAIMock
from openai_responses.stores import StateStore


@pytest.fixture(scope="module")
def shared_state():
    return StateStore()


@openai_responses.mock()
def test_create_assistant(openai_mock: OpenAIMock, shared_state: StateStore):
    openai_mock.state = shared_state
    ...

@openai_responses.mock()
def test_retrieve_assistant(openai_mock: OpenAIMock, shared_state: StateStore):
    openai_mock.state = shared_state
    ...
```
