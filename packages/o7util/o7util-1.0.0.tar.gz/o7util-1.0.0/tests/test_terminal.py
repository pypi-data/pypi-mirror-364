import unittest
from unittest.mock import patch

import o7util.terminal as o7t

# coverage run -m unittest -v tests.o7util.test_terminal && coverage report && coverage html


class test_terminal(unittest.TestCase):
    def test_get_terminal(self):
        self.assertGreater(o7t.get_width(), 10)
        self.assertGreater(o7t.get_height(), 10)

    @patch("builtins.print")
    def test_print(self, mock):
        o7t.print_header("Title")
        o7t.console_line(left="left", center="center", right="right")
        o7t.console_title_line(left="left", center="center", right="right")
        o7t.clear()
        o7t.console_title(left="left", center="center", right="right")
        o7t.print_line()
        o7t.print_line(char="+", length=10)


class test_format(unittest.TestCase):
    def test_format(self):
        o7t.format_alarm("value")
        o7t.format_warning("value")
        o7t.format_normal("value")

    def test_format_aws_status(self):
        o7t.format_aws_status("STOP")
        o7t.format_aws_status("IN_PROGRESS")
        o7t.format_aws_status("COMPLETE")
        o7t.format_aws_status("SUPERSED")
        o7t.format_aws_status("PROGRESS")
        o7t.format_aws_status("OTHER")

    def test_format_aws_drift(self):
        o7t.format_aws_drift("DRIFTED")
        o7t.format_aws_drift("IN_SYNC")
        o7t.format_aws_drift("UNKNOWN")
        o7t.format_aws_drift("NOT_CHECKED")
        o7t.format_aws_drift("MODIFIED")
        o7t.format_aws_drift("OTHER")

    def test_format_aws_edit(self):
        o7t.format_aws_edit("remove")
        o7t.format_aws_edit("add")
        o7t.format_aws_edit("same")
        o7t.format_aws_edit("change")
        o7t.format_aws_edit("OTHER")

    def test_format_aws_state(self):
        o7t.format_aws_state("shutting-down")
        o7t.format_aws_state("running")
        o7t.format_aws_state("pending")
        o7t.format_aws_state("available")
        o7t.format_aws_state("stop")
        o7t.format_aws_state("other")


if __name__ == "__main__":
    unittest.main()
