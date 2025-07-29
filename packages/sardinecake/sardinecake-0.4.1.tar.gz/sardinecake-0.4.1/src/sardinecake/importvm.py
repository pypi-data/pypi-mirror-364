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


# import a libvirt VM into an OCI bundle

import hashlib
import json
import logging
import os

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


log = logging.getLogger("sardinecake.importvm")


def digest_to_path(digest: str, ocidir: str = "") -> str:
    """convert a digest (e.g. 'sha256:12345') into a path <ocidir>/blobs/<hashtype>/<digest>"""
    pathcomponents = [ocidir, "blobs"]
    pathcomponents += digest.split(":", maxsplit=1)
    return os.path.join(*pathcomponents)


def check_manifest(m: dict, tag: str | None = None, ocidir: str = "") -> str:
    """check if manifest <m> as found in the OCIindex is usable; returns the path to the manifest"""
    digest = None
    if issubclass(type(tag), (list, tuple)):
        digest = ":".join(tag)
        tag = None

    if digest and m.get("digest") != digest:
        return
    if tag and m.get("annotations", {}).get("org.opencontainers.image.ref.name") != tag:
        return
    manifest_path = digest_to_path(m["digest"], ocidir=ocidir)
    if os.path.exists(manifest_path):
        return manifest_path
    log.error(f"manifest not found at {manifest_path!r}")


def getOCIindex(ocidir: str) -> dict:
    """get OCI-index (which includes information on all tags)"""
    # read metadata
    try:
        with open(os.path.join(ocidir, "oci-layout")) as f:
            oci_layout = json.load(f)
        with open(os.path.join(ocidir, "index.json")) as f:
            index = json.load(f)
    except FileNotFoundError as e:
        log.fatal(f"{ocidir} does not look like an OCI-compliant directory: {e}")
        return
    except json.decoder.JSONDecodeError as e:
        log.fatal(f"invalid JSON data in {ocidir!r}: {e}")
        return
    return index


def getOCImanifest(tag: str | None, index: dict, ocidir: str) -> dict:
    """get the manifest for the given tag from the <index> (as returned by getOCIindex()"""
    manifests = index.get("manifests")
    if not manifests:
        log.fatal("no manifests in the container")
        return

    manifest_info = None
    manifest_path = None
    for m in reversed(manifests):
        manifest_path = check_manifest(m, tag=tag or "latest", ocidir=ocidir)
        if manifest_path:
            manifest_info = m
            break

    if not manifest_info and not tag:
        # if the user did not request a specific tag, and there's no 'latest' manifest,
        # just pick the one added last
        m = manifests[-1]
        manifest_path = check_manifest(m, tag=None, ocidir=ocidir)
        if manifest_path:
            manifest_info = m

    if not manifest_info:
        log.fatal("no usable manifest found")
        return

    try:
        with open(manifest_path) as f:
            manifest = json.load(f)
    except OSError:
        log.fatal(f"could not read manifest {manifest_path!r}")
        return
    except json.decoder.JSONDecodeError as e:
        log.fatal(f"invalid JSON data in manifest {manifest_path}: {e}")
        return

    return manifest


def getOCIconfig(manifest: dict, ocidir: str) -> tuple[str, dict]:
    """get the image configuration from a manifest (as returned by getOCImanifest)"""
    config = manifest["config"]
    oci_config_name = config["digest"]
    oci_config = digest_to_path(oci_config_name, ocidir=ocidir)

    if config["mediaType"] != "application/vnd.oci.image.config.v1+json":
        log.fatal(f"unknown mediaType for config: {config['mediaType']!r}")
        return

    try:
        with open(oci_config) as f:
            oci_config = json.load(f)
    except OSError:
        log.fatal(f"could not read oci-config {oci_config!r}")
        return
    except json.decoder.JSONDecodeError as e:
        log.fatal(f"invalid JSON data in oci-config {oci_config!r}: {e}")
        return

    return (oci_config_name, oci_config)


def getOCIlayers(manifest: dict, ocidir: str) -> dict[str, list[str]]:
    """get the layers from the manifest in a mediaType -> [paths] dictionary.
    returns None if there's an error (like a non-existing layer file
    """
    layers = {}
    for lay in manifest.get("layers", []):
        laytype = lay.get("mediaType").split(";")[0]
        laypath = digest_to_path(lay.get("digest"), ocidir=ocidir)
        if not os.path.exists(laypath):
            log.fatal(f"layer {laypath!r} does not exist")
            return
        layers[laytype] = layers.get(laytype, []) + [laypath]
    return layers


def _importVM(
    domain: Domain,
    outdir=".",
    libvirtURI: str | None = None,
    gzipdata=[str],
    quiet: bool = False,
) -> str | None:
    """import a libvirt VM from an OCI compatible bundle.
    returns (name, UUID) of the newly created VM (or None)
    """

    if quiet:
        libvirt.registerErrorHandler((lambda ctx, err: 1), None)

    outdir = os.path.abspath(outdir)
    disks = domain.getDiskFiles()
    log.debug(f"disks: {disks}")
    absdisks = {
        k: v if os.path.isabs(v) else os.path.join(outdir, v) for k, v in disks.items()
    }
    log.debug(f"-> absdisks: {absdisks}")
    domain.changeDiskFiles(absdisks)

    name = domain.getName()

    uuid = None
    with libvirt.open(libvirtURI) as conn:
        olddom = Domain.fromLibVirt(conn, name)
        if olddom:
            log.info(f"VM {name} already exists")
            return (olddom.getName(), olddom.getUUID())
        try:
            x = conn.defineXML(str(domain))
            uuid = (x.name(), x.UUIDString())
        except:
            log.exception(f"couldn't create VM {name}")
            return

    if gzipdata:
        gzipdir = os.path.split(gzipdata[0])[0]
        gzipchunks = [os.path.split(_)[1] for _ in gzipdata]
        try:
            gz.gunzipchunked(gzipdir, outdir, gzipchunks)
        except:
            log.exception(f"failed to extract data into {outdir!r}")
            raise SystemExit("failed to extract data")

    return uuid


