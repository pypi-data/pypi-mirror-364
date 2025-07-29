""" Mesh Box stores the mesh segments requirements in a 3d box format. """
import json
import numpy


class MeshBox:
    """
    UI Mesh box. Rectangles interactively drawn by the user on the magnetogram plot found in the main UI
    : (tkinter_mainapp.py). These are 3d boxes in spherical coordinates.
    t - theta, p - phi, r - radial.
    t0 - coordinate of begin segment. t1- coordinate of end segment (theta).
    ds- the resolution in theta/phi segments.
    tp_var_ds - the ratio growth in theta/phi segments.
    radial_ds- resolution in the radial segments.
    radial_var_ds - the ratio growth in radial segments.
    index - the order of the mesh box in the box_list.
    """
    def __init__(self, t0, t1, p0, p1, r0=None, r1=None, ds=None, radial_ds=None, radial_var_ds=None, tp_var_ds=None):
        self.t0 = numpy.float64(t0)
        self.t1 = numpy.float64(t1)
        self.p0 = numpy.float64(p0)
        self.p1 = numpy.float64(p1)
        self.r0 = r0
        self.r1 = r1
        self.ds = numpy.float64(ds)
        self.radial_ds = radial_ds
        self.radial_var_ds = radial_var_ds
        self.tp_var_ds = tp_var_ds

    def __str__(self):
        return json.dumps(
            self.json_dict(), indent=2, default=lambda o: o.json_dict())

    def json_dict(self):
        return {
            't0': self.t0,
            't1': self.t1,
            'p0': self.p0,
            'p1': self.p1,
            'r0': self.r0,
            'r1': self.r1,
            'ds': self.ds,
            'radial_ds': self.radial_ds,
            'radial_var_ds': self.radial_var_ds,
            'tp_var_ds': self.tp_var_ds
        }
