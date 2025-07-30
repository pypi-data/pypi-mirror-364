import logging

import o7util.pypi as o7pp


def test_basic():
    obj = o7pp.Pypi()
    version = obj.get_latest_version()
    assert isinstance(version, str)

    project = obj.get_project_name()
    assert isinstance(project, str)
    assert project == "o7cli"


def test_invalid(caplog):
    obj = o7pp.Pypi(project="o7cli-invalid-ahshr")

    with caplog.at_level(logging.ERROR):
        version = obj.get_latest_version()
        assert version is None
        assert "Failed to get latest version number" in caplog.text

    project = obj.get_project_name()
    assert isinstance(project, str)
    assert project == "o7cli-invalid-ahshr"


def test_main(mocker):
    """Test main function"""

    mocker.patch.object(o7pp, "__name__", new="__main__")
    o7pp.main()
