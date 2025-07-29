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


# login/logout to a registry

# ~/.docker/config.json
# containers-auth.json(5)
# https://github.com/docker/docker-credential-helpers/

import logging
import subprocess

log = logging.getLogger("sardinecake.auth")


def login(
    registry: str, username: str | None = None, password: str | None = None
) -> bool:
    """login to a registry"""
    cmd = ["skopeo", "login"]
    if username:
        cmd += ["--username", username]
    if password:
        cmd += ["--password-stdin"]
    cmd += [registry]
    if password:
        p = subprocess.Popen(cmd, stdin=subprocess.PIPE)
        p.communicate(password.encode())
    else:
        p = subprocess.run(cmd)

    return not p.returncode


def logout(registry: str | None):
    """logout from a registry
    if <registry> is 'None', logout from *all* registries
    """
    cmd = ["skopeo", "logout"]
    if registry is None:
        cmd.append("--all")
    else:
        cmd.append(registry)

    p = subprocess.run(cmd)
    return not p.returncode


def _main():
    import argparse

    parser = argparse.ArgumentParser(
        description="login to/logout from container registry on a specified server.",
    )

    p = parser.add_argument_group("action")
    p = p.add_mutually_exclusive_group()
    p.add_argument(
        "--login",
        action="store_true",
        default=True,
        help="login to the registry (DEFAULT)",
    )
    p.add_argument(
        "--logout",
        action="store_false",
        dest="login",
        help="logout from the registry",
    )

    p = parser.add_argument_group("credentials")
    p.add_argument(
        "--username",
        help="Username for registry",
    )
    p = p.add_mutually_exclusive_group()
    p.add_argument(
        "--password-stdin",
        action="store_true",
        help="Read the password from stdin",
    )
    p.add_argument(
        "--password",
        help="Password for registry",
    )

    p = parser.add_argument_group("protocol")
    p.add_argument(
        "--insecure",
        dest="secure",
        action="store_false",
        help="connect to the OCI registry via insecure HTTP protocol",
    )
    p.add_argument(
        "--secure",
        dest="secure",
        action="store_true",
        help="connect to the OCI registry via the secure HTTPS protocol (DEFAULT)",
    )

    p = parser.add_argument_group("credential validation")
    p.add_argument(
        "--no-validate",
        dest="validate",
        action="store_false",
        help="skip validation of the registry's credentials before logging-in",
    )

    p.add_argument(
        "--validate",
        dest="validate",
        action="store_true",
        help="validate the registry's credentials before logging-in (DEFAULT)",
    )

    parser.add_argument(
        "registry",
        help="registry to login to (e.g. 'ghcr.io')",
    )

    args = parser.parse_args()

    if args.login:
        x = login(args.registry)
    else:
        x = logout(args.registry)
    print(x)


if __name__ == "__main__":
    _main()
