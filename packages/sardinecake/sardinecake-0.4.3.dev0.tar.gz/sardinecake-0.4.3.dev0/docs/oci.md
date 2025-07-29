sardinecake OCI containers
==========================

`sardinecake` uses the OCI-container format to store disk images and VM configuration.

A typical (smallish) container would have the following manifest:

```json
{
  "config": {
    "digest": "sha256:052bd34899db1f27ea4265fa86206b3d73f28d1c35c3cc22596d3b3a5f178471",
    "mediaType": "application/vnd.oci.image.config.v1+json",
    "size": 752
  },
  "layers": [
    {
      "digest": "sha256:f0d6b024ef42e77e8bc2714a69dcfa2466c4bb31948889fd7ef742fe922c0dca",
      "mediaType": "application/vnd.libvirt.domain.config+xml",
      "size": 1729
    },
    {
      "digest": "sha256:a42e6a4ec25b86998da12e93abc581bc8472d7342a104bbcd985ff7e53e60684",
      "mediaType": "application/vnd.sardinecake.vm.config.v1+json",
      "size": 188
    },
    {
      "digest": "sha256:54990f2c632851ed694fb276934fd2f5cfdd57ceb323a9ea1d3ef883a81af5e5",
      "mediaType": "application/x-qemu-disk+gzip",
      "size": 268435456
    },
    {
      "digest": "sha256:5b3512357721a0b7ad1a28740c6f216cf853aeec7760d6336d401beb2b166df2",
      "mediaType": "application/x-qemu-disk+gzip;chunk=1",
      "size": 48001939
    },
    {
      "digest": "sha256:9a17ea48c875b3b6132ecf14b9ef606a3a33538cb72b704169fa867daba80f12",
      "mediaType": "application/x-qemu-disk+gzip",
      "size": 118426563
    }
  ],
  "mediaType": "application/vnd.oci.image.manifest.v1+json",
  "schemaVersion": 2
}
```

## layers

There are a couple of layers found in a typical sardinecake container.

The `application/vnd.libvirt.domain.config+xml` and `application/x-qemu-disk+gzip`
layers describe a full libvirt VM (configuration + disks).
The `application/vnd.sardinecake.vm.config.v1+json` describes how you can
interact with such a machine.

### `application/vnd.libvirt.domain.config+xml`

This is libvirt's VM configuration, as obtained via `virsh dumpxml`.

!!! note
    when creating a VM, you shouldn't overly optimize it for your local libvirt host -
    one of the ideas of `sardinecake` is to provide VM images that run "anywhere".

    Apart from requiring minimal resources, the CPU should typically be set to something
    like `host-passthrough`.

### `application/x-qemu-disk+gzip`

virtual disk images are gzip compressed individually and can be split into multiple chunks.
The example above contains two qemu disk images.
The first image consists of two chunks `54990f2c` and `5b351235`, which must be concatenated
and gunzipped.
The 2nd image consists of a single chunk `9a17ea48`, which only needs to be gunzipped as is.
The name of each disk image files is stored in the metadata in the head of the gzip data.

#### to tar or not to tar
the serialization of the disk images is somewhat non-standard.
considerations for the format were:

- compressible
    - VM images are typically large, we want to save as much space as possible
- chunkable
    - even compressed images are still large.
      To better handle interrupted uploads and to be able to parallelize downloads,
      files can be split
- allows one to recover the original filename of each file
    - we need to somehow link the image filenames in the libvirt XML to our chunks
- adding new files should not change existing chunks
    - VMs can be extended with new disks, or updated with via difference CoW images.
      We do not want to create new filenames for all the content-addressed layers,
      just because the header of the archive grew a few bytes.

The first three items can be done with `tar`.
However, the 4th item is a bit more complicated, as tar is typically applied *before*
gzipping the entire archive.

This is (and the fact that `gzip` handily stores the filename inside the zipped file)
was the reason why the low-level chunking of individually gzipped files was selected.

!!! LATER
    we probably should switch to concatenated tar archives (`tar --concatenate`),
    which appears to be a somewhat more standardized way to achieve the same thing
    (although still brittle).


### `application/vnd.sardinecake.vm.config.v1+json`
This optional JSON file describes how to access the machine,
e.g. which users are present (and what are their passwords),
and which remote access services are available.

E.g. the following describes a typical vagrant box (user/password are all *vagrant*),
that is accessible via `ssh` on port *22*.:

```JSON
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
```

The full schema description of this file can be found in
[src/sardinecake/schema/sardineconfig.schema.json](https://git.iem.at/devtools/sardinecake/-/blob/main/src/sardinecake/schema/sardineconfig.schema.json).
