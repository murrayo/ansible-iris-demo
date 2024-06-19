#!/usr/bin/python

from ansible.module_utils.basic import AnsibleModule
import subprocess

# Return a list for more useful use of variables


def run_iris_qlist(command):
    try:
        # Execute the command using subprocess, capturing both stdout and stderr
        proc = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        stdout, stderr = proc.communicate()

        # Strip the outputs to remove unnecessary whitespaces and newlines
        stdout = stdout.strip()
        stderr = stderr.strip()

        # Return all information: the stdout and stderr
        return stdout, stderr
    except Exception as e:
        # Return exception message as stderr
        return "", str(e)


def main():
    module_args = dict(instance_name=dict(type="str", required=False))  # Optional instance name parameter

    module = AnsibleModule(argument_spec=module_args, supports_check_mode=True)

    command = ["iris", "qlist"]
    if module.params["instance_name"]:
        command.append(module.params["instance_name"])

    stdout, stderr = run_iris_qlist(command)

    if stderr:
        module.fail_json(msg="Error while executing IRIS qlist", stderr=stderr)
    else:
        # Splitting the stdout on caret and stripping any whitespace to dictionary.
        # TBD. Check output when multiple IRIS instances
        items = [item.strip() for item in stdout.split("^")]
        iris_instance_details = [
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
        ]
        fields = dict(zip(iris_instance_details, items))

        module.exit_json(changed=False, msg="IRIS qlist executed successfully", fields=fields)


if __name__ == "__main__":
    main()
