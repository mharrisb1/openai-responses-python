# Run Steps

!!! note

    Only Assistants V2 is supported

!!! tip

    See [examples](https://github.com/mharrisb1/openai-responses-python/blob/main/examples/test_threads_api.py) for more

## Decorator Arguments

- `latency` - synthetic latency in seconds to introduce to the call(s). Defaults to `0.0`.
- `failures` - number of failures to simulate. Defaults to `0`.
- `state_store` - Optional [state store](../../user_guide/state.md) override for custom and shared states.
- `steps` - Optional steps list. This is needed since there is no create steps route. Defaults to `[]`.
- `validate_thread_exists` - Optional flag for asserting that thread exists. Defaults to `False`.
- `validate_run_exists` - Optional flag for asserting that run exists. Defaults to `False`.

## List run steps

!!! info

    Docs are incomplete but feature is supported

## Retrieve run step

!!! info

    Docs are incomplete but feature is supported
