# Overview

The main interface for this library is the `OpenAIMock` class. This class contains:

- all of the supported [routes](#routes)
- a [state store](state.md) for [stateful routes](#stateful-routes)
- a [RESPX Router](https://lundberg.github.io/respx/api/#router) instance that patches the requests

The class constructor allows you to set a custom base URL and/or a custom initial state.

## Modalities

There are serveral ways to use the `OpenAIMock` class.

### Decorator

The main way is to decorate the test function with `openai_responses.mock()` which wraps the function and provides an instance of the class as a test fixture.

```python linenums="1"
import openai_responses

@openai_responses.mock()
def my_test_function(openai_mock):
  ...
```

### Context manager

For certain scenarios where using the decorator + Pytest fixture is not an option, you can optionally construct the instance and use the router as a context manager.

```python linenums="1"
from openai_responses import OpenAIMock

def test_create_chat_completion():
    openai_mock = OpenAIMock()
    with openai_mock.router:
      ...
```

### Transport

HTTPX clients accept a transport object. These objects are used to actually send the requests. Many people prefer to use transports and their codebase is already setup to make use of swapping different transports out for different environments.

You can create [mock transport](https://www.python-httpx.org/advanced/transports/#mock-transports) with the router object.

```python linenums="1"
import openai
from openai import DefaultHttpxClient

from openai_responses import OpenAIMock
from openai_responses.ext.httpx import MockTransport

def test_create_chat_completion():
    openai_mock = OpenAIMock()
    client = openai.Client(
        api_key="sk-fake123",
        http_client=DefaultHttpxClient(
            transport=MockTransport(openai_mock.router.handler)
        ),
    )
```

## Routes

Routes are accessed following the same interface as the official Python library. For example, if you accessed the `chat.completions.create` route like this in the Python library:

```python linenums="1"
client.chat.completions.create(...)
```

The mock route can be accessed like this:

```python linenums="1"
openai_mock.chat.completions.create
```

Each route class contains:

- a [RESPX Route](https://lundberg.github.io/respx/api/#route_1) instance
- a [Response](responses.md) object

Stateful routes also contain an instance of a [`StateStore`](state.md) for managing resources.

### Stateful routes

While routes like `chat.completions.create` are stateless, routes like those in the new Assistants API are stateful and manage resource objects for you behind the scenes.

For stateless routes, a [state store](state.md) is used to manage resources. Since many of the stateful routes are simple CRUD operations, you do not need to manually set the response.

### Setting the response

You can set the value of the response for all routes by using the setter for the `response` property.

```python linenums="1"
openai_mock.chat.completions.create.response = {
    "choices": [
        {
            "index": 0,
            "finish_reason": "stop",
            "message": {"content": "Hello! How can I help?", "role": "assistant"},
        }
    ]
}
```

The response can be set to either a partial of the OpenAI object, a full OpenAI object, an HTTPX Response, or a function that returns an HTTPX response. See more in [Responses](responses.md).

### Call history

The route instances keep track of the calls to that route. That information is available to you so you can do things like assert a route was only called once, or that a route was not called at all.

```python linenums="1"
assert openai_mock.chat.completions.create.route.call_count == 1
```
