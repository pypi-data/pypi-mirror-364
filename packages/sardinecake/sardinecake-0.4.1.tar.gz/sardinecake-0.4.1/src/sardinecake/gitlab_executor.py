#!/usr/bin/env python3

# gitlab-sardinecake-executor - run GitLab-CI jobs within libvirt VMs
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

_name = "sardinecake.executor"
_version = None

import fnmatch
import os
import time

from . import logger as logging
from . import clone, defaults, ssh
from .importvm import getconfig
from .namespace import Namespace
from .virsh import virSH

try:
    from ._version import version as _version
except ImportError:
    pass


log = logging.getLogger(_name)

BUILD_FAILURE = 1
SYSTEM_FAILURE = 2
BUILD_EXIT_CODE_FILE = None

custom_env = {}


def setup():
    global BUILD_FAILURE
    global SYSTEM_FAILURE
    global BUILD_EXIT_CODE_FILE
    global custom_env

    BUILD_FAILURE = int(os.environ.get("BUILD_FAILURE_EXIT_CODE", BUILD_FAILURE))
    SYSTEM_FAILURE = int(os.environ.get("SYSTEM_FAILURE_EXIT_CODE", SYSTEM_FAILURE))
    BUILD_EXIT_CODE_FILE = os.environ.get("BUILD_EXIT_CODE_FILE", BUILD_EXIT_CODE_FILE)

    prefix = "CUSTOM_ENV_"
    custom_env = {
        k[len(prefix) :]: v for k, v in os.environ.items() if k.startswith(prefix)
    }

    # fallback for easier testing
    for k in ["CI_JOB_IMAGE", "CI_JOB_ID"]:
        if k in custom_env:
            continue
        v = os.environ.get(k)
        if v:
            custom_env[k] = v


def getVersion(libvirtURI=None):
    """get the version of the executor
    (possibly including libvirt version)
    """

    def parseVersion(ver):
        major = ver // 1000000
        minor = (ver % 1000000) // 1000
        release = ver % 1000
        return (major, minor, release)

    try:
        import libvirt

        with libvirt.openReadOnly(libvirtURI) as conn:
            typ = conn.getType()
            libver = {
                "libvirt": parseVersion(conn.getLibVersion()),
                typ: parseVersion(conn.getVersion()),
            }
            libvirt_version = ", ".join(
                f"{t}: {v0}.{v1}.{v2}" for t, (v0, v1, v2) in libver.items()
            )

    except Exception as e:
        log.debug("Unable to query libvirt for version", exc_info=True)
        libvirt_version = None

    ver = ""
    if _version:
        ver = _version
    if libvirt_version:
        ver = f"{ver} ({libvirt_version})"
    ver = ver.strip()
    if ver:
        return ver.strip()


def getVMimage() -> str | None:
    if not custom_env:
        setup()
    env = "CI_JOB_IMAGE"
    img = custom_env.get(env)
    if not img:
        log.fatal(f"no VM defined via {env!r}")
        return None
    return img


def getVMname() -> str | None:
    if not custom_env:
        setup()
    env = "CI_JOB_ID"
    job = custom_env.get(env)
    if job:
        return f"gitlab-{job}"
    log.fatal(f"no GitlabEnv {env!r} found")
    return None


def getVMaddress(
    name: str | None = None,
    timeout: float | None = None,
    libvirtURI: str | None = None,
    protocol: str = "IPv4",
) -> str | None:
    if not name:
        name = getVMname()
    proto = None
    if protocol:
        proto = protocol.lower()

    virsh = virSH(name, libvirtURI=libvirtURI)

    if virsh.isRunning() is None:
        log.error(f"VM {name!r} does not exist")
        return None

    start = time.time() or 0
    now = start
    timeout = timeout or 0

    data = None
    while int(now - start) <= timeout:
        try:
            data = virsh.domifaddr()
            if data:
                break
        except:
            log.debug(f"failed getting {protocol} address for {name!r}", exc_info=True)

        time.sleep(0.5)
        if timeout is not None:
            now = time.time() or 0

    if not data:
        return None

    for dev, ifconf in data.items():
        if proto and ifconf.get("protocol").lower() != proto:
            continue
        IP = ifconf.get("address")
        if IP:
            log.debug(
                f"VM {name!r} has {protocol} {IP} (after {time.time() - start} seconds)"
            )
            return IP
    return None


