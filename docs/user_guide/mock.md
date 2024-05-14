# Mock Class

!!! tip

    The mock class is not intended to be initialized manually by the user. An instance is provided to the test function by Pytest.

The main mock object is the `OpenAIMock` class. This class contains all of the supported routes as well as a private state store for [stateful routes](routes.md#stateful).

The class is initialized on a per-test basis and is accessible as a fixture in Pytest function.

## Routes

The routes try to match the client routes from the official Python library client to make it easy and natural to navigate. So if the create chat completion route in the client is `client.chat.completions.create` then mock route is accessible as `openai_mock.chat.completions.create`. See [routes](routes.md) for more information.

### Call History

Each route has two main properties:

1. `calls` which allows access to call history
2. `response` which allows the user to [define the response](responses.md)

The call history is provided by RESPX and you can see the full documentation [here](https://lundberg.github.io/respx/guide/#call-history).
