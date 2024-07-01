#!/usr/bin/python

from ansible.module_utils.basic import AnsibleModule
import subprocess
import re
import math

def run_iris_command(module, command):
    """Run the iris command for start and stop and return the result."""
    try:
        proc = subprocess.run(command, capture_output=True, text=True, check=False)
        return proc.returncode, proc.stdout.strip(), proc.stderr.strip()
    except FileNotFoundError:
        module.fail_json(msg="'iris' command not found. Please ensure IRIS is installed and iris in the system's PATH.")
    except subprocess.TimeoutExpired:
        module.fail_json(msg="iris command timed out.")
    except subprocess.CalledProcessError as e:
        return e.returncode, e.output.strip(), e.stderr.strip()
    except Exception as e:
        module.fail_json(msg=f"An unexpected error occurred: {str(e)}")

def main():
    module_args = dict(
        instance_name=dict(type="str", required=True),
        action=dict(type="str", required=True, choices=["start", "stop"]),
        quietly=dict(type="bool", required=False, default=False),
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

    if action == "stop" and not quietly:
        module.fail_json(msg="The 'quietly' parameter is required for 'stop'.")

    command = ["iris", action, module.params["instance_name"]]

    # Build the command with conditional flags using a dictionary mapping
    flags_map = {
        "help": module.params["help"],
        "quietly": quietly,
        "nostu": action == "start" and module.params["nostu"],
        "nouser": action == "stop" and module.params["nouser"],
        "bypass": action == "stop" and module.params["bypass"],
        "restart": action == "stop" and module.params["restart"],
        "nofailover": action == "stop" and module.params["nofailover"],
    }
    command.extend([flag for flag, enabled in flags_map.items() if enabled])

    return_code, stdout, stderr = run_iris_command(module, command)

    changed = return_code == 0
    if action == "stop" and return_code == 0:
        changed = stdout != ""

    result = {"changed": changed, "stdout": stdout, "stderr": stderr}

    # Check if the error message contains "is already up!"
    if "is already up!" in stdout or "is already up!" in stderr:
        module.exit_json(changed=False, msg="No change required: Instance is already up")

    # Parse memory information if the start command was successful or if restart was True
    if return_code == 0 and (action == "start" or (action == "stop" and module.params["restart"])):
        memory_dict = {}
        for line in stdout.split("\n"):
            for search_string in ["shared memory", "global buffers", "routine buffers"]:
                if search_string in line:
                    numbers = re.findall(r"\d+", line)
                    if numbers:
                        memory_dict[search_string] = int(numbers[0])

        if memory_dict:
            result["memory_info"] = {
                f"iris_start_{key.replace(' ', '_')}": value for key, value in memory_dict.items()
            }

            # Additional 2MB hugepages calculation (if needed)
            if "shared memory" in memory_dict:
                result["memory_info"]["iris_start_hugepages_2MB"] = math.ceil(
                    (memory_dict["shared memory"] / 2) * 1.02
                )

    if return_code == 0:
        module.exit_json(**result)
    else:
        module.fail_json(msg="IRIS command execution failed", **result)

if __name__ == "__main__":
    main()