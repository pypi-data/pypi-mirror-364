# ************************************************************************
# Copyright 2023 O7 Conseils inc (Philippe Gosselin)
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

"""Package to information from Pypi"""

import json
import logging
import urllib.request

# import pprint

logger = logging.getLogger(__name__)


# *************************************************
#
# *************************************************
class Pypi:
    """Class to explore Pypi"""

    # *************************************************
    #
    # *************************************************
    def __init__(self, project="o7cli"):
        self.project = project

    # *************************************************
    #
    # *************************************************
    def get_project_name(self):
        """Stub to remove not enough method"""
        return self.project

    # *************************************************
    #
    # *************************************************
    def get_latest_version(self):
        """List all files in the current directory"""
        url = f"https://pypi.org/pypi/{self.project}/json"

        data = None
        try:
            with urllib.request.urlopen(url=url) as response:  # noqa: S310
                data = json.load(response)

        except urllib.error.HTTPError:
            data = None

        if data is None:
            logger.error("Failed to get latest version number")
            return None

        version = data.get("info", {}).get("version", None)
        return version


# *************************************************
# To Test Class
# *************************************************
def main():
    """Main function to test the class"""
    if __name__ == "__main__":
        the_pypi = Pypi()
        the_version = the_pypi.get_latest_version()
        print(f"{the_version=}")


main()
