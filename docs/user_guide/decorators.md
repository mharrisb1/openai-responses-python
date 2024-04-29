# Decorators

Each mock decorator will have the following options:

- `latency` - synthetic latency in seconds to introduce to the call(s). Defaults to `0.0`.
- `failures` - number of failures to simulate. Defaults to `0`.

All stateful mocks will have these additional arguments:

- `state_store` - Optional [state store](state.md) override for custom and shared states.

Some decorators will have additional arguments which are listed on the respective [endpoints](../endpoints/index.md) page.

All decorator arguments are optional but if you want to mock a response from a model you'll need to provide. This library does not automatically generate responses from LLMs.

Arguments have all been well-defined so autocompletion and type hints are available.
