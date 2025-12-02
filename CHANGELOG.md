# Changelog

See [releases](https://github.com/mharrisb1/openai-responses-python/releases) for more.

## v0.13.1

Pull Requests:

- [#73: feat: support mock async stream](https://github.com/mharrisb1/openai-responses-python/issues/73)

## v0.13.0

> [!IMPORTANT]
> Breaking change

Bumps support min version to OpenAI v2.0+

Pull Requests:

- [#76: chore(deps): bump openai support to v2+](https://github.com/mharrisb1/openai-responses-python/issues/76)

## v0.12.0

> [!IMPORTANT]
> Breaking change

Promotes vector store routes from beta. This is a breaking change and now the minimum supported SDK version is v1.66. Also adds Python 3.13 to test matrix.

Issues:

- [#70: OpenAI v1.66.0 Compatibility: openai.types.beta.vector_store Missing](https://github.com/mharrisb1/openai-responses-python/issues/70)

Pull Requests:

- [#71: fix(routes): promote vector stores from beta](https://github.com/mharrisb1/openai-responses-python/issues/71)
- [#72: chore(ci): add Python 3.13 to test matrix](https://github.com/mharrisb1/openai-responses-python/issues/72)

## v0.11.6

Relaxes strict support range for OpenAI Python SDK in hopes that schemas/models are matured and won't have breaking changes. See [#69: openai-responses 0.11.4 requires openai<1.60,>=1.50](https://github.com/mharrisb1/openai-responses-python/issues/69) for conversation.

## v0.11.5

Bumps support range to include OpenAI Python SDK v1.60.

## v0.11.4

Bumps support range to include OpenAI Python SDK v1.59.

## v0.11.3

Pins minimum RESPX version to v0.22.0 with support for HTTPX v0.28. Closes [#67: Add support for OpenAI 1.55](https://github.com/mharrisb1/openai-responses-python/issues/67)

## v0.11.2

Bumps support range to include OpenAI Python SDK v1.54.

## v0.11.1

Bumps support range to include OpenAI Python SDK v1.51.

## v0.11.0

OpenAI Python SDK minimum version is now v1.50.

## 0.10.3

Bumps support range to include OpenAI Python SDK v1.47.

## 0.10.2

Bumps support range to include OpenAI Python SDK v1.45 and includes o1 family of models in fetch models response.

Issues:

- [#60: fix: models constant is stale](https://github.com/mharrisb1/openai-responses-python/issues/60)

## 0.10.1

Bumps support range to include OpenAI Python SDK v1.43.

## 0.10.0

Adds support for [moderations endpoint](https://platform.openai.com/docs/api-reference/moderations/create).

Issues:

- [#23: feat: add support for moderation endpoint](https://github.com/mharrisb1/openai-responses-python/issues/23)

Pull requests:

- [#61: feat(routes): add moderation route support](https://github.com/mharrisb1/openai-responses-python/issues/61)

## 0.9.1

Bumps support range to include OpenAI Python SDK v1.42. Also adds env for testing Pydantic V1 and V2 in tox.

## 0.9.0

Adds support for [structured outputs](https://openai.com/index/introducing-structured-outputs-in-the-api/) and the `beta.chat.completions` route.

Misc:

- Adds a working example of how to use this library to test `langchain-openai` (asked about in [#58: Would `openai-responses-python` work with langchain_openai?](https://github.com/mharrisb1/openai-responses-python/issues/58))

## 0.8.5

Bumps support range to include OpenAI Python SDK v1.40.

## 0.8.4

Bumps support range to include OpenAI Python SDK v1.38. Also removes dependency on `faker`.

## 0.8.3

Bumps support range to include OpenAI Python SDK v1.37.

## 0.8.2

Bumps support range to include OpenAI Python SDK v1.36.

## 0.8.1

Bumps support range to include OpenAI Python SDK v1.35.

## 0.8.0

Breaking change that removes the event method on the event stream classes and forces the user to explicitly define and construct the generated events.

This will help cut down on feature drift overtime since this is relying on OpenAI's types instead of relying on custom code that tried to make this easier for the user.

Closed:

- [#54: feat: change Event class generator for EventDelta](https://github.com/mharrisb1/openai-responses-python/issues/54)

## 0.7.0

Pulls in breaking changes fromr from OpenAI Python SDK v1.32+ and pins version support to `>=1.32,<1.35`

## 0.6.1

Pins OpenAI SDK version to `>=1.25,<1.32`

## 0.6.0

Adds vector store responses

Closed:

- [#24: feat: support vector store endpoints](https://github.com/mharrisb1/openai-responses-python/issues/24)
- [#47: feat: support vector store file batch endpoint](https://github.com/mharrisb1/openai-responses-python/issues/47)
- [#49: feat: create vector store from assistant and thread create](https://github.com/mharrisb1/openai-responses-python/issues/49)

## 0.5.0

Adds routes for models and retrieving file content.

Closed:

- [#22: feat: support models endpoint](https://github.com/mharrisb1/openai-responses-python/issues/22)
- [#46: feat(routes): add retrieve file content route](https://github.com/mharrisb1/openai-responses-python/issues/46)

## 0.4.1

Adds setter for `OpenAIMock` state store

## 0.4.0

> [!IMPORTANT]
> Breaking change

> [!NOTE]
> ✨ Streaming support is here

Tons of changes:

- New `EventStream` and `AsyncEventStream` objects to create mock event streams
- `OpenAIMock` class now exposes state store through `state` property
- Updated and more organized API
- Replacement of `calls` property on routes in favor of `route` property
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
