import math
import datetime

import unittest
from unittest.mock import patch

import o7util.conversion

# coverage run -m unittest -v tests.test_conversion && coverage report && coverage html


class Test_Speed(unittest.TestCase):
    def test_ms_to_km(self):
        test = o7util.conversion.speed_ms_to_knot(1)
        self.assertEqual(test, 1.944)

    def test_ms_to_km_2(self):
        test = o7util.conversion.speed_ms_to_knot(3)
        self.assertEqual(test, 5.832)

    def test_uv_to_ws(self):
        test = o7util.conversion.speed_uv_to_ws(2, 2)
        self.assertEqual(test, math.sqrt(8))

    def test_uv_to_ws_2(self):
        test = o7util.conversion.speed_uv_to_ws(0, 2)
        self.assertEqual(test, 2)


class TestDirection(unittest.TestCase):
    def test_deg_to_txt_n(self):
        txt = o7util.conversion.direction_deg_to_txt(11)
        self.assertEqual(txt, "N")

    def test_deg_to_txt_nne(self):
        txt = o7util.conversion.direction_deg_to_txt(12)
        self.assertEqual(txt, "NNE")

        txt = o7util.conversion.direction_deg_to_txt(33)
        self.assertEqual(txt, "NNE")

    def test_deg_to_txt_ne(self):
        txt = o7util.conversion.direction_deg_to_txt(34)
        self.assertEqual(txt, "NE")

    def test_deg_to_txt_nno(self):
        txt = o7util.conversion.direction_deg_to_txt(348)
        self.assertEqual(txt, "NNO")

    def test_deg_to_txt_n2(self):
        txt = o7util.conversion.direction_deg_to_txt(349)
        self.assertEqual(txt, "N")
        txt = o7util.conversion.direction_deg_to_txt(360)
        self.assertEqual(txt, "N")

    def test_deg_to_txt_nan(self):
        txt = o7util.conversion.direction_deg_to_txt(float("nan"))
        self.assertEqual(txt, "")

    def test_uv_to_n(self):
        deg = o7util.conversion.direction_uv_to_deg(0, -1)
        self.assertEqual(deg, 0)

    def test_uv_to_ne(self):
        deg = o7util.conversion.direction_uv_to_deg(-1, -1)
        self.assertEqual(deg, 45)

    def test_uv_to_e(self):
        deg = o7util.conversion.direction_uv_to_deg(-1, 0)
        self.assertEqual(deg, 90)

    def test_uv_to_s(self):
        deg = o7util.conversion.direction_uv_to_deg(0, 1)
        self.assertEqual(deg, 180)

    def test_uv_to_w(self):
        deg = o7util.conversion.direction_uv_to_deg(1, 0)
        self.assertEqual(deg, 270)


class TestTodatetime(unittest.TestCase):
    def test_none(self):
        val = o7util.conversion.to_datetime(None)
        self.assertIsNone(val)

    def test_second(self):
        val = o7util.conversion.to_datetime(1636851600)
        self.assertIsInstance(val, datetime.datetime)
        self.assertEqual(val.year, 2021)

    def test_millisecond(self):
        val = o7util.conversion.to_datetime(1636851600000)
        self.assertIsInstance(val, datetime.datetime)
        self.assertEqual(val.year, 2021)

    def test_small_values(self):
        val = o7util.conversion.to_datetime(1)
        self.assertIsInstance(val, int)
        self.assertEqual(val, 1)


class to_elapse_senconds(unittest.TestCase):
    def test_none(self):
        val = o7util.conversion.to_elapse_senconds(None)
        self.assertIsNone(val)

    def test_int(self):
        val = o7util.conversion.to_elapse_senconds(10)
        self.assertIsInstance(val, float)
        self.assertEqual(val, 10.0)

    def test_float(self):
        val = o7util.conversion.to_elapse_senconds(101.1)
        self.assertIsInstance(val, float)
        self.assertEqual(val, 101.1)

    def test_string(self):
        val = o7util.conversion.to_elapse_senconds("12.3")
        self.assertIsInstance(val, float)
        self.assertEqual(val, 12.3)

    def test_datetime(self):
        val = o7util.conversion.to_elapse_senconds(datetime.datetime.now())
        self.assertIsInstance(val, float)

    def test_datetime_with_tz(self):
        dt = datetime.datetime(2016, 3, 13, 5, tzinfo=datetime.timezone.utc)
        val = o7util.conversion.to_elapse_senconds(dt)
        self.assertIsInstance(val, float)

    def test_timedelta(self):
        past = datetime.datetime.now() - datetime.timedelta(days=1)
        diff = datetime.datetime.now() - past
        val = o7util.conversion.to_elapse_senconds(diff)
        self.assertIsInstance(val, float)


class to_int(unittest.TestCase):
    def test_none(self):
        val = o7util.conversion.to_int(None)
        self.assertIsNone(val)

    def test_good(self):
        val = o7util.conversion.to_int("123")
        self.assertIsInstance(val, int)
        self.assertEqual(val, 123)

    def test_bad(self):
        val = o7util.conversion.to_int("ieduhde")
        self.assertIsNone(val)


class to_float(unittest.TestCase):
    # coverage run -m unittest -v tests.util.test_convert.to_float && coverage html

    def test_none(self):
        val = o7util.conversion.to_float(None)
        self.assertIsNone(val)

    def test_good(self):
        val = o7util.conversion.to_float("1.23")
        self.assertIsInstance(val, float)
        self.assertEqual(val, 1.23)

    def test_bad(self):
        val = o7util.conversion.to_float("ieduhde")
        self.assertIsNone(val)


if __name__ == "__main__":
    unittest.main()
