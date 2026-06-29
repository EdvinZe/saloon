import importlib


def reload_config(monkeypatch, **env):
    keys = {
        "AI_DEBUG": "",
        "AI_PROVIDER": "",
        "AI_MODEL": "",
        "GEMINI_MODEL": "",
        "GROQ_MODEL": "",
    }
    for key in keys:
        monkeypatch.delenv(key, raising=False)
    for key, value in env.items():
        monkeypatch.setenv(key, value)

    import app.core.config as config

    return importlib.reload(config)


def test_ai_config_defaults_to_groq_with_provider_models(monkeypatch):
    config = reload_config(monkeypatch)

    assert config.get_ai_provider() == "groq"
    assert config.get_gemini_model() == "gemini-2.5-flash"
    assert config.get_groq_model() == "llama-3.1-8b-instant"


def test_ai_config_provider_specific_models_win(monkeypatch):
    config = reload_config(
        monkeypatch,
        AI_MODEL="legacy-model",
        GEMINI_MODEL="gemini-custom",
        GROQ_MODEL="groq-custom",
    )

    assert config.get_gemini_model() == "gemini-custom"
    assert config.get_groq_model() == "groq-custom"


def test_ai_config_legacy_ai_model_remains_fallback(monkeypatch):
    config = reload_config(monkeypatch, AI_MODEL="legacy-model")

    assert config.get_gemini_model() == "legacy-model"
    assert config.get_groq_model() == "legacy-model"


def test_ai_debug_defaults_to_enabled_when_env_missing(monkeypatch):
    config = reload_config(monkeypatch)

    assert config.is_ai_debug_enabled() is True


def test_ai_debug_false_disables_debug(monkeypatch):
    config = reload_config(monkeypatch, AI_DEBUG="false")

    assert config.is_ai_debug_enabled() is False
