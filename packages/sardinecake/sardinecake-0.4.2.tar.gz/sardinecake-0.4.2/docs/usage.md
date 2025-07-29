Usage
=====

## Installation

To use sardinecake, first install it using pip:

```console
(.venv) $ pip install sardinecake
```

### Dependencies
`sardinecake` has a number of dependencies. the noteable ones are
- `skopeo` a cmdline tool to handle OCI containers (**must** be installed separately)
- `libvirt-python` interacting with libvirt (most likely you will need to be able to
   compile and link against `libvirt` for this; you will need `libvirt-dev` more)
- `pyqcow` (optional) library for interacting with QEMU CoW disk image files

When running a Debian based system, it is probably easiest to just install
the system provided packages and allow your virtualenv to use them:

```sh
VENV=.
sudo apt-get install \
         skopeo qemu-utils \
         python3-libvirt python3-magic \
         python3-paramiko python3-jsonschema
virtualenv --system-site-packages ${VENV}
. ${VENV}/bin/activate
```


## Using VMs

1. (login to a registry for read permissions with `sarde login` (once))
2. *fetch* the VM with `sarde fetch`
3. *import* the VM with `sarde import`
4. start the VM


```sh
export LIBVIRT_DEFAULT_URI=qemu:///system
sarde login registry.example.org
sarde fetch registry.example.org/sardines/debian12:latest
name=$(sarde import registry.example.org/sardines/debian12:latest)
virsh start "$(name)"
```

As can be seen, `import` returns the name of the created VM,
so you can easily start the VM afterwards.

For convenience, the `pull` command combines `fetch` and `import`.
So mostly, you should be able to simply do:

```sh
name=$(sarde pull registry.example.org/sardines/debian12:latest)
virsh start "$(name)"
```

!!! note

    By default, `sarde import` (and thus `sarde pull`) generates a
    unique VM name, based entirely on the VM data (disks and configuration).
    This is nice in automated environments (where you cannot manually intervene
    to guarantee uniqueness of the name), but comes at the expense of names
    that are not human friendly.

## Creating new VMs

1. Prepare your VM in libvirt.
2. *export* the VM with `sarde export`
3. (login to a registry for write permissions with `sarde login` (once))
4. *publish* the VM with `sarde push`

```sh
export LIBVIRT_DEFAULT_URI=qemu:///system
sarde login registry.example.org
sarde export --tag registry.example.org/sardines/debian12:latest debian12
sarde push registry.example.org/sardines/debian12:latest
```

### Restrictions

You probably should only *export* VMs that are **shut down**.

When using copy-on-write thin copies for disk images, make sure that:

- they live in the same directory as their backing files (all of them)

- the backing images are references via relative paths (all of them)

You can check whether these requirements are met by using
```sh
disk="mydisk.qcow2

! qemu-img info --backing-chain "${disk}" \
        | egrep "^backing file:" \
        | sed -e 's|\s*(actual path: .*)||' \
        | grep "/" \
|| (echo "disk image must use relative paths!"; false)
```

(LATER this restriction might eventually be resolved by `sarde` automatically
converting the backing-chain).

## Configuration

You can provide a default configuration in `~/.config/sardinecake/sarde.ini` and `/etc/sardinecake/sarde.ini`.
You can provide different configurations for each sub-command (by using a section named like the subcommand),
though in practice this is probably of little use, as all sub-commands inherit the configuration from the `[DEFAULT]` section.

They keys in the configuration files are the same as the long option names without the leading double-dash.
So `sarde list --connect qemu:///system` is equivalent to using:

```ini
[list]
connect = qemu:///system
```

You can provide an alternative configuration file by setting the `SARDE_CONF_FILES` environment variable to
a list of colon-separated filenames:

```sh
export SARDE_CONF_FILES=mysarde.ini
sarde list
```

See [examples/sarde.ini](https://git.iem.at/devtools/sardinecake/-/blob/main/examples/sarde.ini)
