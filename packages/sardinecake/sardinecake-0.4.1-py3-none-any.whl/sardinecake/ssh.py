#!/usr/bin/env python3

# sardinecake - run GitLab-CI jobs within libvirt VMs
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

import os
import subprocess

from contextlib import contextmanager
import logging as logging

log = logging.getLogger("sardinecake.ssh")


@contextmanager
def SSH(*args, **kwargs):
    import paramiko

    class IgnorePolicy(paramiko.client.MissingHostKeyPolicy):
        """
        Policy that silently ignores any missing host keys.
        """

        def missing_host_key(self, client, hostname, key):
            log.debug(
                "Unknown {} host key for {}: {}".format(
                    key.get_name(),
                    hostname,
                    paramiko.client.hexlify(key.get_fingerprint()),
                )
            )

    if "port" in kwargs and not kwargs["port"]:
        del kwargs["port"]

    try:
        client = paramiko.SSHClient()
        client.load_system_host_keys()
        client.set_missing_host_key_policy(IgnorePolicy)
        client.connect(*args, **kwargs)
        yield client
    finally:
        client.close()


def checkSSH(
    host: str,
    username: str | None = None,
    password: str | None = None,
    key_filename: str | list[str] | None = None,
    timeout: float | None = None,
    port: int | None = None,
) -> bool | None:
    """test whether we can open an SSH connection to <host>"""
    try:
        with SSH(
            host,
            username=username,
            password=password,
            key_filename=key_filename,
            timeout=timeout,
            port=port,
        ) as client:
            pass
    except TimeoutError as e:
        log.error("SSH connection to VM timed out!")
        log.debug(f"ssh://{username}@{host} timed out with {e}")
        return False
    except Exception as e:
        log.exception(f"ssh://{username}@{host} failed with {e}")
        return None
    return True


def channel2file(inchan, outfile):
    """write data received from <inchan> to <outfile>"""
    written = 0
    while inchan.recv_ready():
        written += outfile.write(inchan.recv(65536))
    return written


def getbashexports(env={}):
    if not env:
        return b""
    cmd = subprocess.run(
        ["bash", "-c", "set"],
        stdout=subprocess.PIPE,
        env={str(k): str(v) for k, v in env.items()},
    )
    result = []
    for line in cmd.stdout.splitlines():
        k = line.split(b"=", maxsplit=1)
        if k[0].decode() in env:
            result.append(b"export " + line)
    return b"\n".join(result)


def run_commands(host, commands, **kwargs):
    """execute (on <host>) the given <commands> within a bash
    <kwargs> are passed to SSH.
    """

    ret = None
    with (
        open("/dev/stdout", "wb", buffering=0) as binout,
        SSH(host, **kwargs) as client,
    ):
        stdin, stdout, stderr = client.exec_command("/bin/bash", get_pty=False)
        stdin.write(commands)
        while not stdout.channel.exit_status_ready():
            channel2file(stdout.channel, binout)
        channel2file(stdout.channel, binout)
        ret = stdout.channel.exit_status

    return ret


