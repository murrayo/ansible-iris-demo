# Ansible modules and IRIS demo  
  
I have created some example Ansible modules that add functionality beyond simply using the Ansible built-in Command or Shell modules to manage IRIS. You can use these as an inspiration for creating your own modules. My hope is that this will be the start of creating an IRIS community Ansible collection.  
  
Please see the [InterSystems Developer Community post](https://community.intersystems.com/post/ansible-modules-and-iris-demo)  for background and links to the conference presentation.
  
---  
  
# If you are new to Ansible  
  
There are many resources for learning Ansible. For a good overview, I suggest this series: https://www.youtube.com/watch?v=3RiVKs8GHYQ  
  
Or search for `JayTheLinuxGuy Ansible LearnLinux TV`
## You need to connect to your servers with ssh and keys  
  
This is the most common way to manage remote Linux servers, so I expect you to know how to connect your servers with ssh.  However, if you need a refresher, the second video in the series is a good introduction to an SSH overview and setup for connecting using SSH keys.  
  
If you are connecting to AWS or other networks, you may need to use other methods to use keys and create SSH trust between the Ansible control node and target hosts.   
  
---  
  
# Running the demos  
  
## Update the inventory

You need to add your hosts to the `inventory` file. For the demos you only need one or more host names in the `[db_servers]` group. The other groups are just examples to explain grouping in the presentation.

## Review the install paths and the install file names. 

The demos assume that your infrastructure is configured and you have Red Hat 9 or Ubuntu 22 installed. This is important because I am installing IRIS for these specific OS versions and demonstrating the Ansible `when` clause using these versions.

> You need to review the group variables file if you are going to install IRIS for a different OS or version. See the file `group_vars/db_servers/iris_db_servers.yml` as shown below.

```
# Install IRIS  
target_install_file_path: "/data/iris_install_files"  
iris_install_directory: "/iris"  
  
iris_app_database_directory: "/data/databases"  
  
rhel_9_iris_install_file: "IRISHealth-2024.1.0.267.2-lnxrh9x64.tar.gz"  
ubuntu_22_04_iris_install_file: "IRISHealth-2024.1.0.267.2-lnxubuntu2204x64.tar.gz"  
rhel_9_iris_install_file_base: "IRISHealth-2024.1.0.267.2-lnxrh9x64"  
ubuntu_22_04_iris_install_file_base: "IRISHealth-2024.1.0.267.2-lnxubuntu2204x64"
```

>This GitHub repository does not include the IRIS install files or an IRIS key file. You will need to download and include the files in the directory structure before you run the demos.

There are empty placeholder files in the `roles/install_iris/files` directory. 

## Demos

### Upload files to host(s) and install IRIS

This demo runs the playbook `playbooks/iris_db_server_demo.yml`, which runs the `roles/install_iris` role.

``` shell
ansible-playbook playbooks/iris_db_server_demo.yml
```

### Other demos

I use tags to run individual demos. For example, this demo runs the `playbooks/demos.yml`, which runs the `roles/iris_demos` role. 

``` shell
ansible-playbook playbooks/demos.yml --tags "qlist_demo"
```

If you look in the `main.yml` task in `roles/iris_demos/tasks` you will see the included tasks and their tags. For example:

``` YAML
# qlist demo  
- name: IRIS qlist demo  
  ansible.builtin.import_tasks: iris_qlist.yml  
  tags: ["qlist_demo"]
```

As you should expect, the source for this task is at `roles/iris_demos/tasks/iris_qlist.yml`

To see a range of activities and to avoid running tasks before a prerequisite is not ready I suggest you explore the demos and source in this order:

``` shell
ansible-playbook playbooks/demos.yml --tags "qlist_demo"

ansible-playbook playbooks/demos.yml --tags "ansible_dump_demo"

ansible-playbook playbooks/demos.yml --tags "start_stop_builtin_demo","never"

ansible-playbook playbooks/demos.yml --tags "start_stop_demo"

ansible-playbook playbooks/demos.yml --tags "start_stop_systemd_demo"

ansible-playbook playbooks/demos.yml --tags "cpf_merge_demo"

ansible-playbook playbooks/demos.yml --tags "cpf_merge_action_demo"

ansible-playbook playbooks/demos.yml --tags "iris_terminal_demo"

ansible-playbook playbooks/demos.yml --tags "hugepages_demo"
```

### Ansible dump demo

Task: `config_dump.yml`

``` shell
ansible-playbook playbooks/demos.yml --tags "ansible_dump_demo"
```

Files are sent to:

``` YAML
"{{ role_path }}/files/{{ inventory_hostname }}_vars.json"

For example:
"msg": "Dump of variable sent to: /Users/moldfiel/projects/all_live_projects/bitbucket_tc-performance-analysis-tools/gs2024-ansible-demo/ansible-project-tc/roles/db_server/files/monitor1_vars.json"
```

For example search for `architecture` in the output file. Your group and other variables are at the end of the file.

---
