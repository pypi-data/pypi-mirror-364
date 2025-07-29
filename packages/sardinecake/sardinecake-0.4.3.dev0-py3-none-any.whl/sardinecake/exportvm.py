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


# export a libvirt VM into an OCI bundle

import datetime
import hashlib
import json
import logging
import os
import tempfile
import time


import libvirt

try:
    from .domain import Domain
    from . import gziparchive as gz
    from . import qcow
    from . import utils
except ImportError:
    from domain import Domain
    import gziparchive as gz
    import qcow
    import utils


log = logging.getLogger("sardinecake.exportvm")


def export2json(data, outdir):
    """encodes <data> to JSON and writes it to outdir, using the hash of the content as filename.
    returns a (hash, filesize) tuple"""
    jdata = json.dumps(data, indent=2)
    name = hashlib.sha256(jdata.encode()).hexdigest()
    with open(os.path.join(outdir, name), "w") as f:
        size = f.write(jdata)
    return (name, size)


def checkRelativeDiskimages(disks: list) -> bool:
    errors = 0
    for disk in disks:
        try:
            imagechain = list(qcow.QCOW(disk).getBackingChain(normalize=False))
        except:
            log.exception("problems with getting the backing chain")
            imagechain = [disk]
        baseimage = imagechain[0]
        basedir = os.path.dirname(baseimage)
        backingimages = imagechain[1:]
        for idx, backimage in enumerate(backingimages):
            backdir = os.path.dirname(backimage)
            if not backdir:
                continue
            errors += 1
            log.error(
                f"backing file #{idx} for {baseimage!r} in {basedir!r} in the wrong directory!"
            )
            if os.path.abspath(os.path.join(basedir, backdir)) == os.path.abspath(
                basedir
            ):
                # backing file lives in the same directory as the original image,
                # but nevertheless uses a path
                # this can be easily fixed with 'qemu-img'
                log.error(
                    f"""You can make the backing file relative with the following command:
```
qemu-img rebase -F qcow2 -u -b {os.path.basename(backimage)!r} {os.path.abspath(baseimage)!r}
```"""
                )
            else:
                log.error(
                    f"""Disk image and backing file live in different directories
Use something like the following to fix this:
```
mv {os.path.abspath(os.path.join(basedir, backdir))!r} {os.path.abspath(basedir)!r}
qemu-img rebase -F qcow2 -u -b {os.path.basename(backimage)!r} {os.path.abspath(baseimage)!r}
```"""
                )
    return errors == 0