def checkVMOnline(
    vmname: str,
    username: str | None = None,
    password: str | None = None,
    key_filename: str | list[str] | None = None,
    port: int | None = None,
    timeout: float | None = None,
    libvirtURI: str | None = None,
) -> str | None:
    """check if the given VM can be accessed with ssh://username:password@...
    on success, returns the IP of the VM; otherwise returns None
    """
    try:
        log.info("Waiting for the VM to become online...")
        IP = getVMaddress(vmname, timeout=timeout, libvirtURI=libvirtURI)
    except Exception as e:
        log.exception(f"failed to get IP address for {vmname!r}")
        return None

    if not IP:
        log.exception(f"couldn't get IP address for {vmname!r}")
        return None

    if username:
        # check whether the host is SSH-able
        log.info("Waiting for the VM to become SSH-able...")
        if not ssh.checkSSH(
            IP,
            username=username,
            password=password,
            key_filename=key_filename,
            port=port,
            timeout=timeout,
        ):
            return None
        log.info("Was able to SSH!")
        log.debug(f"ssh://{username}@{IP} success!")

    log.info("VM is ready.")
    return IP


def getAuth(args: Namespace, vmconfig: dict = {}) -> dict:
    """get dict with authentication information from args"""
    auth = {}
    vmconfig = vmconfig or {}

    users = vmconfig.get("users")
    if users:
        u = users[0] or {}
        auth.setdefault("username", u.get("username"))
        auth.setdefault("password", u.get("password"))
        auth.setdefault("port", u.get("port"))
    auth = {k: v for k, v in auth.items() if v is not None}

    try:
        auth.setdefault("username", args.username)
    except AttributeError:
        pass
    try:
        auth.setdefault("password", args.password)
    except AttributeError:
        pass

    try:
        keypath = args.identity_file
        if keypath:
            if os.path.isdir(keypath):
                # list files in keypath (https://stackoverflow.com/a/3207973/1169096)
                keypath = next(os.walk(keypath), (None, None, []))[2]
            auth.setdefault("key_filename", keypath)
    except AttributeError:
        pass

    return auth


def do_logtest(args):
    """print at various loglevels"""
    for name, level in logging.getLevelNamesMapping().items():
        log.log(level, name)

    print(f"log-level: {log.level}/{log.getEffectiveLevel()}")
    print(args)


def do_config(args):
    """configure subsequent stages of GitLab runner the runner"""
    import json
    import sys

    driver = {
        "name": _name or "gitlab-sardinecake-executor",
    }
    ver = getVersion(args.connect)
    if ver:
        driver["version"] = ver

    try:
        builds_dir = args.guest_builds_dir
    except AttributeError:
        pass
    try:
        cache_dir = args.guest_cache_dir
    except AttributeError:
        pass

    job_env = {}

    # build the config dictionary
    localvars = locals()

    def makeConfig(*args):
        result = {}
        for k in args:
            v = localvars.get(k)
            if v:
                result[k] = v
        return result

    data = makeConfig(
        "driver",
        "job_env",
        "builds_dir",
        "cache_dir",
    )

    json.dump(data, sys.stdout)


