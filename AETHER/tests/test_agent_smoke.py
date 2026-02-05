from aether.agent import default_agent_from_env


def test_calc_tool_path():
    agent = default_agent_from_env()
    res = agent.run("calculate: 2*(3+4)")
    assert "14" in res.final


def test_note_tool_path(tmp_path, monkeypatch):
    monkeypatch.setenv("AETHER_WORKSPACE", str(tmp_path))
    agent = default_agent_from_env()
    res = agent.run("note: hello")
    assert "Saved note" in res.final
    assert (tmp_path / "notes.txt").exists()