def _exportVM(
    vmname: str,
    outdir=".",
    libvirtURI: str | None = None,
    chunksize: int | None = None,
    vmconfig: dict = {},
    libvirtconfigfile: str | None = None,
    quiet: bool = False,
    allow_absolutebaseimages: bool = False,
) -> tuple[str, str] | None:
    """export a libvirt VM into an OCI compatible bundle.
    returns the SHA256 hash of the manifest file and the config file.
    or None (if something went wrong)
    """

    def chunkzip(filename, outdir, chunksize, mimetype=None, name=None):
        if mimetype is None:
            mimetype = utils.mimetype(filename)
        if mimetype:
            mimetype = f"{mimetype}+gzip"
        chunks = gz.gzipchunked(filename, outdir, chunksize=chunksize, name=name)
        layers = []
        for c in chunks:
            chunk_stat = os.stat(os.path.join(outdir, c))
            layer = {
                "digest": f"sha256:{c}",
            }
            if mimetype:
                params = ""
                if layers:
                    params = f";chunk={len(layers)}"
                layer["mediaType"] = mimetype + params
            layer["size"] = chunk_stat.st_size

            layers.append(layer)
        return layers

    def timestamp2iso(timestamp):
        ts = datetime.datetime.fromtimestamp(
            timestamp, datetime.datetime.now().astimezone().tzinfo
        )
        return ts.isoformat()

    mtime = None
    newimages = {}
    newdisks = {}
    layers = []
    history = []
    diffids = []

    config = {}
    image_cfg = {}

    if libvirtconfigfile:
        domain = Domain.fromXMLFile(libvirtconfigfile)
    else:
        domain = Domain.fromLibVirt(libvirtURI, vmname, quiet=quiet)
    if not domain:
        log.fatal(f"VM {vmname} not found!")
        return

    image_cfg = {
        "architecture": domain.getCPU(),
        "os": domain.getOS(),
        "created": None,
    }

    disks = domain.getDiskFiles()
    if not disks:
        raise KeyError(f"VM {vmname!r} does not have any exportable disks")

    # check if disk images are good
    if not checkRelativeDiskimages(disks.values()):
        if allow_absolutebaseimages:
            log.warning("Proceeding despite possible problems with disk images")
        else:
            log.fatal("Refusing to export with problematic disk images")
            return

    os.makedirs(outdir, exist_ok=True)

    # layer #1: the libvirt VM definition (added at the end)

    # layer #2: vm sardine config (username, password,...)
    if vmconfig:
        vmcfg = export2json(vmconfig, outdir)
        layers += [
            {
                "digest": f"sha256:{vmcfg[0]}",
                "mediaType": "application/vnd.sardinecake.vm.config.v1+json",
                "size": vmcfg[1],
            }
        ]
        history += [
            {
                "created": timestamp2iso(time.time()),
            }
        ]
        diffids.append(f"sha256:{vmcfg[0]}")

    # layer #3..N: disks
    for dev, diskimage in disks.items():
        try:
            imagechain = reversed(qcow.QCOW(diskimage).getBackingChain())
        except:
            log.debug(f"couldn't get backing chain for {diskimage!r}", exc_info=True)
            imagechain = [diskimage]

        basename = None
        for d in imagechain:
            basename = os.path.basename(d)
            n, x = os.path.splitext(basename)
            infix = ""
            while f"{n}{infix}{x}" in newimages:
                if not infix:
                    infix = 0
                infix -= 1
                basename = f"{n}{infix}{x}"
                log.error(f"{d!r} already exists...adding to {basename}")

            if not d:
                log.error(f"incomplete backing chain for {diskimage!r}")
                continue
            # store the hash of the uncompressed data
            log.info(f"hashing {d!r}")
            with open(d, "rb") as f:
                digest = hashlib.file_digest(f, "sha256")
                diffids.append(f"sha256:{digest.hexdigest()}")
                history += [
                    {
                        "created": time.time(),  # os.stat(d).st_mtime,
                        "created_by": f"gzip -6 -c {os.path.basename(d)} | split -b {chunksize} {os.path.basename(d)}.gz # approximately",
                    }
                ]
            log.info(f"chunkzipping {d!r} as {basename}")
            layers += chunkzip(d, outdir, chunksize=chunksize, name=basename)
            newimages[basename] = True
        if basename:
            newdisks[dev] = basename

    domain.changeDiskFiles(newdisks)
    domain.anonymize()

    # layer #1: VMconfig
    vmconfig = domain.toXML()
    vmconfig_hash = hashlib.sha256(vmconfig.encode()).hexdigest()
    with open(os.path.join(outdir, vmconfig_hash), "w") as f:
        vmconfig_size = f.write(vmconfig)
        layers.insert(
            0,
            {
                "digest": f"sha256:{vmconfig_hash}",
                "mediaType": "application/vnd.libvirt.domain.config+xml",  # isn't there a real mimetype?
                "size": vmconfig_size,
            },
        )
        history.insert(
            0,
            {
                "created": timestamp2iso(time.time()),
                "created_by": f"virsh dumpxml {vmname!r}",
            },
        )
        diffids.insert(
            0,
            f"sha256:{vmconfig_hash}",
        )

    # mtime = max(_["mtime"] for _ in alldisks)
    if diffids:
        image_cfg["rootfs"] = {
            "type": "layers",  # not really true!
            "diff_ids": diffids,
        }

    if history:
        image_cfg["history"] = history

    if mtime:
        mtimestamp = datetime.datetime.fromtimestamp(
            mtime, datetime.datetime.now().astimezone().tzinfo
        )
        image_cfg["created"] = timestamp2iso(mtime)
    else:
        image_cfg["created"] = timestamp2iso(time.time())

    if not image_cfg["created"]:
        del image_cfg["created"]

    # finally write the image configuration
    imageconfig_hash, imageconfig_size = export2json(image_cfg, outdir)
    config = {
        "digest": f"sha256:{imageconfig_hash}",
        "mediaType": "application/vnd.oci.image.config.v1+json",
        "size": imageconfig_size,
    }

    # and write the manifest
    manifest = {
        "config": config,
        "layers": layers,
        "mediaType": "application/vnd.oci.image.manifest.v1+json",
        "schemaVersion": 2,
    }

    manif_hash, _ = export2json(manifest, outdir)

    return (manif_hash, imageconfig_hash)


