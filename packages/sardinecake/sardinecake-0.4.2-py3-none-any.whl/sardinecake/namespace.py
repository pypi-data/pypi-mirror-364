#!/usr/bin/env python3

"""
data-storage that provides both attribute- and dict-like access
"""

# sardinecake - run GitLab-CI jobs within libvirt VMs
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


class Namespace:
    """
    A data storage that provides both attribute- and dict-like access.

    """

    def __init__(self, **kwargs):
        self._dict = kwargs
        self.items = self._dict.items
        self.keys = self._dict.keys
        self.values = self._dict.values
        self.get = self._dict.get

    def __repr__(self):
        typename = type(self).__name__
        args = ", ".join(f"{k}: {v!r}" for k, v in self._dict.items())
        return f"{typename}({args})"

    def __len__(self):
        return self._dict.__len__()

    def __iter__(self):
        return self._dict.__iter__()

    def __getitem__(self, x):
        return self.get(x)

    def __getattr__(self, x):
        return self.get(x)

    def __contains__(self, x):
        return self._dict.__contains__(x)

    def __hasattr__(self, x):
        return self._dict.__contains__(x)

    def setdefaults(self, defaults: dict):
        """Insert each key with a value of defaults, if the key is not in the Namespace.

        Return the (updated) Namespace object.
        """
        for k, v in defaults.items():
            self._dict.setdefault(k, v)
        return self


if __name__ == "__main__":
    ns = Namespace(foo=12, bar="pizza")
    print(ns)

    def check(key, value, attrvalue):
        """assert"""
        if ns[key] != value:
            raise AssertionError(f"ns[{key!r}]={ns[key]!r} != {value!r}")
        if value != attrvalue:
            raise AssertionError(f"ns.{key}={attrvalue} != {value!r}")

    check("foo", 12, ns.foo)
    check("bar", "pizza", ns.bar)
    check("nada", None, ns.nada)
