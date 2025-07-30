import pandas as pd

import o7util.pandas


def test_to_from_excel():
    dfs = {
        "array1": pd.DataFrame({"a": [1, 2, 3], "b": [4, 5, 6]}),
        "array2": pd.DataFrame({"c": [7, 8, 9], "d": [10, 11, 12]}),
        "array3": pd.DataFrame({"a": [1, 2, 3], "b": [4, 5, 6], "c": [7, 8, 9], "d": [10, 11, 12]}),
    }

    dfs["array2"].set_index("c", inplace=True)
    dfs["array3"].set_index(["a", "b"], inplace=True)

    o7util.pandas.dfs_to_excel(dfs, "./cache/test.xlsx")

    new_dfs = o7util.pandas.dfs_from_excel("./cache/test.xlsx")

    # print(new_dfs)

    assert len(new_dfs.keys()) == len(dfs.keys())

    assert new_dfs["array1"].equals(dfs["array1"])
    assert new_dfs["array2"].equals(dfs["array2"])
    assert new_dfs["array3"].equals(dfs["array3"])


def test_cities():
    """Test with a DataFrame with a MultiIndex"""

    df = pd.DataFrame(
        [
            {"city": "Toronto", "province": "Ontario", "country": "Canada"},
            {"city": "Ottawa", "province": "Ontario", "country": "Canada"},
            {"city": "Montreal", "province": "Quebec", "country": "Canada"},
            {"city": "Quebec", "province": "Quebec", "country": "Canada"},
            {"city": "New York", "province": "New York", "country": "USA"},
            {"city": "Los Angeles", "province": "California", "country": "USA"},
        ]
    )
    df.set_index(["country", "province"], inplace=True)

    dfs = {"cities": df}

    o7util.pandas.dfs_to_excel(dfs, "./cache/test_cities.xlsx")

    new_dfs = o7util.pandas.dfs_from_excel("./cache/test_cities.xlsx")

    print(new_dfs)

    assert len(new_dfs.keys()) == len(dfs.keys())
    assert new_dfs["cities"].equals(dfs["cities"])
