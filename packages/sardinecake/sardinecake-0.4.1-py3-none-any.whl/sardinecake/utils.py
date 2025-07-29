#!/usr/bin/env python3

# sardinecake - manage VMs via OCI
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


# parts if this code are:
# Copyright (c) 2021 Peter Odding
#
# Permission is hereby granted, free of charge, to any person obtaining
# a copy of this software and associated documentation files (the
# "Software"), to deal in the Software without restriction, including
# without limitation the rights to use, copy, modify, merge, publish,
# distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so, subject to
# the following conditions:
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE
# LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
# OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION
# WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

import itertools
import json
import logging
import numbers
import os
import re

log = logging.getLogger("sardinecake.utils")

try:
    import magic

    def mimetype(filename: str) -> str | None:
        """guess the mimetype for a file (returns None if the filename cannot be guessed)"""
        try:
            import pathlib

            filename = pathlib.Path(filename).resolve()
        except:
            pass

        try:
            return magic.from_file(filename, mime=True)
        except OSError:
            return None

except ImportError:

    def mimetype(filename: str) -> str | None:
        """guess the mimetype for a file (returns None if the filename cannot be guessed)"""
        import subprocess

        try:
            p = subprocess.run(
                ["file", "-E", "-L", "--brief", "--mime-type", filename],
                stdout=subprocess.PIPE,
                check=True,
            )
            for line in p.stdout.splitlines():
                try:
                    # yikes, error messages go to stdout
                    if b" " in line:
                        continue
                    return line.decode()
                except:
                    continue
        except (OSError, subprocess.SubprocessError):
            return None
        return None


# © 2021, Peter Odding (expat)
# pilfered from https://github.com/xolox/python-humanfriendly/
def tokenize(text: str) -> list:
    """
    Tokenize a text into numbers and strings.

    :param text: The text to tokenize (a string).
    :returns: A list of strings and/or numbers.

    This function is used to implement robust tokenization of user input in
    functions like :func:`.parse_size()` and :func:`.parse_timespan()`. It
    automatically coerces integer and floating point numbers, ignores
    whitespace and knows how to separate numbers from strings even without
    whitespace. Some examples to make this more concrete:

    >>> from humanfriendly.text import tokenize
    >>> tokenize('42')
    [42]
    >>> tokenize('42MB')
    [42, 'MB']
    >>> tokenize('42.5MB')
    [42.5, 'MB']
    >>> tokenize('42.5 MB')
    [42.5, 'MB']
    """
    tokenized_input = []
    for token in re.split(r"(\d+(?:\.\d+)?)", text):
        token = token.strip()
        if re.match(r"\d+\.\d+", token):
            tokenized_input.append(float(token))
        elif token.isdigit():
            tokenized_input.append(int(token))
        elif token:
            tokenized_input.append(token)
    return tokenized_input


# © 2021, Peter Odding (expat)
# © 2024, IOhannes m zmölnig (AGPL)
# modified from https://github.com/xolox/python-humanfriendly/

size_units = {
    "k": 1024**1,
    "m": 1024**2,
    "g": 1024**3,
    "t": 1024**4,
    "p": 1024**5,
    "e": 1024**6,
    "z": 1024**7,
    "y": 1024**8,
    "kb": 1000**1,
    "mb": 1000**2,
    "gb": 1000**3,
    "tb": 1000**4,
    "pb": 1000**5,
    "eb": 1000**6,
    "zb": 1000**7,
    "yb": 1000**8,
    "kilobyte": 1000**1,
    "megabyte": 1000**2,
    "gigabyte": 1000**3,
    "terabyte": 1000**4,
    "petabyte": 1000**5,
    "exabyte": 1000**6,
    "zettabyte": 1000**7,
    "yottabyte": 1000**8,
    "kib": 1024**1,
    "mib": 1024**2,
    "gib": 1024**3,
    "tib": 1024**4,
    "pib": 1024**5,
    "eib": 1024**6,
    "zib": 1024**7,
    "yib": 1024**8,
    "kibibyte": 1024**1,
    "mebibyte": 1024**2,
    "gibibyte": 1024**3,
    "tebibyte": 1024**4,
    "pebibyte": 1024**5,
    "exbibyte": 1024**6,
    "zebibyte": 1024**7,
    "yobibyte": 1024**8,
}


