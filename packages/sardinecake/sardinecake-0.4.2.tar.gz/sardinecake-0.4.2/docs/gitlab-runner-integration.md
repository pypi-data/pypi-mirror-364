`gitlab-sardinecake-executor` - gitlab-runner integration
=========================================================

The `gitlab-sardinecake-executor` can be used for running GitLab-CI jobs within VMs managed by sardinecake.

## Configuration

#### gitlab-runner

Tell `gitlab-runner` (via `/etc/gitlab-runner/config.toml`) to use `sardinecake` as the custom executor:

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

See [examples/gitlab-sardinecake-executor.ini](https://git.iem.at/devtools/sardinecake/-/blob/main/examples/gitlab-sardinecake-executor.ini)

#### gitlab-ci.yml
Now you can use libvirt VMs in your `.gitlab-ci.yml`:

```yml
# You can use any libvirt VM the executor knows about
image: registry.example.org/sardines/debian12:latest

test:
  # In case you tagged runners that have
  # GitLab sardinecake Executor configured on them
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
