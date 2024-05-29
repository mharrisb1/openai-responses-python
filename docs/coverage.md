# Coverage

??? warning "File attatchments"

    There is currently no support for actually attaching files to assistant resources. Subscribe to [#5: feat: add support for attached files for all assistants APIs](https://github.com/mharrisb1/openai-responses-python/issues/5) to be notified when it is added.

??? note "Legacy endpoints"

    [Legacy endpoints](https://platform.openai.com/docs/api-reference/completions) are not supported and are not on the roadmap.

The end-goal of this library is to eventually support all OpenAI API routes. See the [roadmap](https://github.com/mharrisb1/openai-responses-python/blob/main/CONTRIBUTING.md#roadmap) for more information.

| Route                              |         Supported          |    Streaming Supported     | Route Type |
| ---------------------------------- | :------------------------: | :------------------------: | ---------- |
| **Audio**                          |
| Create speech                      |  :material-close:{ .red }  |             -              | -          |
| Create transcription               |  :material-close:{ .red }  |             -              | -          |
| Create translation                 |  :material-close:{ .red }  |             -              | -          |
| **Chat**                           |
| Create chat completion             | :material-check:{ .green } | :material-check:{ .green } | Stateless  |
| **Embeddings**                     |
| Create embedding                   | :material-check:{ .green } |             -              | Stateless  |
| **Fine-tuning**                    |
| Create fine-tuning job             |  :material-close:{ .red }  |             -              | -          |
| List fine-tuning jobs              |  :material-close:{ .red }  |             -              | -          |
| List fine-tuning events            |  :material-close:{ .red }  |             -              | -          |
| List fine-tuning checkpoints       |  :material-close:{ .red }  |             -              | -          |
| Retrieve fine-tuning job           |  :material-close:{ .red }  |             -              | -          |
| Cancel fine-tuning                 |  :material-close:{ .red }  |             -              | -          |
| **Batch**                          |
| Create batch                       |  :material-close:{ .red }  |             -              | -          |
| Retrieve batch                     |  :material-close:{ .red }  |             -              | -          |
| Cancel batch                       |  :material-close:{ .red }  |             -              | -          |
| List batch                         |  :material-close:{ .red }  |             -              | -          |
| **Files**                          |
| Upload file                        | :material-check:{ .green } |             -              | Stateful   |
| List files                         | :material-check:{ .green } |             -              | Stateful   |
| Retrieve file                      | :material-check:{ .green } |             -              | Stateful   |
| Delete file                        | :material-check:{ .green } |             -              | Stateful   |
| Retrieve file content              | :material-check:{ .green } |             -              | Stateful   |
| **Images**                         |
| Create image                       |  :material-close:{ .red }  |             -              | -          |
| Create image edit                  |  :material-close:{ .red }  |             -              | -          |
| Create image variation             |  :material-close:{ .red }  |             -              | -          |
| **Models**                         |
| List models                        | :material-check:{ .green } |             -              | Stateful   |
| Retrieve model                     | :material-check:{ .green } |             -              | Stateful   |
| Delete a fine-tuned model          |  :material-close:{ .red }  |             -              | -          |
| **Moderations**                    |
| Create moderation                  |  :material-close:{ .red }  |             -              | -          |
| **Assistants**                     |
| Create assistant                   | :material-check:{ .green } |             -              | Stateful   |
| List assistants                    | :material-check:{ .green } |             -              | Stateful   |
| Retrieve assistant                 | :material-check:{ .green } |             -              | Stateful   |
| Modify assistant                   | :material-check:{ .green } |             -              | Stateful   |
| Delete assistant                   | :material-check:{ .green } |             -              | Stateful   |
| **Threads**                        |
| Create thread                      | :material-check:{ .green } |             -              | Stateful   |
| Retrieve thread                    | :material-check:{ .green } |             -              | Stateful   |
| Modify thread                      | :material-check:{ .green } |             -              | Stateful   |
| Delete thread                      | :material-check:{ .green } |             -              | Stateful   |
| **Messages**                       |
| Create message                     | :material-check:{ .green } |             -              | Stateful   |
| List messages                      | :material-check:{ .green } |             -              | Stateful   |
| Retrieve message                   | :material-check:{ .green } |             -              | Stateful   |
| Modify message                     | :material-check:{ .green } |             -              | Stateful   |
| Delete message                     | :material-check:{ .green } |             -              | Stateful   |
| **Runs**                           |
| Create run                         | :material-check:{ .green } | :material-check:{ .green } | Stateful   |
| Create thread and run              | :material-check:{ .green } | :material-check:{ .green } | Stateful   |
| List runs                          | :material-check:{ .green } |             -              | Stateful   |
| Retrieve run                       | :material-check:{ .green } |             -              | Stateful   |
| Modify run                         | :material-check:{ .green } |             -              | Stateful   |
| Submit tool outputs to run         | :material-check:{ .green } | :material-check:{ .green } | Stateful   |
| Cancel run                         | :material-check:{ .green } |             -              | Stateful   |
| **Run Steps**                      |
| List run steps                     | :material-check:{ .green } |             -              | Stateful   |
| Retrieve run step                  | :material-check:{ .green } |             -              | Stateful   |
| **Vector Stores**                  |
| Create vector store                | :material-check:{ .green } |             -              | Stateful   |
| List vector stores                 | :material-check:{ .green } |             -              | Stateful   |
| Retrieve vector store              | :material-check:{ .green } |             -              | Stateful   |
| Modify vector store                | :material-check:{ .green } |             -              | Stateful   |
| Delete vector store                | :material-check:{ .green } |             -              | Stateful   |
| **Vector Store Files**             |
| Create vector store file           | :material-check:{ .green } |             -              | Stateful   |
| List vector store files            | :material-check:{ .green } |             -              | Stateful   |
| Retrieve vector store file         |  :material-close:{ .red }  |             -              | -          |
| Delete vector store file           |  :material-close:{ .red }  |             -              | -          |
| **Vector Store File Batches**      |
| Create vector store file batch     |  :material-close:{ .red }  |             -              | -          |
| Retrieve vector store file batch   |  :material-close:{ .red }  |             -              | -          |
| Cancel vector store file batch     |  :material-close:{ .red }  |             -              | -          |
| List vector store files in a batch |  :material-close:{ .red }  |             -              | -          |
