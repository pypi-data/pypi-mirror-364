""" Adjusted Mesh Segment

Building a mesh can be broken down into four steps.
Here, we will contribute to compute step 2, and 3.

In step 2: Adjust mesh segments.
    While running mesh/resolve_mesh_segments() if there is a need to add segments or delete segments then the class
    below is called.

In step 3: Build Legacy mesh.
    In the function below "get_legacy_segment()" it takes in a mesh segment with a specified domain,
    resolution, and ratio.
    Then computes its total number of points and the ratio between the begin and end ds (ds1/ds0).

The solution details are explained below:
    * Note: these equations are also in the mkdocs static site under "mesh equations".

    For each segment I want to know the number of points it will take me to go
    either a fixed distance at a certain cell-to-cell ratio, R, OR get to a
    fixed new ds at a certain R.

    The MAS mesh equation calculates the next segment ds as ds(i+1) = R*ds(i),
    where R is the cell to cell mesh expansion ratio.

    This looks like the equation for ds as a function of npts: ds(n) = ds(0)*R^n

    What I need is to determine the number of points for each segment that goes
    from s0 to s1, satisfying certain constrains.

    Currently I divide this into three cases:

    CONSTANT: simplest, R=1, n = (s1-s0)/ds0

    FIXED_LENGTH: Go a fixed distance at a specified ratio starting at a given
                  ds0. Integrate the ds(n) equation, get S = ds0*(R^n - 1)/ln(R)
                  Solve this for n, get n = ln[ ln(R)*S/ds0 +1]/ln(R)

    FIXED_DS: Specify the DS at both sides (ds0, and ds1) and attempt to find a
              Solution that does this in the fewest number of points, at a fixed R
            - Solve ds1 = ds0*R^n, which is n = ln(ds1/ds0)/ln(R).
              Then the length is S = ds0*(R^n - 1)/ln(R)
            - HOWEVER, the length is not constrained to be s1-s0 --> it will
              be shorter or longer.
              - shorter case is simple, add const mesh at larger ds to make up gap
              - longer case means you have to go back to previous or next seg
              ---> a solution may not be found if it crosses others.
                - solving this issue adds most of complexity of the code because
                  I have to add recursion and a lot of case checking.

"""

import json
import numpy
from .legacy_mesh_segment import LegacyMeshSegment

EPSILON = 1 / numpy.power(10, 10)


