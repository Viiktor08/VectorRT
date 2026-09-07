from app.config import is_load_test_target_allowed, is_target_allowed


def test_whitelisted_target_is_allowed():
    assert is_target_allowed("10.10.10.10") is True


def test_ip_outside_whitelist_is_rejected():
    assert is_target_allowed("8.8.8.8") is False


def test_malformed_ip_is_rejected():
    assert is_target_allowed("not-an-ip") is False


def test_load_test_allowed_only_for_http_target():
    assert is_load_test_target_allowed("10.10.10.11") is True  # web-target
    assert is_load_test_target_allowed("10.10.10.10") is False  # ssh-target, sin HTTP
