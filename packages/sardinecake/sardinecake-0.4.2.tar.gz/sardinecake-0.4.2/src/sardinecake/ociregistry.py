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


# push/pull interaction with an OCI registry

# skopeo-copy(1)
# container-transports(5)
# `skopeo copy "docker://alpine:${tag}" "oci:OCI/alpine:${tag}"`
# this fetches the raw blobs to ./OCI/alpine (the OCI dir must exist!))
# - multiple tags can be copied to the same directory (index.json then contains multiple manifests)

import os
import logging
import subprocess

try:
    from . import utils
except ImportError:
    import utils


log = logging.getLogger("sardinecake.ociregistry")


def fetch(container: str, ocidir: str = "", sourcecontainer: str | None = None) -> bool:
    """fetch a container from a registry"""
    srccontainer = sourcecontainer or container
    contain, tag = utils.split_imagetag(container)
    if not issubclass(type(tag), str):
        container = contain
    dstcontainer = os.path.join(ocidir or "", container)
    dstcontainerdir = os.path.join(ocidir or "", contain)

    # skopeo copy docker://ghcr.io/cirruslabs/macos-monterey-vanilla:latest oci:monterey:latest
    os.makedirs(dstcontainerdir, exist_ok=True)
    cmd = ["skopeo", "copy", f"docker://{srccontainer}", f"oci:{dstcontainer}"]
    log.debug(cmd)

    args = {}
    if log.getEffectiveLevel() >= logging.INFO:
        args["stdout"] = subprocess.DEVNULL
        args["stderr"] = subprocess.DEVNULL

    p = subprocess.run(cmd, **args)
    if p.returncode:
        raise SystemExit(p.returncode)
    return True


def push(container: str, ocidir: str = "", targetcontainer: str | None = None) -> bool:
    """push a container to a registry"""
    srccontainer = os.path.join(ocidir or "", container)
    dstcontainer = targetcontainer or container

    cmd = ["skopeo", "copy"]
    cmd += [f"oci:{srccontainer}", f"docker://{dstcontainer}"]
    log.debug(cmd)

    p = subprocess.run(cmd)
    if p.returncode:
        raise SystemExit(p.returncode)
    return True


def delete(container: str, ocidir: str | None = None) -> bool:
    """delete a container from the registry (if ocidir is None) or the local directory"""
    if ocidir:
        container = f"oci:{os.path.join(ocidir, container)}"
    else:
        container = f"docker://{container}"

    cmd = ["skopeo", "delete", container]
    p = subprocess.run(cmd)
    if p.returncode:
        raise SystemExit(p.returncode)
    return True


def _main():
    import argparse

    parser = argparse.ArgumentParser(
        description="fetch/push a sardine container from/to a registry.",
    )

    p = parser.add_argument_group("action")
    p = p.add_mutually_exclusive_group()
    p.add_argument(
        "--fetch",
        action="store_true",
        default=True,
        help="fetch container from registry (DEFAULT)",
    )
    p.add_argument(
        "--push",
        action="store_false",
        dest="fetch",
        help="push container to registry",
    )

    parser.add_argument(
        "container",
        help="container to push/fetch",
    )

    args = parser.parse_args()

    if args.fetch:
        x = fetch(args.container)
    else:
        x = push(args.container)
    print(x)


if __name__ == "__main__":
    _main()
