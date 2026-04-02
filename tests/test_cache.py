import time

from restful.auth.cache import TokenCache


def test_save_and_load(tmp_path):
    cache = TokenCache(path=tmp_path / "cache.json")
    cache.save("https://test", "tok-abc", int(time.time()) + 3600)
    assert cache.load("https://test") == "tok-abc"


def test_load_expired(tmp_path):
    cache = TokenCache(path=tmp_path / "cache.json", skew_s=60)
    cache.save("https://test", "tok-old", int(time.time()) - 10)
    assert cache.load("https://test") is None


def test_load_missing_key(tmp_path):
    cache = TokenCache(path=tmp_path / "cache.json")
    assert cache.load("https://unknown") is None


def test_multiple_keys(tmp_path):
    cache = TokenCache(path=tmp_path / "cache.json")
    cache.save("https://vm1", "tok-1", int(time.time()) + 3600)
    cache.save("https://vm2", "tok-2", int(time.time()) + 3600)
    assert cache.load("https://vm1") == "tok-1"
    assert cache.load("https://vm2") == "tok-2"


def test_file_permissions(tmp_path):
    import os

    cache = TokenCache(path=tmp_path / "cache.json")
    cache.save("https://test", "tok", int(time.time()) + 3600)
    mode = os.stat(cache.path).st_mode & 0o777
    assert mode == 0o600
