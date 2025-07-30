#!/usr/bin/env python
# ************************************************************************
# Copyright 2024 O7 Conseils inc (Philippe Gosselin)
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# ************************************************************************
"""Package Pandas help function"""

import ast
import os

import pandas as pd


def dfs_to_excel(dfs: dict[pd.DataFrame], filename):
    """Save a dictionary of DataFrame to Excel"""

    # Ensure the directory exists
    directory = os.path.dirname(filename)
    if directory and not os.path.exists(directory):
        os.makedirs(directory)

    # pylint: disable=abstract-class-instantiated
    with pd.ExcelWriter(filename) as writer:
        index_infos = []
        for key, df in dfs.items():
            # Make sure the index has a name
            if df.index.name is None:
                df.index.name = "_"
            df.to_excel(writer, sheet_name=key)
            index_infos.append(df.index.names)

        # Save index information in extra sheet
        df_info = pd.DataFrame(
            {
                "key": list(dfs.keys()),
                "index": index_infos,
            }
        )
        df_info.to_excel(writer, sheet_name="_pandas_info_")

        print(f"File saved in: {filename}")


def dfs_from_excel(filename) -> dict[pd.DataFrame]:
    """Load a dictionary of DataFrame from Excel"""

    dfs = {}

    with pd.ExcelFile(filename) as reader:
        df_infos = reader.parse(sheet_name="_pandas_info_", index_col=0)
        df_infos = df_infos.set_index("key")

        for key in reader.sheet_names:
            if key == "_pandas_info_":
                continue

            index_info = ast.literal_eval(df_infos.loc[key, "index"])

            dfs[key] = reader.parse(sheet_name=key, index_col=None)

            # forward fill the index, to_excel does not save the index
            for index in index_info:
                dfs[key][index] = dfs[key][index].ffill()

            dfs[key] = dfs[key].set_index(index_info)

        print(f"File loaded from file: {filename}")

    return dfs
