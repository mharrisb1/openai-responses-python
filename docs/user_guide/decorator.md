# Decorator

The `mock` decorator is currently the only official way to use this library.

```python linenums="1"
@openai_responses.mock()
def test_my_code():
    pass
```

The decorator accepts two optional arguments (with more coming soon):

1. `base_url`: override the base URL which defaults to [https://api.openai.com](https://api.openai.com)
2. `state`: override the default empty state used for [stateful routes](routes.md#stateful)
