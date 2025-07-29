"""test the translation of psi mesh tool "mesh.f". The translated py module is in mesh/generator/bin/psi_mesh_tool.py"""

from mesh_generator.bin.call_mesh_shell_command import call_shell_command
from mesh_generator.bin.psi_mesh_tool import write_mesh_res_file
import unittest


class TestMeshCases(unittest.TestCase):
    def test_theta_mesh_res(self):
        for i in range(1, 17):
            # file with mesh requirements.
            output_file = "output/output02_mesh_t_" + str(i) + ".dat"

            # file with mesh points.
            mesh_res_for = "fortran_mesh_res/mesh_res_t_" + str(i) + ".dat"
            mesh_res_py = "py_mesh_res/mesh_res_t_" + str(i) + ".dat"

            # write fortran file
            call_shell_command(output_file, mesh_res_for)
            # write python file
            write_mesh_res_file(mesh_res_py, output_file)

            # open both fortran and python files and compare the lines.
            with open(mesh_res_for, 'r') as fortran:
                output_for = fortran.readlines()

            with open(mesh_res_py, 'r') as py:
                output_py = py.readlines()

            # check if both files have the same number of lines.
            self.assertTrue(len(output_py), len(output_for))

            # compare each line in the two files.
            for ii in range(0, len(output_for)):
                self.assertTrue(output_py[ii], output_for[ii])

    def test_phi_mesh_res(self):
        for i in range(1, 30):
            # file with mesh requirements.
            output_file = "output/output02_mesh_p_" + str(i) + ".dat"

            # file with mesh points.
            mesh_res_for = "fortran_mesh_res/mesh_res_p_" + str(i) + ".dat"
            mesh_res_py = "py_mesh_res/mesh_res_p_" + str(i) + ".dat"

            # write fortran file
            call_shell_command(output_file, mesh_res_for)
            # write python file
            write_mesh_res_file(mesh_res_py, output_file)

            # open both fortran and python files and compare the lines.
            with open(mesh_res_for, 'r') as fortran:
                output_for = fortran.readlines()

            with open(mesh_res_py, 'r') as py:
                output_py = py.readlines()

            # check if both files have the same number of lines.
            self.assertTrue(len(output_py), len(output_for))

            # compare each line in the two files.
            for ii in range(0, len(output_for)):
                self.assertTrue(output_py[ii], output_for[ii])

    def test_r_mesh_res(self):
        for i in range(1, 6):
            # file with mesh requirements.
            output_file = "output/output02_mesh_r_" + str(i) + ".dat"

            # file with mesh points.
            mesh_res_for = "fortran_mesh_res/mesh_res_r_" + str(i) + ".dat"
            mesh_res_py = "py_mesh_res/mesh_res_r_" + str(i) + ".dat"

            # write fortran file
            call_shell_command(output_file, mesh_res_for)
            # write python file
            write_mesh_res_file(mesh_res_py, output_file)

            # open both fortran and python files and compare the lines.
            with open(mesh_res_for, 'r') as fortran:
                output_for = fortran.readlines()

            with open(mesh_res_py, 'r') as py:
                output_py = py.readlines()

            # check if both files have the same number of lines.
            self.assertTrue(len(output_py), len(output_for))

            # compare each line in the two files.
            for ii in range(0, len(output_for)):
                self.assertTrue(output_py[ii], output_for[ii])


if __name__ == "__main__":
    unittest.main()
