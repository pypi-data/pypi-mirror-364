"""
- "run_shell_command" is the main function for calling command
  line executeables.
"""
import os
import subprocess


def run_shell_command(command: str, dirname: str, debug=False):
    """
    Execute a shell command inside python.

    Arguments:
        command: a string containing the command and its arguments.
        dirname: a string containing the path of the desired working directory.
    """
    process = subprocess.Popen(
        command, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        shell=True, cwd=dirname)

    try:
        stdout, stderr = process.communicate(timeout=300)
        if debug:
            for line in stdout.strip().decode().splitlines():
                print(line)
            for line in stderr.strip().decode().splitlines():
                print(line)
    except subprocess.TimeoutExpired:
        process.kill()

    # check the return code here, if non-zero, print the output and raise an exception.
    if process.returncode != 0:
        print('')
        print('ERROR: run_shell_command returned a non-zero exit code!', process.returncode)
        print('  Shell command:', command)
        print('  STDOUT: ')
        for line in stdout.strip().decode().splitlines():
            print('    ' + line)
        print('  STDERR: ')
        for line in stderr.strip().decode().splitlines():
            print('    ' + line)
        raise RuntimeError('Shell command: ' + str(command) + ' returned exit code: ' + str(process.returncode))

    return process.returncode


if __name__ == "__main__":
    command = "mesh output02_mesh_t.dat -o mesh_res.txt"
    run_shell_command(command, os.getcwd(), debug=True)
