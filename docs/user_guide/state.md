# State

If you want to establish state prior to a test run you can pass a state store instance into the decorator.

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
