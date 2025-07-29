sardine cake - managing libvirt via OCI registries
==================================================

this is a framework inspired by [tart](https://github.com/cirruslabs/tart) for
sharing libvirt VMs via  OCI-compatible container registries.

the user-facing program shall be called `sarde` (or `sard`?), as it sounds
similar to `tart`.

the "sardine" as inspired by the [libvirt](https://libvirt.org) logo,
the "sardine cake" (or fishcake) is some kind of gross-ish (i think, but idk)
tarte.

(`quiche` would have been a nice bow to QEMU, but that is already taken.
`sardine` itself is taken as well)


# Motivation

The main motivation for `sarde` comes from running isolated *Continuous Integration* (CI) jobs
within Virtual Machines (VMs).

When setting up such a system (e.g. using `GitLab-CI`) you quickly notice that you need
a way to distribute VM images to the various runners, so that they all use the same VMs.
Ideally the same mechanism can be used for the CI-users to specify the image to run their jobs on.

Most CI jobs run in isolated *Linux* containers via `docker`, that solves this issue very nicely.

Unfortunately, this doesn't work so well for non-Linux containers.
AFAIK, even when running `docker` on *macOS* or *Windows*, inside the containers you are still on *Linux*.

For *macOS* (on Apple Silicon), [Cirrus Labs](https://cirruslabs.org/) have released their fantastic
[tart](https://github.com/cirruslabs/tart) toolset, which works very similar to `docker` but instead
uses full-fledged VMs.
I especially like, that they adopted the [Open Container Initiative](https://opencontainers.org/) (OCI) approach
for distributing VM images (OCI evolved from *Docker*, so Docker registries are a subset of OCI registries.
The differences are so small that many registry providers to be used with Docker can be used as
arbitrary OCI compliant registries).

For *Windows*, I'm not aware of a similar solution.
This is where `sarde` comes into play.
It tries to be as general as possible, building on top of `libvirt`.
(So it should be usable with all the virtualization solutions supported by `libvirt`.
In practice we only test qemu/kvm, though).

As such, `sarde` is not concerned with *running* VMs:
this is already handled well enough by `libvirt`.



# Usage

## Using VMs

1. (login to a registry for read permissions with `sarde login` (once))
2. *fetch* the VM with `sarde pull`
3. *import* the VM with `sarde import`
4. start the VM


```sh
export LIBVIRT_DEFAULT_URI=qemu:///system
sarde login registry.example.org
sarde fetch registry.example.org/sardines/debian12:latest
name=$(sarde import registry.example.org/sardines/debian12:latest)
virsh start "$(name)"
```

As can be seen `sarde import` returns the name of the created VM,
so you easily start the VM afterwadrs.

For convenience, the `pull` command combines `fetch` and `import`.
So mostly, you should be able to simply do:

```sh
name=$(sarde pull registry.example.org/sardines/debian12:latest)
virsh start "$(name)"
```

### notes
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

### restrictions

You probably should only *export* VMs that are **shut down**.

When using copy-on-write thin copies for disk images, makes sure that
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
So `sarde list --connect qemu:///system` is equivalent to using

```
[list]
connect = qemu:///system
```

You can provide an alternative configuration file by setting the `SARDE_CONF_FILES` environment variable to
a list of colon-separated filenames:

```sh
export SARDE_CONF_FILES=mysarde.ini
sarde list
```

See [examples/sarde.ini](examples/sarde.ini)

# gitlab-runner integration

The `gitlab-sardinecake-executor` can be used for running GitLab-CI jobs within VMs managed by sardinecake.

## Configuration

#### gitlab-runner

Tell `gitlab-runner` to use `sardinecake` as the custom executor:

```toml
[[runners]]
  # ...
  builds_dir = "/home/vagrant/build"
  cache_dir = "/home/vagrant/cache"
  executor = "custom"

  [runners.custom]
    config_exec = "gitlab-sardinecake-executor"
    config_args = [ "config" ]
    prepare_exec = "gitlab-sardinecake-executor"
    prepare_args = [ "prepare" ]
    run_exec = "gitlab-sardinecake-executor"
    run_args = [ "run" ]
    cleanup_exec = "gitlab-sardinecake-executor"
    cleanup_args = [ "cleanup" ]
```

#### gitlab-sardinecake-executor

`gitlab-sardinecake-executor` looks for INI-style configuration files in
- `/etc/gitlab-runner/gitlab-sardinecake-executor.ini`
- `~/.config/gitlab-runner/gitlab-sardinecake-executor.ini` (in the home directory of the user running `gitlab-sardinecake-executor`)

```ini
[DEFAULT]
# how to connect to the sardinecake daemon
connect = qemu:///system
# where the downloaded OCI containers are stored
ocidir = /var/lib/sardinecake/OCI/
# where the extracted VMs are stored
vmdir = /var/lib/sardinecake/VMs/
```

See [examples/gitlab-sardinecake-executor.ini](examples/gitlab-sardinecake-executor.ini)

#### gitlab-ci.yml
Now you can use libvirt VMs in your `.gitlab-ci.yml`:

```yml
# You can use any libvirt VM the executor knows about
image: registry.example.org/sardines/debian12:latest

test:
  # In case you tagged runners that have
  # GitLab Libvirt Executor configured on them
  tags:
    - sardinecake

  script:
    - uname -a
```

## Caveats

sardinecake VMs can be rather large.
E.g. a Windows VM with various MSYS2/MinGW flavours installed can easily require a disk-image that takes 60GB.
In the `sardinecake` OCI containers, these disk images are stored compressed (about ½ the size).

Nevertheless, when cloning a VM for the first time, the data has to be downloaded and uncompressed,
which may take a while.

Both the OCI containers and VMs created from the containers are kept on disk, so future uses should bring up the
VM very fast (within seconds).
