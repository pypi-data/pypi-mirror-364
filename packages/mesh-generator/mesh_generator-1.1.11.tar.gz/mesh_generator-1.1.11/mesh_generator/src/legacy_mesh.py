"""Legacy Mesh

Legacy mesh - (step 3 of building a mesh). The legacy mesh preserves the mesh requirements including the mesh
domain, phi_shift, BG_RATIO, and legacy segment list. The legacy mesh segment list contains the mesh segment total
number of points, ratio, and domain. For more details about legacy mesh segments go to src/legacy_mesh_segment.py
"""

import json
import numpy
from mesh_generator.src.legacy_mesh_segment import LegacyMeshSegment
from mesh_generator.src.mesh_segment import MeshSegment


class LegacyMesh:
    def __init__(self, lower_bnd, upper_bnd, periodic=False, phi_shift=0.0):
        self.lower_bnd = numpy.float64(lower_bnd)
        self.upper_bnd = numpy.float64(upper_bnd)
        self.periodic = periodic
        self.phi_shift = numpy.float64(phi_shift)
        self.BG_RATIO = MeshSegment.DEFAULT_BG_REGION_RATIO
        self.segment_list = numpy.array([], dtype=LegacyMeshSegment)

    def __str__(self):
        return json.dumps(
            self.json_dict(), indent=2, default=lambda o: o.json_dict())

    def json_dict(self):
        return {
            'lower_bnd': self.lower_bnd,
            'upper_bnd': self.upper_bnd,
            'periodic': self.periodic,
            'phi_shift': self.phi_shift,
            'BG_RATIO': MeshSegment.DEFAULT_BG_REGION_RATIO,
            'segment_list': [segment.json_dict() for segment in self.segment_list.tolist()]
        }

    def insert_mesh_segment(self, new_segment, beg_index=0):
        """
        Inserts a mesh segment into the list of mesh segments and returns its
        position in the list. The mesh segments in the list are sorted by the
        start position followed by the end position in ascending order.

        Setting `beg_index` allows the comparison and insertion to start at
        `beg_index` instead of the beginning of the list, which may speed up
        the insertion process. However, it can break the sorting order of the
        mesh segments in the list if used without care.
        """
        for index in range(beg_index, len(self.segment_list)):
            segment = self.segment_list[index]
            if new_segment.s0 < segment.s0:
                break
            elif new_segment.s0 == segment.s0:
                if new_segment.s1 > segment.s1:
                    index += 1
                break
        else:
            index = len(self.segment_list)

        if index == -1:
            self.segment_list = numpy.append(self.segment_list, new_segment)
        else:
            self.segment_list = numpy.insert(
                self.segment_list, index, new_segment)

        return index
