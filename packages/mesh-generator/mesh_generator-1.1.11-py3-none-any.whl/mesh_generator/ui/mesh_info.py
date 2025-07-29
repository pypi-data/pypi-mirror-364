"""
Mesh Info stores the mesh requirements.
"""
import json
import numpy
from mesh_generator.ui.mesh_box import MeshBox


class MeshInfo:
    """
    UI Mesh dictionary. The dictionary will include the mesh requirements inputted by the user in
    tkinter ui - tkinter_mainapp.py.
    -lower and upper bounds for theta/phi/radial coordinates.
    - BG_RATIO - the ratio in regions that the user does not specify a fixed ds. (regions you do not care about) t/p
    - FG_RATIO - the maximum ration in regions that the user does specify a fixed ds. (regions you do care about) t/p
    - box_list - a list of 3d boxes with mesh segment requirements.
    """

    def __init__(self, lower_bnd_t=0., upper_bnd_t=numpy.pi, lower_bnd_p=0, upper_bnd_p=2 * numpy.pi, lower_bnd_r=1.0,
                 upper_bnd_r=2.5, BG_RATIO=1.06, FG_RATIO=1.03, RADIAL_BG_RATIO=1.06, RADIAL_FG_RATIO=1.03,
                 box_list=numpy.array([], dtype=MeshBox)):
        self.lower_bnd_t = float(lower_bnd_t)
        self.upper_bnd_t = float(upper_bnd_t)
        self.lower_bnd_p = float(lower_bnd_p)
        self.upper_bnd_p = float(upper_bnd_p)
        self.lower_bnd_r = float(lower_bnd_r)
        self.upper_bnd_r = float(upper_bnd_r)
        self.BG_RATIO = float(BG_RATIO)
        self.FG_RATIO = float(FG_RATIO)
        self.RADIAL_BG_RATIO = float(RADIAL_BG_RATIO)
        self.RADIAL_FG_RATIO = float(RADIAL_FG_RATIO)
        self.box_list = box_list

    def __str__(self):
        return json.dumps(
            self.json_dict(), indent=4, default=lambda o: o.json_dict())

    def json_dict(self):
        return {
            'lower_bnd_t': self.lower_bnd_t,
            'upper_bnd_t': self.upper_bnd_t,
            'lower_bnd_p': self.lower_bnd_p,
            'upper_bnd_p': self.upper_bnd_p,
            'lower_bnd_r': self.lower_bnd_r,
            'upper_bnd_r': self.upper_bnd_r,
            'BG_RATIO': self.BG_RATIO,
            'FG_RATIO': self.FG_RATIO,
            'RADIAL_BG_RATIO': self.RADIAL_BG_RATIO,
            'RADIAL_FG_RATIO': self.RADIAL_FG_RATIO,
            'box_list': self.type_box_list()
        }

    def insert_mesh_box(self, index, new_cube):
        """
            Insert a 3d Box to the list of UI boxes.
        """
        self.box_list = numpy.insert(self.box_list, index, new_cube)

    def append_mesh_box(self, new_cube):
        """
            Append a 3d box to the list of UI boxes.
        """
        self.box_list = numpy.append(self.box_list, new_cube)

    def type_box_list(self):
        if isinstance(self.box_list, list):
            return self.box_list
        else:
            return self.box_list.tolist()
