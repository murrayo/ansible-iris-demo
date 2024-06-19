#!/usr/bin/python

from ansible.module_utils.basic import AnsibleModule
import subprocess

# Used for processing
import re
import math


def run_iris_command(command):
    """
    Run an Iris command and return the result.

    :param command: The command to be executed.
    :type command: str
    :return: A tuple containing the return code, stdout, and stderr of the command.
    :rtype: tuple
    """

    try:
        # Execute the command using subprocess, capturing both stdout and stderr
        proc = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        stdout, stderr = proc.communicate()

        # Always strip the outputs to remove unnecessary whitespaces and newlines
        stdout = stdout.strip()
        stderr = stderr.strip()

        # Return all information: whether it succeeded, the stdout, and stderr
        return proc.returncode, stdout, stderr
    except Exception as e:
        # Return error code, empty stdout, and exception message as stderr
        return 1, "", str(e)


def main():
    module_args = dict(
        instance_name=dict(type="str", required=True),
        action=dict(type="str", required=True, choices=["start", "stop"]),
        quietly=dict(type="bool", required=False, default=False),  # 'quietly' parameter
        nostu=dict(type="bool", default=False),
        nouser=dict(type="bool", default=False),
        bypass=dict(type="bool", default=False),
        restart=dict(type="bool", default=False),
        nofailover=dict(type="bool", default=False),
        help=dict(type="bool", default=False),
    )

    module = AnsibleModule(argument_spec=module_args, supports_check_mode=True)

    action = module.params["action"]
    quietly = module.params["quietly"]

    # Ensure 'quietly' is True for 'stop' action
    if action == "stop" and not quietly:
        module.fail_json(msg="The 'quietly' parameter must be True for the 'stop' action.")

    command = ["iris", module.params["action"], module.params["instance_name"]]
    # Append additional flags based on parameters
    if module.params["help"]:
        command.append("help")
    if module.params["quietly"]:
        command.append("quietly")

    if module.params["action"] == "start":
        if module.params["nostu"]:
            command.append("nostu")

    elif module.params["action"] == "stop":
        if module.params["nouser"]:
            command.append("nouser")
        if module.params["bypass"]:
            command.append("bypass")
        if module.params["restart"]:
            command.append("restart")
        if module.params["nofailover"]:
            command.append("nofailover")

    # Run the command and check the result
    return_code, stdout, stderr = run_iris_command(command)

    # Specific message handling
    memory_dict = {}
    output_dict = {}
    if stdout == "IRIS is already up!":
        module.exit_json(changed=False, msg="No change required: " + stdout)

    elif "Starting Control Process" in stdout:
        input_string = stdout
        # Keywords and their associated dictionary keys
        search_strings = ["shared memory", "global buffers", "routine buffers"]

        # Split the input string into lines and process each line
        for line in input_string.split("\n"):
            # Check each search string in the current line
            for search_string in search_strings:
                if search_string in line:
                    # Extract all numbers from the line
                    numbers = re.findall(r"\d+", line)
                    # Find the position of the search string and get the closest number
                    start_index = line.find(search_string)
                    closest_number = None
                    closest_distance = float("inf")

                    # Loop through each number found
                    for number in numbers:
                        # Find the index of the number
                        number_index = line.find(number)
                        # Calculate the distance to the search string
                        distance = abs(number_index - start_index)

                        # Check if this number is closer than the previously found closest
                        if distance < closest_distance:
                            closest_distance = distance
                            closest_number = int(number)

                    # If a number was found, add it to the dictionary
                    if closest_number is not None:
                        memory_dict[search_string] = closest_number

        output_dict = {f"iris_start_{key}": value for key, value in memory_dict.items()}

        # Add 2MB hugepages to the dictionary
        if "shared memory" in memory_dict:
            output_dict["iris_start_hugepages_2MB"] = math.ceil((memory_dict["shared memory"] / 2) * 1.02)

        # vars cannot have spaces
        output_dict = {key.replace(" ", "_"): value for key, value in output_dict.items()}

    # if iris is already stopped, the iris command return code is 0, means changed (?)
    changed = bool(stdout) if module.params["action"] == "stop" else (return_code == 0)

    # General command result handling
    if return_code == 0:
        module.exit_json(
            changed=True, msg="Command executed successfully", stdout=stdout, stderr=stderr, memory_info=output_dict
        )
    else:
        module.fail_json(msg="IRIS command execution failed", stdout=stdout, stderr=stderr)


if __name__ == "__main__":
    main()
