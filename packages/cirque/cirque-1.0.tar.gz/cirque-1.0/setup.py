# Copyright (c) 2023-2024 Quantum Interface (quantuminterface@ipe.kit.edu)
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
from setuptools import setup

import site
import sys

# With python 3.6, installing editable fails when installing to user-site
if sys.version_info <= (3, 7):
    site.ENABLE_USER_SITE = "--user" in sys.argv[1:]


if __name__ == "__main__":
    setup()
