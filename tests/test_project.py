from pm_kit.project import find_project_dir, load_project

import pytest


def test_load_project(tmp_path):
    (tmp_path / "project.yaml").write_text(
        'name: "test"\ndescription: "a test project"\n'
    )
    config = load_project(tmp_path)
    assert config["name"] == "test"
    assert config["description"] == "a test project"


def test_find_project_dir(tmp_path, monkeypatch):
    (tmp_path / "project.yaml").write_text("name: test\n")
    child = tmp_path / "sub" / "deep"
    child.mkdir(parents=True)
    monkeypatch.chdir(child)

    result = find_project_dir()
    assert result == tmp_path


def test_find_project_dir_not_found(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    with pytest.raises(FileNotFoundError):
        find_project_dir()
