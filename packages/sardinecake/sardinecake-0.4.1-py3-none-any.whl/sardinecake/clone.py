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

import libvirt

try:
    from .domain import Domain
    from . import qcow
except ImportError:
    from domain import Domain
    import qcow

log = logging.getLogger("sardinecake.clone")

START_PRINTXML = 0
START_DEFINE = 1
START_EPHEMERAL = 2
START_PERSISTENT = 3


def cloneQCOW2(source: str, target: str | None = None) -> str:
    """copy-on-write clone of a QCOW2 file <source> to another QCOW2 file
    if target is None, the clone will be in the same directory as the source, and the name will be derived from the source basename.
    if target is a directory (or ends with "/"), the clone will be in the given directory, and the name will be derived from the source basename.
    otherwise, target is a the prospective name of the output file.
    cloneQCOW2 will refuse to overwrite existing images, and use a unique filename when required.
    the actual filename of the cloned image is returned
    """
    import subprocess

    # qemu-img create -f qcow2 -b base.qcow2 -F qcow2 clone.qcow2

    # check if source exists and can be opened (otherwise raise a standard error)
    with open(source) as f:
        pass

    if not target:
        target = source
    elif os.path.isdir(target) or not os.path.basename(target):
        target = os.path.join(target, os.path.basename(source))

    # ensure that output directory exists
    outdir = os.path.dirname(target)
    os.makedirs(outdir, exist_ok=True)

    base, ext = os.path.splitext(target)

    i = ""
    while True:
        target = f"{base}{i}{ext}"
        try:
            targetfd = open(target, "x")
            break
        except FileExistsError:
            pass
        if not i:
            i = 0
        i -= 1

    targetfd.close()

    log.debug(f"shallow-cloning {source!r} to {target!r}")

    q = qcow.QCOW(target)
    q.create(backing_file=source)

    if not q:
        return

    return target


def cloneDisks(disks: dict[str, str], outputdir: str | None) -> dict[str, str]:
    """shallow-clones the given disks into output dir

    <disks> is a dictionary that maps IDs to disk paths.
    a similar map from IDs to cloned paths is returned
    """
    return {k: cloneQCOW2(v, outputdir) for k, v in disks.items()}


def clone(
    srcname: str,
    dstname: str,
    startmode: int = START_DEFINE,
    libvirtURI: str | None = None,
    mac: str | None = None,
    outdir: str | None = None,
    quiet: bool = False,
    omit_backingstore: bool | None = None,
):
    """do a fast clone of a VM
    <srcname>: original VM
    <dstname>: VM to be created
    <startmode>: how to start the newly created VM
    <libvirtURI>: connection URI to the libvirt server
        (note that only local QCOW2 disks can be cloned)
    <mac>: MAC-address of cloned network interface (use None for a new random MAC)
    <outdir>: place for the shallow cloned disks images (use None to use the same directory as the input disk images)
    <quiet>: if True, suppress libvirt errors

    <omit_backingstore>: if True, does not create a <backingStore/> entry for COW-images (might work around a bug with older libvirt)
      if None, tries to autodetect whether the <backingStore/> should be omitted
    """

    if quiet:
        libvirt.registerErrorHandler((lambda ctx, err: 1), None)

    libvirt_open = libvirt.open
    if startmode == START_PRINTXML:
        libvirt.openReadOnly

    with libvirt_open(libvirtURI) as conn:
        if omit_backingstore is None:
            omit_backingstore = conn.getLibVersion() < 9010000

        dom = Domain.fromLibVirt(conn, srcname)
        if not dom:
            raise KeyError(f"Couldn't find original VM {srcname!r}")

        if not dstname:
            suffix = 0
            while True:
                if suffix:
                    name = f"{srcname}-clone-{suffix}"
                else:
                    name = f"{srcname}-clone"
                if not Domain.fromLibVirt(conn, name):
                    dstname = name
                    break
                suffix += 1

        if Domain.fromLibVirt(conn, dstname):
            raise KeyError(f"cloned VM {dstname!r} already exists")

        dom.anonymize(mac_address=mac)
        dom.changeName(dstname)

        srcdisks = dom.getClonableDisks()

        log.debug(f"cloning disks {srcdisks} to {outdir!r}")
        cloneddisks = cloneDisks(srcdisks, outdir)
        log.debug(f"cloned disks {cloneddisks}")

        backing_files = {}
        if not omit_backingstore:
            backing_files = {
                dev: qcow.getBackingChain(disk) for dev, disk in srcdisks.items()
            }
        dom.changeDiskFiles(cloneddisks, backing_files=backing_files)

        if startmode == START_PRINTXML:
            print(dom)
        elif startmode == START_EPHEMERAL:
            log.debug(f"start ephemeral VM {dstname!r}")
            conn.createXML(dom.toXML())
            for d in cloneddisks.values():
                log.debug(f"deleting ephemeral volume {d!r}")
                os.unlink(d)
        else:
            log.debug(f"define cloned VM {dstname!r}")
            vm = conn.defineXML(dom.toXML())
            if startmode == START_PERSISTENT:
                log.debug(f"starting persistent VM {dstname!r}")
                vm.create()


