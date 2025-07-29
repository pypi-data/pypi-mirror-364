"""
A function "get_num_points()" to return the total number of points in t/p/r mesh. The total number of points
is found in bin/output.dat file.
"""


def get_num_points(file_path):
    """
    Return the total number of mesh points. Line 5 in bin.output.dat file.
    """
    with open(file_path, 'r') as res:
        num_points = res.readlines()[5]

    return num_points
