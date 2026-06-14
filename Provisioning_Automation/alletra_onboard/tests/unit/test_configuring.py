from alletra_onboard.application.configuring import (
    masked_gl_credentials,
    read_env,
    set_env_values,
    update_gl_credentials,
)


def test_set_env_values_preserves_comments_and_other_keys(tmp_path):
    env = tmp_path / ".env"
    env.write_text("# my comment\nGL_CLIENT_ID=old\nOTHER=keepme\n\nGL_TOKEN_URL=oldurl\n", encoding="utf-8")
    set_env_values(env, {"GL_CLIENT_ID": "newid", "GL_TOKEN_URL": "newurl"})
    text = env.read_text(encoding="utf-8")
    assert "# my comment" in text
    assert "OTHER=keepme" in text
    assert read_env(env)["GL_CLIENT_ID"] == "newid"
    assert read_env(env)["GL_TOKEN_URL"] == "newurl"


def test_set_env_values_blank_keeps_existing(tmp_path):
    env = tmp_path / ".env"
    env.write_text("GL_CLIENT_SECRET=keepsecret\n", encoding="utf-8")
    set_env_values(env, {"GL_CLIENT_SECRET": "", "GL_CLIENT_ID": "id"})  # blank secret must not wipe it
    values = read_env(env)
    assert values["GL_CLIENT_SECRET"] == "keepsecret"
    assert values["GL_CLIENT_ID"] == "id"


def test_set_env_values_appends_new_keys(tmp_path):
    env = tmp_path / ".env"  # does not exist yet
    set_env_values(env, {"GL_CLIENT_ID": "id"})
    assert read_env(env)["GL_CLIENT_ID"] == "id"


def test_update_gl_credentials_masks_secret(tmp_path):
    env = tmp_path / ".env"
    update_gl_credentials(env, {"GL_CLIENT_ID": "id", "GL_CLIENT_SECRET": "sec", "GL_TOKEN_URL": "url"})
    masked = masked_gl_credentials(env)
    assert masked["GL_CLIENT_ID"] == "id"
    assert masked["GL_CLIENT_SECRET"] == "****"
    # the real secret is still in the file (just masked in the API view)
    assert read_env(env)["GL_CLIENT_SECRET"] == "sec"
