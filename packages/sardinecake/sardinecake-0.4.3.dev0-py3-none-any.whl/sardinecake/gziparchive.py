#!/usr/bin/env python3

# gziparchive - poor mans archive with only gzip
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

# the gzip format is meant for compressing single files.
# it decidedly is **not** meant to compress multiple files and be able to
# reconstruct the individual files. this job is left for tar.
#
# nevertheless, this module tries to do exactly that:
# - compress multiple files (with no intermediate layer)
# - deflate the individual files
#
# it uses the fact that gzip streams have a header that (optionally) stores
# the original filename.
# also, gzip streams can be concatenated.
# so if we know the stream boundaries (or can guess them), we can restore the original
# files (but only the basenames)
#
# motivation: we want to be able to transmit difference files
# (for large disk images) efficiently.
#
# - our transport is OCI containers
# - to ease parallel downloads, a large file is split into multiple chunks
# - for QCOW2 we can use thin copies (which are effectively difference images)
#   to modify the large disk images without modifying the actual data.
# - for storing and downloading, we would like the original data to stay intact
#   (and reusable).
# - if we did a .tar.gz, this would modify the original data (at least the header(?))
# - since we are already chunking the data, we can conveniently start new chunks when
#   a new file is "added", thus helping the restore-process in guessing where the
#   next stream starts


import gzip
import hashlib
import logging
import os
import struct
import tempfile
import time


log = logging.getLogger("sardinecake.gziparchive")


def parseGZIPHeader(filename: str) -> dict:
    """parse the header of a filename to see if it is a GZip file
    returns a dict with the parsed information (or None)
    """
    OSs = {
        0: "FAT filesystem (MS-DOS, OS/2, NT/Win32)",
        1: "Amiga",
        2: "VMS (or OpenVMS)",
        3: "Unix",
        4: "VM/CMS",
        5: "Atari TOS",
        6: "HPFS filesystem (OS/2, NT)",
        7: "Macintosh",
        8: "Z-System",
        9: "CP/M",
        10: "TOPS-20",
        11: "NTFS filesystem (NT)",
        12: "QDOS",
        13: "Acorn RISCOS",
    }
    methods = {
        8: "DEFLATE",
    }

    FTEXT, FHCRC, FEXTRA, FNAME, FCOMMENT = 1, 2, 4, 8, 16

    def read_until_NULL(fp):
        data = None
        while True:
            s = fp.read(1)
            if not s or s == b"\000":
                break
            data = (data or b"") + s
        return data

    data = b""
    fextra = None
    fname = None
    fcomment = None
    fcrc = None
    with open(filename, "rb") as f:
        header = f.read(10)
        data += header

        try:
            (magic, method, flags, last_mtime, extra_flags, OS) = struct.unpack(
                "<HBBIBB", header
            )
        except struct.error:
            # couldn't read all data... not a GZip file
            return None
        if magic != 0x8B1F:
            # bag magic
            return None

        if flags & FEXTRA:
            # Read & discard the extra field, if present
            dat = f.read(2)
            data += dat
            (extra_len,) = struct.unpack("<H", dat)
            fextra = f.read(extra_len)
            data += fextra
            # TODO: parse extra data
        if flags & FNAME:
            # Read and discard a null-terminated string containing the filename
            fname = read_until_NULL(f)
            data += fname
        if flags & FCOMMENT:
            # Read and discard a null-terminated string containing a comment
            fcomment = read_until_NULL(f)
            data += fcomment
        if flags & FHCRC:
            # CRC16
            fcrc = f.read(2)
            data += fcrc

    result = {"magic": data[:2]}
    method = methods.get(method)
    if method:
        result["method"] = method
    if last_mtime:
        result["mtime"] = time.localtime(last_mtime)

    OS = OSs.get(OS)
    if OS:
        result["OS"] = OS

    if fextra:
        # TODO: parse extra data
        pass
    if fname:
        result["name"] = fname.decode(encoding="iso-8859-1")
    if fcomment:
        result["comment"] = fcomment.decode(encoding="iso-8859-1")
    if fcrc:
        # TODO: check CRC
        pass

    return result


def parseGZIPFooter(filename: str) -> dict:
    """parse the footer (END) of a filename assuming it is a GZip file.
    returns a dict with the parsed information (or None)
    """
    with open(filename, "rb") as f:
        try:
            f.seek(0, os.SEEK_END)
            f.seek(f.tell() - 8, os.SEEK_SET)
        except ValueErrir:
            return None
        data = f.read(8)
        return {
            "crc": data[:4],
            "size": struct.unpack("<I", data[4:]),  # size of the uncompressed data!
        }


