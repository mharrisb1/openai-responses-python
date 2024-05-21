import json

import openai
from openai.types.beta.threads.run_submit_tool_outputs_params import ToolOutput

import openai_responses
from openai_responses import OpenAIMock
from openai_responses.stores import StateStore
from openai_responses.ext.httpx import Request, Response, post
from openai_responses.ext.respx import Route
from openai_responses.helpers.mergers.runs import merge_run_with_partial


def polled_get_run_responses(
    request: Request,
    route: Route,
    state_store: StateStore,
    thread_id: str,
    run_id: str,
) -> Response:
    run = state_store.beta.threads.runs.get(run_id)
    assert run
    if route.call_count < 4:
        run.status = "in_progress"
        state_store.beta.threads.runs.put(run)
        return Response(200, request=request, json=run.model_dump())

    else:
        run = merge_run_with_partial(
            run,
            {
                "thread_id": thread_id,
                "status": "requires_action",
                "required_action": {
                    "type": "submit_tool_outputs",
                    "submit_tool_outputs": {
                        "tool_calls": [
                            {
                                "id": "call_abc123",
                                "type": "function",
                                "function": {
                                    "name": "get_current_temperature",
                                    "arguments": json.dumps(
                                        {
                                            "location": "San Francisco, CA",
                                            "unit": "Farenheit",
                                        }
                                    ),
                                },
                            }
                        ]
                    },
                },
            },
        )
        state_store.beta.threads.runs.put(run)
        return Response(200, request=request, json=run.model_dump())


@openai_responses.mock()
def test_external_api_mock(openai_mock: OpenAIMock):
    client = openai.Client(api_key="sk-fake123")

    assistant = client.beta.assistants.create(
        instructions="You are a weather bot. Use the provided functions to answer questions.",
        model="gpt-4o",
        tools=[
            {
                "type": "function",
                "function": {
                    "name": "get_current_temperature",
                    "description": "Get the current temperature for a specific location",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "location": {
                                "type": "string",
                                "description": "The city and state, e.g., San Francisco, CA",
                            },
                            "unit": {
                                "type": "string",
                                "enum": ["Celsius", "Fahrenheit"],
                                "description": "The temperature unit to use. Infer this from the user's location.",
                            },
                        },
                        "required": ["location", "unit"],
                    },
                },
            },
        ],
    )

    thread = client.beta.threads.create()
    client.beta.threads.messages.create(
        thread_id=thread.id,
        role="user",
        content="What's the weather in San Francisco today?",
    )

    run = client.beta.threads.runs.create(
        thread_id=thread.id,
        assistant_id=assistant.id,
    )

    # add response with side effects
    openai_mock.beta.threads.runs.retrieve.response = polled_get_run_responses

    # add new mock for non-OpenAI API
    openai_mock.router.post(url="https://api.myweatherapi.com").mock(
        Response(200, json={"value": "57"})
    )

    while True:
        run = client.beta.threads.runs.retrieve(run.id, thread_id=thread.id)
        if run.status == "requires_action":
            assert run.required_action
            tool_outputs: list[ToolOutput] = []
            for tool in run.required_action.submit_tool_outputs.tool_calls:
                if tool.function.name == "get_current_temperature":
                    res = post(
                        url="https://api.myweatherapi.com",
                        json=json.loads(tool.function.arguments),
                    )
                    data: dict[str, str] = res.json()
                    tool_outputs.append(
                        {
                            "tool_call_id": tool.id,
                            "output": data["value"],
                        }
                    )
                else:
                    raise ValueError

            assert len(tool_outputs) > 0
            client.beta.threads.runs.submit_tool_outputs(
                run.id,
                thread_id=thread.id,
                tool_outputs=tool_outputs,
            )
            break
        else:
            continue

    assert openai_mock.beta.assistants.create.calls.call_count == 1
    assert openai_mock.beta.threads.create.calls.call_count == 1
    assert openai_mock.beta.threads.messages.create.calls.call_count == 1
    assert openai_mock.beta.threads.runs.create.calls.call_count == 1
    assert openai_mock.beta.threads.runs.retrieve.calls.call_count == 5
    assert openai_mock.beta.threads.runs.submit_tool_outputs.calls.call_count == 1
