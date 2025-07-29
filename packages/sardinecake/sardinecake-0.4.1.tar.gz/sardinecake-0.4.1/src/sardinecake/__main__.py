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

_version = None

import json
import logging
import os
import pathlib

from .utils import parse_size, checkSchema
from . import defaults

try:
    from ._version import version as _version
except ImportError:
    pass

log = logging.getLogger("sardinecake")
logging.basicConfig()

SYSTEM_FAILURE = 1

example_container = "registry.example.org/sardines/debian:stable"


def do_selftest(args):
    """perform some tests (mostly about logging) and printout stuff"""
    import pprint
    import sys

    glob = dict(globals())
    del glob["__builtins__"]

    log.error(f"NAME: {__name__!r}")
    log.error(f"FILE: {__file__!r}")

    log.warning(pprint.pformat(glob, sort_dicts=False))
    log.warning(pprint.pformat(sys.argv, sort_dicts=False))

    for name, level in logging.getLevelNamesMapping().items():
        log.log(level, name)

    print(f"log-level: {log.level}/{log.getEffectiveLevel()}")
    print(args)


def do_login(args):
    from .auth import login

    registry = args.registry
    username = args.username
    password = args.password
    log.debug(f"LOGIN to {registry!r} as {username!r}")
    if not login(registry, username=username, password=password):
        raise SystemExit(f"Failed to login to {registry!r}")


def do_logout(args):
    from .auth import logout

    registry = args.registry
    if registry == "*":
        registry = None
    log.debug(f"LOGOUT from {registry!r}")
    logout(registry)


def do_fetch(args):
    from .ociregistry import fetch

    container = args.container
    ocidir = args.ocidir
    sourcecontainer = args.source
    log.debug(f"FETCH {sourcecontainer!r} as {container!r} into {ocidir!r}")
    if not fetch(container, ocidir=ocidir, sourcecontainer=sourcecontainer):
        raise SystemExit(f"failed to fetch {container!r}")


def do_push(args):
    from .ociregistry import push

    container = args.container
    ocidir = args.ocidir
    targetcontainer = args.target
    log.debug(f"PUSH {container!r} from {ocidir!r} to {targetcontainer!r}")
    if not push(container, ocidir=ocidir, targetcontainer=targetcontainer):
        raise SystemExit(f"failed to push {container!r}")


