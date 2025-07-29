import os
import logging

from pathlib import Path
from getpass import getuser, getpass
from nornir import InitNornir
from nornir.core.task import Task, Result
from nornir_netmiko.tasks import netmiko_send_command
from nornir_utils.plugins.functions import print_result

HOME_DIR = Path(os.path.expanduser('~'))
SETTINGS_FILE = Path(HOME_DIR) / "config.yml"


class TaskHandler:
    def __init__(self):
        self.nr = InitNornir(config_file=SETTINGS_FILE,
                             dry_run=True,
                             )
        if not self.nr.inventory.defaults.username:
            self.nr.inventory.defaults.username = input("Username: ")
        if not self.nr.inventory.defaults.password:
            self.nr.inventory.defaults.password = getpass()
    
    def filter(self, site, role):
        self.nr = self.nr.filter(site=site, role=role)
    
    def show_version_task(self, task: Task) -> Result:
        return Result(
            host = task.host,
            show_ver = task.run(
                task=netmiko_send_command,
                command_string="show version"
            ),
            result = f"{task.host.name}"
        )

    def test_multiple_commands(self, task: Task) -> Result:
        return Result(
            host = task.host,
            show_ver = task.run(
                task=netmiko_send_command,
                command_string="show version"
            ),
            ip_int_bri = task.run(
                task=netmiko_send_command,
                command_string="show ip int bri"
            ),
            result = f"{task.host.name}"
        )
    
    def show(self, command) -> Result:
        if not command:
            logging.error("must provide a command to run")
            return
        return self.nr.run(task=netmiko_send_command, command_string=command)

    def print_output(self, result):
        return print_result(result)
    
    def run(self, task_name):
        if not task_name:
            logging.error("must provide a task name to run")
            return
        actions = {
            'show version': self.nr.run(task=self.show_version_task),
            'test': self.nr.run(task=self.test_multiple_commands)
        }
        return actions.get(task_name, 'show version')
