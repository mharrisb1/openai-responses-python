from langchain_openai import ChatOpenAI
from pydantic.v1 import SecretStr

import openai_responses
from openai_responses import OpenAIMock


@openai_responses.mock()
def test_langchain_chat_openai_invoke(openai_mock: OpenAIMock):
    openai_mock.chat.completions.create.response = {
        "choices": [
            {
                "index": 0,
                "finish_reason": "stop",
                "message": {
                    "content": "J'adore la programmation.",
                    "role": "assistant",
                },
            }
        ]
    }

    llm = ChatOpenAI(
        name="My Custom Chatbot",
        model="gpt-4o",
        temperature=0,
        max_tokens=None,
        timeout=None,
        max_retries=2,
        api_key=SecretStr("sk-fake123"),
    )

    messages = [
        (
            "system",
            "You are a helpful assistant that translates English to French. Translate the user sentence.",
        ),
        ("human", "I love programming."),
    ]
    ai_msg = llm.invoke(messages)
    assert ai_msg.content == "J'adore la programmation."  # type: ignore