def do_list(args):
    # list all (locally) available images
    # --------------------------
    # docker: | REPOSITORY | TAG | IMAGE ID  (short config digest) | CREATED | SIZE |
    # docker --digest:  | REPOSITORY | TAG | (manifest) DIGEST | IMAGE ID (short config digest) | CREATED | SIZE |
    #
    # skopeo get by hash: container@sha256:<1234567890>; where <1234567890> is the *full* manifest digest
    # docker get by hash: container@sha256:<1234567890>; where <1234567890> is the *full* manifest digest
    # we can run:
    # - docker run <container>:<tag>
    # - docker run <container>@sha256:<manifestdigest>
    # - docker run <shortconfigdigest>
    # - docker run <any length of the config digest that is unique)
    # gitlab-docker-executor prints:
    # "Using docker image sha256:<configdigest> for <name>:<tag> with digest <name>@sha256:<manifestdigest> ..."
    #
    # --------------------------
    # tart  : | source | name | disk | size | state |
    #
    # the <name> lists all tags (in the form <container>:<tag>) and the corresponding hash
    # (in the form <container>@sha256:<manifesthash>)
    # --------------------------
    # sarde : ?
    # for the text form, we probably should go with 'tart' (but leaving out disk resp size; or put it at the end)
    # | source | name | state |
    # the JSON form should contain the name and (both) the hashes separately
    from .importvm import getconfig
    from .domain import lookupVM

    log.debug(f"LIST containers in {args.ocidir!r}")
    title = {
        "source": "SOURCE",
        "name": "NAME",
        "id": "IMAGE ID",
        "state": "STATE",
        "tag": "",
        "digest": "",
    }
    states = {
        True: "running",
        False: "stopped",
        None: "missing",
    }

    root = pathlib.Path(args.ocidir)
    dirs = [
        p.parent
        for p in root.glob("**/oci-layout")
        if (p.parent / "index.json").exists()
    ]
    # (container, manifest-file, tag)
    sardines = []
    for p in dirs:
        with (p / "index.json").open() as f:
            name = p.relative_to(root)
            index = json.load(f)

        for m in index["manifests"]:
            tag = m.get("annotations", {}).get("org.opencontainers.image.ref.name")
            digest_m = m.get("digest")
            manifestpath = p / "blobs" / os.path.join(*digest_m.split(":"))
            with manifestpath.open() as f:
                manifest = json.load(f)
            digest_c = manifest["config"]["digest"]
            state = None
            dom = lookupVM(name=digest_c, conn=args.connect, quiet=True)
            if dom:
                state = bool(dom.isActive())
            sardines.append(
                {
                    "source": "oci",
                    "name": str(name),
                    "tag": tag,
                    "digest": digest_m,
                    "id": digest_c,
                    "state": state,
                }
            )

    if args.format == "json":
        print(json.dumps(sardines, indent=2))
    else:
        fieldsize = {k: len(v) for k, v in title.items()}
        for s in sardines:
            for k, v in s.items():
                fieldsize[k] = max(fieldsize.get(k, 0), len(str(v)))
                fieldsize[k] = max(fieldsize.get(k, 0), len(str(k)))

        formatstr = "%s\t%s\t%s"
        size_source = fieldsize["source"]
        size_name = max(fieldsize["tag"], fieldsize["digest"]) + fieldsize["name"] + 1
        size_id = fieldsize["id"]
        size_state = fieldsize["state"]
        formatstr = f"%-{size_source}s\t%-{size_name}s\t%-{size_id}s\t%-{size_state}s"

        sardines = sorted(sardines, key=lambda x: (x["id"], x["name"], x["tag"] or ""))
        lastid = None
        print(formatstr % (title["source"], title["name"], title["id"], title["state"]))
        for sardine in sardines:
            if lastid != sardine["id"]:
                lastid = sardine["id"]
                name = f"{sardine['name']}@{sardine['digest']}"
                state = states.get(sardine["state"], states[None])
                print(formatstr % (sardine["source"], name, sardine["id"], state))
            if sardine["tag"]:
                name = f"{sardine['name']}:{sardine['tag']}"
                state = '   "   '
                print(formatstr % (sardine["source"], name, sardine["id"], state))


def do_getconfig(args):
    from .importvm import getconfig

    if args.raw:
        ocidir = args.container
    else:
        ocidir = os.path.join(args.ocidir or "", args.container)

    log.debug(f"GETCONFIG for {args.container!r} in {args.ocidir!r}")
    result = getconfig(
        ocidir=ocidir,
    )
    if result is None:
        log.debug(f"no configuration found for {args.container!r}")
        return
    print(json.dumps(result, indent=2))


def do_clone(args):
    from .importvm import importvm, getconfig
    from . import clone

    log.debug(f"CLONE {args}")

    # first make sure that the source container is available
    try:
        raw = args.raw
    except:
        raw = False

    if raw:
        ocidir = None
    else:
        ocidir = args.ocidir or ""

    container = args.container
    vmdir = args.vmdir

    try:
        cfg = clone.fetch_and_clone(
            container=container,
            vm=args.target,
            ocidir=ocidir,
            vmdir=vmdir,
            libvirtURI=args.connect,
        )
    except Exception as e:
        log.debug("clone failed", exc_info=True)
        raise SystemExit(e)
    print(json.dumps(cfg, indent=2))


