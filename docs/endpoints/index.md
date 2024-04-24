# Coverage

??? warning "Streaming Support"

    Currently, there is no support for streaming. This is a top feature request so once I have time to tackle it I will.
    Subscribe to [#3: feat: streaming support](https://github.com/mharrisb1/openai-responses-python/issues/3) to be notified when it is added.

Table is assembled according to APIs listed in the [OpenAI API Reference](https://platform.openai.com/docs/api-reference)

| Endpoint                               |        Supported         | Streaming Supported | Mock Type    |
| -------------------------------------- | :----------------------: | :-----------------: | ------------ |
| Audio                                  |     :material-close:     |          -          | Stateless    |
| [Chat](chat.md)                        |   :material-check-all:   |  :material-close:   | Stateless    |
| [Embeddings](embeddings.md)            |   :material-check-all:   |          -          | Stateless    |
| Fine-tuning                            |     :material-close:     |          -          | Stateful     |
| Batch                                  |     :material-close:     |          -          | Stateful     |
| [Files](files.md)                      |   :material-check:[^1]   |          -          | Stateful     |
| Images                                 |     :material-close:     |          -          | Stateless    |
| Models                                 |     :material-close:     |          -          | Stateful[^2] |
| Moderations                            |     :material-close:     |          -          | Stateless    |
| [Assistants](assistants/assistants.md) |   :material-check:[^3]   |          -          | Stateful     |
| [Threads](assistants/threads.md)       |   :material-check-all:   |          -          | Stateful     |
| [Messages](assistants/messages.md)     |   :material-check:[^3]   |          -          | Stateful     |
| [Runs](assistants/runs.md)             | :material-check:[^4][^5] |  :material-close:   | Stateful     |
| [Run Steps](assistants/run_steps.md)   |   :material-check:[^6]   |          -          | Stateful     |
| Vector Stores                          |     :material-close:     |          -          | Stateful     |
| Vector Store Files                     |     :material-close:     |          -          | Stateful     |
| Vector Store File Batches              |     :material-close:     |          -          | Stateful     |
| Completions (Legacy)                   |     :material-close:     |  :material-close:   | Stateless    |

:material-close: = Not implemented

:material-check: = Partially implemented

:material-check-all: = Fully implemented

[^1]: Need to add support for retrieving file content
[^2]: Blocked by fine-tuning support
[^3]: Need to add support for attached files
[^4]: Need to add support for create thread and run
[^5]: No state changes on submit tool call
[^6]: Fragile API for run steps
