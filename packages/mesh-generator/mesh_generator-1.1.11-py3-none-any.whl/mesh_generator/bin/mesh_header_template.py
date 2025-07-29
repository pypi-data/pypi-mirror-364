"""
Template to write mesh_header.dat file that will later be used for
MAS MHD code.
"""

import textwrap


def write_mesh_header(tmp_mas_p_file: str, tmp_mas_t_file: str, tmp_mas_r_file: str, mesh_header_file_path: str):
    """ write mesh_header.dat file in bin folder. This formatting is copied from Cooper's IDL code.
    :param mesh_header_file_path: path and file name of resulted mesh_header.dat file.
    :param tmp_mas_r_file: mas radial mesh file path.
    :param tmp_mas_t_file: mas theta mesh file path.
    :param tmp_mas_p_file: mas phi mesh file path.
    """

    # open mas theta mesh file and read the input.
    with open(tmp_mas_t_file, "r") as theta:
        data_t = theta.readlines()

    # open mas phi mesh file and read the input.
    with open(tmp_mas_p_file, "r") as phi:
        data_p = phi.readlines()

    # open mas radial mesh file and read the input.
    with open(tmp_mas_r_file, "r") as radial:
        data_r = radial.readlines()

    # open mesh header file.
    with open(mesh_header_file_path, "w") as mesh_header:
        mesh_header.write(' &topology\n')

        # nr = total number of points. 2nd line in tmp_r file.
        # nr is the half mesh total number of points.
        mesh_header.write(data_r[1])

        # nt = total number of points. 1st line in tmp_t file.
        # nt is the half mesh total number of points.
        mesh_header.write(data_t[0])

        # np = total number of phi points. 1st line in tmp_p file.
        # np is the half mesh total number of points.
        mesh_header.write(data_p[0])

        mesh_header.write(' /\n')
        mesh_header.write(' &data\n')

        # r mesh info.
        mesh_header.write('  r0=1.00\n')
        mesh_header.write(data_r[0])
        mesh_header.write(textwrap.fill(data_r[2], width=70, subsequent_indent="    ") + "\n")
        mesh_header.write(textwrap.fill(data_r[3], width=70, subsequent_indent="    ") + "\n")
        mesh_header.write(textwrap.fill(data_r[4], width=70, subsequent_indent="    ") + "\n")

        # theta mesh info.
        mesh_header.write(textwrap.fill(data_t[1], width=70, subsequent_indent="    ") + "\n")
        mesh_header.write(textwrap.fill(data_t[2], width=70, subsequent_indent="    ") + "\n")
        mesh_header.write(textwrap.fill(data_t[3], width=70, subsequent_indent="    ") + "\n")

        # phi mesh info.
        mesh_header.write(textwrap.fill(data_p[1], width=70, subsequent_indent="    ") + "\n")
        mesh_header.write(textwrap.fill(data_p[2], width=70, subsequent_indent="    ") + "\n")
        mesh_header.write(textwrap.fill(data_p[3], width=70, subsequent_indent="    ") + "\n")
        mesh_header.write(textwrap.fill(data_p[4], width=70, subsequent_indent="    ") + "\n")


if __name__ == "__main__":
    from mesh_generator.bin.tmp_mas_template import write_tmp_mas_file

    write_tmp_mas_file(mesh_type="t", tmp_mesh_dir_name="tmp_mesh_t.dat", tmp_mas_dir_name="tmp_mas_t.dat")
    write_tmp_mas_file(mesh_type="p", tmp_mesh_dir_name="tmp_mesh_p.dat", tmp_mas_dir_name="tmp_mas_p.dat")
    write_tmp_mas_file(mesh_type="r", tmp_mesh_dir_name="tmp_mesh_r.dat", tmp_mas_dir_name="tmp_mas_r.dat")
    write_mesh_header(tmp_mas_p_file="tmp_mas_p.dat",
                      tmp_mas_t_file="tmp_mas_t.dat",
                      tmp_mas_r_file="tmp_mas_r.dat",
                      mesh_header_file_path="mesh_header.dat")
