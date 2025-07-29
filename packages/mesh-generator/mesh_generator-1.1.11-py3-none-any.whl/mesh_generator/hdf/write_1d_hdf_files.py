""" In this Python module, we write 1D hdf files with r/t/p mesh spacing. """
from mesh_generator.hdf.psihdf import wrhdf_1d
import numpy as np
from scipy.interpolate import interp1d
import os


def write_1d_mesh_hdf(outdir: str, mesh_name: str, r, t, p, fac=1.0, type='.hdf'):
    """ Interpolate and build half meshes.
    :param type: ".hdf" or ".h5"
    :param outdir: directory to save mesh file.
    :param mesh_name: name of mesh file.
    :param fac: factor for interpolation spacing.
    :param p: phi mesh spacing, array.
    :param t: theta mesh spacing, array.
    :param r: radial mesh spacing, array.
    """
    # number of elements in r/p/t arrays.
    nR = len(r)
    nT = len(t)
    nP = len(p)

    # get the output main mesh using interpolate.
    nr_out = round(nR * fac)
    nt_out = round(nT * fac)
    np_out = round(nP * fac)

    # 1d interpolation.
    r_interp = interp1d(np.arange(nR), r, fill_value="extrapolate")
    t_interp = interp1d(np.arange(nT), t, fill_value="extrapolate")
    p_interp = interp1d(np.arange(nP), p, fill_value="extrapolate")

    r_new = r_interp(np.arange(nr_out) / (nr_out - 1) * (nR - 1))
    t_new = t_interp(np.arange(nt_out) / (nt_out - 1) * (nT - 1))
    p_new = p_interp(np.arange(np_out) / (np_out - 1) * (nP - 1))

    # get the half mesh for this new main mesh.
    # initialize the half mesh arrays.
    r_half = np.zeros(nr_out + 1)
    t_half = np.zeros(nt_out + 1)
    p_half = np.zeros(np_out + 1)

    r_half[0] = r_new[0] - (r_new[1] - r_new[0]) / 2
    r_half[1: -1] = np.array([(np.roll(r_new, -1) + r_new)[: nr_out - 1] / 2])
    r_half[-1] = r_new[nr_out - 1] + (r_new[nr_out - 1] - r_new[nr_out - 2]) / 2

    t_half[0] = t_new[0] - (t_new[1] - t_new[0]) / 2
    t_half[1: -1] = np.array([(np.roll(t_new, -1) + t_new)[: nt_out - 1] / 2])
    t_half[-1] = t_new[nt_out - 1] + (t_new[nt_out - 1] - t_new[nt_out - 2]) / 2

    p_half[1: -1] = np.array([(np.roll(p_new, -1) + p_new)[: np_out - 1] / 2])
    p_half[0] = p_half[-2] - 2 * np.pi
    p_half[-1] = p_half[1] + 2 * np.pi

    # write 1d hdf files.
    wrhdf_1d(hdf_filename=os.path.join(outdir, 'mesh_' + str(mesh_name) + '_main_r' + type), x=[], f=r_new)
    wrhdf_1d(hdf_filename=os.path.join(outdir, 'mesh_' + str(mesh_name) + '_main_t' + type), x=[], f=t_new)
    wrhdf_1d(hdf_filename=os.path.join(outdir, 'mesh_' + str(mesh_name) + '_main_p' + type), x=[], f=p_new)

    # write 1d half mesh hdf files.
    wrhdf_1d(hdf_filename=os.path.join(outdir, 'mesh_' + str(mesh_name) + '_half_r' + type), x=[], f=r_half)
    wrhdf_1d(hdf_filename=os.path.join(outdir, 'mesh_' + str(mesh_name) + '_half_t' + type), x=[], f=t_half)
    wrhdf_1d(hdf_filename=os.path.join(outdir, 'mesh_' + str(mesh_name) + '_half_p' + type), x=[], f=p_half)