class FileBucketReader:
    def __init__(self, indir, filenames):
        self._indir = indir
        self._filenames = iter(filenames)
        self._fd = None
        self._opened = []
        self._opened += self._next()

    def _next(self):
        if self._fd:
            self._fd.close()
        self._fd = None
        try:
            filename = next(self._filenames)
        except StopIteration:
            return False
        self._fd = open(os.path.join(self._indir, filename), "rb")
        return filename

    def read(self, size=-1):
        if not self._fd:
            if not self._next():
                # EOFs
                return b""

        if size > 0:
            ret = self._fd.read(size)
            if not ret:
                # no data read, maybe we just hit the EOF of the current file
                if not self._next():
                    return ret
                ret = self._fd.read(size)
        else:
            #  wants to read *all* data?
            ret = b""
            while self._fd:
                r = self._fd.read(size)
                if r:
                    ret += r
                else:
                    self._next()
        return ret

    def __enter__(self):
        return self

    def __exit__(self, type, value, tb):
        if self._fd:
            self._fd.close()
        self._fd = None


class FileBucketWriter:
    def __init__(self, outdir, chunksize=None):
        if chunksize and chunksize < 0:
            raise ValueError(f"chunksize must be positive or 0 (got {chunksize})")

        os.makedirs(outdir, exist_ok=True)
        self._outdir = outdir
        self._chunksize = chunksize

        self._hashes = []
        self._currentsize = 0

        self._file = None
        self._hasher = None

    def _write(self, buffer):
        bufsize = len(buffer)
        self._hasher.update(buffer)
        self._file.write(buffer)
        self._currentsize += bufsize

    def _close(self):
        if self._hasher:
            hashstr = self._hasher.hexdigest()
            self._hashes.append(hashstr)
            if self._file:
                try:
                    os.link(self._file.name, os.path.join(self._outdir, hashstr))
                    log.info(f"wrote chunk #{len(self._hashes):03}: {hashstr!r}")
                except FileExistsError:
                    # file exists; since the filename is a hash, this means that the it is the same file
                    log.info(
                        f"skipped existing chunk #{len(self._hashes):03}: {hashstr!r}"
                    )
                    pass
        self._hasher = None
        self._file = None

    def _next(self):
        """finish up the current file, open the next one"""
        self._close()

        os.makedirs(self._outdir, exist_ok=True)
        self._hasher = hashlib.new("SHA256")
        self._file = tempfile.NamedTemporaryFile(dir=self._outdir, prefix=".")
        self._currentsize = 0

    def write(self, buffer):
        """write some data"""
        bufsize = len(buffer)
        # if chunksize:
        #    sizefree = self._chunksize - self._currentsize
        #    if size < sizefree:

        if not self._file:
            self._next()

        if self._chunksize:
            while buffer:
                size = len(buffer)
                maxsize = min(size, self._chunksize - self._currentsize)

                if maxsize <= 0:
                    # currentsize => chunksize: proceed to next file
                    self._next()
                    continue

                buf = buffer[:maxsize]
                buffer = buffer[maxsize:]
                self._write(buf)
        else:
            # not chunking; just write the data to the file
            self._write(buffer)

        return bufsize

    def close(self):
        """close the remaining file-handle, return a list of created hashes"""
        self._close()
        return self._hashes

    def hashes(self):
        """return a list of created hashes so far"""
        return self._hashes

    def __enter__(self):
        return self

    def __exit__(self, type, value, tb):
        self.close()


def gzipchunked(
    infilename,
    outdirname,
    compresslevel=6,
    mtime=None,
    chunksize: int | None = None,
    name: str | None = None,
):
    """compressed the <infilename> with gzip, writing the result to <outdirname>/
    if the <outdirname> directory does not exist it will be created.
    the resulting compressed files will have a maximum size of <chunksize>,
    multiple files are created if needed.
    if chunksize is falsish, no re-chunking is performed.

    the filenames of the split gzip compressed data, is the SHA256 hexdigest of the compressed data.

    if <mtime> is falsish, it is read from <infilename> (otherwise it behaves the same as with gzip.GzipFile)
    compresslevel behaves the same as gzip.GzipFile.
    if <name> is not None, it is used for embedding the filename into the gzip stream.
    if <name> is None, <infilename> is used instead

    returns the names (hashes, without the directory) of the files written.
    """
    import shutil

    if not mtime:
        mtime = os.stat(infilename).st_mtime
    log.debug(f"gzipchunk(infile={infilename!r}, outdir={outdirname!r}, name={name!r})")
    if name is None:
        name = infilename
    count = 0
    with (
        open(infilename, "rb") as f_in,
        FileBucketWriter(outdirname, chunksize=chunksize) as f_chunky,
        gzip.GzipFile(
            filename=name,
            fileobj=f_chunky,
            mode="wb",
            compresslevel=compresslevel,
            mtime=mtime,
        ) as f_out,
    ):
        shutil.copyfileobj(f_in, f_out)
        hashes = f_chunky.hashes()
    return hashes


