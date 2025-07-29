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


# a generic domain representation (with backing as XML, libvirt,...)

import logging
import libvirt
from xml.dom import minidom
from xml.parsers import expat as expatparser

log = logging.getLogger("sardinecake.domain")


def _getChildrenByTagName(parent, tagName):
    """get all immediate children of <parent> that match the tagname"""
    for element in parent.getElementsByTagName(tagName):
        if element.parentNode == parent:
            yield element


def _addChild(parent, tagname):
    """add a new child Element with the specified tag to <parent>.
    returns the new child"""
    el = minidom.Element(tagname)
    parent.appendChild(el)
    el.ownerDocument = parent.ownerDocument
    return el


def _addBackingStore(parent, source, format):
    try:
        backingStore = parent.getElementsByTagName("backingStore")
        if backingStore:
            backingStore = backingStore[0]
        else:
            backingStore = _addChild(parent, "backingStore")

        for el in backingStore.childNodes:
            backingStore.removeChild(el)
        backingStore.setAttribute("type", "file")
        _addChild(backingStore, "format").setAttribute("type", format)
        _addChild(backingStore, "source").setAttribute("file", source)
    except:
        log.exception(f"adding backing file {backing_file} failed")
        backingStore = None
    return backingStore


def lookupVM(name, conn=None, quiet=False):
    if quiet:
        libvirt.registerErrorHandler((lambda ctx, err: 1), None)
    if not issubclass(type(conn), libvirt.virConnect):
        conn = libvirt.openReadOnly(conn)
    lookups = [conn.lookupByName, conn.lookupByUUIDString, conn.lookupByUUID]
    for lookup in lookups:
        try:
            return lookup(name)
        except libvirt.libvirtError:
            pass


