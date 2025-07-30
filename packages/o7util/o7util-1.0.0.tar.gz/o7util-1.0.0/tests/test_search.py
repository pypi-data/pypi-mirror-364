import unittest
import datetime
import o7util.search

# coverage run -m unittest -v tests.test_search && coverage report && coverage html


theData = {
    "name": "Ronald",
    "address": {"street": "1 Big Mac", "city": "Supersize"},
    "employee": '{"kitchen": 6, "front" : 2}',
}

data_bad_jason = {
    "name": "Ronald",
    "address": {"street": "1 Big Mac", "city": "Supersize"},
    "employee": '{"kitchen, "front" : 2}',
}


class Test_SearchValueInDict(unittest.TestCase):
    def test_none(self):
        result = o7util.search.value_in_dict("nothing", None)
        self.assertIsNone(result)

    def test_not_in_dict(self):
        result = o7util.search.value_in_dict("nothing", theData)
        self.assertIsNone(result)

    def test_direct(self):
        result = o7util.search.value_in_dict("name", theData)
        self.assertEqual(result, "Ronald")

    def test_indirect(self):
        result = o7util.search.value_in_dict("address.city", theData)
        self.assertEqual(result, "Supersize")

    def test_indirect_with_string_format(self):
        result = o7util.search.value_in_dict("employee.kitchen", theData)
        self.assertEqual(result, 6)

    def test_indirect_with_bad_json(self):
        result = o7util.search.value_in_dict("employee.kitchen", data_bad_jason)
        self.assertIsNone(result)


if __name__ == "__main__":
    unittest.main()