class MeshSegment:
    # Mesh points distance in background area. INF value indicates that the
    # mesh can be as coarse as possible.
    BG_REGION_DS = numpy.inf

    # Ratio of mesh with constant density.
    CONSTANT_DS_RATIO = 1.00

    # Default ratio of mesh with decreasing density (increasing ds) in area
    # of interest and background area respectively.
    DEFAULT_FG_REGION_RATIO = 1.03
    DEFAULT_BG_REGION_RATIO = 1.06

    def __init__(self, s0, s1, ds=None, var_ds_ratio=None):
        """
        float: s0 and s1
            Lower and upper boundaries respectively.
        float: ds
            Distance between two mesh points, which represents density.
        float: var_ds_ratio
            Ratio between two subsequent distances of mesh with decreasing
            density (increasing ds).
        """
        if ds is None:
            ds = MeshSegment.BG_REGION_DS

        if var_ds_ratio is None:
            var_ds_ratio = MeshSegment.DEFAULT_BG_REGION_RATIO \
                if ds == MeshSegment.BG_REGION_DS \
                else MeshSegment.DEFAULT_FG_REGION_RATIO

        self.s0 = numpy.float64(s0)
        self.s1 = numpy.float64(s1)
        self.ds0 = numpy.float64(ds)
        self.ds1 = numpy.float64(ds)
        self.var_ds_ratio = numpy.float64(var_ds_ratio)

    def __str__(self):
        return json.dumps(
            self.json_dict(), indent=2, default=lambda o: o.json_dict())

    def json_dict(self):
        return {
            's0': self.s0,
            's1': self.s1,
            'ds0': self.ds0,
            'ds1': self.ds1,
            'var_ds_ratio': self.var_ds_ratio,
            'ratio': self.get_ratio()
        }

    @staticmethod
    def validate_bnd(s0, s1):
        return s0 < s1

    @staticmethod
    def validate_ds(ds0, ds1=None):
        if ds0 <= 0.0:
            return False

        if ds1 is not None and ds1 <= 0.0:
            return False

        return True

    def set_ds(self, ds0, ds1=None):
        """set the mesh segments ds0 and ds1 (begin and end resolution respectively)."""
        if ds1 is None:
            ds1 = ds0

        self.ds0 = numpy.float64(ds0)
        self.ds1 = numpy.float64(ds1)

    @staticmethod
    def validate_var_ds_ratio(var_ds_ratio):
        return var_ds_ratio > 0.0 and var_ds_ratio != MeshSegment.CONSTANT_DS_RATIO

    def set_var_ds_ratio(self, var_ds_ratio):
        self.var_ds_ratio = numpy.float64(var_ds_ratio)

    def segment_is_valid(self):
        return self.validate_bnd(self.s0, self.s1) \
               and self.validate_ds(self.ds0, self.ds1) \
               and self.validate_var_ds_ratio(self.var_ds_ratio)

    def get_ratio(self):
        """
        Returns the effective ratio based on the ds values on both end points.
        A mesh with constant density has a ratio of 1.0. Otherwise, the ratio
        will be according to the user specification.
        """
        if self.has_increasing_ds():
            return self.var_ds_ratio if self.var_ds_ratio > 1.0 \
                else 1.0 / self.var_ds_ratio
        elif self.has_decreasing_ds():
            return self.var_ds_ratio if self.var_ds_ratio < 1.0 \
                else 1.0 / self.var_ds_ratio
        else:
            return MeshSegment.CONSTANT_DS_RATIO

    def is_fixed_length(self):
        """
        Returns whether this segment has an unspecified ds value on one of the
        end points. This represents a background area where the mesh can be as
        coarse as possible.
        """
        return (self.ds0 == MeshSegment.BG_REGION_DS \
                or self.ds1 == MeshSegment.BG_REGION_DS) \
               and self.ds0 != self.ds1

    def is_fixed_ds(self):
        """
        Returns whether this segment has specific and different ds values on
        both end points. This represents an area of interest where the mesh
        is either decreasing or increasing in density.
        """
        return self.ds0 != MeshSegment.BG_REGION_DS \
               and self.ds1 != MeshSegment.BG_REGION_DS \
               and self.ds0 != self.ds1

    def is_constant(self):
        """
        Returns whether this segment has one specific ds value on both end
        points. This represents an area of interest where the mesh has constant
        density i.e., distributed evenly across the region.
        """
        return self.ds0 != MeshSegment.BG_REGION_DS and self.ds0 == self.ds1

    def has_increasing_ds(self):
        """
        Returns whether the mesh in this segment has increasing ds values i.e.,
        decreasing density.
        """
        return self.ds0 < self.ds1

    def has_decreasing_ds(self):
        """
        Returns whether the mesh in this segment has decreasing ds values i.e.,
        increasing density.
        """
        return self.ds0 > self.ds1

    def get_ds0_using_num_points(self, num_points):
        """
        Returns ds0 using the segments number of points and ratio. In this case usually, ds0 = inf.
        """
        ratio = 1 / self.get_ratio()
        return self.ds1 * numpy.power(ratio, int(num_points))

    def get_ds1_using_num_points(self, num_points):
        """
        Returns ds1 using the segments number of points and ratio. In this case usually, ds1 = inf.
        """
        return self.ds0 * numpy.power(self.get_ratio(), int(num_points))

    def get_ratio_given_num_points(self, num_points):
        """ Returns the ratio when ds1 and ds0 are fixed and num_points is also fixed. """
        if self.ds0 != numpy.inf:
            ds0 = self.ds0
        else:
            ds0 = self.get_ds0_using_num_points(num_points)

        if self.ds1 != numpy.inf:
            ds1 = self.ds1
        else:
            ds1 = self.get_ds1_using_num_points(num_points)

        return numpy.exp(numpy.log(ds1 / ds0) / num_points)

    def get_length(self):
        """
        Returns the segment length.
        """
        return self.s1 - self.s0

    def get_legacy_ratio(self):
        """
        Returns the segment ratio between mesh distances at the two end points.
        """
        if self.is_constant():
            return 1.0
        elif self.is_fixed_ds():
            return self._get_legacy_ratio_fixed_ds_mesh()
        elif self.is_fixed_length():
            return self._get_legacy_ratio_fixed_length_mesh()

        raise Exception('Unknown mesh segment type.')

    def get_num_points(self):
        """
        Returns the minimum number of mesh points this segment would need to
        meet its constraints.
        """
        if self.is_constant():
            return self._get_num_points_constant_mesh()
        elif self.is_fixed_ds():
            return self._get_num_points_fixed_ds_mesh()
        elif self.is_fixed_length():
            return self.get_num_points_fixed_length_mesh()

        raise Exception('Unknown mesh segment type.')

    def get_legacy_mesh_segments(self, lower_bnd, upper_bnd):
        """
        Important function to compute legacy mesh segment.
        Here we compute the 3 mesh segment types: constant/fixed_ds/fixed_length.
        It handles the overshooting fixed_ds cases by adding a small constant segment to fill in the gap.
        """
        legacy_mesh_segment_list = numpy.array([])

        if self.is_constant() or self.is_fixed_length():
            legacy_segment = LegacyMeshSegment(
                self.s0, self.s1, self.get_legacy_ratio(),
                self.get_num_points())
            legacy_mesh_segment_list = numpy.append(
                legacy_mesh_segment_list, legacy_segment)
            return legacy_mesh_segment_list

        segment_num_points = self.get_num_points()
        legacy_ratio = self.get_legacy_ratio()
        segment_length = self.get_length()
        length_var_ds = self._get_length_using_num_points(segment_num_points)

        if length_var_ds < segment_length - EPSILON:
            if self.has_increasing_ds():
                length_cst_ds = self.s0 + length_var_ds
                new_cst_segment = MeshSegment(
                    length_cst_ds, self.s1, self.ds1)
                legacy_segment = LegacyMeshSegment(
                    self.s0, new_cst_segment.s0, legacy_ratio,
                    segment_num_points)
                legacy_new_cst_segment = LegacyMeshSegment(
                    new_cst_segment.s0, new_cst_segment.s1,
                    new_cst_segment.get_legacy_ratio(),
                    new_cst_segment.get_num_points())
                legacy_mesh_segment_list = numpy.append(
                    legacy_mesh_segment_list, legacy_segment)
                legacy_mesh_segment_list = numpy.append(
                    legacy_mesh_segment_list, legacy_new_cst_segment)
            else:
                length_cst_ds = self.s1 - length_var_ds
                new_cst_segment = MeshSegment(
                    self.s0, length_cst_ds, self.ds0)
                legacy_segment = LegacyMeshSegment(
                    new_cst_segment.s1, self.s1, legacy_ratio,
                    segment_num_points)
                legacy_new_cst_segment = LegacyMeshSegment(
                    new_cst_segment.s0, new_cst_segment.s1,
                    new_cst_segment.get_legacy_ratio(),
                    new_cst_segment.get_num_points())
                legacy_mesh_segment_list = numpy.append(
                    legacy_mesh_segment_list, legacy_new_cst_segment)
                legacy_mesh_segment_list = numpy.append(
                    legacy_mesh_segment_list, legacy_segment)
        elif length_var_ds > segment_length + EPSILON:
            if self.has_increasing_ds():
                if self.s1 == upper_bnd:
                    self.ds1 = numpy.inf
                    legacy_segment = LegacyMeshSegment(self.s0, self.s1, self.get_legacy_ratio(), self.get_num_points())
                else:
                    legacy_segment = LegacyMeshSegment(
                        self.s0, self.s0 + length_var_ds, legacy_ratio,
                        segment_num_points)
            else:
                if self.s0 == lower_bnd:
                    self.ds0 = numpy.inf
                    legacy_segment = LegacyMeshSegment(
                        self.s0, self.s1, self.get_legacy_ratio(),
                        self.get_num_points())
                else:
                    legacy_segment = LegacyMeshSegment(
                        self.s1 - length_var_ds, self.s1, legacy_ratio,
                        segment_num_points)

            legacy_mesh_segment_list = numpy.append(
                legacy_mesh_segment_list, legacy_segment)
        else:
            legacy_segment = LegacyMeshSegment(
                self.s0, self.s1, legacy_ratio,
                segment_num_points)
            legacy_mesh_segment_list = numpy.append(
                legacy_mesh_segment_list, legacy_segment)

        return legacy_mesh_segment_list

    def _get_legacy_ratio_fixed_ds_mesh(self):
        """return the segment ratio when segment is of fixed_ds type."""
        return self.ds1 / self.ds0

    def _get_legacy_ratio_fixed_length_mesh(self):
        """return the segment ratio when segment is of fixed_length type."""
        return numpy.power(self.get_ratio(), self.get_num_points())

    def _get_length_using_num_points(self, num_points):
        """
        By knowing the segment's total number of points and ratio we can compute its domain length.
        S = ds0*(R^n - 1)/ln(R)
        """
        if self.is_constant():
            return self.ds0 * num_points
        else:
            if self.has_decreasing_ds():
                ds = self.ds1
                ratio = 1.0 / self.get_ratio()
            else:
                ds = self.ds0
                ratio = self.get_ratio()

        return ds * (numpy.power(ratio, num_points) - 1) / numpy.log(ratio)

    def _get_num_points_constant_mesh(self):
        """Compute the constant mesh segment total number of points."""
        return int(numpy.ceil(self.get_length() / self.ds0))

    def _get_num_points_fixed_ds_mesh(self):
        """Compute the fixed_ds mesh segment total number of points."""
        return int(numpy.ceil(
            numpy.log(self.ds1 / self.ds0) / numpy.log(self.get_ratio())))

    def get_num_points_fixed_length_mesh(self):
        """Compute the fixed_length mesh segment total number of points."""
        if self.has_decreasing_ds():
            ds = self.ds1
            ratio = 1.0 / self.get_ratio()
        else:
            ds = self.ds0
            ratio = self.get_ratio()
        ln_ratio = numpy.log(ratio)

        return int(numpy.ceil(numpy.log(ln_ratio * self.get_length() / ds + 1) / ln_ratio))
