"""
Automation- generate the 3D mesh from a mesh dictionary.
taking this json/dictionary info and generates the mesh WITHOUT calling a UI in the first place.
Then you can write an example that say takes automatically generated mesh requirements (e.g.
MapPipelineCD/Misc/March2012/tdm_region_info.out), builds the box dictionary and then builds the mesh.
"""
import numpy as np
from mesh_generator.bin.call_psi_mesh_tool import create_psi_mesh
from mesh_generator.src.mesh_segment import MeshSegment
from mesh_generator.src.mesh import Mesh
from mesh_generator.bin.mesh_header_template import write_mesh_header
from mesh_generator.bin.tmp_mas_template import write_tmp_mas_file
from mesh_generator.hdf.write_1d_hdf_files import write_1d_mesh_hdf
from mesh_generator.hdf.read_mesh_res import read_tmp_file
import os
import json
import shutil


class MeshRes:
    def __init__(self, save_mesh_dir, json_file_path):
        # first load the data in json file.
        self.json_file_path = json_file_path
        self.dict_data = self.read_json_file_return_dict()

        # path for parent folder.
        self.save_mesh_dir = save_mesh_dir

        self.get_mesh_theta()
        self.get_mesh_phi()
        self.get_mesh_radial()
        self.mesh_header()
        self.write_hdf_file()
        self.copy_json_file()

    def read_json_file_return_dict(self):
        """ read input json file and return dict"""
        with open(self.json_file_path, 'r') as data:
            dict_data = json.load(data)
        return dict_data

    def copy_json_file(self):
        """ copy json file to the folder. """
        shutil.copy(src=self.json_file_path, dst=os.path.join(self.save_mesh_dir, "mesh_requirements.json"))

    def mesh_header(self):
        """ write a mesh_header file """
        write_mesh_header(tmp_mas_r_file=os.path.join(self.save_mesh_dir, "tmp_mas_r.dat"),
                          tmp_mas_t_file=os.path.join(self.save_mesh_dir, "tmp_mas_t.dat"),
                          tmp_mas_p_file=os.path.join(self.save_mesh_dir, "tmp_mas_p.dat"),
                          mesh_header_file_path=os.path.join(self.save_mesh_dir, "mesh_header.dat"))

    def write_hdf_file(self):
        """ write 1d hdf file with mesh spacing."""
        r, dr, r_ratio = read_tmp_file(name_of_tmp_file=os.path.join(self.save_mesh_dir, "mesh_res_r.dat"))
        t, dt, t_ratio = read_tmp_file(name_of_tmp_file=os.path.join(self.save_mesh_dir, "mesh_res_t.dat"))
        p, dp, p_ratio = read_tmp_file(name_of_tmp_file=os.path.join(self.save_mesh_dir, "mesh_res_p.dat"))
        write_1d_mesh_hdf(outdir=self.save_mesh_dir, mesh_name="1x", r=r, t=t, p=p, fac=1.0)

    def get_mesh_theta(self):
        if 'BG_RATIO' in self.dict_data.keys():
            MeshSegment.DEFAULT_BG_REGION_RATIO = self.dict_data['BG_RATIO']
        if 'FG_RATIO' in self.dict_data.keys():
            MeshSegment.DEFAULT_FG_REGION_RATIO = self.dict_data['FG_RATIO']

        mesh = Mesh(self.dict_data['lower_bnd_t'], self.dict_data['upper_bnd_t'], False)
        for box in self.dict_data['box_list']:
            if box['t0'] is not None and box['t1'] is not None:
                if 0 <= box['t0'] < np.pi and 0 < box['t1'] <= np.pi:
                    mesh.insert_mesh_segment(MeshSegment(box['t0'], box['t1'], box['ds'],
                                                         var_ds_ratio=box['tp_var_ds']))
        if mesh.is_valid():
            adj_mesh = mesh.resolve_mesh_segments().json_dict()
            legacy_mesh = mesh.build_legacy_mesh().json_dict()
            create_psi_mesh(adj_mesh, legacy_mesh, 't', self.save_mesh_dir, output_file_name="tmp_mesh_t.dat",
                            mesh_res_file_name="mesh_res_t.dat", save_plot=True, save_plot_path=self.save_mesh_dir,
                            plot_file_name="theta_mesh_spacing.png")
            write_tmp_mas_file(mesh_type='t', tmp_mesh_dir_name=os.path.join(self.save_mesh_dir, "tmp_mesh_t.dat"),
                               tmp_mas_dir_name=os.path.join(self.save_mesh_dir, "tmp_mas_t.dat"))

    def get_mesh_phi(self):
        if 'BG_RATIO' in self.dict_data.keys():
            MeshSegment.DEFAULT_BG_REGION_RATIO = self.dict_data['BG_RATIO']
        if 'FG_RATIO' in self.dict_data.keys():
            MeshSegment.DEFAULT_FG_REGION_RATIO = self.dict_data['FG_RATIO']

        mesh = Mesh(self.dict_data["lower_bnd_p"], self.dict_data["upper_bnd_p"], True)
        for box in self.dict_data["box_list"]:
            mesh.insert_mesh_segment(MeshSegment(box["p0"], box["p1"], box["ds"], var_ds_ratio=box["tp_var_ds"]))

        if mesh.is_valid():
            adj_mesh = mesh.resolve_mesh_segments().json_dict()
            legacy_mesh = mesh.build_legacy_mesh().json_dict()
            create_psi_mesh(adj_mesh, legacy_mesh, 'p', self.save_mesh_dir, output_file_name="tmp_mesh_p.dat",
                            mesh_res_file_name="mesh_res_p.dat", save_plot=True, save_plot_path=self.save_mesh_dir,
                            plot_file_name="phi_mesh_spacing.png")
            write_tmp_mas_file(mesh_type='p', tmp_mesh_dir_name=os.path.join(self.save_mesh_dir, "tmp_mesh_p.dat"),
                               tmp_mas_dir_name=os.path.join(self.save_mesh_dir, "tmp_mas_p.dat"))

    def get_mesh_radial(self):
        if 'RADIAL_BG_RATIO' in self.dict_data.keys():
            MeshSegment.DEFAULT_BG_REGION_RATIO = self.dict_data['RADIAL_BG_RATIO']
        if 'RADIAL_FG_RATIO' in self.dict_data.keys():
            MeshSegment.DEFAULT_FG_REGION_RATIO = self.dict_data['RADIAL_FG_RATIO']

        mesh = Mesh(self.dict_data["lower_bnd_r"], self.dict_data["upper_bnd_r"], False)
        for box in self.dict_data["box_list"]:
            if box['r0'] is not None and box['r1'] is not None:
                mesh.insert_mesh_segment(MeshSegment(box['r0'], box['r1'], ds=box['radial_ds'],
                                                     var_ds_ratio=box["radial_var_ds"]))

        if mesh.is_valid():
            adj_mesh = mesh.resolve_mesh_segments().json_dict()
            legacy_mesh = mesh.build_legacy_mesh().json_dict()
            create_psi_mesh(adj_mesh, legacy_mesh, 'r', self.save_mesh_dir, output_file_name="tmp_mesh_r.dat",
                            mesh_res_file_name="mesh_res_r.dat", save_plot=True, save_plot_path=self.save_mesh_dir,
                            plot_file_name="r_mesh_spacing.png")
            write_tmp_mas_file(mesh_type='r', tmp_mesh_dir_name=os.path.join(self.save_mesh_dir, "tmp_mesh_r.dat"),
                               tmp_mas_dir_name=os.path.join(self.save_mesh_dir, "tmp_mas_r.dat"))