def importvm(
    ocidir: str,
    outdir: str | None = "./",
    name: str | bool = False,
    libvirtURI: str | None = None,
    quiet: bool = False,
) -> str | None:
    """import a libvirt VM from an OCI compatible bundle.

    if <name> is True, it uses the original name of the VM.
    if <name> is False (or falsish otherwise,  e.g. ''), it uses the SHA256 of the OCI-bundle as the name
    if <outdir> ends with "/", the files are put into a VMnamed subdirectory therein.

    returns the path to the bundle (a subdirectory of <outdir>).
    or None.
    """
    # after a successful run we have:
    """
    <outdir>/<name>/disk1.qemu
    <outdir>/<name>/disk2.qemu
    """
    # resp
    """
    <outdir>/disk1.qemu
    <outdir>/disk2.qemu
    """
    if "/" in (str(name)):
        raise ValueError(f"invalid VM name {name!r}")

    if not outdir:
        outdir = "./"

    ocidir, tag = utils.split_imagetag(ocidir)

    # read metadata
    index = getOCIindex(ocidir)
    if not index:
        return
    manifest = getOCImanifest(tag, index, ocidir)
    if not manifest:
        return

    config_type = manifest.get("config", {}).get("mediaType")
    if config_type != "application/vnd.oci.image.config.v1+json":
        log.fatal(
            f"manifest {manifest_path!r} has invalid OCI image configuration of type {config_type!r}"
        )
        return

    try:
        oci_config_name, oci_config = getOCIconfig(manifest, ocidir)
    except TypeError:
        return

    layers = getOCIlayers(manifest, ocidir)

    domain = None
    libvirt_config = layers.get("application/vnd.libvirt.domain.config+xml")
    if libvirt_config:
        domain = Domain.fromXMLFile(libvirt_config[0])

    if not domain:
        log.fatal(f"couldn't read VM information from {libvirt_config}")
        return

    gzipdata = []
    for k, v in layers.items():
        if k.endswith("+gzip"):
            gzipdata += v

    if name is True:
        name = domain.getName()
        log.debug(f"use original name {name!r}")
    elif not name:
        name = oci_config_name
        domain.changeName(name)
        log.debug(f"use digest name {name!r}")
    else:
        domain.changeName(name)
        log.debug(f"use explicit name {name!r}")

    if not os.path.split(outdir)[1]:
        outdir = os.path.join(outdir, name)

    log.debug(f"importing VM {name!r} to {outdir!r} using chunks {gzipdata}")

    os.makedirs(outdir, exist_ok=True)
    uuid = _importVM(
        domain, outdir=outdir, libvirtURI=libvirtURI, gzipdata=gzipdata, quiet=quiet
    )
    return uuid


def getconfig(ocidir: str) -> dict:
    """get sardinecake configuration from the container at <ocidir>"""
    ocidir, tag = utils.split_imagetag(ocidir)

    # read metadata
    index = getOCIindex(ocidir)
    if not index:
        return
    manifest = getOCImanifest(tag, index, ocidir)
    if not manifest:
        return

    config_type = manifest.get("config", {}).get("mediaType")
    if config_type != "application/vnd.oci.image.config.v1+json":
        log.fatal(
            f"manifest {manifest_path!r} has invalid OCI image configuration of type {config_type!r}"
        )
        return

    try:
        oci_config_name, oci_config = getOCIconfig(manifest, ocidir)
    except TypeError:
        return

    layers = getOCIlayers(manifest, ocidir)
    if layers is None:
        return
    config = layers.get("application/vnd.sardinecake.vm.config.v1+json")
    if not config:
        return
    for c in config:
        with open(c) as f:
            return json.load(f)


def _main():
    import argparse

    p = argparse.ArgumentParser(
        description="import a libvirt VM from an OCI-compliant directory. (such as created by 'sarde export')",
    )
    p.add_argument(
        "--connect",
        help="libvirt connection URI",
    )
    p.add_argument(
        "-n",
        "--name",
        help="VM name to create (DEFAULT: the sha256 of the OCI); specify an empty value ('') to use the original VM name",
    )

    p.add_argument(
        "-o",
        "--outdir",
        default="./",
        help="directory to create VM-files in (use a trailing slash to create a VMnamed directory within)",
    )

    p.add_argument(
        "ocidir",
        help="OCI-compliant directory to import VM from",
    )

    args = p.parse_args()

    x = importvm(
        args.ocidir, outdir=args.outdir, name=args.name, libvirtURI=args.connect
    )
    print(x)


if __name__ == "__main__":
    _main()
