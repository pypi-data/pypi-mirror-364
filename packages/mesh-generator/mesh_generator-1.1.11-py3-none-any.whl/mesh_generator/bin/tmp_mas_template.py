"""Write mesh results in the mesh format for MAS.
Example file phi mesh: (tmp_mas_p.dat)
  np=182
  pfrac=      0.000000E+00, 2.891111E-01, 3.295278E-01, 8.093194E-01
  dpratio=    1.704159E-02, 1.000000E+00, 9.677468E+01, 6.063566E-01
  nfpmesh=5
  phishift= 6.257346E+00

Example file theta mesh: (tmp_mas_t.dat)
  nt=141
  tfrac=      0.000000E+00, 5.043889E-01, 5.606111E-01, 1.000000E+00
  dtratio=    1.826025E-02, 1.000000E+00, 4.525929E+01
  nftmesh=5

Example file radial mesh: (tmp_mas_r.dat)
  r1=10.00
  nr=107
  rfrac=      0.000000E+00, 5.555550E-03, 3.216801E-02, 3.333333E-02, 1.000000E+00
  drratio=    1.000000E+00, 3.359895E+00, 1.000000E+00, 8.819758E+01
  nfrmesh=5
"""


def write_tmp_mas_file(mesh_type: str, tmp_mesh_dir_name: str, tmp_mas_dir_name: str):
    """Write mesh results in the mesh format for MAS."""
    with open(tmp_mesh_dir_name, 'r') as mesh_file:
        mesh_data = mesh_file.readlines()

    if mesh_type == "t":
        with open(tmp_mas_dir_name, "w") as f:
            f.write("  nt=%s\n" % int(int(mesh_data[5])+1))
            tfrac = mesh_data[9].replace("/", "")
            f.write("  tfrac=      " + tfrac)
            dtratio = mesh_data[11].replace("/", "")
            f.write("  dtratio=    " + dtratio)
            f.write("  nftmesh=" + str(mesh_data[-1]))

    if mesh_type == "p":
        with open(tmp_mas_dir_name, "w") as f:
            f.write("  np=%s\n" % int(int(mesh_data[5])+1))
            pfrac = mesh_data[9].replace("/", "")
            f.write("  pfrac=      " + pfrac)
            dpratio = mesh_data[11].replace("/", "")
            f.write("  dpratio=    " + dpratio)
            f.write("  nfpmesh=%s\n" % str(mesh_data[-1]))
            f.write("  phishift= " + "{0:.6E}".format(float(mesh_data[-3])))

    if mesh_type == "r":
        with open(tmp_mas_dir_name, "w") as f:
            f.write("  r1=%s\n" % "{:.2f}".format(float(mesh_data[7].split(",")[1][1:])))
            f.write("  nr=%s\n" % int(int(mesh_data[5])+1))
            rfrac = mesh_data[9].replace("/", "")
            f.write("  rfrac=      " + str(rfrac))
            drratio = mesh_data[11].replace("/", "")
            f.write("  drratio=    " + drratio)
            f.write("  nfrmesh=" + str(mesh_data[-1]))


if __name__ == "__main__":
    import os

    workdir = os.getcwd()
    write_tmp_mas_file("t", workdir + "/tests/py_outputs/POT3D/tmp_mesh_t.dat",
                       workdir + "/tests/py_outputs/POT3D/tmp_mas_t.dat")
    write_tmp_mas_file("p", workdir + "/tests/py_outputs/POT3D/tmp_mesh_p.dat",
                       workdir + "/tests/py_outputs/POT3D/tmp_mas_p.dat")
    write_tmp_mas_file("r", workdir + "/tests/py_outputs/POT3D/tmp_mesh_r.dat",
                       workdir + "/tests/py_outputs/POT3D/tmp_mas_r.dat")
