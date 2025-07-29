"""calling psi_tools "mesh"

Step 4 of creating a 1D mesh:
    *create output files and call fortran "mesh" tool to create a file with mesh points.
    *check if mesh is valid and adjust the legacy mesh total number of points.
    *plot mesh results.
"""
from mesh_generator.bin.plot_legacy_mesh import plot_mesh_results
from mesh_generator.src.mesh_optimizer import MeshOptimizer
import os


def create_psi_mesh(adjusted_mesh: dict, legacy_mesh: dict, mesh_type: str, dir_name: str, output_file_name=None,
                    mesh_res_file_name=None, save_plot=False, show_plot=False, save_plot_path=None,
                    plot_file_name=None, input_mesh=None):
    """
    Create output files and call fortran "mesh" code to create a txt file with mesh points and respective resolution,
    and cell-to-cell ratio.
    :param input_mesh: input mesh as a dict for plotting. Optional just for plotting.
    :param plot_file_name: file name to save plot.
    :param dir_name: path to output file.
    :param mesh_res_file_name: name of file with mesh points. (t,dt, ratio) essential for plotting.
    :param output_file_name: name of file with mesh results. ex: output02_mesh_t.dat
    :param adjusted_mesh: adjusted mesh dictionary (step 2)
    :param save_plot_path: path where to save plot.
    :param save_plot: save plot as png.
    :param show_plot: bool. show matplotlib plot in interactive window.
    :param mesh_type: 't'/'p'/'r', used for plot title.
    :param legacy_mesh: legacy mesh dictionary (step 3)
    """
    # initialize mesh optimizer object that computes the optimal total number of points.
    MeshOpt = MeshOptimizer(adjusted_mesh=adjusted_mesh, legacy_mesh=legacy_mesh, mesh_type=mesh_type,
                            output_file_name=output_file_name, mesh_res_file_name=mesh_res_file_name,
                            dir_name=dir_name)

    # call the mesh optimizer routine.
    MeshOpt()

    # "plot_mesh_res": this function will plot the data in mesh_res.txt
    if save_plot or show_plot:
        plot_mesh_results(input_mesh=input_mesh, adjusted_mesh=adjusted_mesh, s=MeshOpt.s_list,
                          ds=MeshOpt.ds_list, ratio=MeshOpt.r_list, save_plot=save_plot, show_plot=show_plot,
                          label=mesh_type, save_plot_path=save_plot_path, plot_file_name=plot_file_name)


if __name__ == "__main__":
    from tests.ar_test import *

    WorkDir = os.getcwd()
    PlotDir = "../../plots/"

    create_psi_mesh(adjust__mesh_theta_1().json_dict(), legacy__mesh_theta_1().json_dict(), 't', WorkDir,
                    output_file_name="tmp_mesh_t.dat", mesh_res_file_name="mesh_res_t.dat",
                    save_plot=False, show_plot=True, save_plot_path=PlotDir, plot_file_name="theta_t_mesh.png")

    # create_psi_mesh(adjust__mesh_phi_21().json_dict(), legacy__mesh_phi_21().json_dict(), 'p', WorkDir,
    #                 output_file_name="tmp_mesh_p.dat", mesh_res_file_name="mesh_res_p.dat", show_plot=True,
    #                 save_plot=False, input_mesh=get_mesh_phi_21().json_dict())

    # create_psi_mesh(adjust__mesh_r_5().json_dict(), legacy__mesh_r_5().json_dict(), 'r', WorkDir,
    #                 output_file_name="tmp_mesh_r.dat", mesh_res_file_name="mesh_res_r.dat",
    #                 save_plot=True, show_plot=True, save_plot_path=PlotDir, plot_file_name="radial_1_mesh.png")
    #
