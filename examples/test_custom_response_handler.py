import openai

import openai_responses
from openai_responses import OpenAIMock
from openai_responses.ext.httpx import Request, Response
from openai_responses.ext.respx import Route
from openai_responses.helpers.builders.chat import chat_completion_from_create_request


def completion_with_failures(request: Request, route: Route) -> Response:
    """Simulate 2 failures before sending successful response"""
    if route.call_count < 2:
        return Response(500)

    completion = chat_completion_from_create_request(request, extra={"choices": []})

    return Response(201, json=completion.model_dump())


@openai_responses.mock()
def test_create_chat_completion(openai_mock: OpenAIMock):
    openai_mock.chat.completions.create.response = completion_with_failures

    client = openai.Client(api_key="sk-fake123", max_retries=3)
    client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Hello!"},
        ],
    )

    assert openai_mock.chat.completions.create.calls.call_count == 3