def do_prepare(args):
    """create a VM gitlab-${CI_JOB_ID} and wait till it is accessible via SSH"""
    baseVM = None
    cloneVM = None
    timeout = args.timeout
    libvirtURI = args.connect
    outdir = args.vmdir
    ocidir = args.ocidir
    clonedir = args.clonedir

    if outdir and not os.path.exists(outdir):
        # make sure that 'outdir' points to a directory
        outdir = os.path.join(outdir, "")

    if not custom_env:
        setup()

    shownbase = baseVM = custom_env.get("CI_JOB_IMAGE")
    if args.image and args.image != baseVM:
        shownbase = f"{baseVM!r} ({args.image!r})"
        baseVM = args.image

    if not baseVM:
        raise SystemExit("no base image given")

    cloneVM = getVMname()
    if not cloneVM:
        raise SystemExit("unable to get name of cloned VM")

    # start VM
    log.info(f"Pulling the latest version of {shownbase!r} as {cloneVM!r}...")
    try:
        cfg = clone.fetch_and_clone(
            container=baseVM,
            vm=cloneVM,
            ocidir=ocidir,
            vmdir=outdir,
            clonedir=clonedir,
            startmode=clone.START_EPHEMERAL,
            libvirtURI=libvirtURI,
        )
    except Exception as e:
        exc_info = log.getEffectiveLevel() < logging.INFO
        log.fatal(e, exc_info=exc_info)
        return SYSTEM_FAILURE

    auth = getAuth(args, cfg)

    # now wait until we have an SSH-connection
    host = checkVMOnline(
        cloneVM,
        timeout=timeout,
        libvirtURI=libvirtURI,
        **auth,
    )
    if not host:
        return SYSTEM_FAILURE

    if args.prepare_script:
        log.info(f"Running prepare script {args.prepare_script!r}")
        try:
            with open(args.prepare_script) as f:
                cmds = f.read()
            ret = ssh.run_script(
                host,
                args.prepare_script,
                env=custom_env,
                **auth,
            )
            if ret:
                log.error(f"prepare script returned {ret}")
                do_cleanup(args)
                return BUILD_FAILURE
        except Exception as e:
            log.exception("failed to run prepare script")
            do_cleanup(args)
            return BUILD_FAILURE

    user = auth.get("username")
    log.debug(f"{cloneVM!r} is ready as {host!r}")
    if user:
        log.debug(f"You can login via SSH as {user}@{host}")


def do_run(args):
    """run a script within the VM"""
    timeout = 30
    libvirtURI = args.connect

    vmname = getVMname()

    container = custom_env.get("CI_JOB_IMAGE")
    cfg = getconfig(os.path.join(args.ocidir, container))

    auth = getAuth(args, cfg)

    if args.action:
        log.debug(f"Running {args.action!r}")
    else:
        log.warning("Running unknown action")

    if not vmname:
        raise SystemExit("unable to get name of cloned VM")
    try:
        host = getVMaddress(vmname, timeout=timeout, libvirtURI=libvirtURI)
    except Exception as e:
        log.exception(f"failed to get IP address for {vmname!r}")
        return False

    if not host:
        log.fatal(f"Unable to get address of {vmname!r}")
        return SYSTEM_FAILURE
    try:
        ret = ssh.run_script(host, args.script, **auth)
        if ret:
            log.error(f"{args.action} script returned {ret}")
            if BUILD_EXIT_CODE_FILE:
                try:
                    with open(BUILD_EXIT_CODE_FILE, "w") as f:
                        f.write(f"{ret}\n")
                except Exception as e:
                    log.error(f"failed to write {BUILD_EXIT_CODE_FILE!r}: {e}")
            return BUILD_FAILURE
    except Exception as e:
        log.exception(f"failed to run {args.action} script")
        return BUILD_FAILURE
    return ret


def do_cleanup(args):
    """cleanup the VM"""
    cloneVM = getVMname()

    if not cloneVM:
        raise SystemExit("unable to get name of cloned VM")

    virsh = virSH(cloneVM, libvirtURI=args.connect)

    log.info(f"destroy VM {cloneVM!r}")
    if not virsh.destroy():
        raise SystemExit(f"couldn't destroy VM {cloneVM!r}")


