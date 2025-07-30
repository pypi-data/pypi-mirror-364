import unittest
from unittest.mock import patch
import o7util.input as o7i

# coverage run -m unittest -v tests.test_input && coverage report && coverage html


class InputDecorator(unittest.TestCase):
    def test_with_2_params(self):
        def test_function(param1, param2):
            return param1, param2

        obj = o7i._InputDecorator(function=test_function)


class TestInput_IsItOk(unittest.TestCase):
    @patch("builtins.input", return_value="y")
    def test_IsItOk_y(self, input):
        ret = o7i.is_it_ok()
        self.assertEqual(ret, True)

    @patch("builtins.input", return_value="n")
    def test_IsItOk_n(self, input):
        ret = o7i.is_it_ok()
        self.assertEqual(ret, False)

    @patch("builtins.input", return_value="n")
    def test_question_none(self, input):
        ret = o7i.is_it_ok(question="Are you sure !!!")
        self.assertEqual(ret, False)

    @patch("builtins.input")
    def test_invalid_answer(self, input):
        input.side_effect = ["w", "n"]
        ret = o7i.is_it_ok(question=None, color=None)
        self.assertEqual(ret, False)


class TestInputWait(unittest.TestCase):
    @patch("builtins.input", return_value="y")
    def test_wait(self, input):
        o7i.wait_input()


class TestInput_InputInt(unittest.TestCase):
    @patch("builtins.input", return_value="1")
    def test_1(self, input):
        ret = o7i.input_int()
        self.assertEqual(ret, 1)

    @patch("builtins.input", return_value="22")
    def test_22(self, input):
        ret = o7i.input_int()
        self.assertEqual(ret, 22)

    @patch("builtins.print")
    @patch("builtins.input", return_value="n")
    def test_n(self, input, print):
        ret = o7i.input_int()
        self.assertEqual(ret, None)


class TestInput_InputString(unittest.TestCase):
    @patch("builtins.input", return_value="1")
    def test_1(self, input):
        ret = o7i.input_string()
        self.assertEqual(ret, "1")

    @patch("builtins.input", return_value="abc")
    def test_abc(self, input):
        ret = o7i.input_string()
        self.assertEqual(ret, "abc")

    @patch("builtins.input", return_value=ValueError())
    def test_error(self, input):
        ret = o7i.input_string()
        self.assertEqual(ret, "")


class TestInput_InputMulti(unittest.TestCase):
    @patch("builtins.input", return_value="1")
    def test_1(self, input):
        ret = o7i.input_multi()
        self.assertIsInstance(ret, int)
        self.assertEqual(ret, 1)

    @patch("builtins.input", return_value="abc")
    def test_abc(self, input):
        ret = o7i.input_multi()
        self.assertIsInstance(ret, str)
        self.assertEqual(ret, "abc")


if __name__ == "__main__":
    unittest.main()
