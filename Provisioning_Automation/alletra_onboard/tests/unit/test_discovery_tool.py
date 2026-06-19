from alletra_onboard.adapters.system.discovery_tool import _search_dirs, find_discovery_tool


def test_explicit_path_wins(tmp_path, monkeypatch):
    exe = tmp_path / "HPE Discovery Tool-1.1.1.33.exe"
    exe.write_text("")
    monkeypatch.setenv("DISCOVERY_TOOL_PATH", str(exe))
    assert find_discovery_tool() == exe


def test_globs_desktop_and_ignores_sha256(tmp_path, monkeypatch):
    desktop = tmp_path / "Desktop"
    desktop.mkdir()
    exe = desktop / "HPE Discovery Tool-1.1.1.33.exe"
    exe.write_text("")
    (desktop / "HPE Discovery Tool-1.1.1.33.exe.sha256").write_text("")  # must be ignored
    monkeypatch.delenv("DISCOVERY_TOOL_PATH", raising=False)
    monkeypatch.setenv("DISCOVERY_TOOL_DIR", str(desktop))  # scan our temp desktop first
    found = find_discovery_tool()
    assert found == exe


def test_search_dirs_priority_and_dedup(tmp_path, monkeypatch):
    monkeypatch.setenv("DISCOVERY_TOOL_DIR", str(tmp_path / "tool"))
    monkeypatch.setenv("USERPROFILE", str(tmp_path / "user"))
    monkeypatch.setenv("PUBLIC", str(tmp_path / "user"))  # same Desktop -> must de-dup
    dirs = [str(d) for d in _search_dirs()]
    assert dirs[0] == str(tmp_path / "tool")  # explicit override is searched first
    assert dirs.count(str(tmp_path / "user" / "Desktop")) == 1  # de-duplicated