def parseArgs():
    import argparse

    def add_common_args(parser):
        p = parser.add_argument_group("libvirt options")
        p.add_argument(
            "--connect",
            help="libvirt connection URI",
        )

        p = parser.add_argument_group("verbosity")
        p.add_argument(
            "-v",
            "--verbose",
            action="count",
            help="raise verbosity (can be given multiple times)",
        )
        p.add_argument(
            "-q",
            "--quiet",
            action="count",
            help="lower verbosity (can be given multiple times)",
        )

        p.add_argument(
            "--no-run",
            action="store_true",
            help="don't actually run (exit early)",
        )

        p = parser.add_argument_group(
            "SSH options",
            description="fallback SSH credentials (if none are provided by the VM)",
        )
        p.add_argument(
            "-u",
            "--username",
            help=f"SSH user (DEFAULT: {defaults.executor.username})",
        )
        p.add_argument(
            "-p",
            "--password",
            help="SSH password",
        )
        p.add_argument(
            "--identity-file",
            help="SSH identity file for authentication (if a password is required, uses '--password')",
        )

        return parser

    def add_default_args(subparsers, name=None, fallbacks={}, func=None, **kwargs):
        if any([name, func]) and not all([subparsers, name, func]):
            raise ValueError("inconsistent arguments for add_subparser()")

        if name:
            if "help" in kwargs and "description" not in kwargs:
                kwargs["description"] = kwargs["help"]
            p = subparsers.add_parser(name, **kwargs)
            add_common_args(p)
        else:
            p = subparsers

        # fallbacks.setdefault("ocidir", defaults.sarde.oci_path)
        # fallbacks.setdefault("vmdir", defaults.sarde.vmdisk_path)
        # fallbacks.setdefault("verbose", 0)
        # fallbacks.setdefault("quiet", 0)
        mydefaults = defaults.executor.get(name) or defaults.executor.get(None) or {}
        fallbacks.update(mydefaults)
        fallbacks["func"] = func

        if func:
            p.set_defaults(**fallbacks)

        return p

    # common args for all sub-parsers and the top-level parser
    common = argparse.ArgumentParser(add_help=False)
    add_common_args(common)

    parser = argparse.ArgumentParser(
        description="""Custom GitLab Runner executor to run jobs inside ephemeral libvirt virtual machines.""",
        parents=[
            common,
        ],
    )

    add_default_args(parser)

    parser.add_argument(
        "-V",
        "--version",
        action="version",
        version=_version or "<unknown>",
    )

    subparsers = parser.add_subparsers(required=True, title="commands")
    p = add_default_args(
        subparsers, "config", func=do_config, help="Configure GitLab Runner"
    )

    p = add_default_args(
        subparsers,
        "prepare",
        func=do_prepare,
        help="Prepare a libvirt VM for execution",
    )
    p.add_argument(
        "--timeout",
        type=int,
        help=f"libvirt connection timeout for VM boot and SSH connection (DEFAULT: {defaults.executor.timeout})",
    )
    p.add_argument(
        "--prepare-script",
        help="path to script (on hypervisor) that is executed within the VM to complete the preparation",
    )
    p.add_argument(
        "--clonedir",
        help="directory for storing disk images of (ephemeral) clone VMs",
    )
    g = p.add_argument_group("expert/dev options")
    g.add_argument(
        "--vmdir",
        help="directory where VM images (extracted from the OCI containers) are stored",
    )
    g.add_argument(
        "--ocidir",
        help="directory where OCI containers are stored",
    )
    p.add_argument(
        "--omit-backingstore",
        default=None,
        action="store_true",
        help="Do not create a <backingStore/> tag in the new guest definition (might be needed for older libvirt versions)",
    )

    p = add_default_args(
        subparsers, "run", func=do_run, help="Run GitLab's scripts in libvirt VM"
    )
    p.add_argument(
        "script",
        help="script file to execute",
    )
    p.add_argument(
        "action",
        help="Name of the action being executed",
    )

    p = add_default_args(
        subparsers,
        "cleanup",
        func=do_cleanup,
        help="Cleanup libvirt VM after job finishes",
    )

    common_args, remainder = common.parse_known_args()
    args = parser.parse_args()

    # fix common args
    for k, v in common_args._get_kwargs():
        if v is None:
            continue
        setattr(args, k, v)

    # merge verbosity settings
    if args.verbose or args.quiet:
        args.verbosity = (args.verbose or 0) - (args.quiet or 0)
        verbosity = args.verbosity
    else:
        args.verbosity = None
        verbosity = defaults.executor.verbosity
    log.setLevel(max(1, logging.INFO - 10 * verbosity))

    del args.quiet
    del args.verbose

    fun = args.func
    del args.func

    return (fun, args)