def run_script(host, script, env={}, **kwargs):
    """copy script to <host> and execute it; possibly sourcing a file containing the <env> vars first"""
    dirname = f"gitlab-{os.getpid()}"
    scriptname = os.path.join(dirname, "script")
    envname = os.path.join(dirname, "wrapper")

    log.debug(f"run {script} on {host}")
    ret = None
    with (
        open(script) as f,
        open("/dev/stdout", "wb", buffering=0) as binout,
        SSH(host, **kwargs) as client,
    ):
        sftp = client.open_sftp()
        # (try to) touch /var/log/lastlog, so ssh does not not complain if it is missing
        try:
            with sftp.open("/var/log/lastlog", "ab") as lastlog:
                pass
        except OSError as e:
            log.debug(f"couldn't touch lastlog: {e}")

        try:
            sftp.mkdir(dirname)
            log.debug(f"creating script {scriptname!r}")
            sftp.putfo(f, scriptname)
            sftp.chmod(scriptname, 0o711)
            log.debug(f"creating env-file {envname!r}")
            with sftp.open(envname, "wb") as envfd:
                envfd.write(b"#!/usr/bin/env bash\n")
                envfd.write(
                    b"if set -o | grep pipefail > /dev/null; then set -o pipefail; fi\n"
                )
                envfd.write(b"set -o errexit\n")
                envfd.write(b"set +o noclobber\n\n")
                envfd.write(getbashexports(env))
                envfd.write(b"\n\n")
                if False:
                    # this gobbles the script's exit-code
                    envfd.write(
                        b""": | eval $'%s\\n' 2>&1\nexit 0\n""" % scriptname.encode()
                    )
                else:
                    # this preserves the exit code
                    envfd.write(b"set +o errexit\n")
                    envfd.write(b""": | eval $'%s\\n' 2>&1\n""" % scriptname.encode())

            sftp.chmod(envname, 0o711)

            stdin, stdout, stderr = client.exec_command(
                envname, get_pty=False, environment=env
            )
            while not stdout.channel.exit_status_ready():
                channel2file(stdout.channel, binout)
            channel2file(stdout.channel, binout)
            ret = stdout.channel.exit_status
        finally:
            try:
                sftp.unlink(scriptname)
                sftp.unlink(envname)
                sftp.rmdir(dirname)
            except Exception as e:
                log.debug(f"Failed to cleanup {dirname!r} on {host!r}: {e}")

    return ret


if __name__ == "__main__":
    import argparse
    import sys
    from urllib.parse import urlparse

    logging.basicConfig()

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--timeout",
        type=float,
        help="timeout for SSH-connection (DEFAULT: no timeout)",
    )
    p = parser.add_argument_group("script")
    p.add_argument(
        "--script",
        help="script to run on the server",
    )
    p.add_argument(
        "--env",
        type=lambda x: x.split("=", maxsplit=1),
        default=[],
        action="append",
        help="environment for the script (use 'VAR=value'); can be given multiple times",
    )
    parser.add_argument(
        "URI",
        type=urlparse,
        help="SSH-URI to check for connectivity (e.g. 'ssh://user:password@example.com')",
    )

    p = parser.add_argument_group("verbosity")
    p.add_argument(
        "-v",
        "--verbose",
        action="count",
        help="Raise verbosity (can be given multiple times)",
    )
    p.add_argument(
        "-q",
        "--quiet",
        action="count",
        help="Lower verbosity (can be given multiple times)",
    )

    args = parser.parse_args()

    # merge verbosity settings
    if args.verbose or args.quiet:
        args.verbosity = (args.verbose or 0) - (args.quiet or 0)
        verbosity = args.verbosity
    else:
        args.verbosity = None
        verbosity = 0  # defaults.verbosity
    # logging.setVerbosity(verbosity)
    log.setLevel(max(1, logging.INFO - 10 * verbosity))
    del args.quiet
    del args.verbose

    uri = args.URI
    if uri.scheme != "ssh":
        parser.exit(1, "URI-schema must be 'ssh'")

    env = {}
    for kv in args.env:
        try:
            k, v = kv
        except ValueError:
            log.error(f"env must be a 'key=value' pair... ignoring {kv[0]!r}")
            continue
        env[k] = v

    if args.script:
        try:
            with open(args.script) as f:
                pass
        except Exception as e:
            parser.exit(1, f"build-script cannot be opened: {e}")

    if checkSSH(
        uri.hostname, username=uri.username, password=uri.password, port=uri.port
    ):
        print(f"SSH connection to {uri.hostname!r} OK.", file=sys.stderr)
    else:
        raise SystemExit(f"couldn't establish an SSH connection to {uri.hostname}.\n")

    if args.script:
        ret = run_script(
            uri.hostname,
            args.script,
            env=env,
            username=uri.username,
            password=uri.password,
            port=uri.port,
        )
        if ret:
            parser.exit(ret, f"script exited with: {ret}\n")
