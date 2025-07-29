import os
import subprocess
import json
import time

from pybenutils.network.ssh_utils import run_commands as run_ssh_commands
from pybenutils.utils_logger.config_logger import get_logger

logger = get_logger()


class ParallelsCLI:
    """Parallels CLI utility class to manage Parallels virtual machines using the Parallels CLI tool"""

    def __init__(self, host='', host_user='', host_password=''):
        """Parallels CLI utility class to manage Parallels virtual machines using the Parallels CLI tool

        :param host: Remote Parallels server host. Leave empty to run on the localhost
        :param host_user: Remote Parallels server host user. Leave empty when running locally
        :param host_password: Remote Parallels server host user password. Leave empty when running locally
        """
        self.host = host if host else os.environ.get("PARALLELS_HOST", '')
        self.host_user = host_user if host_user else os.environ.get("PARALLELS_HOST_USER", '')
        self.host_password = host_password if host_password else os.environ.get("PARALLELS_HOST_PASS", '')
        self.local_host = bool(host)
        if not self.local_host:
            assert self.host, 'Missing host'
            assert self.host_user, 'Missing host user'
            assert self.host_password, 'Missing host password'

        self.cli_exec = "prlctl"

    def pprint(self, function_name, *args, **kwargs):
        res = getattr(self, function_name)(*args, **kwargs)
        if isinstance(res, dict) or isinstance(res, list):
            return json.dumps(res, indent=4)
        else:
            return res

    def run_command(self, args, assert_exit_code=True):
        """Executes a Parallels CLI command and returns the output

        :param args: List of arguments to pass to the subprocess.run
        :param assert_exit_code: Asserting exit code of the command
        :return: Stdout
        """
        for i in range(len(args)):
            if ' ' in args[i]:  # Handle vm names with spaces
                args[i] = f'"{args[i]}"'
        commands_list = [self.cli_exec] + args
        if self.local_host:
            try:
                logger.info(f"Executing command: {' '.join(args)}")
                result = subprocess.run(commands_list, capture_output=True, text=True, check=assert_exit_code)
                return result.stdout.strip()
            except subprocess.CalledProcessError as e:
                if assert_exit_code:
                    logger.error(f"Command failed: {e.stderr.strip()}")
                    return ''
                else:
                    return e.stderr.strip()
        else:
            res = run_ssh_commands(server=self.host,
                                    username=self.host_user,
                                    password=self.host_password,
                                    commands=[' '.join(commands_list)],
                                    )
            if assert_exit_code and res[0]['ssh_stderr']:
                logger.error(f"Command failed: {res[0]['ssh_stderr']}")
                return ''
            return res[0]['ssh_stdout']

    def send_vm_command(self, vm_name, args, assert_exit_code=False):
        """Send command to run on the vm

        :param vm_name: Vm name or uuid
        :param args: List of arguments to pass to the subprocess.run
        :param assert_exit_code: Asserting exit code of the command
        :return: Stdout
        """
        return self.run_command(["exec", vm_name] + args, assert_exit_code=assert_exit_code)

    def send_vm_command_by_ssh(self, vm_name, command, vm_user, vm_pass):
        """Send ssh command to vm

        :param vm_name: Vm name or uuid
        :param command: Command string to send via ssh
        :param vm_user: Vm ssh user
        :param vm_pass: Vm ssh password
        :return:
        """
        assert command, 'Missing command'
        assert vm_user, 'Missing vm user'
        hostname = self.get_vm_hostname(vm_name)
        assert hostname, 'Vm does not have a valid IP address! ABORTING!'

        logger.info(f"Executing command on {vm_name} via ssh: {command}")
        return run_ssh_commands(
            server=hostname,
            username=vm_user,
            password=vm_pass,
            commands=[command]
        )

    def list_vms(self):
        """Lists all available virtual machines

        :return: List of vms objects: [{'uuid':'123-abc', 'status': 'running', 'ip-configured':'-', 'name':'macOS'}]
        """
        # https://docs.parallels.com/parallels-desktop-developers-guide/command-line-interface-utility/manage-virtual-machines-from-cli/general-virtual-machine-management/list-virtual-machines
        res = self.run_command(["list", "-a", '-j'])
        return json.loads(res)

    def get_vms(self, vm_name=''):
        """Returns a full list of vms, or list with matching vms by id or name

        :param vm_name: Vm name or uuid. Leave empty to return all available virtual machines
        :return: List of matching vms
        """
        if not vm_name:
            return self.list_vms()
        for vm in self.list_vms():
            if vm_name in [vm.get('name'), vm.get('uuid')]:
                return [vm]
        return []

    def start_vm(self, vm_name: str):
        """Starts a specified virtual machine, optionally from a snapshot

        :param vm_name: Vm name or uuid
        :return: Vm dict
        """
        vm_name = vm_name
        assert vm_name, 'Missing vm name / uuid'

        if self.get_state(vm_name) == 'running':
            logger.info(f"VM '{vm_name}' is already running.")
            return self.get_vms(vm_name)[0]

        self.run_command(["start", vm_name])
        self.wait_for_vm(vm_name, raise_on_failure=True)
        return self.get_vms(vm_name)[0]

    def stop_vm(self, vm_name: str, force=False):
        """Stops a specified virtual machine

        :param vm_name: Vm name or uuid
        :param force: Adds '--kill' flag to stop vm forcefully
        :return: Stdout
        """
        args = ["stop", vm_name]
        if force:
            args.append("--kill")
        return self.run_command(args)

    def pause_vm(self, vm_name: str):
        """Pauses a specified virtual machine

        :param vm_name: Vm name or uuid
        :return: Stdout
        """
        return self.run_command(["pause", vm_name])

    def resume_vm(self, vm_name: str):
        """Resumes a paused virtual machine

        :param vm_name: Vm name or uuid
        :return: Stdout
        """
        return self.run_command(["resume", vm_name])

    def get_vm_info(self, vm_name: str) -> dict:
        """Gets detailed information about a virtual machine

        :param vm_name: Vm name or uuid
        :return: Information dict
        """
        output = self.run_command(["list", vm_name, "--info", "--json"])
        return json.loads(output)[0] if output else {}

    def get_state(self, vm_name: str) -> str:
        """Returns the state of the specified virtual machine

        :param vm_name: Vm name or uuid
        :return: Stdout
        """
        vm_info = self.get_vm_info(vm_name)
        return vm_info.get('State', 'unknown')

    def create_snapshot(self, vm_name: str, snapshot_name: str):
        """Creates a snapshot of a virtual machine

        :param vm_name: Vm name or uuid
        :param snapshot_name: Snapshot name to create
        :return: Stdout
        """
        return self.run_command(["snapshot", vm_name, "--name", snapshot_name])

    def delete_snapshot(self, vm_name: str, snapshot_name):
        """Deletes a snapshot from a virtual machine

        :param vm_name: Vm name or uuid
        :param snapshot_name: Snapshot name to create
        :return: Stdout
        """
        return self.run_command(["snapshot-delete", vm_name, "--name", snapshot_name])

    def revert_to_snapshot(self, vm_name: str, snapshot_name: str):
        """Reverts a virtual machine to a specified snapshot

        :param vm_name: Vm name or uuid
        :param snapshot_name: Snapshot name to create
        :return: Stdout
        """
        snapshot_id = self.resolve_snapshot_id(vm_name, snapshot_name)
        return self.run_command(["snapshot-switch", vm_name, "--id", snapshot_id])

    def resolve_snapshot_id(self, vm_name: str, snapshot_name: str):
        """Finds the snapshot ID based on the snapshot name

        :param vm_name: Vm name or uuid
        :param snapshot_name: Snapshot name to create
        :return: Stdout
        """
        output = self.run_command(["snapshot-list", vm_name, "--json"])
        if output:
            try:
                snapshots = json.loads(output)
                snapshot_id = next((_id for _id, data in snapshots.items() if data.get("name") == snapshot_name), None)
                if snapshot_id:
                    logger.info(f"Found snapshot ID: {snapshot_id}")
                return snapshot_id
            except json.JSONDecodeError:
                logger.error("Failed to parse snapshot list JSON.")
        return ''

    def wait_for_vm(self, vm_name: str, timeout=120, raise_on_failure=False):
        """Waits for the VM to become ready

        :param vm_name: Vm name or uuid
        :param timeout: Seconds to wait for the VM to become ready
        :param raise_on_failure: Raises an TimeoutError exception if the VM is not ready within the timeout
        :return: True if the VM is ready, False otherwise
        """
        end_time = time.time() + timeout
        while time.time() <= end_time:
            try:
                output = self.run_command(["exec", vm_name, "hostname"])
                if output:
                    logger.info(f"VM '{vm_name}' is up and running.")
                    return True
                else:
                    time.sleep(2)
            except Exception as e:
                time.sleep(2)
        logger.warning(f"Timed out waiting for VM '{vm_name}' to become ready")
        if raise_on_failure:
            raise TimeoutError(f"Timed out waiting for VM {vm_name} to become ready")
        return False

    def create_vm(self, vm_name: str, args: list):
        """Creates a virtual machine.

        Details about args can be found in the official Parallels CLI docs: https://docs.parallels.com/parallels-desktop-developers-guide/command-line-interface-utility/manage-virtual-machines-from-cli/general-virtual-machine-management/create-a-virtual-machine

        :param vm_name: New vm name
        :param args: Additional args to pass to the 'create' command, e.g. ['--ostype', 'ubuntu-64'] or ['--ostemplate', '<source name>']
        :return: Stdout
        """
        return self.run_command(["create", vm_name] + args)

    def delete_vm(self, vm_name: str):
        """Deletes the given vm

        :param vm_name: Vm name or uuid
        :return: Stdout
        """
        return self.run_command(["delete", vm_name])

    def get_snapshots(self, vm_name: str):
        """Returns a list of available snapshots from given vm

        :param vm_name: Vm name or uuid
        :return: Stdout
        """
        return self.run_command(["snapshot-list", vm_name])

    def get_vm_hostname(self, vm_name: str):
        """Return the vm's hostname

        :param vm_name: Vm name or uuid
        :return: Stdout
        """
        return self.run_command(['exec', vm_name, 'hostname'])
