import pytest

from alletra_onboard.config import Settings


@pytest.fixture(autouse=True)
def _isolate_settings_from_dotenv(monkeypatch):
    """Keep unit tests deterministic regardless of a local operator .env.

    The CLI reads GreenLake credentials from a .env in the working directory. That file
    must not leak into tests that assert on missing/explicit credentials, so disable
    .env loading and clear any GL_* process env for the duration of each test.
    """
    monkeypatch.setitem(Settings.model_config, "env_file", None)
    for key in (
        "GL_CLIENT_ID",
        "GL_CLIENT_SECRET",
        "GL_MEMBER_WORKSPACE_ID",
        "GL_TOKEN_URL",
        "GL_BASE_URL",
    ):
        monkeypatch.delenv(key, raising=False)
