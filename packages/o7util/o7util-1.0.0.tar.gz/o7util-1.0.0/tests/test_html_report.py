import unittest
import datetime
from unittest.mock import patch

import o7util.html_report as o7hr

# coverage run -m unittest -v tests.o7_util.test_html_report && coverage report && coverage html


class Test_Basic(unittest.TestCase):
    # *************************************************
    #
    # *************************************************
    def test_none(self):
        table = o7hr.HtmlReport()
        self.assertIsInstance(table, o7hr.HtmlReport)

    # *************************************************
    #
    # #*************************************************
    def test_basic(self):
        the_obj = o7hr.HtmlReport()

        the_obj.add_section(title="Section 1", html="<b>Section 1 HTML</b>")
        the_html = the_obj.generate()


if __name__ == "__main__":
    unittest.main()
