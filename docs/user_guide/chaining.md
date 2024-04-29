# Chaining

To mock more than one API endpoint, you can chain decorators as much as you'd like.

```python linenums="1"
@openai_responses.mock.beta.threads()
@openai_responses.mock.beta.threads.runs()
def test_list_runs(threads_mock: ThreadsMock, runs_mock: RunsMock):
    client = OpenAI(api_key="fakeKey")
    thread = client.beta.threads.create()

    for _ in range(20):
        client.beta.threads.runs.create(thread.id, assistant_id="asst_abc123")

    runs = client.beta.threads.runs.list(thread.id)

    assert len(runs.data) == 20

    assert threads_mock.create.route.calls.call_count == 1
    assert runs_mock.create.route.calls.call_count == 20
    assert runs_mock.list.route.calls.call_count == 1
```

!!! tip

    To share state between mocks, see the [state](state.md) page in the user guide.
