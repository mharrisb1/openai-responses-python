import tiktoken
from openai.types.completion_usage import CompletionUsage
from openai.types.chat.chat_completion import ChatCompletion
from openai.types.chat.completion_create_params import CompletionCreateParams


def count_tokens(model: str, text: str) -> int:
    encoding = tiktoken.encoding_for_model(model)
    return len(encoding.encode(text))


def add_token_usage_for_completion(
    completion: ChatCompletion,
    params: CompletionCreateParams,
) -> None:
    if completion.usage:
        return

    generated = ""
    for choice in completion.choices:
        if choice.message.content:
            generated += choice.message.content
        elif choice.message.tool_calls:
            for tool_call in choice.message.tool_calls:
                generated += tool_call.function.arguments

    prompt = ""
    for message in params["messages"]:
        prompt += str(message.get("content"))

    completion_tokens = count_tokens(completion.model, generated)
    prompt_tokens = count_tokens(completion.model, prompt)
    total_tokens = completion_tokens + prompt_tokens

    completion.usage = CompletionUsage(
        completion_tokens=completion_tokens,
        prompt_tokens=prompt_tokens,
        total_tokens=total_tokens,
    )
