# Changelog

See [releases](https://github.com/mharrisb1/openai-responses-python/releases) for more.

## 0.4.0

> [!IMPORTANT]
> Breaking change

> [!NOTE]
> ✨ Streaming support is here

Tons of changes:

- New `EventStream` and `AsyncEventStream` objects to create mock event streams
- `OpenAIMock` class now exposes state store through `state` property
- Updated and more organized API
- New examples:
  - Create run with streaming
  - Create run with streaming (async)
  - Exporting router as transport to use as `http_client` in OpenAI client constructor
- Plus some small bug fixes and QoL enhancements

## 0.3.4

Overriding base URL was not working properly for Azure endpoints. Thanks @mapohjola for pointing this out. This moves the version prefix (i.e. `/v1`) from the OpenAI routes to the default base URL. Also added an example using Azure endpoints.

Closed:

- [#9: feat: base url override](https://github.com/mharrisb1/openai-responses-python/issues/9)

## 0.3.3

Fixes incorrect partial type definition for run step tool calls.

## 0.3.2

Adds `router` property on `OpenAIMock` class to expose instance of [respx.MockRouter](https://github.com/lundberg/respx/blob/366dd0bea824464e6ec9242a88f9b390a9dd74cb/respx/router.py#L323) to easily allow user to add additional routes to mock like non-OpenAI API calls, or enable a call to a route to pass through to the external service.

Usage example can be found [here](https://github.com/mharrisb1/openai-responses-python/blob/main/examples/test_router_usage.py).

Closed:

- [#36: feat(api): expose RESPX router as property](https://github.com/mharrisb1/openai-responses-python/issues/36)

## 0.3.1

Fixes:

- [#31: feat: add support for null args on create_and_run](https://github.com/mharrisb1/openai-responses-python/issues/31)
- [#32: feat: add support for parameters in client.beta.threads.messages.list](https://github.com/mharrisb1/openai-responses-python/issues/32)

Thanks @pietroMonta42 for finding these issues.

## 0.3.0

> [!IMPORTANT]
> Breaking change

Introducing an all-new API that is both simpler to use and much more flexible. See [docs](https://mharrisb1.github.io/openai-responses-python) for more.

In addition to a new API, this release closed these issues:

- [#1: feat: ability to raise exceptions](https://github.com/mharrisb1/openai-responses-python/issues/1)
- [#9: feat: base url override](https://github.com/mharrisb1/openai-responses-python/issues/9)
- [#28: feat: automatically share state between chained mocks](https://github.com/mharrisb1/openai-responses-python/issues/28)

Additional notes:

- Removes token estimation. This is now the responsibility of the user to provided mock token count
- Adds more example files
- Still not completely happy with current state of mocking run steps. Will likely change in the near future.

## 0.2.1

> [!WARNING]
> Deprecated

Fixes issue where messages included in run create params (using `additional_messages`) was ignored.

- [#10: fix: create run ignores additional_messages](https://github.com/mharrisb1/openai-responses-python/issues/10)

## 0.2.0

> [!CAUTION]
> Yanked

Migrates assistant endpoints to Assistants V2

- [#8: feat: assistants v2](https://github.com/mharrisb1/openai-responses-python/issues/8)
- [#13: feat(endpoints): add token usage estimates to chat endpoint](https://github.com/mharrisb1/openai-responses-python/issues/13)

## 0.1.1

> [!CAUTION]
> Yanked

Fixes some issues with chat completions and other stateless mocks

- [#7: fix(endpoints): fix issues with chat completions endpoint](https://github.com/mharrisb1/openai-responses-python/issues/7)

## 0.1.0

> [!CAUTION]
> Yanked

Initial release with minimally useful support for what I needed.
