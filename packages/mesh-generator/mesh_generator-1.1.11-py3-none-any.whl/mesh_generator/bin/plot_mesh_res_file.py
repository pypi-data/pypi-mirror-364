"""
Plotting the psi mesh data results saved in the file mesh_res[t/p/r].dat
"""
import numpy as np
from matplotlib import pyplot as plt
import time
import os


def plot_mesh_res(input_mesh: dict, adjusted_mesh: dict, save_plot: bool, mesh_res_file_name: str,
                  show_plot: bool, label: str, save_plot_path: str, plot_file_name: str):
    """
       plot the mesh points in tmp_mesh_r.dat

       Arguments:
           :param input_mesh: dict with input mesh requirements.
           :param mesh_res_file_name: name of file with mesh res. Ex) mesh_res_r.dat
           :param plot_file_name: name of the png file saved.
           :param save_plot_path: path to save png plot.
           :param show_plot: bool: if true it will show the matplotlib figure. Interactive widget.
           :param save_plot: dictionary with adjusted mesh segments.
           :param adjusted_mesh: bool: if true it will save the plot as a png in plot file.
           :param label:  't'/'p'/'r'
       """
    xvals, yvals, rvals = [], [], []

    with open(str(mesh_res_file_name), "r") as f:
        fig, axs = plt.subplots(2, figsize=(7, 6.5))
        for idx, line in enumerate(f):
            if idx >= 1:
                for word in line.split()[1:2]:
                    xvals.append(float(word))
                for word in line.split()[2:3]:
                    yvals.append(float(word))
                for word in line.split()[3:4]:
                    rvals.append(float(word))

    # Set the plot title by the mesh type (theta/phi/radial)
    if label == 't':
        axs[0].set_xlabel(' \u03B8 ')
        axs[1].set_xlabel(' \u03B8 ')
        axs[0].set_ylabel('\u0394 \u03B8')
        title = "Theta Mesh Spacing"
    if label == 'p':
        axs[0].set_xlabel(' \u03C6 ')
        axs[1].set_xlabel(' \u03C6 ')
        axs[0].set_ylabel('\u0394 \u03C6')
        plt.axvline(x=0, dashes=[6, 2], color='gray')
        plt.axvline(x=np.pi * 2, dashes=[6, 2], color='gray')
        title = "Phi Mesh Spacing"
    if label == 'r':
        axs[0].set_xlabel(' r ')
        axs[1].set_xlabel(' r ')
        axs[0].set_ylabel('\u0394 r')
        title = "Radial Mesh Spacing"

    # total number of points is also the total number of rows in bin/mesh_res.txt file.
    num_of_points = str(idx)
    axs[0].set_title(title + ", n = " + num_of_points, y=1.3)  # add it to the title
    # plot the legacy mesh
    axs[0].plot(xvals, yvals, label="Final mesh")
    # plot the mesh ratio
    axs[1].plot(xvals, rvals, label='Ratio')
    axs[1].set_title("Ratio", y=1.3)
    seg_label_ratio = "Input segment requirements"
    seg_label =  "Input segment requirements"
    adj_label = "Adjusted segments"
    # plot step 2 of creating a mesh. The segments after calling the function resolve_mesh_segments() in mesh src/
    for i in range(0, 2):
        for segments in adjusted_mesh['segment_list']:
            s1 = segments['s1'] + (adjusted_mesh['phi_shift'])
            s0 = segments['s0'] + (adjusted_mesh['phi_shift'])
            if s1 <= adjusted_mesh["upper_bnd"]:
                axs[i].axvline(x=s1, dashes=[6, 2], color='gray')
            if s0 >= adjusted_mesh["lower_bnd"]:
                axs[i].axvline(x=s0, dashes=[6, 2], color='gray')
            axs[0].plot([s1, s0], [segments['ds1'], segments['ds0']], linewidth=1, color='aqua', label=adj_label)
            adj_label = "_nolegend_"

        if input_mesh is not None:
            for segment in input_mesh['segment_list']:
                s1 = segment['s1'] + (input_mesh['phi_shift'])
                s0 = segment['s0'] + (input_mesh['phi_shift'])
                if s1 <= adjusted_mesh["upper_bnd"]:
                    axs[i].axvline(x=s1, dashes=[6, 2], color='gray')
                if s0 >= adjusted_mesh["lower_bnd"]:
                    axs[i].axvline(x=s0, dashes=[6, 2], color='gray')
                if i == 0:
                    if segment['ds0'] is not np.inf:
                        axs[0].hlines(segment['ds0'], s0, s1, linewidth=1.5, color='k', label=seg_label)
                        seg_label = "_nolegend_"
                    if segment['var_ds_ratio'] != input_mesh["BG_RATIO"]:
                        axs[1].hlines(segment['var_ds_ratio'], s0, s1, linewidth=1, color='k', label=seg_label_ratio)
                        seg_label_ratio = "_nolegend_"
                        axs[1].hlines(1/segment['var_ds_ratio'], s0, s1, linewidth=1, color='k', label=seg_label_ratio)
                        seg_label_ratio = "_nolegend_"
        axs[i].axvline(x=adjusted_mesh['upper_bnd'], dashes=[6, 2], color='gray')
        axs[i].axvline(x=adjusted_mesh['lower_bnd'], dashes=[6, 2], color='gray')

    fig.canvas.set_window_title(title)
    axs[0].legend(bbox_to_anchor=(0, 1.02, 1, 0.2), loc="lower left", mode="expand", ncol=3)
    axs[1].legend(bbox_to_anchor=(0, 1.02, 1, 0.2), loc="lower left", mode="expand", ncol=3)
    plt.tight_layout()

    if save_plot:
        if plot_file_name is None:
            plot_file_name = str(time.ctime()) + " " + title + ".png"

        plot_path = os.path.join(save_plot_path, plot_file_name)
        plt.savefig(plot_path)

    if show_plot:
        plt.show()


