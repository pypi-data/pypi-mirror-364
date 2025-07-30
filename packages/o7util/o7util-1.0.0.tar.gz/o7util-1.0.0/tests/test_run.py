import os

import o7util.run as o7r

# coverage run -m unittest -v tests.test_run && coverage report && coverage html


def test_No_Timeout():
    test = o7r.run("sleep 0.5")
    assert test[0] == 0


def test_Timeout_NotExpired():
    test = o7r.run("sleep 0.5", timeout=2)
    assert test[0] == 0


def test_Timeout_Expired():
    test = o7r.run("sleep 1", timeout=1)
    assert test[0] == -9


def test_NotExistingFile():
    test = o7r.run("./cdkhceiukhui.shs", timeout=1)
    assert test[0] != 0


# def test_timeout_expired_on_nt(self):
#     os.name = 'nt'
#     with patch('subprocess.run') as mock:
#         mock.return_value = None
#         test = o7r.run('sleep 2', shell = True, timeout = 1)
#     self.assertEqual(test[0], -9)


def test_get_process_children():
    test = o7r.get_process_children(os.getpid())
    assert isinstance(test, list)


def test_main(mocker):
    """Test main function"""

    mocker.patch.object(o7r, "__name__", new="__main__")
    o7r.main()
