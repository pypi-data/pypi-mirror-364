import unittest
import datetime
import o7util.format

# coverage run -m unittest -v tests.test_format && coverage report && coverage html


class Test_Datetime(unittest.TestCase):
    def test_datetime(self):
        dtTest = datetime.datetime(2021, 10, 7)
        result = o7util.format.to_datetime(dtTest)
        self.assertEqual(result, "2021-10-07 00:00:00")

    def test_datetime_format1(self):
        dtTest = datetime.datetime(2021, 10, 7)
        result = o7util.format.to_datetime(dtTest, "%Y")
        self.assertEqual(result, "2021")

    def test_timestamps(self):
        dtTest = 1000000000000
        result = o7util.format.to_datetime(dtTest)
        self.assertEqual(result, "2001-09-09 01:46:40")

    def test_none(self):
        result = o7util.format.to_datetime(None)
        self.assertEqual(result, "")

    def test_other(self):
        result = o7util.format.to_datetime("Blah")
        self.assertEqual(result, "")


class Test_ElapseTime(unittest.TestCase):
    def test_datetime(self):
        dtTest = datetime.datetime.now() - datetime.timedelta(days=5)
        result = o7util.format.elapse_time(dtTest)
        self.assertEqual(result, "5.0 day")

    def test_datetime_years(self):
        dtTest = datetime.datetime.now() - datetime.timedelta(days=366)
        result = o7util.format.elapse_time(dtTest)
        self.assertEqual(result, "1.0 yr")

    def test_datetime_tzaware(self):
        dtTest = datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(hours=13)
        result = o7util.format.elapse_time(dtTest)
        self.assertEqual(result, "13.0 hr")

    def test_timestamp(self):
        dtTest = datetime.datetime.now() - datetime.timedelta(days=8)
        result = o7util.format.elapse_time(dtTest.timestamp())
        self.assertEqual(result, "8.0 day")

    def test_duration(self):
        dtTest = datetime.datetime.now() - datetime.timedelta(days=55)
        duration = datetime.datetime.now() - dtTest
        result = o7util.format.elapse_time(duration)
        self.assertEqual(result, "55.0 day")

    def test_seconds_int(self):
        result = o7util.format.elapse_time(23)
        self.assertEqual(result, "23.0 sec")

    def test_seconds_txt(self):
        result = o7util.format.elapse_time("61")
        self.assertEqual(result, "1.0 min")

    def test_seconds_float(self):
        result = o7util.format.elapse_time(123.7)
        self.assertEqual(result, "2.1 min")

    def test_none(self):
        result = o7util.format.elapse_time(None)
        self.assertEqual(result, "")

    def test_other(self):
        result = o7util.format.elapse_time([])
        self.assertEqual(result, "NA")


class Test_Bytes(unittest.TestCase):
    def test_zero(self):
        result = o7util.format.to_bytes(0)
        self.assertEqual(result, "0.0 B")

    def test_none(self):
        result = o7util.format.to_bytes(None)
        self.assertEqual(result, "")

    def test_mega(self):
        result = o7util.format.to_bytes(1024 * 1024 * 2)
        self.assertEqual(result, "2.0 MB")

    def test_pega(self):
        result = o7util.format.to_bytes(1024 * 1024 * 2 * 1024 * 1024 * 1024)
        self.assertEqual(result, "2.0 PB")


def test_to_percent():
    assert o7util.format.to_percent(0.123456, decimals=2) == "12.35 %"

    assert o7util.format.to_percent(None) == ""

    assert o7util.format.to_percent("o7") == "o7"


if __name__ == "__main__":
    unittest.main()
