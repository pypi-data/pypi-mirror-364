""" Read in mesh_res.dat files with mesh 1D points, resolution, and cell to cell ratio. """
import numpy as np
import subprocess


def read_tmp_file(name_of_tmp_file: str):
    """Read mesh_res_r/t/p.dat in mesh_generator/bin with mesh points. This will be used to write hdf visc file.
    :param name_of_tmp_file: str. name of the tmp file.
    :return: s, ds, ratio
    """
    total_num_of_points = file_len(name_of_tmp_file) - 1
    s = np.zeros(total_num_of_points)
    ds = np.zeros(total_num_of_points)
    ratio = np.zeros(total_num_of_points)

    with open(str(name_of_tmp_file), 'r') as f:
        for idx, line in enumerate(f):
            if idx >= 1:
                vec_line = line.split()
                s[idx - 1] = float(vec_line[1])
                ds[idx - 1] = float(vec_line[2])
                ratio[idx - 1] = float(vec_line[3])
    return s, ds, ratio


def file_len(file_name):
    """ Returns the number of lines in a file. """
    p = subprocess.Popen(['wc', '-l', file_name], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    result, err = p.communicate()
    if p.returncode != 0:
        raise IOError(err)
    return int(result.strip().split()[0])
