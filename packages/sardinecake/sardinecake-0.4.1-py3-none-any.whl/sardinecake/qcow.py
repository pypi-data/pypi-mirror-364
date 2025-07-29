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

import os
import logging
import subprocess

log = logging.getLogger("sardinecake.qcow")


class QCOW:
    def __init__(self, filename: str):
        try:
            self.getBackingChain = self._getBackingChain_pyqcow
        except AttributeError as e:
            pass
        self._filename = filename

    def getBackingChain(self, normalize=True) -> list[str]:
        """get the backing chain (recursively) for the QCOW2 image.
        returns the full backing chain, starting with ourself.
        if one backing-file could not be resolved, the list terminates with a None.
        on error, and an exception might be thrown
        """

        def actualNormalized(data: str) -> (str, str):
            """extract the actual resp. the normalized path, depending on the <normalize> value"""
            data = data.strip()
            if not data:
                return data
            data = [_.strip() for _ in data.split("(actual path: ", maxsplit=1)]
            if normalize and len(data) > 1:
                return data[1][:-1]
            return data[0]

        filename = self._filename

        p = subprocess.run(
            ["qemu-img", "info", "--backing-chain", filename],
            stdout=subprocess.PIPE,
            check=True,
            env={"LANG": "C"},
        )

        backingfiles = [
            actualNormalized(line.split(b":", maxsplit=1)[1].decode())
            for line in p.stdout.splitlines()
            if line.startswith(b"backing file:")
        ]
        return [filename] + backingfiles

    try:
        import pyqcow

        def _getBackingChain_pyqcow(self, normalize=True, _cwd=None):
            """set help(QCOW.getBackingChain) for a description"""
            import pyqcow

            filename = self._filename
            fullname = os.path.join(_cwd or "", filename)

            if normalize:
                result = [fullname]
            else:
                result = [filename]

            with open(fullname, "rb") as f:
                q = pyqcow.file()
                q.open_file_object(f)
                backingfile = q.get_backing_filename()
            if not backingfile:
                return result
            dirname = os.path.dirname(fullname)
            try:
                bfiles = (
                    QCOW(backingfile).getBackingChain(normalize=normalize, _cwd=dirname)
                    or []
                )
            except OSError:
                bfiles = [None]
            return result + bfiles

        del pyqcow

    except ImportError:
        pass

    def commit(self) -> list[str]:
        """commit any changes from the current file into it's backing-file (if any).
        this basically merges changes to the backing-file, and removes them from *this*file.

        returns the backing-chain if the given file.
        only the first item in the list is modified!

        e.g. snapshot.qcow2 -> child.qcow2 -> master.qcow2

        # merge all changes from 'snapshot.qcow2' into 'child.qcow2'
        # ('master.qcow2' is left as is)
        >>> QCOW("snapshot.qcow2").commit()
        ['child.qcow2', 'master.qcow2']

        # merge all changes from 'child.qcow2' into 'master.qcow2'
        # TODO: does this invalidate 'snapshot.qcow2'?
        >>> QCOW("child.qcow2").commit()
        ['master.qcow2']

        >>> QCOW("master.qcow2").commit()
        []
        """

        backingchain = self.getBackingChain()
        filename = self._filename

        if not backingchain:
            return None
        p = subprocess.run(
            ["qemu-img", "commit", filename],
            check=True,
        )
        return backingchain[1:]

    def create(self, size: int | None = None, backing_file: str | None = None):
        """create a new QCOW2 image.
        either <size> xor <backing_file> must be present.
        """
        if bool(size) == bool(backing_file):
            raise ValueError(
                f"You have to specify either size ({size}) OR backing_file ({backing_file})"
            )
        cmd = ["qemu-img", "create", "-f", "qcow2"]
        if backing_file:
            cmd += ["-F", "qcow2", "-b", backing_file]

        cmd.append(self._filename)

        if size:
            cmd.append(str(size))

        log.debug(cmd)

        args = {}
        if log.getEffectiveLevel() >= logging.INFO:
            args["stdout"] = subprocess.DEVNULL
            args["stderr"] = subprocess.DEVNULL
        else:
            args["stdout"] = subprocess.sys.stderr

        p = subprocess.run(
            cmd,
            **args,
        )

        if p.returncode:
            return False

        return True


def _main():
    import argparse

    parser = argparse.ArgumentParser(
        description="manipulate QCOW2 images",
    )
    subparsers = parser.add_subparsers(required=True)

    p_check = subparsers.add_parser(
        "backingchain", help="Get the backing chain of the QCOW2 files"
    )
    p_check.set_defaults(fun="getBackingChain")
    p_check.add_argument(
        "--no-normalize",
        action="store_false",
        dest="normalize",
        help="Output path names as stored within the qcow file(s).",
    )
    p_check.add_argument(
        "--normalize",
        action="store_true",
        default=True,
        help="Output normalized path names (DEFAULT)",
    )

    p_merge = subparsers.add_parser(
        "commit",
        help="Merge the changes from the QCOW2 file into its (1st level) backing file",
    )
    p_merge.set_defaults(fun="commit")

    for p in [p_check, p_merge]:
        p.add_argument("file", nargs="+", help="qcow2 file(s) to work on")

    args = parser.parse_args()

    kwargs = {}
    try:
        kwargs["normalize"] = args.normalize
    except AttributeError:
        pass
    print(f"applying {args.fun!r}")

    for filename in args.file:
        qcow = QCOW(filename)

        fun = getattr(qcow, args.fun)
        try:
            chain = fun(**kwargs)
        except Exception as e:
            log.exception(f"couldn't do {args.fun!r}")
            chain = e
        print(f"{filename} -> {chain}")


def getBackingChain(disk: str) -> list[str]:
    "gets backing chain if the disk (including the <disk> as first item)"
    try:
        return QCOW(disk).getBackingChain()
    except:
        pass
    return [disk]


if __name__ == "__main__":
    _main()
