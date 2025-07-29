#!/usr/bin/env python3

# gitlab-sardinecake-executor - run GitLab-CI jobs within libvirt VMs
#
# Copyright © 2024, IOhannes m zmölnig, forum::für::umläute
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU Affero General Public License as
#  published by the Free Software Foundation, either version 3 of the
#  License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU Affero General Public License for more details.
#
#  You should have received a copy of the GNU Affero General Public License
#  along with this program.  If not, see <http://www.gnu.org/licenses/>.

_name = "sardinecake.defaults"
_version = None

import logging

from .namespace import Namespace

try:
    from ._version import version as _version
except ImportError:
    pass

log = logging.getLogger(_name)

sarde = Namespace(
    oci_path="./oci",
    vmdisk_path="./",
)

executor = Namespace(
    username="vagrant",
    password="vagrant",
    timeout=30,
    verbosity=0,
)


BUILD_FAILURE = 1
SYSTEM_FAILURE = 2


def _main():
    logging.basicConfig()


if __name__ == "__main__":
    _main()
