"""Mesh Generator PSI

Create a 1D Mesh in Python.

Important subpackages:
src- mesh calculations.
bin- output .dat files, optimization, plotting.


Documentation: https://q.predsci.com/docs/mesh_generator/

"""
from mesh_generator import src
from mesh_generator import bin
from mesh_generator import hdf
from mesh_generator import ui
from mesh_generator.src.mesh import Mesh
from mesh_generator.src.mesh_segment import MeshSegment
from mesh_generator.bin.call_psi_mesh_tool import create_psi_mesh
from mesh_generator.hdf.read_mesh_res import read_tmp_file
from mesh_generator.hdf.write_1d_hdf_files import write_1d_mesh_hdf
from mesh_generator.ui.upload_magnetogram import MeshGeneratorUI
from mesh_generator.bin.mesh_header_template import write_mesh_header
