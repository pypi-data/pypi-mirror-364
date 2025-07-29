""" A function "plot_hdf()" to plot an hdf file. (magnetogram)"""
import numpy as np
from mesh_generator.ui.psihdf import rdhdf_2d


def plot_hdf(hdf_file_path):
    p, t, br_pt = rdhdf_2d(hdf_file_path)
    # NOTE: pcolorfast and pcolormesh want the coords of pixel corners not centers --> build a "half mesh" for p & t.
    # - This means making an array that is n+1 size and has the midpoint positions of the original.
    # - I choose to clip the endpoints of the half mesh to the original bounds, vs extrapolate.
    # - see also https://matplotlib.org/api/_as_gen/matplotlib.pyplot.pcolormesh.html .
    ph = np.concatenate([[p[0]], 0.5 * (p[1:] + p[:-1]), [p[-1]]])
    th = np.concatenate([[t[0]], 0.5 * (t[1:] + t[:-1]), [t[-1]]])
    return [ph, th, br_pt]


if __name__ == "__main__":
    # Choose the files to read, point the base_path to where you put the MapPipeline folder
    hdf_file_path = "/Users/opalissan/Desktop/br_caplan_shine_fill_pt.h5"
    plot_hdf(hdf_file_path)
