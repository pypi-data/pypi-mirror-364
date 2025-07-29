# net-task-client

net_task_client is a network task client using nornair to run tasks on multiple devices.

## To Install

```
py -m pip install net-task-client
Please create the following files to run the client.
Example config, hosts, groups, defaults are included with the git package.

~/
├── defaults.yml
├── groups.yml
├── hosts.yml
├── config.yml

```

## Usage
Please make sure you update the inventory file hosts.yml with your settings.
```
import net_task_client
client = net_task_client.TaskHandler()
output = client.run('show version')
client.print_output(output)
```