def do_export(args):
    from .exportvm import exportvm

    name = args.name
    container = args.container or name
    libvirtURI = args.connect
    libvirtConfig = args.libvirtconfig
    if libvirtConfig:
        libvirtURI = None

    log.debug(f"EXPORT {name!r} to {args.ocidir!r} as {container!r}")

    try:
        raw = args.raw
    except:
        raw = False

    vmconfig = None
    if args.vmconfig:
        with open(args.vmconfig) as f:
            vmconfig = json.load(f)
            check = checkSchema(vmconfig, "sardineconfig")
            if check is False:
                log.fatal(
                    f"VM-config {args.vmconfig!r} does not comply with the sardine-config schema"
                )
                raise SystemExit(1)
            if not check:
                log.warning(
                    f"Could not verify VM-config {args.vmconfig!r} against schema"
                )

    if raw:
        ocidir = container
    else:
        ocidir = os.path.join(args.ocidir or "", container)
    chunksize = args.chunksize

    log.debug(f"exporting {name!r} to {ocidir!r} with chunks of {chunksize} bytes")

    result = exportvm(
        name,
        outdir=ocidir,
        libvirtURI=libvirtURI,
        libvirtconfigfile=libvirtConfig,
        chunksize=chunksize,
        vmconfig=vmconfig,
        quiet=log.getEffectiveLevel() >= logging.INFO,
    )
    if result is None:
        raise SystemExit(1)
    print(result)


def do_import(args):
    from .importvm import importvm

    try:
        raw = args.raw
    except:
        raw = False

    if raw:
        ocidir = args.container
    else:
        ocidir = os.path.join(args.ocidir or "", args.container)

    vmdir = args.vmdir
    name = args.name

    log.debug(f"IMPORT {args.container!r} from {args.ocidir} to {vmdir!r} as {name!r}")

    result = importvm(
        ocidir=ocidir,
        outdir=vmdir,
        name=name,
        libvirtURI=args.connect,
        quiet=log.getEffectiveLevel() >= logging.INFO,
    )
    if result is None:
        raise SystemExit(1)
    try:
        if args.print_uuid:
            print(result[1])
        else:
            print(result[0])
    except IndexError:
        print(result)


def do_pull(args):
    log.debug(f"PULL {args}")

    do_fetch(args)
    do_import(args)


def readConfig(configfiles: list[str], with_default=False) -> dict:
    import configparser

    converters = {
        "verbose": int,
        "quiet": int,
        "chunksize": parse_size,
        "vmdir": os.path.expanduser,
        "ocidir": os.path.expanduser,
    }

    config = configparser.ConfigParser()
    config.read(os.path.expanduser(f) for f in configfiles)

    configuration = {
        section: dict(config[section].items())
        for section in config
        if with_default or config.default_section != section
    }

    defaults = configuration.get(config.default_section)
    if defaults:
        del configuration[config.default_section]
    configuration[None] = defaults

    # fix types
    for name, section in configuration.items():
        for k, converter in converters.items():
            if not converter:
                continue
            if k in section:
                section[k] = converter(section[k])

    return configuration