def parseConfigs(configfiles, default):
    """parse configuration file(s)
    any given keyword arguments override settings in the configuration files
    """
    import configparser

    # general options
    # - libvirt URI
    # - specify VM clone/start command
    # - only allow images that have a configuration section
    # per VM options
    # - ssh credentials
    # - cache/build directories (currently not implemented)
    example = """
[DEFAULT]
# general options
connect = qemu:///system

# VM-defaults
username = vagrant
password = vagrant
guest-builds-dir "/path/on/guest/builds"
guest-cache-dir "/path/on/guest/cache"
builds-dir "/path/on/host/builds"
cache-dir "/path/on/host/cache"


# VM overrides (per VM-name)
[win10]
    username = admin
    password = secret
    """

    def section2dict(section, options=None, excluded_options=[]) -> dict:
        """turn a ConfigParser section into a dict"""
        getters = {
            "omit_backingstore": "boolean",
            "timeout": "float",
            "verbosity": "int",
        }
        result = {}
        if options is None:
            options = cfg.options(section)
        for option in options:
            opt = option.lower().replace("-", "_")
            if opt in excluded_options:
                continue
            getter = getattr(cfg, "get" + getters.get(opt, ""))
            result[opt] = getter(section, option)
        return result

    globaloptions = ["verbosity", "no-run"]
    default_configfiles = [
        "/etc/gitlab-runner/gitlab-sardinecake-executor.ini",
        os.path.expanduser("~/.config/gitlab-runner/gitlab-sardinecake-executor.ini"),
    ]

    cfg = configparser.ConfigParser()
    default_section = cfg.default_section
    cfg.default_section = None
    log.debug(f"Loading configurations from {configfiles or default_configfiles}")
    did_configfiles = cfg.read(configfiles or default_configfiles)
    if not did_configfiles:
        log.warning(f"No configuration files found!")
    else:
        log.debug(f"Loaded configurations from {did_configfiles}")

    data = {}
    for section in cfg:
        if section is None:
            continue
        sectiondata = section2dict(section, excluded_options=globaloptions)
        if sectiondata:
            data[section] = sectiondata

    if default_section in data:
        defaultcfg = data[default_section]
        del data[default_section]
    else:
        defaultcfg = {}

    defaultcfg.update(default)
    data[None] = defaultcfg

    return data


def getConfiguration() -> dict:
    """get configurations.
    this is the configuration precedence (first beats the rest):
    - container specific config
      - container-specific config in .ini-files
      - container-specific config from embedded config
    - general config
      - cmdline arguments
      - default section in .ini-files
    *this* function does not know about the embedded configs yet.
    so it returns a dictionary with VM -> config mappings.
    the special VM <None> contains the general config (merged)
    """

    img = getVMimage()

    # read cmdline arguments
    fun, args = parseArgs()
    log.debug(args)
    cfg_default = {k: v for k, v in args.__dict__.items() if v is not None}

    # read configuration
    configfiles = []
    userconf = os.getenv("GITLAB_SARDINECAKE_EXECUTOR_CONF_FILES")
    if userconf:
        configfiles = userconf.split(":")
    else:
        try:
            configfiles = args.config
            del args.config
        except AttributeError:
            pass

    cfg = parseConfigs(configfiles, cfg_default)
    log.debug(cfg)

    # get the default configuration for our image:
    cfg_default = cfg[None]
    del cfg[None]
    cfg_image = {}
    if img in cfg:
        cfg_image = cfg[img]
    elif img:
        wildcardconfigs = {k: v for k, v in cfg.items() if fnmatch.fnmatch(img, k)}
        if wildcardconfigs:
            # get the best match (most beginning characters match):
            cfg_image = sorted(
                wildcardconfigs.items(), key=lambda x: len(x[0]), reverse=True
            )[0][1]

    imgcfg = Namespace(**cfg_image)
    imgcfg.setdefaults(cfg_default)
    imgcfg.setdefaults(defaults.executor)

    log.debug(imgcfg)
    if imgcfg.verbosity is not None:
        log.setLevel(max(1, logging.INFO - 10 * imgcfg.verbosity))

    return (fun, imgcfg)


def _main():
    global log
    logging.basicConfig()
    log = logging.getLogger("sardinecake")
    setup()
    try:
        fun, args = getConfiguration()
    except SystemExit as e:
        if e.code and type(e.code) != int:
            log.fatal(e)
            raise SystemExit(SYSTEM_FAILURE)
        raise (e)

    if args.no_run:
        raise SystemExit(0)

    ret = None
    try:
        ret = fun(args)
    except SystemExit as e:
        if e.code and type(e.code) != int:
            log.fatal(e)
            raise SystemExit(SYSTEM_FAILURE)
        raise (e)
    raise SystemExit(ret)


if __name__ == "__main__":
    _main()
