import pytest

from app.config import _parse_origins, load_settings


def test_parse_origins_defaults_to_wildcard():
    assert _parse_origins(None) == ["*"]
    assert _parse_origins("") == ["*"]


def test_parse_origins_trims_and_splits_values():
    assert _parse_origins("https://a.example, https://b.example ") == [
        "https://a.example",
        "https://b.example",
    ]


def test_development_allows_default_cors(monkeypatch):
    monkeypatch.delenv("APP_ENV", raising=False)
    monkeypatch.delenv("CORS_ORIGINS", raising=False)

    settings = load_settings()

    assert settings.app_env == "development"
    assert settings.cors_origins == ["*"]


def test_production_requires_explicit_cors(monkeypatch):
    monkeypatch.setenv("APP_ENV", "production")
    monkeypatch.delenv("CORS_ORIGINS", raising=False)

    with pytest.raises(RuntimeError, match="CORS_ORIGINS"):
        load_settings()


def test_production_accepts_explicit_cors(monkeypatch):
    monkeypatch.setenv("APP_ENV", "production")
    monkeypatch.setenv("CORS_ORIGINS", "https://synapse.example")

    settings = load_settings()

    assert settings.cors_origins == ["https://synapse.example"]
