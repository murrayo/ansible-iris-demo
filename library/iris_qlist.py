#!/usr/bin/env python3

from ansible.module_utils.basic import AnsibleModule
import subprocess
import shlex
import shutil

IRIS_INSTANCE_DETAILS = [
    "iris_qlist_instance_name",
    "iris_qlist_instance_install_directory",
    "iris_qlist_version_identifier",
    "iris_qlist_current_status_for_the_instance",
    "iris_qlist_configuration_file_name_last_used",
    "iris_qlist_super_server_port_number",
    "iris_qlist_web_server_port_number",
    "iris_qlist_jdbc_gateway_port_number",
    "iris_qlist_instance_status",
    "iris_qlist_product_name_of_the_instance",
    "iris_qlist_mirror_member_type",
    "iris_qlist_mirror_status",
    "iris_qlist_instance_data_directory",
    "iris_qlist_extra_field_not_in_documentation",
]

def command_exists(command):
    """
    Check if a command exists on the system.

    Args:
        command (str): The command to check.

    Returns:
        bool: True if the command exists, False otherwise.
    """
    return shutil.which(command) is not None

def run_iris_qlist(instance_name=None):
    """
    Run the 'iris qlist' command with optional instance name.

    Args:
        instance_name (str): The name of the IRIS instance.

    Returns:
        tuple: stdout and stderr from the command execution.
    """
    command = ["iris", "qlist"]
    if instance_name:
        command.append(shlex.quote(instance_name))

    try:
        result = subprocess.run(
            command,
            capture_output=True,
            check=True,
            text=True,
        )
        return result.stdout.strip(), None
    except subprocess.CalledProcessError as e:
        return None, e.stderr.strip()

def main():
    module = AnsibleModule(
        argument_spec=dict(
            instance_name=dict(type="str", required=False),
        ),
        supports_check_mode=True,
    )

    # Check if the 'iris' command exists
    if not command_exists("iris"):
        module.fail_json(msg="'iris' command not found. Please ensure IRIS is installed and iris in the system's PATH.")

    instance_name = module.params.get("instance_name")

    # Validate the instance name if provided
    if instance_name and not instance_name.isalnum():
        module.fail_json(msg="Invalid instance name. Only alphanumeric characters are allowed.")

    stdout, stderr = run_iris_qlist(instance_name)

    if stderr:
        module.fail_json(msg="IRIS qlist failed", stderr=stderr)

    items = [item.strip() for item in stdout.split("^")]
    if len(items) != len(IRIS_INSTANCE_DETAILS):
        module.fail_json(msg="Unexpected IRIS qlist output format", output=stdout)

    fields = dict(zip(IRIS_INSTANCE_DETAILS, items))
    module.exit_json(changed=False, msg="IRIS qlist executed successfully", fields=fields)

if __name__ == "__main__":
    main()
