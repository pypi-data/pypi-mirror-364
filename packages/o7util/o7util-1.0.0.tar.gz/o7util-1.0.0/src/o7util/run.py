# ************************************************************************
# Copyright 2023 O7 Conseils inc (Philippe Gosselin)
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# ************************************************************************
"""Run a process with a timeout"""

import os
import subprocess


# *************************************************
#
# *************************************************
def get_process_children(pid: int) -> list[int]:
    """Get the children of the process"""

    ret = []
    cmds = [
        "ps",
        "--no-headers",
        "-o",
        "pid",
        "--ppid",
        str(pid),
    ]

    with subprocess.Popen(  # noqa: S603
        cmds,
        shell=False,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    ) as proc:
        stdout = proc.communicate()[0]

        ret = [int(proc) for proc in stdout.split()]

    return ret


# *************************************************
# Run a process with a timeout
# *************************************************
def run(args, cwd=None, timeout=None, env=None) -> tuple[int, str, str]:
    """Run a process with a timeout"""

    # Ref: https://docs.python.org/3/library/subprocess.html
    ret = (-1, "", "")
    pid = None
    cmds = args.split()
    try:
        with subprocess.Popen(  # noqa: S603
            cmds,
            cwd=cwd,
            shell=False,
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        ) as proc:
            pid = proc.pid
            stdout, stderr = proc.communicate(timeout=timeout)
            ret = (proc.returncode, stdout.decode("utf-8"), stderr.decode("utf-8"))

    except FileNotFoundError:
        # print(f"ERROR: not able to found execution file: {args}")
        ret = (-8, "", "")

    except subprocess.TimeoutExpired:
        # print (f"Need to kill PID {proc.pid}, os.name {os.name} sys.platform {sys.platform}")

        if os.name == "nt":
            cmds = [
                "tasklist",
                "/F",  # force
                "/T",  # tree
                "/PID",  # process id
                str(pid),
                ">",
                "o7util-tasklist.log",
            ]
            subprocess.run(  # noqa: S603
                cmds,
                shell=False,
                check=False,
            )
        else:
            proc.kill()
            proc.communicate()

        ret = (-9, "", "")

    return ret


# *************************************************
# To Test Class
# *************************************************
def main():
    """Main function to test the class"""
    if __name__ == "__main__":
        print(get_process_children(os.getpid()))

        print("Sleeping for 4 sesonds")
        test = run("sleep 4", timeout=1)
        print(test)
        print("Sleeping for 1 sesonds")
        test = run("sleep 1")
        print(test)


main()
