`sarde` - cli tool to manage sardinecake
========================================

`sarde` provides the basic glue to use `virsh`
together with an OCI-storage.

## Working with local VM images

### List local containers - `sarde list`

List all available containers, found in the local OCI cache.
Apart from the source (currently always 'oci') and the name of the image
(as specified when `fetch`ing or `clone`ing an image), it will also print
the image ID (shared by identical containers) and the current state,
which can be either "*missing*" (if the container has not yet been `import`ed),
"*stopped*" (if the container has been imported but is not running) or
"*running*"" (if the container is currently a running as a VM).

```sh
sarde list
```

The default is to output the information in a human readable format:

```text
SOURCE  NAME                                                   IMAGE ID               STATE
oci     registry.example.org/sardines/debian@sha256:f99c5178   sha256:052bd348        stopped
oci     registry.example.org/sardines/debian:latest            sha256:052bd348           "
oci     foo.example.com/ubuntu@sha256:c44c1d53                 sha256:f2c4820d        missing
```

A more machine-friendly output can be obtained with the `--format` flag:
```sh
sarde list --format=json
```

Here the `state` is either `null` (*missing*), `false` (*stopped*) or `true` (*running*):

```json

[
  {
    "source": "oci",
    "name": "registry.example.org/sardines/debian",
    "tag": "latest",
    "digest": "sha256:f99c5178740d0cc0ddbb46ecdd50fbb89bbac69336757582224d098bb7ae69d2",
    "id": "sha256:052bd34899db1f27ea4265fa86206b3d73f28d1c35c3cc22596d3b3a5f178471",
    "state": false
  },
  {
    "source": "oci",
    "name": "foo.example.com/ubuntu",
    "tag": null,
    "digest": "sha256:c44c1d53837b1a7380c3a2aa75b601aa849f0318a03a82e4bfb0a9ca9587e010",
    "id": "sha256:f2c4820d5b9cd8e1f070dbc11cdcd154203e2bc246b6b7123469a286947d6507",
    "state": null
  }
]
```


### Import a VM from an OCI bundle - `sarde import`

Create a VM from an OCI container.

OCI containers are not runnable per se, you have to first re-assemble them into VM (disk images,...).
This is done via the `import` command.

The following will create a VM named '*mydebian*' from the local '*registry.example.org/sardines/debian:latest*' container:

```sh
sarde import -n mydebian 'registry.example.org/sardines/debian:latest'
```

If you do not specify a name for the VM, a unique name is generated automatically.
`sarde import` will return the name of the newly created VM,
so you can start it with `virsh`:

```sh
name=$(sarde import 'registry.example.org/sardines/debian:latest')
virsh start "${name}"
```


The container has to be available locally.
A convenient alternative is to use the `pull` command, which will fetch the container first if needed.




### Export a VM to an OCI bundle - `sarde export`

Convert a VM disk image to an OCI container.

This will create an OCI-container 'mydebian:latest' from the 'mydebian' VM:
```sh
sarde export --chunksize 256MiB mydebian mydebian:latest
```

This should create a (local) OCI-container 'registry.example.com/sardines/mydebian:sid' from the 'mydebian' VM:
```sh
sarde export --chunksize 256MiB mydebian 'registry.example.com/sardines/mydebian:sid'
```

Given a *chunk size*, the VM's compressed disk images will be split into chunks of the given size,
which might allow for parallel downloads.

Once a VM has been exported to an OCI-container, you can `push` it to a registry.


!!! NOTE
    If your VM uses a disk with a backing file, that backing file **must** be in the same directory
    as the depending disk image, and it **must** use a relative path.
    To make a backing file relative, you can use something like:

```sh
qemu-img rebase -F qcow2 -u -b base.img child.img
```

(Local) backing files are the recommended way for smallish updates of already existing images,
as this will allow the OCI-storage (both local and remote) to reuse existing data chunks.
Given that typical VM disks are about 50GB, this can safe considerable amount of disk space
and also speed up transmission of the OCI containers.


### Clone a VM - `sarde clone`

Creates a local virtual machine by cloning either a remote or another local virtual machine.


### Get VM config from an OCI bundle - `sarde getconfig`

This gets the meta-configuration of an OCI-container,
required to make actual use of the VM once it is running.

It contains such crucial information as valid login credentials
and available services to access the machine.

```sh
sarde getconfig 'registry.example.org/sardines/debian:latest'
```

The output is formatted as JSON, like so:

```json
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

The configuration might be empty, in which case, nothing is printed.

## Registry authentication

### Login to an OCI registry - `sarde login`

For pushing images to a registry (and sometimes for pulling),
you often need to authenticate yourself.

Do this via the `login` command.

```sh
sarde login registry.example.org
```

Once you no longer need to authenticate, `logout` again.

Registry interaction is (currently) handled by 'skopeo', which will store
credentials in `${XDG_RUNTIME_DIR}/containers/auth.json`
(which is typically an ephemeral (it doesn't survive reboots) file,
that can only be accessed by the current user).


### Logout from an OCI registry - `sarde logout`

For pushing images to a registry (and sometimes for pulling),
you often need to authenticate yourself. Do this via the `login` command.

Once you no longer need to authenticate, `logout` again.


```sh
sarde logout registry.example.org
```


## Storing/retrieving VM images to/from an OCI registry

### Push a VM to a registry - `sarde push`


Push a container from the local OCI cache (e.g. previously `export`ed from a VM),
to a remote registry.
Most likely you will have to `login` first, in order to be allowed to push.
By default, the local container name is used to determine the destination.

E.g. a container named 'registry.example.org/sardines/debian:stable' will be pushed to the 'registry.example.org'
host as 'sardines/debian:stable':

```sh
sarde push 'registry.example.org/sardines/debian:stable'
```

You can specify a different destination with the `--target` flag.

```sh
sarde push --target 'registry.example.org/sardines/debian:latest' 'registry.example.org/sardines/debian:bookworm'
```

This is especially useful, if the local OCI container does not point to a registry:

```sh
sarde push --target 'registry.example.org/sardines/debian:latest' 'debian:bookworm'
```


### Fetch a VM from the registry - `sarde fetch`

Download a VM image from the registry, and store it in the OCI cache
(as specified via the `--ocidir` flag).

```sh
sarde fetch 'registry.example.org/sardines/debian:latest'
```

This will fetch the given image and store it as a number of blobs under
'${ocidir}/registry.example.org/sardines/debian/'.


Use `import` to create the actual VM from these blobs:

```sh
sarde fetch 'registry.example.org/sardines/debian:latest'
sarde import 'registry.example.com/sardines/debian:latest'
```


### Pull VM from a registry, and import it - `sarde pull`

This is a simple shortcut that combines
`sarde fetch` (fetching an OCI container from a repository)
and `sarde import` (import a VM from a local OCI container).

E.g.
```sh
sarde pull 'registry.example.org/sardines/debian:latest'
```

Is equivalent to

```sh
sarde fetch 'registry.example.org/sardines/debian:latest'
sarde import 'registry.example.com/sardines/debian:latest'
```


## misc

### `sarde selftest`

Test logging with verbosity and whatelse.
