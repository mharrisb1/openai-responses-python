import openai
import pytest

import openai_responses
from openai_responses import OpenAIMock


@pytest.fixture()
def client():
    return openai.Client(api_key="sk-fake123")


@openai_responses.mock()
def test_create_moderation_returns_default(
    openai_mock: OpenAIMock, client: openai.Client
):
    expected_prefix = "modr-"
    expect_model = "text-moderation-007"

    actual = client.moderations.create(input="Test input")

    assert actual.id.startswith(
        expected_prefix
    ), f"Expected id to start with {expected_prefix}"
    assert actual.model == expect_model
    assert len(actual.results) == 0
    assert openai_mock.moderations.create.route.call_count == 1


@openai_responses.mock()
def test_create_moderation_applies_defaults_if_partial_response_provided(
    openai_mock: OpenAIMock, client: openai.Client
):
    openai_mock.moderations.create.response = {
        "results": [
            {
                "flagged": True,
                "categories": {"harassment": True, "violence/graphic": True},
                "category_scores": {"harassment": 0.9, "violence/graphic": 0.8},
            }
        ]
    }

    actual = client.moderations.create(input="Test input")

    assert len(actual.results) == 1
    assert actual.results[0].model_dump(by_alias=True) == {
        "flagged": True,
        "categories": {
            "harassment": True,
            "harassment/threatening": False,
            "hate": False,
            "hate/threatening": False,
            "illicit": False,
            "illicit/violent": False,
            "self-harm": False,
            "self-harm/instructions": False,
            "self-harm/intent": False,
            "sexual": False,
            "sexual/minors": False,
            "violence": False,
            "violence/graphic": True,
        },
        "category_applied_input_types": {
            "harassment": [],
            "harassment/threatening": [],
            "hate": [],
            "hate/threatening": [],
            "illicit": [],
            "illicit/violent": [],
            "self-harm": [],
            "self-harm/instructions": [],
            "self-harm/intent": [],
            "sexual": [],
            "sexual/minors": [],
            "violence": [],
            "violence/graphic": [],
        },
        "category_scores": {
            "harassment": 0.9,
            "harassment/threatening": 0.0,
            "hate": 0.0,
            "hate/threatening": 0.0,
            "illicit": 0.0,
            "illicit/violent": 0.0,
            "self-harm": 0.0,
            "self-harm/instructions": 0.0,
            "self-harm/intent": 0.0,
            "sexual": 0.0,
            "sexual/minors": 0.0,
            "violence": 0.0,
            "violence/graphic": 0.8,
        },
    }
