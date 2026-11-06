from alletra_onboard.domain.policies import redact


def test_redacts_bearer_token():
    assert redact("Authorization: Bearer abc.def") == "Authorization: Bearer <redacted>"
