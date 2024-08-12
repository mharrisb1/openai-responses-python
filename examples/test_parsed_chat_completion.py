from datetime import datetime

import openai
from pydantic import BaseModel

import openai_responses
from openai_responses import OpenAIMock


class CalendarEvent(BaseModel):
    name: str
    date: str
    participants: list[str]


@openai_responses.mock()
def test_create_chat_completion(openai_mock: OpenAIMock):
    openai_mock.beta.chat.completions.create.response = {
        "choices": [
            {
                "index": 0,
                "finish_reason": "stop",
                "message": {
                    "content": CalendarEvent(
                        name="Example Event",
                        date=datetime.now().strftime("%Y-%m-%d"),
                        participants=[
                            "Alice",
                            "Bob",
                            "Claire",
                        ],
                    ).model_dump_json(),
                    "role": "assistant",
                },
            }
        ]
    }

    client = openai.Client(api_key="sk-fake123")

    completion = client.beta.chat.completions.parse(
        model="gpt-4o-2024-08-06",
        messages=[
            {"role": "system", "content": "Extract the event information."},
            {
                "role": "user",
                "content": "Alice and Bob are going to a science fair on Friday.",
            },
        ],
        response_format=CalendarEvent,
    )

    event = completion.choices[0].message.parsed
    assert event
    assert event.name == "Example Event"
    assert datetime.strptime(event.date, "%Y-%m-%d").date() == datetime.now().date()
    assert len(event.participants) == 3
