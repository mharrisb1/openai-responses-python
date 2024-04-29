# State

State is managed in a custom state store. For stateful [mocks](mocks.md) you can define a custom state prior to a test run or allow a fresh empty state to be created. Additionally, you can share state between [chained mocks](chaining.md).

!!! note

    State store is still a work in progress and the API may change at any time. For instance, sharing state between chained mocks should happen automatically. Subscribe to [#28: feat: automatically share state between chained mocks](https://github.com/mharrisb1/openai-responses-python/issues/28) to be notified of when that is added.

## Defining custom state

If you want to establish state prior to a test run you can pass a state store instance as an argument in the decorator. Every stateful mock can accept a custom state store instance.

```python linenums="1"
from openai import OpenAI
from openai.types.beta.assistant import Assistant

import openai_responses
from openai_responses.state import StateStore

custom_state_store = StateStore()

asst = Assistant(id="asst_abc123"...)  # create assistant
custom_state_store.beta.assistants.put(asst)  # put assistant in state store


@openai_responses.mock.assistants(state_store=custom_state_store):
def test_retrieve_assistant():
    client = OpenAI(api_key="fakeKey")
    found = client.beta.assistants.retrieve("asst_abc123")
```

## Sharing state

If you're using more than one decorator and you want those mocks to be able to access a common state, you can do so like the example below.

```python linenums="1"
from openai import OpenAI

import openai_responses
from openai_responses.state import StateStore

shared_state = StateStore()

@openai_responses.mock.beta.assistants(state_store=shared_state)
@openai_responses.mock.beta.threads(state_store=shared_state)
@openai_responses.mock.beta.threads.runs(state_store=shared_state)
def test_create_thread_run():
    ...
```

!!! tip

    For assistants mocks, make sure to flip on the validate exists flags so the mock will ensure that the resource actually exists in the state store.
