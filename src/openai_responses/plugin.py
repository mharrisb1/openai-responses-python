import pytest

from . import OpenAIMock


def pytest_configure(config: pytest.Config):
    config.addinivalue_line(
        "markers",
        "openai_mock: OpenAI API mocker object",
    )


@pytest.fixture()
def openai_mock() -> OpenAIMock:
    return OpenAIMock()
