import unittest

import o7util.color

# coverage run -m unittest -v tests.o7util.test_color && coverage report && coverage html


class test_color(unittest.TestCase):
    def test_dec_to_hex(self):
        color = o7util.color.dec_to_hex(1, 1, 1)
        self.assertEqual(color, "#ffffff")

        color = o7util.color.dec_to_hex(0, 0, 0)
        self.assertEqual(color, "#000000")

        color = o7util.color.dec_to_hex(0.25, 0.5, 75)
        self.assertEqual(color, "#3f7f4ab5")

    def test_scale_b_to_r_to_y(self):
        color = o7util.color.scale_b_to_r_to_y(0, 0, 10)
        self.assertEqual(color, "#00ffff")

        color = o7util.color.scale_b_to_r_to_y(0, 0, 0)
        self.assertEqual(color, "#ff00ff")

    def test_scale_red_to_green(self):
        color = o7util.color.scale_red_to_green(0, 0, 10, 2)
        self.assertEqual(color, "#ff0000")

        color = o7util.color.scale_red_to_green(0, 0, 0, 2)
        self.assertEqual(color, "#ffff1fe")

    def test_scale_3_step(self):
        color = o7util.color.scale_3_step(val=5, min_val=7, mid_val=15, max_val=30)
        self.assertEqual(color, "#ffffff")

        color = o7util.color.scale_3_step(val=15, min_val=7, mid_val=15, max_val=30)
        self.assertEqual(color, "#00ff00")

        color = o7util.color.scale_3_step(val=30, min_val=7, mid_val=15, max_val=30)
        self.assertEqual(color, "#ff0000")

    def test_color_scale_tests(self):
        html = o7util.color.color_scale_tests()
        self.assertIn("</table>", html)


def test_main(mocker):
    """Test main function"""

    mocker.patch.object(o7util.color, "__name__", new="__main__")
    o7util.color.main()


if __name__ == "__main__":
    unittest.main()
