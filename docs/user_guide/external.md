# External APIs

Since this project is powered by [RESPX](https://lundberg.github.io/respx), all API calls to HTTPX or HTTP Core will be patched. If a route is not mocked, then this will result in an error.

For example, if you're calling to external APIs for [function calling](https://platform.openai.com/docs/assistants/tools/function-calling) and your testing these function calls with this project, then you will need to add a custom mock for that route.

A [respx.Router](https://lundberg.github.io/respx/api/#router) instance is exposed from the main `OpenAIMock` object. This allows you to use the interface provided by RESPX to define your own mock.

```python linenums="1"
openai_mock.router.post(url="https://api.myweatherapi.com").mock(
    Response(200, json={"value": "57"})
)
```

See full example [here](https://github.com/mharrisb1/openai-responses-python/blob/35-featapi-expose-router-as-prop/examples/test_router_usage.py) or view RESPX mocking docs [here](https://lundberg.github.io/respx/guide/#mocking-responses).

## Pass Through

If you want a call to not be mocked and actually be sent to an external service, then you can use RESPX's [pass through](https://lundberg.github.io/respx/guide/#pass-through) feature.

```python linenums="1"
openai_mock.router.post(url="https://api.myweatherapi.com").pass_through()
```
