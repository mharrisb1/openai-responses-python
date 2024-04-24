# Runs

!!! note

    Only Assistants V2 is supported

!!! tip

    See [examples](https://github.com/mharrisb1/openai-responses-python/blob/main/examples/test_threads_api.py) for more

## Decorator Arguments

- `latency` - synthetic latency in seconds to introduce to the call(s). Defaults to `0.0`.
- `failures` - number of failures to simulate. Defaults to `0`.
- `state_store` - Optional [state store](../../user_guide/state.md) override for custom and shared states.
- `sequence` - Optional state sequences for create and/or retrieve. Will use sequence `n` for call `n - failure`. Defaults to `{}`
- `validate_thread_exists` - Optional flag for asserting that thread exists. Defaults to `False`.
- `validate_assistant_exists` - Optional flag for asserting that assistant exists. Defaults to `False`.

## Create run

!!! warning

    Messages created with `additional_messages` request params are currently ignored. Subscribe to [#10: fix: create run ignores `additional_messages`](https://github.com/mharrisb1/openai-responses-python/issues/10) to be notified when this is fixed

!!! info

    Docs are incomplete but feature is supported

## Create thread and run

!!! warning

    Not implemented. Subscribe to [#11: feat: support create thread and run route](https://github.com/mharrisb1/openai-responses-python/issues/11) to be notified when support is added.

## Retrieve run

!!! info

    Docs are incomplete but feature is supported

## Modify run

!!! info

    Docs are incomplete but feature is supported

## Submit tool outputs to run

!!! info

    Docs are incomplete but feature is supported

## Cancel run

!!! info

    Docs are incomplete but feature is supported
