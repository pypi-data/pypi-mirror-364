"""
- "run_shell_command"
call the fortran mesh and create a txt file with the resulting mesh points.
"""
import os
from mesh_generator.bin.shell_command import run_shell_command


def call_shell_command(output_path, mesh_res_path):
    """
    - "run_shell_command"
    call the fortran mesh and create a txt file with the resulting mesh points.
    """
    # bash command
    command = "mesh " + str(output_path) + " -o " + str(mesh_res_path)
    run_shell_command(command, os.getcwd(), debug=True)