class Domain:
    try:
        from typing import Self as _self

        _self = _self | None
    except ImportError:
        _self = "Domain"

    archmap = {
        # ###############################################
        # allowed values are (https://go.dev/doc/install/source#environment)
        # - "amd64" (64-bit x86, the most mature port)
        # - "386" (32-bit x86)
        # - "arm" (32-bit ARM)
        # - "arm64" (64-bit ARM)
        # - "ppc64le" (PowerPC 64-bit, little-endian)
        # - "ppc64" (PowerPC 64-bit, big-endian)
        # - "mips64le" (MIPS 64-bit, little-endian)
        # - "mips64" (MIPS 64-bit, big-endian)
        # - "mipsle" (MIPS 32-bit, little-endian)
        # - "mips" (MIPS 32-bit, big-endian)
        # - "s390x" (IBM System z 64-bit, big-endian)
        # - "wasm" (WebAssembly 32-bit)
        # ###############################################
        # keys found in /usr/share/libvirt/schemas/basictypes.rng
        "aarch64": "arm64",
        "alpha": "alpha",  # :-(
        "armv7l": "arm",
        "armv6l": "arm",
        "cris": "cris",  # :-(
        "i686": "386",
        "ia64": "ia64",  # :-(
        "lm32": "lm32",  # :-(
        "loongarch64": "loongarch64",  # :-(
        "m68k": "m68k",  # :-(
        "microblaze": "microblaze",  # :-(
        "microblazeel": "microblazeel",  # :-(
        "mips": "mips",
        "mipsel": "mipsle",
        "mips64": "mips64",
        "mips64el": "mips64le",
        "openrisc": "openrisc",  # :-(
        "parisc": "parisc",  # :-(
        "parisc64": "parisc64",  # :-(
        "ppc": "ppc",  # :-(
        "ppc64": "ppc64",
        "ppc64le": "ppc64le",
        "ppcemb": "ppcemb",  # :-(
        "riscv32": "riscv32",  # :-(
        "riscv64": "riscv64",  # :-(
        "s390": "s390",  # :-(
        "s390x": "s390x",
        "sh4": "sh4",  # :-(
        "sh4eb": "sh4eb",  # :-(
        "sparc": "sparc",  # :-(
        "sparc64": "sparc64",  # :-(
        "unicore32": "unicore32",  # :-(
        "x86_64": "amd64",
        "xtensa": "xtensa",  # :-(
        "xtensaeb": "xtensaeb",  # :-(
    }
    osmap = {
        # ###############################################
        # allowed values are (https://go.dev/doc/install/source#environment)
        # - "android"
        # - "darwin"
        # - "dragonfly"
        # - "freebsd"
        # - "illumos"
        # - "ios" ?
        # - "js"  ?
        # - "linux"
        # - "netbsd"
        # - "openbsd"
        # - "plan9" ?
        # - "solaris"
        # - "wasip1" ?
        # - "windows"
        # ###############################################
        # these are extracted from osinfo
        # check if '://<key>' is contained in the os ID
        # order matters!
        "android-x86.org": "android",
        "apple.com/": "darwin",
        "dragonflybsd.org/": "dragonfly",  # "dragonflybsd",
        "freebsd.org/": "freebsd",
        "freedos.org/": "dos",  # :-(
        "guix.gnu.org/guix/hurd": "hurd",  # :-(
        "guix.gnu.org/": "linux",
        "haiku-os.org/": "haiku",  # :-(
        "microsoft.com/msdos/": "dos",  # :-(
        "microsoft.com/win/1.": "win16",  # :-(
        "microsoft.com/win/2.": "win16",  # :-(
        "microsoft.com/win/3.": "win16",  # :-(
        "microsoft.com/win/9": "win9x",  # :-(
        "microsoft.com/win/me": "win9x",  # :-(
        "microsoft.com/": "windows",  # "winnt"
        "netbsd.org/": "netbsd",
        "novell.com/": "netware",  # :-(
        "omnios.org/": "illumos",
        "openbsd.org/": "openbsd",
        "openindiana.org/": "illumos",
        "oracle.com/solaris/": "solaris",
        "oracle.com/": "linux",
        "smartos.org/": "illumos",
        "sun.com/": "solaris",
        None: "linux",  # all the rest is linux
    }

    def __init__(self, xml: str):
        """create a Domain from a libvirt XML description"""
        self.xml = minidom.parseString(xml)

    def toXML(self):
        """get an XML representation (as a string) of the domain"""
        return self.xml.toxml()

    def __str__(self):
        """get a string representation (as XML)"""
        return self.toXML()

    def __repr__(self):
        return f"{type(self).__name__}({self.toXML()!r})"

    def getCPU(self):
        """get CPU family of the VM"""
        for os in self.xml.getElementsByTagName("os"):
            for typ in os.getElementsByTagName("type"):
                arch = typ.getAttribute("arch")
                if arch:
                    return self.archmap.get(arch, arch)

    def getOS(self):
        """get (lowercased) OS family of the VM"""
        for metadata in self.xml.getElementsByTagName("metadata"):
            for os in self.xml.getElementsByTagName("libosinfo:os"):
                osid = os.getAttribute("id")
                if osid:
                    for k, v in self.osmap.items():
                        if k and f"://{k}" in osid:
                            return v
        return self.osmap.get(None) or "unknown"

    def getDisks(self) -> dict[str, str]:
        """get all disks as dicts"""
        disks = []
        for diskType in self.xml.getElementsByTagName("disk"):
            disk = {}
            for diskNode in diskType.childNodes:
                name = diskNode.nodeName
                if name[0:1] == "#":
                    continue
                disk[name] = {
                    diskNode.attributes[attr].name: diskNode.attributes[attr].value
                    for attr in diskNode.attributes.keys()
                }
            disks.append(
                {
                    "type": diskType.getAttribute("type"),
                    "device": diskType.getAttribute("device"),
                    "file": disk.get("source", {}).get("file"),
                    "driver": disk.get("driver", {}).get("type"),
                    "target": disk.get("target", {}).get("dev"),
                }
            )
        return disks

    def getDiskFiles(self) -> dict[str, str]:
        """get the path to all file-based disks.
        returns a target-device -> source-file mapping
        """
        return {
            disk["target"]: disk["file"]
            for disk in self.getDisks()
            if disk.get("type") == "file" and disk.get("file")
        }

    def changeDiskFiles(
        self,
        disks: dict[str, str],
        backing_files: dict[str, str] = {},
        clear_old_backing_files: bool | None = True,
    ):
        """changes the disk-files according to the target-device -> source-file mapping in <disks>
        if <clear_old_backing_files> is True, remove all existing backing files
        if <clear_old_backing_files> is False, keep existing backing files
        if <backing_files> is None, keep existing (non-empty) backing files
        """
        changed = {}
        missed = {}
        if not backing_files:
            backing_files = {}
        for disk in self.xml.getElementsByTagName("disk"):
            if disk.getAttribute("type") != "file":
                continue
            target = None
            for t in disk.getElementsByTagName("target"):
                target = t.getAttribute("dev")
                if target in disks:
                    break
                target = None
            if not target:
                continue
            format = "qcow2"
            for d in disk.getElementsByTagName("driver"):
                format = d.getAttribute("type")
                break

            # remove empty backingStores
            if clear_old_backing_files is not False:
                for b in _getChildrenByTagName(disk, "backingStore"):
                    if not clear_old_backing_files:
                        if b.attributes.items():
                            continue
                        if b.hasChildNodes():
                            continue
                    log.debug(f"deleting backingStore node {b.toxml()!r}")
                    b.parentNode.removeChild(b)

            newsource = disks.get(target)
            backfiles = backing_files.get(target, [])
            if type(backfiles) == str:
                backfiles = [backfiles]
            missed[newsource] = True
            for s in disk.getElementsByTagName("source"):
                source = s.getAttribute("file")
                if source:
                    s.setAttribute("file", newsource)
                    changed[target] = newsource
                    missed[newsource] = False
                    # add backingstore if required
                    backparent = s.parentNode
                    for backing_file in backfiles:
                        backparent = _addBackingStore(backparent, backing_file, format)
                        if not backparent:
                            break

                    break

        # check if there were some elements that lacked a <source/> tag,
        # even though there was a matching <disk>
        disks = {k: v for k, v in disks.items() if missed.get(v)}
        if missed:
            log.debug(f"missed: {missed}")
            log.debug(f"missedisks: {disks}")
            for disk in self.xml.getElementsByTagName("disk"):
                if disk.getAttribute("type") != "file":
                    continue
                target = None
                for t in disk.getElementsByTagName("target"):
                    target = t.getAttribute("dev")
                    if target in disks:
                        break
                    target = None
                if not target:
                    continue
                newsource = disks.get(target)
                _addChild(disk, "source").setAttribute("file", newsource)
                changed[target] = newsource

        # return all the disks that have been changed
        return changed

    def getClonableDisks(self) -> dict:
        """check if all disks are either QCOW2-file-based disks or (implicitly sharable) CD-ROMs
        returns a dictionary of targetdev:qcow2image mappings
        exits if an unsupported device is found"""
        disks = {}
        for idx, d in enumerate(self.getDisks()):
            device = d.get("device")
            driver = d.get("driver")
            dtype = d.get("type")
            if device == "cdrom":
                continue
            if device != "disk":
                raise ValueError(f"Disk#{idx} is is an unsupported device {device!r}")
            if dtype != "file":
                raise ValueError(
                    f"Disk#{idx} is {dtype!r}-based (only 'file' is supported)"
                )
            # check if the disk is qcow2 based
            if driver != "qcow2":
                raise ValueError(
                    f"Disk#{idx} is of type {driver!r} (only 'qcow2' is supported)"
                )
            disks[d["target"]] = d["file"]
        return disks

    def getUUID(self) -> str | None:
        """get the UUID of the VM (if it has one)"""
        for uuidtag in _getChildrenByTagName(self.xml, "uuid"):
            return uuidtag.firstChild.wholeText

    def changeName(self, name: str | None) -> str | None:
        """change the <name> of the VM.
        returns the old name.
        if <name> is None, the name is not changed.
        on error, None is returned
        """
        nametag = None
        for nametag in self.xml.getElementsByTagName("name"):
            break
        if not nametag or not nametag.parentNode.parentNode == self.xml:
            return
        oldname = nametag.firstChild.wholeText
        if name is not None:
            nametag.firstChild.replaceWholeText(name)
        return oldname

    def getName(self) -> str | None:
        """get the <name> of the VM.
        on error, None is returned
        """
        return self.changeName(None)

    def anonymize(
        self, remove_uuid=True, remove_watchdog=True, mac_address: str | None = None
    ) -> bool:
        """remove instance specific information (like UUID, mac,...)
        use Domain.changeDiskFiles() and Domain.setName() to manually cleanup some more
        """
        domain = None
        for domain in self.xml.getElementsByTagName("domain"):
            break
        if not domain:
            return False

        if remove_uuid:
            for uuid in _getChildrenByTagName(domain, "uuid"):
                domain.removeChild(uuid)

        if remove_watchdog:
            # the 'itco' watchdog gives us trouble with older(?) libvirt
            for devices in _getChildrenByTagName(domain, "devices"):
                for watchdog in _getChildrenByTagName(devices, "watchdog"):
                    if watchdog.getAttribute("model") == "itco":
                        devices.removeChild(watchdog)

        for mac in domain.getElementsByTagName("mac"):
            if mac.parentNode.tagName != "interface":
                continue
            if mac.hasAttribute("address"):
                mac.removeAttribute("address")
            if mac_address:
                mac.setAttribute("address", mac_address)

        return True

    @classmethod
    def fromLibVirt(
        cls, conn: libvirt.virConnect | str | None, name: str, quiet=False
    ) -> _self:
        """create Domain from data fetched for libvirt VM <name>.
        if <conn> is a libvirt.virConnect, it is used (but not closed)
        otherwise a temporary readonly libvirt.virConnect is established (and closed) using <conn> as the connection specification.
        if <quiet> is True, libvirt errors are suppressed (effects future libvirt invocations)
        """
        dom = lookupVM(name=name, conn=conn, quiet=quiet)
        if dom:
            try:
                return cls(dom.XMLDesc())
            except expatparser.ExpatError:
                pass

    @classmethod
    def fromXMLFile(cls, filename: str) -> _self:
        """create Domain from XML file"""
        try:
            with open(filename) as f:
                xml = f.read()
        except OSError:
            return

        try:
            return cls(xml)
        except expatparser.ExpatError:
            pass


def _main():
    import argparse

    p = argparse.ArgumentParser(
        description="print some info about a libvirt Domain (VM)",
    )
    p.add_argument(
        "--connect",
        help="libvirt connection URI",
    )

    p.add_argument(
        "name",
        help="VM to export",
    )

    args = p.parse_args()

    with libvirt.openReadOnly(args.connect) as conn:
        d = Domain.fromLibVirt(conn, args.name)
    if not d:
        raise SystemExit(f"VM {args.name!r} does not exist")
    print(d)
    print("")
    print(f"CPU: {d.getCPU()}")
    print(f"OS : {d.getOS()}")
    print(f"disks: {d.getDiskFiles()}")
    print("")
    d.anonymize()
    print(d)


if __name__ == "__main__":
    _main()