def exportvm(
    vmname: str,
    outdir: str,
    libvirtURI: str | None = None,
    chunksize: int | None = None,
    vmconfig: dict = {},
    libvirtconfigfile: str | None = None,
    quiet: bool = False,
) -> str | None:
    """export a libvirt VM into an OCI compatible bundle.
    returns the hashdigest of the config
    or None.
    """
    # after a successful run we have:
    """
<outdir>/
<outdir>/oci-layout
<outdir>/index.json
<outdir>/blobs/sha256/<sha>   -> application/vnd.oci.image.manifest.v1+json
<outdir>/blobs/sha256/<sha:a> -> application/vnd.oci.image.config.v1+json
<outdir>/blobs/sha256/<sha:b> -> application/vnd.iem.sarde.config.v1+xml
<outdir>/blobs/sha256/<sha:x> -> application/application/x-qemu-disk+gzip
<outdir>/blobs/sha256/<sha:y> -> application/application/x-qemu-disk+gzip
<outdir>/blobs/sha256/<sha:z> -> application/application/gzip
[...]
    """
    # extract optional <tag> from container
    outcontainerdir, tag = utils.split_imagetag(outdir)
    if not issubclass(type(tag), str):
        tag = None

    oci_layout = {
        "imageLayoutVersion": "1.0.0",
    }
    container_index = {
        "schemaVersion": 2,
        "manifests": [],
    }

    if all([libvirtURI, libvirtconfigfile]):
        raise ValueError(
            f"libvirt connection {libvirtURI!r} and configuration {libvirtconfigfile!r} are mutually exclusive"
        )

    if not outcontainerdir:
        raise ValueError(f"output directory must not be empty: {outdir!r}")

    os.makedirs(outcontainerdir, exist_ok=True)

    (manifest_hash, imageconfig_hash) = (None, None)
    try:
        chunksdir = os.path.join(outcontainerdir, "blobs", "sha256")

        result = _exportVM(
            vmname,
            outdir=chunksdir,
            libvirtURI=libvirtURI,
            libvirtconfigfile=libvirtconfigfile,
            vmconfig=vmconfig,
            chunksize=chunksize,
            quiet=quiet,
        )
        try:
            manifest_hash, imageconfig_hash = result
        except TypeError:
            manifest_hash = imageconfig_hash = None
        if not imageconfig_hash:
            raise utils.TryException

        # read old oci-layout
        try:
            with open(os.path.join(outcontainerdir, "oci-layout"), "r") as f:
                oci_layout = json.load(f)
        except FileNotFoundError:
            pass
        except Exception as e:
            log.debug("Unable to read old oci-layout index", exc_info=True)

        # read old image manifest
        try:
            with open(os.path.join(outcontainerdir, "index.json"), "r") as f:
                container_index = json.load(f)
        except FileNotFoundError:
            pass
        except Exception as e:
            log.debug("Unable to read old container index", exc_info=True)

        manifest_stat = os.stat(os.path.join(chunksdir, manifest_hash))
        manifest = {
            "mediaType": "application/vnd.oci.image.manifest.v1+json",
            "digest": f"sha256:{manifest_hash}",
            "size": manifest_stat.st_size,
        }
        if tag:
            manifest["annotations"] = {
                "org.opencontainers.image.ref.name": tag,
            }

        container_index["manifests"].append(manifest)

        with open(os.path.join(outcontainerdir, "oci-layout"), "w") as f:
            json.dump(oci_layout, f, indent=2)

        with open(os.path.join(outcontainerdir, "index.json"), "w") as f:
            json.dump(container_index, f, indent=2)

    except utils.TryException:
        pass
    finally:
        utils.rmdirs(outcontainerdir, ["", "blobs", "sha256"])

    return imageconfig_hash


def _main():
    import argparse

    p = argparse.ArgumentParser(
        description="export a libvirt VM to an OCI-compliant directory.",
    )
    p.add_argument(
        "--connect",
        help="libvirt connection URI",
    )
    p.add_argument(
        "-o",
        "--outdir",
        default=".",
        help="output directory",
    )
    p.add_argument(
        "--chunksize",
        type=int,
        default=1024 * 1024,
        help="chunksize (in bytes)",
    )
    p.add_argument(
        "name",
        help="VM to export",
    )

    args = p.parse_args()

    x = exportvm(args.name, libvirtURI=args.connect, chunksize=args.chunksize)
    print(x)


if __name__ == "__main__":
    _main()
