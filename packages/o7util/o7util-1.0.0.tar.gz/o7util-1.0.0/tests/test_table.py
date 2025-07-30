import datetime
import unittest
from unittest.mock import patch

import o7util.table as o7t

# coverage run -m unittest -v tests.test_table && coverage report && coverage html


class Test_Basic(unittest.TestCase):
    # *************************************************
    #
    # *************************************************
    def test_none(self):
        table = o7t.Table()
        self.assertIsInstance(table, o7t.Table)

    # *************************************************
    #
    # #*************************************************
    def test_basic(self):
        param = o7t.TableParam(
            title="Cloudformation Stacks for region: ca-central-1",
            columns=[
                o7t.ColumnParam(title="id", type="i"),
                o7t.ColumnParam(title="Name", type="str", min_width=40, data_col="StackName"),
                o7t.ColumnParam(
                    title="Creation",
                    type="date",
                    max_width=10,
                    data_col="CreationTime",
                    format="%Y-%m-%d",
                ),
                o7t.ColumnParam(title="Updated", type="since", data_col="UpdateTime"),
                o7t.ColumnParam(
                    title="Status",
                    type="str",
                    fix_width=15,
                    data_col="StackStatus",
                    format="aws-status",
                ),
                o7t.ColumnParam(
                    title="Alert",
                    type="str",
                    data_col="Alert",
                    alarm=True,
                    normal=False,
                ),
            ],
        )
        datas = [
            {
                "StackName": "first-stack",
                "CreationTime": datetime.datetime(2021, 8, 23),
                "UpdateTime": datetime.datetime(2021, 8, 24),
                "StackStatus": "COMPLETE",
                "Alert": True,
            },
            {
                "StackName": "second-stack",
                "CreationTime": datetime.datetime(2021, 8, 23),
                "UpdateTime": datetime.datetime(2021, 10, 24),
                "StackStatus": "UPDATING",
                "Alert": False,
            },
        ]

        table = o7t.Table(param=param)
        self.assertIsInstance(table, o7t.Table)
        self.assertEqual(table.param.title, "Cloudformation Stacks for region: ca-central-1")
        self.assertEqual(len(table.param.columns), 6)
        self.assertEqual(len(table.raw_datas), 0)
        self.assertIsNone(table.process_datas)

        table.update_data(datas)
        self.assertEqual(len(table.param.columns), 6)
        self.assertEqual(len(table.raw_datas), 2)

        with patch("builtins.print") as printMock:
            table.print()

        self.assertEqual(len(table.process_datas), 2)

        html = table.generate_html()

    # *************************************************
    #
    # #*************************************************
    def test_too_large(self):
        param = o7t.TableParam(
            with_footer=False,
            columns=[
                o7t.ColumnParam(title="id", type="i"),
                o7t.ColumnParam(title="Name", type="str", fix_width=1000, data_col="StackName"),
                o7t.ColumnParam(
                    title="Creation",
                    type="date",
                    max_width=10,
                    data_col="CreationTime",
                    format="%Y-%m-%d",
                ),
                o7t.ColumnParam(title="Updated", type="since", data_col="UpdateTime", sort="des"),
                o7t.ColumnParam(
                    title="Status",
                    type="str",
                    fix_width=15,
                    data_col="StackStatus",
                    format="aws-status",
                ),
                o7t.ColumnParam(
                    title="Alert",
                    type="str",
                    data_col="Alert",
                    alarm=True,
                    normal=False,
                ),
            ],
        )
        datas = [
            {
                "StackName": "first-stack",
                "CreationTime": datetime.datetime(2021, 8, 23),
                "UpdateTime": datetime.datetime(2021, 8, 24),
                "StackStatus": "COMPLETE",
                "Alert": True,
            },
            {
                "StackName": "second-stack",
                "CreationTime": datetime.datetime(2021, 8, 23),
                "UpdateTime": datetime.datetime(2021, 10, 24),
                "StackStatus": "UPDATING",
                "Alert": False,
            },
        ]

        table = o7t.Table(param=param, datas=datas)
        with patch("builtins.print") as printMock:
            table.print()

        html = table.generate_html()

    # *************************************************
    #
    # #*************************************************
    def test_print_with_data(self):
        param = o7t.TableParam(
            with_group=True,
            with_header=False,
            columns=[
                o7t.ColumnParam(title="id", type="i"),
                o7t.ColumnParam(
                    title="Creation",
                    type="date",
                    max_width=10,
                    data_col="CreationTime",
                    format="%Y-%m-%d",
                ),
                o7t.ColumnParam(title="Updated", type="since", data_col="UpdateTime", sort="des"),
                o7t.ColumnParam(
                    title="Status",
                    type="str",
                    fix_width=15,
                    data_col="StackStatus",
                    format="aws-status",
                ),
                o7t.ColumnParam(
                    title="Alert",
                    type="str",
                    data_col="Alert",
                    alarm=True,
                    normal=False,
                ),
                o7t.ColumnParam(
                    title="FooterSum",
                    type="float",
                    data_col="AverageCpu",
                    footer="sum",
                    group="footer",
                ),
                o7t.ColumnParam(
                    title="FooterAvr",
                    type="float",
                    data_col="AverageCpu",
                    footer="avg",
                    group="footer",
                ),
                o7t.ColumnParam(
                    title="FooterMax",
                    type="float",
                    data_col="AverageCpu",
                    footer="max",
                    group="footer",
                ),
                o7t.ColumnParam(
                    title="FooterMin",
                    type="float",
                    data_col="AverageCpu",
                    footer="min",
                    group="footer",
                ),
                o7t.ColumnParam(
                    title="FooterCount",
                    type="float",
                    data_col="AverageCpu",
                    footer="count",
                ),
            ],
        )
        datas = [
            {
                "StackName": "first-stack",
                "CreationTime": datetime.datetime(2021, 8, 23),
                "UpdateTime": datetime.datetime(2021, 8, 24),
                "StackStatus": "COMPLETE",
                "Alert": True,
                "AverageCpu": 10.4,
            },
            {
                "StackName": "second-stack",
                "CreationTime": datetime.datetime(2021, 8, 23),
                "UpdateTime": datetime.datetime(2021, 10, 24),
                "StackStatus": "UPDATING",
                "Alert": False,
                "AverageCpu": 30.4,
            },
        ]

        table = o7t.Table(param=param)
        with patch("builtins.print") as printMock:
            table.print(datas=datas)
            table.print()

        table.process_datas = None
        html = table.generate_html(datas=datas)


