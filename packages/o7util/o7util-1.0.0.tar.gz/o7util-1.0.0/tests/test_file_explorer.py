import unittest
from unittest.mock import patch
import o7util.file_explorer as o7fe

# coverage run -m unittest -v tests.console.test_file_explorer && coverage html


class FileExplorer(unittest.TestCase):
    # ---------------------------------------------------------------------------------------------
    #
    # ---------------------------------------------------------------------------------------------
    # https://stackoverflow.com/questions/21046717/python-mocking-raw-input-in-unittests
    # https://docs.python.org/3/library/unittest.mock.html
    #
    @patch("builtins.print")
    @patch("builtins.input", return_value="b")
    def test_Select_Back(self, *args, **kwargs):
        the_fe = o7fe.FileExplorer(cwd=".").select_file()

    @patch("builtins.print")
    @patch("builtins.input", return_value="b")
    def test_With_Filter(self, mockInput, mockPrint):
        the_fe = o7fe.FileExplorer(cwd=".").select_file(filters={"extensions": [".py"]})

    @patch("builtins.print")
    @patch("builtins.input")
    def test_menu_options(self, mockInput, mockPrint):
        mockInput.side_effect = ["p", "r", "b"]
        theFE = o7fe.FileExplorer(cwd=".").select_file(filters={"extensions": [".py"]})

    @patch("builtins.print")
    @patch("builtins.input")
    def test_menu_select_dir(self, mockInput, mockPrint):
        mockInput.side_effect = ["1", "b"]
        theFE = o7fe.FileExplorer(cwd=".").select_file(filters={"extensions": [".py"]})

    @patch("builtins.print")
    @patch("builtins.input")
    def test_menu_filter_no_est(self, mockInput, mockPrint):
        mockInput.side_effect = ["1", "b"]
        theFE = o7fe.FileExplorer(cwd=".").select_file(filters={"other": [".py"]})

    @patch("builtins.print")
    @patch("builtins.input")
    def test_menu_select_file(self, mockInput, mockPrint):
        theFE = o7fe.FileExplorer(cwd=".")
        theList = theFE.scan_directory()

        mockInput.side_effect = [str(len(theList)), "b"]
        theFE.select_file()


if __name__ == "__main__":
    unittest.main()
