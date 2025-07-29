"""Legacy Mesh Segments

The mesh legacy segments contain the segment's domain, ratio, and total number of points.
The legacy mesh segments are calculated in src/mesh_segement.py.
"""
import json
import numpy


class LegacyMeshSegment:
    def __init__(self, s0, s1, ratio, num_points):
        self.s0 = numpy.float64(s0)
        self.s1 = numpy.float64(s1)
        self.ratio = numpy.float64(ratio)
        self.num_points = num_points

    def __str__(self):
        return json.dumps(
            self.json_dict(), indent=2, default=lambda o: o.json_dict())

    def __eq__(self, other):
        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        return self.__dict__ != other.__dict__

    def json_dict(self):
        return self.__dict__
