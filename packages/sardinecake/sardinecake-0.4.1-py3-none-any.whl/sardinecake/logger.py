#!/usr/bin/env python3

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

from logging import *
import logging

_log = None


class ColoredFormatter(logging.Formatter):
    HEADER = "\033[95m"
    OKBLUE = "\033[94m"
    OKCYAN = "\033[96m"
    OKGREEN = "\033[92m"
    WARNING = "\033[93m"
    FAIL = "\033[91m"
    ENDC = "\033[0m"
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"

    grey = "\033[38;20m"
    yellow = "\033[33;20m"
    green = "\033[92m"
    red = "\033[31;20m"
    bold_red = "\033[31;1m"
    dim = "\033[2m"
    reset = "\033[0m"

    def __init__(self, fmt=None, datefmt=None, style="%"):
        kwargs = {
            "style": style,
            "datefmt": datefmt or "%Y-%m-%d %H:%M:%S",
        }
        super().__init__(fmt=fmt, **kwargs)

        fmt = self._fmt

        self._formatter = {
            logging.DEBUG: logging.Formatter(self.dim + fmt + self.reset, **kwargs),
            # logging.INFO: logging.Formatter(self.green + fmt + self.reset, **kwargs),
            logging.INFO: logging.Formatter(self.reset + fmt + self.reset, **kwargs),
            logging.WARNING: logging.Formatter(
                self.yellow + fmt + self.reset, **kwargs
            ),
            logging.ERROR: logging.Formatter(self.red + fmt + self.reset, **kwargs),
            logging.CRITICAL: logging.Formatter(
                self.bold_red + fmt + self.reset, **kwargs
            ),
        }
        self._defaultformatter = logging.Formatter(**kwargs)

    def format(self, record):
        formatter = self._formatter.get(record.levelno, self._defaultformatter)
        return formatter.format(record)


def getLogger(name):
    global _log
    log = _log = logging.getLogger(name)
    logging.basicConfig()

    ch = logging.StreamHandler()
    ch.setFormatter(ColoredFormatter("%(asctime)s %(message)s"))

    master = logging.getLogger()
    for h in master.handlers:
        master.removeHandler(h)
    master.addHandler(ch)

    return log


def setVerbosity(verbosity: int | None, baselevel=logging.WARNING):
    if not verbosity:
        verbosity = 0
    if not _log:
        raise UserWarning("no logger initialized yet")
    _log.setLevel(max(1, baselevel - verbosity * 10))


if __name__ == "__main__":
    log = getLogger("test")
    setVerbosity(10)
    for name, level in logging.getLevelNamesMapping().items():
        log.log(level, name)