def parse_size(size: str) -> numbers.Number:
    """parse a string with a a size-specifyer (such as 'MB' or 'G') into bytes
    the case of the specifier is ignored, as is whitespace.

    | specifier     | expands to  | value       |
    |---------------|-------------|-------------|
    | '7M'          | 7 MebiBytes | 7*1024*1024 |
    | '7MB'         | 7 MegaBytes | 7*1000*1000 |
    | '7 MiB'       | 7 MebiBytes | 7*1024*1024 |
    | '7 megabyte'  | 7 MegaBytes | 7*1000*1000 |
    | '7  mebiBYTE' | 7 MebiBytes | 7*1024*1024 |
    """
    tokens = tokenize(size)
    if not tokens:
        return None
    num = tokens[0]
    if not issubclass(type(num), numbers.Number):
        raise ValueError(f"Invalid number in size string {size!r}")
    if len(tokens) > 2:
        raise ValueError(f"Invalid size string {size!r}")
    factor = 1.0
    if len(tokens) == 2:
        factor = size_units.get(str(tokens[1]).lower())
        if not factor:
            raise ValueError(f"Invalid unit {tokens[1]} in {size!r}")
    return factor * num


def split_imagetag(path: str) -> (str, str | dict[str, str]):
    """splits a path with optional tag-decoration into a (path, tag) tuple.
    if the tag-decoration is a hashdigest, the returned <tag> is actually a
    <algo>: <digest> tuple.

    >>> split_imagetag('registry.example.org/sardines/debian:stable')
    ('registry.example.org/sardines/debian', 'stable')

    >>> split_imagetag('registry.example.org/sardines/debian')
    ('registry.example.org/sardines/debian', None)
    """
    try:
        path, digest = path.split("@", maxsplit=1)
        algo, digest = digest.split(":", maxsplit=1)
        return (path, (algo, digest))
    except ValueError:
        pass
    try:
        path, tag = path.split(":", maxsplit=1)
    except ValueError:
        tag = None
    return (path, tag)


def rmdirs(basedir: str, subdirs: list[str]) -> list[str]:
    """removes stacked subdirs, relative to <basedir>
    returns the full paths to the directories that have been removed

    >>> rmdirs('/tmp', ['', 'foo', 'bar'])
    ['/tmp/foo/bar', '/tmp/foo', '/tmp']
    """
    result = []
    for d in reversed(list(itertools.accumulate(subdirs, os.path.join))):
        xdir = os.path.join(basedir, d)
        try:
            os.rmdir(xdir)
            result.append(xdir)
        except OSError:
            return result
    return result


def checkSchema(data, schemaname: str):
    """checks whether <data> corresponds to JSON schema as described in the <schemaname> file."""
    import jsonschema

    schemafiles = [
        os.path.join("schema", f"{schemaname}.schema.json"),
        os.path.join(os.path.dirname(__file__), "schema", f"{schemaname}.schema.json"),
    ]
    schema = None
    for schemafile in schemafiles:
        try:
            log.debug(f"loading schema from {schemafile!r}")
            with open(schemafile) as f:
                schema = json.load(f)
                break
        except OSError:
            pass
    if not schema:
        return None
    try:
        jsonschema.validate(data, schema)
        return True
    except jsonschema.exceptions.ValidationError as e:
        log.debug(f"validating data against {schemaname} schema failed", exc_info=True)
        return False


class TryException(BaseException):
    """dummy exception that can be used to break out of a 'try'-clause"""

    pass


if __name__ == "__main__":

    def _show(size):
        print(f"{size!r} \t-> {parse_size(size)!r}")

    def _test():
        sizes = [
            "12",
            "1.2",
        ]
        units = "GB GiB kB kilobyte Gibibyte"
        for u in [None] + units.split():
            for s in sizes:
                if not u:
                    _show(s)
                else:
                    for f in ["%s%s", "%s %s", " %s\t%s "]:
                        _show(f % (s, u))

    _test()
