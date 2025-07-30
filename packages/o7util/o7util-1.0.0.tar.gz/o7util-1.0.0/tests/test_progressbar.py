import o7util.progressbar

# coverage run -m unittest -v tests.test_progressbar && coverage report && coverage html


def test_basic():
    bar = o7util.progressbar.ProgressBar()
    bar.kick()
    bar.kick(inc=0)


def test_main(mocker):
    """Test main function"""

    mocker.patch.object(o7util.progressbar, "__name__", new="__main__")
    o7util.progressbar.main()
