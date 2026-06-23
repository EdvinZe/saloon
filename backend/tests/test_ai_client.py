import pytest

from app.ai.client import AIDisabledError, AIClient


def test_ai_client_factory_selects_groq(monkeypatch: pytest.MonkeyPatch):
    sentinel = object()
    monkeypatch.setattr("app.ai.client.get_ai_provider", lambda: "groq")
    monkeypatch.setattr("app.ai.providers.groq_provider.GroqProvider", lambda: sentinel)

    assert AIClient()._build_provider() is sentinel


def test_ai_client_factory_selects_gemini(monkeypatch: pytest.MonkeyPatch):
    sentinel = object()
    monkeypatch.setattr("app.ai.client.get_ai_provider", lambda: "gemini")
    monkeypatch.setattr("app.ai.providers.gemini_provider.GeminiProvider", lambda: sentinel)

    assert AIClient()._build_provider() is sentinel


def test_ai_client_factory_rejects_unknown_provider(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr("app.ai.client.get_ai_provider", lambda: "unknown")

    with pytest.raises(AIDisabledError, match="Unsupported AI provider"):
        AIClient()._build_provider()