def gunzipchunked(indirname, outdirname, bucketfiles):
    """decompress the <bucketfiles> in <indirname> into files in <outdirname>

    the actual compressed files can be split into multiple <bucketfiles>
    <bucketfiles> must have the correct order.

    <bucketfiles> might contain multiple compressed files.
    """
    import shutil

    # partition the bucketfiles to start with a gzip header
    gzipheaders = [
        parseGZIPHeader(os.path.join(indirname, filename)) for filename in bucketfiles
    ]
    headerfiles = [
        filename for filename, headers in zip(bucketfiles, gzipheaders) if headers
    ]

    buckets = []
    metadata = []
    bucket = []
    for b, h in zip(bucketfiles, gzipheaders):
        if h:
            # start a new bucket
            bucket = []
            buckets.append(bucket)
            metadata.append(h)
        bucket.append(b)

    os.makedirs(outdirname, exist_ok=True)

    unzippedfiles = []
    for b, h in zip(buckets, metadata):
        mtime = h.get("mtime")
        name = h.get("name")
        if name:
            name = os.path.basename(name)
            outfilename = os.path.join(outdirname, name)
            f_out = open(outfilename, "wb")
        else:
            f_out = tempfile.NamedTemporaryFile(dir=outdirname, delete=False)
            outfilename = f_out.name
        with (
            FileBucketReader(indirname, b) as f_chunky,
            gzip.GzipFile(fileobj=f_chunky, mode="rb") as f_in,
        ):
            shutil.copyfileobj(f_in, f_out)
        f_out.close()
        if mtime and outfilename:
            mtime = time.mktime(mtime)
            os.utime(outfilename, times=(mtime, mtime))
        unzippedfiles.append(outfilename)

    return unzippedfiles


def _tests():
    _testdata = bytes(range(256)) * 4
    testdata = {"count": 0}

    def getOutdir():
        testcount = testdata["count"] = testdata.get("count", 0) + 1
        return f"/tmp/gzipchunk/{testcount}"

    def _test1(outpath, chunksize=None):
        outfile = FileBucketWriter(outpath, chunksize=chunksize)
        with gzip.GzipFile(filename="blabla", fileobj=outfile, mode="wb") as gz:
            gz.write(_testdata)
        hashes = outfile.close()
        print(" ".join(hashes))

    def _test2(outpath, chunksize=None):
        with (
            FileBucketWriter(outpath, chunksize=chunksize) as outfile,
            gzip.GzipFile(filename="blabla", fileobj=outfile, mode="wb") as gz,
        ):
            gz.write(_testdata)
            hashes = outfile.hashes()
        print(" ".join(hashes))

    def _test3(infilename, outpath, chunksize=None):
        with (
            open(infilename, "rb") as infile,
            FileBucketWriter(outpath, chunksize=chunksize) as outfile,
            gzip.GzipFile(filename=infilename, fileobj=outfile, mode="wb") as gz,
        ):
            gz.write(infile.read())
            hashes = outfile.hashes()
        print(" ".join(hashes))

    def _test4(infilename, outpath, chunksize=None):
        import shutil

        with (
            open(infilename, "rb") as infile,
            FileBucketWriter(outpath, chunksize=chunksize) as outfile,
            gzip.GzipFile(filename=infilename, fileobj=outfile, mode="wb") as gz,
        ):
            shutil.copyfileobj(infile, gz)
            hashes = outfile.hashes()
        print(" ".join(hashes))

    def _test5(infilename, outpath, chunksize=None):
        import shutil

        mtime = os.stat(infilename).st_mtime
        with (
            open(infilename, "rb") as infile,
            FileBucketWriter(outpath, chunksize=chunksize) as outfile,
            gzip.GzipFile(
                filename=infilename, fileobj=outfile, mode="wb", mtime=mtime
            ) as gz,
        ):
            shutil.copyfileobj(infile, gz)
            hashes = outfile.hashes()
        print(" ".join(hashes))

    def _test6(infilename, outpath, chunksize=None):
        hashes = gzipchunked(infilename, outpath, chunksize=chunksize)
        print(" ".join(hashes))

    _test1(getOutdir())
    _test1(getOutdir(), 50)
    _test2(getOutdir())
    _test2(getOutdir(), 50)
    _test3(__file__, getOutdir())
    _test3(__file__, getOutdir(), 512)
    _test4(__file__, getOutdir())
    _test4(__file__, getOutdir(), 512)
    _test5(__file__, getOutdir())
    _test5(__file__, getOutdir(), 512)
    _test6(__file__, getOutdir())
    _test6(__file__, getOutdir(), 512)


if __name__ == "__main__":
    _tests()
