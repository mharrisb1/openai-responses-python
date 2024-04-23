# Coverage

??? warning "Streaming Support"

    Currently, there is no support for streaming. This is a top feature request so once I have time to tackle it I will. Subscribe to [#3: feat: streaming support](https://github.com/mharrisb1/openai-responses-python/issues/3) to be notified when it is added.

Table is assembled according to APIs listed in the [OpenAI API Reference](https://platform.openai.com/docs/api-reference)

| Endpoint                    |          Supported           | Streaming Supported | Mock Type     |
| --------------------------- | :--------------------------: | :-----------------: | ------------- |
| Audio                       |       :material-close:       |          -          | Stateless     |
| [Chat](chat.md)             |     :material-check-all:     |  :material-close:   | Stateless     |
| [Embeddings](embeddings.md) |     :material-check-all:     |          -          | Stateless     |
| Fine-tuning                 |       :material-close:       |          -          | Stateful      |
| Files                       |     :material-check:[^1]     |          -          | Stateful      |
| Images                      |       :material-close:       |          -          | Stateless     |
| Models                      |       :material-close:       |          -          | Stateless[^2] |
| Moderations                 |       :material-close:       |          -          | Stateless     |
| Assistants                  |     :material-check:[^3]     |          -          | Stateful      |
| Threads                     |     :material-check-all:     |          -          | Stateful      |
| Messages                    |     :material-check:[^3]     |          -          | Stateful      |
| Runs                        | :material-check:[^4][^5][^6] |  :material-close:   | Stateful      |
| Completions                 |       :material-close:       |  :material-close:   | Stateless     |

:material-close: = Not supported

:material-check: = Partially supported

:material-check-all: = Fully supported

[^1]: Need to add support for retrieving file content
[^2]: Stateless until fine-tuning is supported then it will need to be stateful
[^3]: Need to add support for attached files
[^4]: Need to add support for create thread and run
[^5]: Fragile API for run steps
[^6]: No state changes on submit tool call
