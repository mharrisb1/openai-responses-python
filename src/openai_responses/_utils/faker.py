from faker import Faker
from faker_openai_api_provider import OpenAiApiProvider

__all__ = ["faker"]

fake = Faker()
fake.add_provider(OpenAiApiProvider)
faker: OpenAiApiProvider.Api = fake.openai()