def parseArgs(default):
    import argparse

    formatter = argparse.RawDescriptionHelpFormatter

    def add_common_args(parser: argparse.ArgumentParser):
        p = parser.add_argument_group("libvirt")
        p.add_argument(
            "--connect",
            help="libvirt connection URI",
        )

        p = parser.add_argument_group("verbosity")
        p.add_argument(
            "-v",
            "--verbose",
            action="count",
            help="Raise verbosity (can be given multiple times)",
        )
        p.add_argument(
            "-q",
            "--quiet",
            action="count",
            help="Lower verbosity (can be given multiple times)",
        )
        p.add_argument(
            "--no-run",
            default=None,
            action="store_true",
            help="Don't actually run (exit early)",
        )

        return parser

    # common args for all sub-parsers and the top-level parser
    common = argparse.ArgumentParser(add_help=False)
    add_common_args(common)

    parser = argparse.ArgumentParser(
        description="manage libvirt VMs via OCI registries",
        parents=[common],
    )

    def add_default_args(subparsers, name=None, fallbacks={}, func=None, **kwargs):
        if any([name, func]) and not all([subparsers, name, func]):
            raise ValueError("inconsistent arguments for add_subparser()")

        if name:
            if "help" in kwargs and "description" not in kwargs:
                kwargs["description"] = kwargs["help"]
            p = subparsers.add_parser(name, **kwargs)
            add_common_args(p)
        else:
            p = subparsers

        fallbacks.setdefault("ocidir", defaults.sarde.oci_path)
        fallbacks.setdefault("vmdir", defaults.sarde.vmdisk_path)
        fallbacks.setdefault("verbose", 0)
        fallbacks.setdefault("quiet", 0)
        mydefaults = default.get(name) or default.get(None) or {}
        fallbacks.update(mydefaults)
        fallbacks["func"] = func

        if func:
            p.set_defaults(**fallbacks)

        return p

    add_default_args(parser)

    parser.add_argument(
        "-V",
        "--version",
        action="version",
        version=_version or "<unknown>",
    )

    subparsers = parser.add_subparsers(required=True, title="commands")

    # ################### login ###################
    p = add_default_args(
        subparsers,
        "login",
        func=do_login,
        help="Login to a registry",
        formatter_class=formatter,
        epilog="""
For pushing images to a registry (and sometimes for pulling),
you often need to authenticate yourself. Do this via the 'login' command.

        %(prog)s registry.example.org

Once you no longer need to authenticate, 'logout' again.

Registry interaction is (currently) handled by 'skopeo', which will store
credentials in `${XDG_RUNTIME_DIR}/containers/auth.json`.
""",
    )
    p.add_argument(
        "-u",
        "--username",
        help="Username for registry",
    )
    p.add_argument(
        "-p",
        "--password",
        help="Password for registry",
    )
    p.add_argument(
        "registry",
        help="Registry to login to (e.g. 'registry.example.org')",
    )

    # ################### logout ###################
    p = add_default_args(
        subparsers,
        "logout",
        func=do_logout,
        help="Logout from a registry",
        formatter_class=formatter,
        epilog="""
For pushing images to a registry (and sometimes for pulling),
you often need to authenticate yourself. Do this via the 'login' command.

Once you no longer need to authenticate, 'logout' again.

        %(prog)s registry.example.org
""",
    )

    p.add_argument(
        "registry",
        help="""Registry to logout from (e.g. 'registry.example.org').
        Use '*' for removing cached credentials for ALL registries in the auth file.""",
    )

    # ################### pull ###################
    p = add_default_args(
        subparsers,
        "pull",
        func=do_pull,
        help="Pull VM from a registry, and import it into libvirt",
        formatter_class=formatter,
        epilog="""
        This is a shortcut for 'sarde fetch' and 'sarde import'
""",
    )

    g = p.add_argument_group("input")
    g.add_argument(
        "container",
        help=f"Container to pull (e.g. {example_container!r})",
    )
    g.add_argument(
        "-d",
        "--ocidir",
        help="""Directory where OCI containers are stored (DEFAULT: %(default)r)""",
    )
    g.add_argument(
        "-s",
        "--source",
        help="Fetch the specified container, rather than <container>",
    )

    g = p.add_argument_group("output")
    # <name> is omitted (or optional) - use the SHA256 instead
    g.add_argument(
        "-n",
        "--name",
        help="Destination VM name (DEFAULT: create a unique name)",
    )
    g.add_argument(
        "-o",
        "--vmdir",
        "--outdir",
        help="Output directory to extract VM disk images to (DEFAULT: %(default)r)",
    )

    g = p.add_argument_group("return")
    g.add_argument(
        "--print-uuid",
        action="store_true",
        help="Return UUID of the imported VM, rather than it's name.",
    )

    # ################### fetch ###################
    p = add_default_args(
        subparsers,
        "fetch",
        func=do_fetch,
        help="Fetch a VM from the registry",
        formatter_class=formatter,
        epilog="""
Download a VM image from the registry, and store it in the OCI cache
(as specified via the '--ocidir' flag).

        %(prog)s registry.example.org/sardines/debian:latest

This will fetch the given image and store it as a number of blobs under
'${ocidir}/registry.example.org/sardines/debian/'.
Use 'import' to create the actual VM from these blobs.
""",
    )
    g = p.add_argument_group("input")
    g.add_argument(
        "-s",
        "--source",
        help="Fetch the specified container, rather than <container>",
    )
    g = p.add_argument_group("output")
    g.add_argument(
        "container",
        help=f"Container to fetch (e.g. {example_container!r})",
    )
    g.add_argument(
        "-d",
        "--ocidir",
        help="""Directory where OCI containers are stored (DEFAULT: %(default)r)""",
    )

    # ################### push ###################
    p = add_default_args(
        subparsers,
        "push",
        func=do_push,
        help="Push a VM to a registry",
        formatter_class=formatter,
        epilog="""Push a container from the local OCI cache (e.g. previously 'export'ed from a VM),
to a remote registry.
Most likely you will have to 'login' first, in order to be allowed to push.
By default, the local container name is used to determine the destination.
E.g. a container named 'registry.example.org/sardines/debian:stable' will be pushed to the 'registry.example.org'
host as 'sardines/debian:stable'.

        %(prog)s registry.example.org/sardines/debian:stable

You can specify a different destination with the '--target' flag.

        %(prog)s --target 'registry.example.org/sardines/debian:latest' 'registry.example.org/sardines/debian:bookworm'

This is especially useful, if the local OCI container does not point to a registry:
        %(prog)s --target 'registry.example.org/sardines/debian:latest' 'debian:bookworm'
""",
    )
    g = p.add_argument_group("input")
    g.add_argument(
        "container",
        help=f"Container to push (e.g. {example_container!r})",
    )
    g = p.add_argument_group("output")
    g.add_argument(
        "-d",
        "--ocidir",
        help="""Directory where OCI containers are stored (DEFAULT: %(default)r)""",
    )
    g.add_argument(
        "-t",
        "--target",
        help="Push to the specified container, rather than <container>",
    )

    # ################### list ###################
    p = add_default_args(
        subparsers,
        "list",
        func=do_list,
        help="List local containers.",
        formatter_class=formatter,
        epilog="""
List all available containers, found in the local OCI cache.
Apart from the source (currently always 'oci') and the name of the image
(as specified when 'fetch'ing or 'clone'ing an image), it will also print
the image ID (shared by identical containers) and the current state,
which can be either "missing" (if the container has not yet been 'import'ed),
"stopped" (if the container has been imported but is not running) or
"running"" (if the container is currently a running as a VM).

        $ %(prog)s
        SOURCE  NAME                                          IMAGE ID               STATE
        oci     registry.example.org/debian@sha256:f99c5178   sha256:052bd348        stopped
        oci     registry.example.org/debian:latest            sha256:052bd348           "
        oci     foo.example.com/ubuntu@sha256:c44c1d53        sha256:f2c4820d        missing

A machine-friendly output can be obtained via the '--format json' flag.
""",
    )

    g = p.add_argument_group("input")
    g.add_argument(
        "-d",
        "--ocidir",
        help="""Directory where OCI containers are stored (DEFAULT: %(default)r)""",
    )
    g = p.add_argument_group("input")
    g.add_argument(
        "--format",
        default="text",
        choices=["text", "json"],
        type=lambda x: str(x).lower(),
        help="""Directory where OCI containers are stored (DEFAULT: %(default)r)""",
    )

    # ################### getconfig ###################
    p = add_default_args(
        subparsers,
        "getconfig",
        func=do_getconfig,
        help="Get VM config from an OCI bundle",
        formatter_class=formatter,
        epilog="""Gets the (very basic) configuration of the OCI container,
detailing users (and their passwords) as well as exposed services;
formatted as JSON.

        %(prog)s registry.example.org/debian:latest
        {
          "users": [
            {
              "username": "vagrant",
              "password": "vagrant"
            }
          ],
          "services": [
            {
              "service": "ssh",
              "port": 22,
              "protocol": "tcp"
            }
          ]
        }

The configuration might be empty, in which case, nothing is printed.
""",
    )

    g = p.add_argument_group("input")
    g.add_argument(
        "container",
        help="""Container created by 'sarde export' or 'sarde fetch' (found in <OCIDIR>).""",
    )
    gx = g.add_mutually_exclusive_group()
    gx.add_argument(
        "-d",
        "--ocidir",
        help="""Directory where OCI containers are stored (DEFAULT: %(default)r)""",
    )
    gx.add_argument(
        "--raw",
        action="store_true",
        help="""Assume that <container> is a directory path, rather than an OCI container within <OCIDIR>""",
    )

    # ################### export ###################
    p = add_default_args(
        subparsers,
        "export",
        func=do_export,
        help="Export VM to an OCI bundle",
        formatter_class=formatter,
        epilog="""
Convert a VM disk image to an OCI container

This will create an OCI-container 'mydebian:latest' from the 'mydebian' VM:
        %(prog)s --chunksize 256MiB mydebian mydebian:latest

This should create a (local) OCI-container 'registry.example.com/sardines/mydebian:sid' from the 'mydebian' VM:
        %(prog)s --chunksize 256MiB mydebian 'registry.example.com/sardines/mydebian:sid

Once a VM has been exported to an OCI-container, you can 'push' it to a registry.


NOTE
If your VM uses a disk with a backing file, that backing file MUST be in the same directory
as the depending disk image, and it MUST use a relative path.
To make a backing file relative, you can use something like:

        qemu-img rebase -F qcow2 -u -b base.img child.img

""",
    )

    g = p.add_argument_group("input")
    g.add_argument(
        "--vmconfig",
        help="""JSON-file containing additional VM configuration (like username/password).""",
    )
    g.add_argument(
        "--libvirtconfig",
        help="""XML-file containing the libvirt configuration for the VM.
        Useful if you want to export the disks of an existing VM with a generic VM configuration.
        The DEFAULT is to obtain configuration from libvirt.
        Normally you shouldn't need this (EXPERTS ONLY).""",
    )
    g.add_argument(
        "name",
        help="""Source VM name""",
    )

    g = p.add_argument_group("output")
    g.add_argument(
        "container",
        nargs="?",
        help="""Container to export into.""",
    )
    g.add_argument(
        "--chunksize",
        type=parse_size,
        help="""Split gzipped disk images into chunks of the given size
        (in bytes; but specifiers like 'GiB' or 'MB' are recognized). (DEFAULT: do not split)""",
    )
    gx = g.add_mutually_exclusive_group()
    gx.add_argument(
        "-d",
        "--ocidir",
        help="""Directory where OCI containers are stored (DEFAULT: %(default)r)""",
    )
    gx.add_argument(
        "--raw",
        action="store_true",
        help="""Assume that <container> is a directory path, rather than an OCI container within <OCIDIR>""",
    )

    # ################### import ###################
    p = add_default_args(
        subparsers,
        "import",
        func=do_import,
        help="Import VM from an OCI bundle",
        formatter_class=formatter,
        epilog="""Create a VM from an OCI container.

OCI containers are not runnable per se, you have to first re-assemble them into VM (disk images,...).
This is done via the 'import' command.

The following will create a VM named 'mydebian' from the local 'registry.example.org/debian:latest' container.

        %(prog)s -n mydebian registry.example.org/debian:latest

The container has to be available locally.
A convenient alternative is to use the 'pull' command, which will fetch container first if needed.
""",
    )

    g = p.add_argument_group("input")
    g.add_argument(
        "container",
        help="""Container created by 'sarde export' or 'sarde fetch' (found in <OCIDIR>).""",
    )
    gx = g.add_mutually_exclusive_group()
    gx.add_argument(
        "-d",
        "--ocidir",
        help="""Directory where OCI containers are stored (DEFAULT: %(default)r)""",
    )
    gx.add_argument(
        "--raw",
        action="store_true",
        help="""Assume that <container> is a directory path, rather than an OCI container within <OCIDIR>""",
    )

    g = p.add_argument_group("output")
    # <name> is omitted (or optional) - use the SHA256 instead
    g.add_argument(
        "-n",
        "--name",
        help="Destination VM name (DEFAULT: create a unique name)",
    )
    g.add_argument(
        "-o",
        "--vmdir",
        "--outdir",
        help="Output directory to extract VM disk images to (DEFAULT: %(default)r)",
    )

    g = p.add_argument_group("return")
    g.add_argument(
        "--print-uuid",
        action="store_true",
        help="Return UUID of the imported VM, rather than it's name.",
    )

    # ################### clone ###################
    p = add_default_args(
        subparsers,
        "clone",
        func=do_clone,
        help="Clone a VM",
        description="Creates a local virtual machine by cloning either a remote or another local virtual machine.",
        formatter_class=formatter,
        epilog="""
""",
    )

    g = p.add_argument_group("input")
    g.add_argument(
        "-d",
        "--ocidir",
        help="""Directory where OCI containers are stored (DEFAULT: %(default)r)""",
    )
    g.add_argument(
        "container",
        metavar="source",
        help="""Source container.""",
    )

    g = p.add_argument_group("output")
    g.add_argument(
        "-o",
        "--vmdir",
        "--outdir",
        help="Output directory to extract VM disk images to (DEFAULT: %(default)r)",
    )
    g.add_argument(
        "target",
        help="""Target VM.""",
    )

    # ################### selftest ###################
    p = add_default_args(
        subparsers,
        "selftest",
        func=do_selftest,
        help="Test logging with verbosity and whatelse",
        formatter_class=formatter,
        epilog="""
        '%(prog)s' creates output at various loglevels and prints some internal data about the Python state.
""",
    )

    # ################### ###### ###################

    common_args, remainder = common.parse_known_args()
    args = parser.parse_args()

    # fix common args
    for k, v in common_args._get_kwargs():
        if v is None:
            continue
        setattr(args, k, v)

    # merge verbosity settings
    if args.verbose or args.quiet:
        args.verbosity = (args.verbose or 0) - (args.quiet or 0)
        verbosity = args.verbosity
    else:
        args.verbosity = None
        verbosity = 0  # defaults.verbosity
    # logging.setVerbosity(verbosity)
    log.setLevel(max(1, logging.INFO - 10 * verbosity))
    del args.quiet
    del args.verbose

    fun = args.func
    del args.func

    return (fun, args)


def _main():
    userconf = os.getenv("SARDE_CONF_FILES")
    if userconf:
        configfiles = userconf.split(":")
    else:
        configfiles = [
            "/etc/sardinecake/sarde.ini",
            "~/.config/sardinecake/sarde.ini",
        ]
    defaults = readConfig(configfiles, with_default=True)

    try:
        fun, args = parseArgs(defaults)
    except SystemExit as e:
        if e.code and type(e.code) != int:
            log.fatal(e)
        raise

    log.debug(f"configuration-files: {configfiles}")
    log.debug(f"default config     : {defaults}")
    log.debug(f"function           : {fun}")
    log.debug(f"arguments          : {args}")

    if args.no_run:
        raise SystemExit(0)

    ret = None
    try:
        ret = fun(args)
    except SystemExit as e:
        if e.code and type(e.code) != int:
            log.fatal(e)
            raise SystemExit(SYSTEM_FAILURE)
        raise (e)
    raise SystemExit(ret)


if __name__ == "__main__":
    _main()
