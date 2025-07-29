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

import logging
import os
import subprocess

log = logging.getLogger("sardinecake.virsh")


class virSH:
    cmd_context = {
        "autostart": "domain",
        "backup-begin": "domain",
        "backup-dumpxml": "domain",
        "blkiotune": "domain",
        "checkpoint-create": "domain",
        "checkpoint-create-as": "domain",
        "checkpoint-list": "domain",
        "console": "domain",
        "cpu-baseline": "file",
        "cpu-compare": "file",
        "cpu-stats": "domain",
        "create": "file",
        "define": "file",
        "desc": "domain",
        "destroy": "domain",
        "domblkerror": "domain",
        "domblkinfo": "domain",
        "domblklist": "domain",
        "domblkstat": "domain",
        "domcontrol": "domain",
        "domdirtyrate-calc": "domain",
        "domdisplay": "domain",
        "domdisplay-reload": "domain",
        "domfsfreeze": "domain",
        "domfsinfo": "domain",
        "domfsthaw": "domain",
        "domfstrim": "domain",
        "domhostname": "domain",
        "domid": "domain",
        "domifaddr": "domain",
        "domiflist": "domain",
        "dominfo": "domain",
        "domjobabort": "domain",
        "domjobinfo": "domain",
        "domlaunchsecinfo": "domain",
        "dommemstat": "domain",
        "domname": "domain",
        "dompmwakeup": "domain",
        "domsetlaunchsecstate": "domain",
        "domstate": "domain",
        "domtime": "domain",
        "domuuid": "domain",
        "dump": "domain",
        "dumpxml": "domain",
        "edit": "domain",
        "emulatorpin": "domain",
        "guest-agent-timeout": "domain",
        "guestinfo": "domain",
        "guestvcpus": "domain",
        "hypervisor-cpu-compare": "file",
        "iface-define": "file",
        "iface-destroy": "interface",
        "iface-dumpxml": "interface",
        "iface-edit": "interface",
        "iface-mac": "interface",
        "iface-name": "interface",
        "iface-start": "interface",
        "iface-undefine": "interface",
        "inject-nmi": "domain",
        "iothreadinfo": "domain",
        "lxc-enter-namespace": "domain",
        "managedsave": "domain",
        "managedsave-dumpxml": "domain",
        "managedsave-edit": "domain",
        "managedsave-remove": "domain",
        "memtune": "domain",
        "metadata": "domain",
        "migrate": "domain",
        "migrate-compcache": "domain",
        "migrate-getmaxdowntime": "domain",
        "migrate-getspeed": "domain",
        "migrate-postcopy": "domain",
        "net-autostart": "network",
        "net-create": "file",
        "net-define": "file",
        "net-desc": "network",
        "net-destroy": "network",
        "net-dhcp-leases": "network",
        "net-dumpxml": "network",
        "net-edit": "network",
        "net-info": "network",
        "net-name": "network",
        "net-port-list": "network",
        "net-start": "network",
        "net-undefine": "network",
        "net-uuid": "network",
        "nodedev-autostart": "device",
        "nodedev-create": "file",
        "nodedev-define": "file",
        "nodedev-destroy": "device",
        "nodedev-detach": "device",
        "nodedev-dumpxml": "device",
        "nodedev-info": "device",
        "nodedev-reattach": "device",
        "nodedev-reset": "device",
        "nodedev-start": "device",
        "nodedev-undefine": "device",
        "numatune": "domain",
        "nwfilter-binding-create": "file",
        "nwfilter-define": "file",
        "perf": "domain",
        "pool-autostart": "pool",
        "pool-build": "pool",
        "pool-create": "file",
        "pool-define": "file",
        "pool-delete": "pool",
        "pool-destroy": "pool",
        "pool-dumpxml": "pool",
        "pool-edit": "pool",
        "pool-info": "pool",
        "pool-name": "pool",
        "pool-refresh": "pool",
        "pool-start": "pool",
        "pool-undefine": "pool",
        "pool-uuid": "pool",
        "qemu-agent-command": "domain",
        "qemu-monitor-command": "domain",
        "reboot": "domain",
        "reset": "domain",
        "restore": "file",
        "resume": "domain",
        "save": "domain",
        "save-image-dumpxml": "file",
        "save-image-edit": "file",
        "schedinfo": "domain",
        "screenshot": "domain",
        "secret-define": "file",
        "secret-dumpxml": "secret",
        "secret-get-value": "secret",
        "secret-set-value": "secret",
        "secret-undefine": "secret",
        "send-key": "domain",
        "shutdown": "domain",
        "snapshot-create": "domain",
        "snapshot-create-as": "domain",
        "snapshot-current": "domain",
        "snapshot-delete": "domain",
        "snapshot-edit": "domain",
        "snapshot-info": "domain",
        "snapshot-list": "domain",
        "snapshot-parent": "domain",
        "snapshot-revert": "domain",
        "start": "domain",
        "suspend": "domain",
        "ttyconsole": "domain",
        "undefine": "domain",
        "update-memory-device": "domain",
        "vcpucount": "domain",
        "vcpuinfo": "domain",
        "vcpupin": "domain",
        "vncdisplay": "domain",
        "vol-delete": "vol",
        "vol-dumpxml": "vol",
        "vol-info": "vol",
        "vol-key": "vol",
        "vol-list": "pool",
        "vol-name": "vol",
        "vol-path": "vol",
        "vol-pool": "vol",
        "vol-wipe": "vol",
    }

    def __init__(self, context, libvirtURI=None):
        self._context = context
        self._cmd = ["virsh"]
        if libvirtURI:
            self._cmd += ["--connect", libvirtURI]

    def __call__(self, cmd: str, *args, **kwargs):
        ctx = self.cmd_context.get(cmd)
        if ctx and self._context:
            context = [f"--{ctx}", self._context]
        else:
            context = []

        command = self._cmd + [cmd] + context + list(args)
        kwargs.setdefault("stderr", subprocess.DEVNULL)

        # set LANG to 'C' (unless overridden)
        env = kwargs.get("env")
        if env and "LANG" in env:
            pass
        else:
            if not env:
                env = dict(os.environ)
            env["LANG"] = "C"
        kwargs["env"] = env
        return subprocess.run(command, **kwargs)

    def isRunning(self) -> bool | None:
        """check if VM is running (->true), or not (->false)
        returns None if the VM does not exist"""
        try:
            x = self("domstate", check=True, stdout=subprocess.PIPE)
        except:
            return
        if b"running" in x.stdout:
            return True
        return False

    def domifaddr(self) -> dict:
        """get IPs of VM"""
        x = self("domifaddr", stdout=subprocess.PIPE)
        try:
            x.check_returncode()
        except:
            return

        stdout = [line for line in x.stdout.splitlines()[2:] if line]
        if not stdout:
            return

        ret = {}
        for line in stdout:
            data = line.decode().split()
            ip = data[3].split("/")[0]
            ret[data[0]] = {
                "mac": data[1],
                "protocol": data[2],
                "address": ip,
                "network": data[3],
            }
        return ret

    def destroy(self, graceful=False, remove_logs=False) -> bool:
        """destroy domain"""
        args = []
        if graceful:
            args += ["--graceful"]
        if remove_logs:
            args += ["--remove-logs"]
        x = self("destroy", *args, stdout=subprocess.PIPE)
        return x.returncode == 0


if __name__ == "__main__":
    import argparse

    logging.basicConfig()

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--connect",
        type=str,
        help="connection URI for libvirt",
    )
    parser.add_argument(
        "vm",
        help="VM name",
    )
    args = parser.parse_args()
    if args.connect is None:
        virsh = virSH(args.vm)
    else:
        virsh = virSH(args.vm, libvirtURI=args.connect)
    print(virsh)
    print(f"running: {virsh.isRunning()}")
    print(f"IP: {virsh.domifaddr()}")