def fetch_and_clone(
    container: str,
    vm: str,
    ocidir: str,
    vmdir: str,
    clonedir: str | None = None,
    startmode: int = START_DEFINE,
    libvirtURI: str | None = None,
):
    """fetches a <container>, imports it and creates an ephemeral clone
    returns the configuration of the VM (as known).
    raises exceptions on failure
    """
    from .ociregistry import fetch
    from .importvm import importvm, getconfig

    if ocidir is None:
        oci = container
    else:
        oci = os.path.join(ocidir or "", container)

    clonedir = clonedir or vmdir

    quiet = (log.getEffectiveLevel() >= logging.INFO,)

    log.info(f"fetching {container!r}")
    if not fetch(container, ocidir=ocidir):
        raise RuntimeError(f"failed to fetch {container!r}")

    log.info(f"importing {container!r}")
    basevm = importvm(
        ocidir=oci,
        outdir=vmdir,
        name=None,
        libvirtURI=libvirtURI,
        quiet=quiet,
    )
    if not basevm:
        raise RuntimeError(f"failed to import {container}")

    config = getconfig(ocidir=oci) or {}
    config["name"] = vm

    log.info(f"cloning {container!r} as {vm}")
    clone(
        srcname=basevm[0],
        dstname=vm,
        startmode=startmode,
        libvirtURI=libvirtURI,
        outdir=clonedir,
        quiet=quiet,
        omit_backingstore=None,
    )

    return config


# #########################################################################
def _parseArgs():
    """parse commandline arguments"""
    import argparse

    parser = argparse.ArgumentParser(
        description="""Duplicate a virtual machine, changing all the unique host side configuration like MAC address, name, etc.""",
        epilog="""This is very similar to 'virt-clone(1)', but uses shallow clones for copy-on-write disks.
Currently, only QCOW2 disks are supported.
    """,
    )
    parser.set_defaults(start=START_DEFINE)

    parser.add_argument(
        "--connect",
        metavar="URI",
        help="Connect to hypervisor with libvirt URI (note that to-be-cloned disks must be locally available)",
    )

    parser.add_argument(
        "name",
        metavar="NEW_NAME",
        nargs="?",
        help="Name for the new guest (overrides the '--name' argument)",
    )

    g = parser.add_argument_group("General Options")
    g.add_argument(
        "-o",
        "--original",
        metavar="SRC_NAME",
        required=True,
        help="Name of the original guest to clone.",
    )
    g.add_argument(
        "-n",
        "--name",
        dest="opt_name",
        metavar="NEW_NAME",
        help="Name for the new guest",
    )

    g = parser.add_argument_group("Clone Options")
    g.add_argument(
        "-m",
        "--mac",
        metavar="NEW_MAC",
        help="New fixed MAC address for the clone guest. Default is a randomly generated MAC.",
    )

    g = parser.add_argument_group("Output Options")
    g.add_argument(
        "--outdir",
        help="Directory to put cloned disk images into",
    )

    g.add_argument(
        "--omit-backingstore",
        action="store_true",
        default=None,
        help="Do not create a <backingStore/> tag in the new guest definition (might be needed for older libvirt versions)",
    )
    g = parser.add_mutually_exclusive_group()
    g.add_argument(
        "--define",
        dest="start",
        action="store_const",
        const=START_DEFINE,
        help="Define a new persistent VM. (DEFAULT)",
    )
    g.add_argument(
        "--print-xml",
        dest="start",
        action="store_const",
        const=START_PRINTXML,
        help="Print the generated domain XML rather than create the guest.",
    )
    g.add_argument(
        "--start-ephemeral",
        dest="start",
        action="store_const",
        const=START_EPHEMERAL,
        help="Start the cloned VM as an ephemeral domain (the VM and all it's disks will be destroyed once powered down).",
    )
    g.add_argument(
        "--start-persistent",
        dest="start",
        action="store_const",
        const=START_PERSISTENT,
        help="Define a new persistent VM and start it.",
    )

    g = parser.add_argument_group("Verbosity")
    g.add_argument(
        "-q",
        "--quiet",
        action="store_true",
        help="Suppress non-error output",
    )
    g.add_argument(
        "-d",
        "--debug",
        action="store_true",
        help="Print debugging information",
    )

    args = parser.parse_args()

    if not args.name:
        args.name = args.opt_name
    del args.opt_name

    # make sure that outdir is a directory (not a filename)
    if args.outdir is not None:
        args.outdir = os.path.join(args.outdir, "")

    if args.debug:
        log.setLevel(logging.DEBUG)

    return args


def _main():
    logging.basicConfig()
    args = _parseArgs()
    log.debug(args)

    try:
        clone(
            args.original,
            args.name,
            startmode=args.start,
            libvirtURI=args.connect,
            mac=args.mac,
            outdir=args.outdir,
            quiet=args.quiet,
            omit_backingstore=args.omit_backingstore,
        )
    except Exception as e:
        log.debug("clone failed", exc_info=True)
        raise SystemExit(e)


if __name__ == "__main__":
    _main()
