import json
from types import SimpleNamespace

import pytest

from app.ai.client import AIDisabledError, AIProviderError, AIProviderQuotaError
from app.ai.providers import groq_provider
from app.ai.providers.groq_provider import GroqProvider
from app.ai.schemas import BookingIntentExtractionContext


class FakeGroqError(Exception):
    def __init__(self, *, status_code: int, message: str) -> None:
        super().__init__(message)
        self.status_code = status_code
        self.message = message


class FakeCompletions:
    def __init__(self, failures: list[Exception], response: object) -> None:
        self.failures = failures
        self.response = response
        self.calls = 0
        self.last_kwargs = None

    def create(self, **kwargs):
        self.calls += 1
        self.last_kwargs = kwargs
        if self.failures:
            raise self.failures.pop(0)
        return self.response


class FakeClient:
    def __init__(self, completions: FakeCompletions) -> None:
        self.chat = SimpleNamespace(completions=completions)


def make_completion(payload: dict[str, object]) -> object:
    return SimpleNamespace(
        choices=[
            SimpleNamespace(
                message=SimpleNamespace(content=json.dumps(payload)),
            )
        ]
    )


def test_groq_provider_missing_api_key_is_configuration_error(
    monkeypatch: pytest.MonkeyPatch,
):
    monkeypatch.setattr(groq_provider, "get_groq_api_key", lambda: "")

    with pytest.raises(AIDisabledError, match="Groq API key is not configured"):
        GroqProvider()


def test_groq_provider_parses_valid_json_response(
    monkeypatch: pytest.MonkeyPatch,
):
    monkeypatch.setattr(groq_provider, "get_groq_api_key", lambda: "gsk_test")
    monkeypatch.setattr(groq_provider, "get_groq_model", lambda: "llama-3.1-8b-instant")

    provider = GroqProvider()
    completion = make_completion(
        {
            "intent": "find_booking_slot",
            "service_query": "Haircut",
            "date": "2026-06-24",
            "time_preference": "at 15.00",
            "time_preference_type": "at",
            "time": "15.00",
            "master_preference": "",
            "missing_fields": [],
            "assistant_message": "I can help find options at 15.00.",
        }
    )
    completions = FakeCompletions(failures=[], response=completion)
    monkeypatch.setattr(provider, "_build_client", lambda: FakeClient(completions))

    result = provider.extract_booking_intent(
        BookingIntentExtractionContext(
            today="2026-06-23",
            service_names=["Haircut"],
            user_message="want tomorow haircut at 15.00",
        )
    )

    assert result.intent == "find_booking_slot"
    assert result.time == "15:00"
    assert result.time_preference == "at 15:00"


def test_groq_provider_invalid_json_does_not_crash(
    monkeypatch: pytest.MonkeyPatch,
):
    monkeypatch.setattr(groq_provider, "get_groq_api_key", lambda: "gsk_test")
    monkeypatch.setattr(groq_provider, "get_groq_model", lambda: "llama-3.1-8b-instant")

    provider = GroqProvider()
    completion = SimpleNamespace(
        choices=[
            SimpleNamespace(message=SimpleNamespace(content="not json")),
        ]
    )
    monkeypatch.setattr(provider, "_build_client", lambda: FakeClient(
        FakeCompletions(failures=[], response=completion)
    ))

    with pytest.raises(AIProviderError):
        provider.extract_booking_intent(
            BookingIntentExtractionContext(
                today="2026-06-23",
                service_names=["Haircut"],
                user_message="look",
            )
        )


def test_groq_provider_uses_json_mode_and_retries_transient_errors(
    monkeypatch: pytest.MonkeyPatch,
):
    sleeps: list[float] = []
    monkeypatch.setattr(groq_provider.time, "sleep", sleeps.append)

    response = object()
    completions = FakeCompletions(
        failures=[
            FakeGroqError(status_code=503, message="temporary outage"),
            FakeGroqError(status_code=502, message="bad gateway"),
        ],
        response=response,
    )
    provider = GroqProvider.__new__(GroqProvider)

    result = provider._create_completion_with_retries(
        client=FakeClient(completions),
        model="llama-3.1-8b-instant",
        prompt="prompt",
    )

    assert result is response
    assert completions.calls == 3
    assert sleeps == [0.5, 1.0]
    assert completions.last_kwargs["response_format"] == {"type": "json_object"}


def test_groq_provider_does_not_retry_rate_limits(monkeypatch: pytest.MonkeyPatch):
    sleeps: list[float] = []
    monkeypatch.setattr(groq_provider.time, "sleep", sleeps.append)

    completions = FakeCompletions(
        failures=[FakeGroqError(status_code=429, message="rate limit exceeded")],
        response=object(),
    )
    provider = GroqProvider.__new__(GroqProvider)

    with pytest.raises(AIProviderQuotaError):
        provider._create_completion_with_retries(
            client=FakeClient(completions),
            model="llama-3.1-8b-instant",
            prompt="prompt",
        )

    assert completions.calls == 1
    assert sleeps == []
