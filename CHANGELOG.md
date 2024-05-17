# Changelog

## 0.3.1

Fixes:

- [#31: feat: add support for null args on create_and_run](https://github.com/mharrisb1/openai-responses-python/issues/31)
- [#32: feat: add support for parameters in client.beta.threads.messages.list](https://github.com/mharrisb1/openai-responses-python/issues/32)

Thanks @pietroMonta42 for finding these issues.

## 0.3.0

> [!IMPORTANT]
> **Breaking change**: Completely redesigned API

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
