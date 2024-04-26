from openai_responses.tokens import count_tokens


def test_count_tokens():
    model = "gpt-4-turbo"
    text = "tiktoken is great!"
    assert count_tokens(model, text) == 6
