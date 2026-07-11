from backend.app.core.config import Settings


def test_settings_reads_openrouter_environment_variables(
    monkeypatch,
) -> None:
    monkeypatch.setenv("OPENROUTER_API_KEY", "router-key")
    monkeypatch.setenv("OPENROUTER_MODEL", "anthropic/claude-3.5-sonnet")

    settings = Settings()

    assert settings.openrouter_api_key == "router-key"
    assert settings.openrouter_model == "anthropic/claude-3.5-sonnet"
