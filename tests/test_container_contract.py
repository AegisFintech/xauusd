from pathlib import Path


def test_docker_context_excludes_secrets_data_and_generated_files():
    ignored = Path(".dockerignore").read_text().splitlines()
    required = {".env", ".venv", "data", "reports", "logs", "backups", ".ssh", ".postgresql", "*.key", "*.pem", "*.crt", "**/__pycache__"}
    assert required.issubset(set(ignored))


def test_runtime_image_is_non_root_and_does_not_copy_the_repository_wholesale():
    source = Path("Dockerfile").read_text()
    assert "USER xauusd" in source
    assert "COPY . ." not in source
    assert "COPY xauusd ./xauusd" in source
    assert "python:3.12.11-slim-bookworm" in source


def test_compose_does_not_inject_full_env_and_uses_read_only_sandbox():
    source = Path("docker-compose.yml").read_text()
    assert "env_file:" not in source
    assert "DATABASE_URL:" in source and "DASHBOARD_USERNAME:" in source and "DASHBOARD_PASSWORD:" in source
    assert "read_only: true" in source and "no-new-privileges:true" in source
    assert "cap_drop:" in source and "127.0.0.1:${PORT:-8080}:8080" in source
    assert "./data:/app/data" in source and "./reports:/app/reports:ro" in source