class DataClass(unittest.TestCase):
    def test_types(self):
        data = o7t.Data(raw=10.4, column_param=o7t.ColumnParam(type="int"))
        self.assertEqual(data.txt, "10")

        data = o7t.Data(raw=10.4, column_param=o7t.ColumnParam(type="float"))
        self.assertEqual(data.txt, "10.4")

    def test_critical(self):
        data = o7t.Data(raw=10.4, column_param=o7t.ColumnParam(type="float", critical_hi=12.0))
        self.assertEqual(data.is_critical, False)
        self.assertEqual(data.txt, "10.4")

        data = o7t.Data(raw=10.4, column_param=o7t.ColumnParam(type="float", critical_hi=5.0))
        self.assertEqual(data.is_critical, True)
        self.assertEqual(data.txt, "10.4")

        txt = data.get_terminal_txt()
        txt, style = data.get_html_txt()

    def test_alarms(self):
        data = o7t.Data(raw=10.4, column_param=o7t.ColumnParam(type="float", alarm_hi=12.0))
        self.assertEqual(data.is_alarm, False)
        self.assertEqual(data.txt, "10.4")

        data = o7t.Data(raw=10.4, column_param=o7t.ColumnParam(type="float", alarm_hi=5.0))
        self.assertEqual(data.is_alarm, True)
        self.assertEqual(data.txt, "10.4")

        data = o7t.Data(
            raw=10.4,
            column_param=o7t.ColumnParam(type="float", alarm_lo=20.0, term_width=10),
        )
        self.assertEqual(data.is_alarm, True)
        self.assertEqual(data.txt, "10.4")

        txt = data.get_terminal_txt()
        txt, style = data.get_html_txt()

    def test_warnings(self):
        data = o7t.Data(
            raw=10.4,
            column_param=o7t.ColumnParam(type="float", warning_hi=12.0, term_width=10),
        )
        self.assertEqual(data.is_warning, False)
        self.assertEqual(data.txt, "10.4")

        data = o7t.Data(raw=10.4, column_param=o7t.ColumnParam(type="float", warning_hi=5.0))
        self.assertEqual(data.is_warning, True)
        self.assertEqual(data.txt, "10.4")

        data = o7t.Data(
            raw=10.4,
            column_param=o7t.ColumnParam(type="float", warning_lo=20.0, term_width=10),
        )
        self.assertEqual(data.is_warning, True)
        self.assertEqual(data.txt, "10.4")

        txt = data.get_terminal_txt()
        txt, style = data.get_html_txt()

    def test_low(self):
        data = o7t.Data(raw=10.4, column_param=o7t.ColumnParam(type="float", low_hi=12.0))
        self.assertEqual(data.is_low, False)
        self.assertEqual(data.txt, "10.4")

        data = o7t.Data(raw=10.4, column_param=o7t.ColumnParam(type="float", low_hi=5.0))
        self.assertEqual(data.is_low, True)
        self.assertEqual(data.txt, "10.4")

        txt = data.get_terminal_txt()
        txt, style = data.get_html_txt()

    def test_format(self):
        data = o7t.Data(raw=10.4, column_param=o7t.ColumnParam(type=None))
        self.assertEqual(data.txt, "")

        data = o7t.Data(
            raw=datetime.datetime(year=2023, month=4, day=4),
            column_param=o7t.ColumnParam(type="datetime"),
        )
        self.assertEqual(data.txt, "2023-04-04 00:00:00")

        data = o7t.Data(raw=1024, column_param=o7t.ColumnParam(type="bytes"))
        self.assertEqual(data.txt, "1.0 KB")

        data = o7t.Data(raw=0.999, column_param=o7t.ColumnParam(type="percent"))
        self.assertEqual(data.txt, "99.9 %")

    def test_terminal_txt(self):
        data = o7t.Data(
            raw="DRIFTED",
            column_param=o7t.ColumnParam(type="str", format="aws-drift", term_width=10),
        )
        txt = data.get_terminal_txt()
        self.assertEqual(txt, "\x1b[91mDRIFTED   \x1b[0m")

        data = o7t.Data(
            raw="remove",
            column_param=o7t.ColumnParam(type="str", format="aws-edit", term_width=10),
        )
        txt = data.get_terminal_txt()
        self.assertEqual(txt, "\x1b[96m\x1b[91mremove    \x1b[0m\x1b[0m")

        data = o7t.Data(
            raw="running",
            column_param=o7t.ColumnParam(type="str", format="aws-state", term_width=10),
        )
        txt = data.get_terminal_txt()
        self.assertEqual(txt, "\x1b[92mrunning   \x1b[0m")

        data = o7t.Data(
            raw="ok",
            column_param=o7t.ColumnParam(type="str", normal="ok", term_width=10),
        )
        txt = data.get_terminal_txt()
        self.assertEqual(txt, "\x1b[92mok        \x1b[39m")


if __name__ == "__main__":
    unittest.main()
