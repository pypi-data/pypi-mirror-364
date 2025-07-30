import unittest
from unittest.mock import patch
import o7util.menu as o7m

# coverage run -m unittest -v tests.o7_util.test_menu && coverage report && coverage html


class General(unittest.TestCase):
    @patch("builtins.print")
    @patch("builtins.input")
    def test_normal_flow(self, input, *args):
        input.side_effect = ["x", "a", "b", "d", "e", "f", "x", "x"]

        the_menu = o7m.Menu(exit_option="x", title="Test Menu")

        the_menu.add_option(
            o7m.Option(
                key="a",
                name="Option A",
                callback=lambda: print("Option A"),
                short="A",
                wait=False,
            )
        )
        the_menu.add_option(
            o7m.Option(key="b", name="Option B", callback=lambda: print("Option B"))
        )
        the_menu.display_callback = lambda: print("Display Callback")

        the_menu.loop()

        the_menu.compact = True
        the_menu.loop()

    @patch("builtins.print")
    @patch("builtins.input")
    def test_with_int(self, input, *args):
        input.side_effect = [1, "x", "x"]

        the_menu = o7m.Menu(exit_option="x", title="Test Menu")

        the_menu.add_option(
            o7m.Option(key="a", name="Option A", callback=lambda: print("Option A"), short="A")
        )
        the_menu.add_option(
            o7m.Option(key="int", name="Option Int", callback=lambda x: print(f"Option {x}"))
        )

        the_menu.loop()

    @patch("builtins.print")
    @patch("builtins.input")
    def test_key_exception(self, input, *args):
        input.side_effect = [KeyboardInterrupt("Boom !")]
        the_menu = o7m.Menu(exit_option="b")

        with self.assertRaises(KeyboardInterrupt):
            the_menu.loop()

    @patch("builtins.print")
    @patch("builtins.input")
    def test_exception(self, input, *args):
        input.side_effect = [Exception("Boom Aain !"), "b", "b"]
        the_menu = o7m.Menu(exit_option="b")
        the_menu.loop()


class ProcessInput(unittest.TestCase):
    @patch("builtins.print")
    def test_int_str(self, *args):
        the_menu = o7m.Menu()
        ret = the_menu.process_input(key="int")
        self.assertEqual(ret, 2)


if __name__ == "__main__":
    unittest.main()
