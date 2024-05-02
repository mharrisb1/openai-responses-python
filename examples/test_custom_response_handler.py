import openai

import openai_responses
from openai_responses import OpenAIMock, Request, Response, Route
from openai_responses.helpers.builders import chat_completion_from_create_request


def custom_response_handler(request: Request, route: Route) -> Response:
    if route.call_count < 2:
        return Response(500)

    completion = chat_completion_from_create_request(request)

    return Response(201, json=completion.model_dump())


@openai_responses.mock()
def test_create_chat_completion(openai_mock: OpenAIMock):
    openai_mock.chat.completions.create.response = custom_response_handler

    client = openai.Client(api_key="sk-fake123", max_retries=3)
    client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Hello!"},
        ],
    )

    assert openai_mock.chat.completions.create.calls.call_count == 3
