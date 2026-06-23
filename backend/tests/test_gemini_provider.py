import pytest

from app.ai.client import AIProviderQuotaError
from app.ai.providers import gemini_provider
from app.ai.providers.gemini_provider import GeminiProvider, _parse_json_object


class FakeGeminiError(Exception):
    def __init__(self, *, code: int, status: str = "", message: str = "") -> None:
        super().__init__(message)
        self.code = code
        self.status = status
        self.message = message


class FakeModels:
    def __init__(self, failures: list[Exception], response: object) -> None:
        self.failures = failures
        self.response = response
        self.calls = 0
        self.last_kwargs = None

    def generate_content(self, **kwargs):
        self.calls += 1
        self.last_kwargs = kwargs
        if self.failures:
            raise self.failures.pop(0)
        return self.response


class FakeClient:
    def __init__(self, models: FakeModels) -> None:
        self.models = models


def test_gemini_provider_retries_transient_errors(monkeypatch: pytest.MonkeyPatch):
    sleeps: list[float] = []
    monkeypatch.setattr(gemini_provider.time, "sleep", sleeps.append)

    response = object()
    models = FakeModels(
        failures=[
            FakeGeminiError(
                code=503,
                status="UNAVAILABLE",
                message="This model is currently experiencing high demand.",
            ),
            FakeGeminiError(code=503, status="UNAVAILABLE", message="Temporary outage"),
        ],
        response=response,
    )
    provider = GeminiProvider.__new__(GeminiProvider)

    result = provider._generate_content_with_retries(
        client=FakeClient(models),
        model="gemini-test",
        contents="prompt",
        config=object(),
    )

    assert result is response
    assert models.calls == 3
    assert sleeps == [0.5, 1.0]


def test_gemini_provider_does_not_retry_bad_requests(monkeypatch: pytest.MonkeyPatch):
    sleeps: list[float] = []
    monkeypatch.setattr(gemini_provider.time, "sleep", sleeps.append)

    error = FakeGeminiError(code=400, status="INVALID_ARGUMENT", message="Bad request")
    models = FakeModels(failures=[error], response=object())
    provider = GeminiProvider.__new__(GeminiProvider)

    with pytest.raises(FakeGeminiError):
        provider._generate_content_with_retries(
            client=FakeClient(models),
            model="gemini-test",
            contents="prompt",
            config=object(),
        )

    assert models.calls == 1
    assert sleeps == []


def test_gemini_provider_does_not_retry_quota_errors(monkeypatch: pytest.MonkeyPatch):
    sleeps: list[float] = []
    monkeypatch.setattr(gemini_provider.time, "sleep", sleeps.append)

    error = FakeGeminiError(
        code=429,
        status="RESOURCE_EXHAUSTED",
        message="You exceeded your current quota",
    )
    models = FakeModels(failures=[error], response=object())
    provider = GeminiProvider.__new__(GeminiProvider)

    with pytest.raises(AIProviderQuotaError):
        provider._generate_content_with_retries(
            client=FakeClient(models),
            model="gemini-test",
            contents="prompt",
            config=object(),
        )

    assert models.calls == 1
    assert sleeps == []


def test_parse_json_object_handles_fenced_json():
    assert _parse_json_object('```json\n{"intent":"greeting"}\n```') == {
        "intent": "greeting",
    }
