import random

__all__ = ["faker"]


class Base62:
    BASE = 62
    CHARSET = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"

    def encode(self, b: bytes) -> str:
        encoded: list[str] = []
        for byte in b:
            i = byte % self.BASE
            encoded.append(self.CHARSET[i])

        return "".join(reversed(encoded))


base62 = Base62()


def gen_id_suffix() -> str:
    b = random.randbytes(24)
    return base62.encode(b)


def gen_id(prefix: str, *, sep: str = "_") -> str:
    return prefix + sep + gen_id_suffix()


class AssistantProvider:
    def id(self) -> str:
        return gen_id("asst")


class ChatProvider:
    def __init__(self) -> None:
        self.completion = ChatProvider.CompletionProvider()

    class CompletionProvider:
        def id(self) -> str:
            return gen_id("chatcmpl")


class FileProvider:
    def id(self) -> str:
        return gen_id("file", sep="-")


class ThreadProvider:
    def __init__(self) -> None:
        self.message = ThreadProvider.MessageProvider()
        self.run = ThreadProvider.RunProvider()

    def id(self) -> str:
        return gen_id("thread")

    class MessageProvider:
        def id(self) -> str:
            return gen_id("msg")

    class RunProvider:
        def __init__(self) -> None:
            self.step = ThreadProvider.RunProvider.StepProvider()

        def id(self) -> str:
            return gen_id("run")

        class StepProvider:
            def __init__(self) -> None:
                self.step_details = (
                    ThreadProvider.RunProvider.StepProvider.StepDetailsProvider()
                )

            def id(self) -> str:
                return gen_id("step")

            class StepDetailsProvider:

                def __init__(self) -> None:
                    self.tool_call = (
                        ThreadProvider.RunProvider.StepProvider.StepDetailsProvider.ToolCallProvider()
                    )

                class ToolCallProvider:
                    def id(self) -> str:
                        return gen_id("call")


class VectorStoreProvider:
    def __init__(self) -> None:
        self.file_batch = VectorStoreProvider.VectorStoreFileBatchProvider()

    def id(self) -> str:
        return gen_id("vs")

    class VectorStoreFileBatchProvider:
        def id(self) -> str:
            return gen_id("vsfb")


class ModerationProvider:
    def id(self) -> str:
        return gen_id(prefix="modr", sep="-")


class Faker:
    def __init__(self) -> None:
        self.chat = ChatProvider()
        self.file = FileProvider()
        self.moderation = ModerationProvider()
        self.beta = Faker.BetaProviders()

    class BetaProviders:
        def __init__(self) -> None:
            self.assistant = AssistantProvider()
            self.thread = ThreadProvider()
            self.vector_store = VectorStoreProvider()


faker = Faker()
