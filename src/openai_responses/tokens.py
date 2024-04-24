import tiktoken


def count_tokens(model: str, text: str) -> int:
    encoding = tiktoken.encoding_for_model(model)
    return len(encoding.encode(text))
