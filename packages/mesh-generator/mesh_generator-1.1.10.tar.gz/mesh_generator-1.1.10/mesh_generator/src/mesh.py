"""Mesh

src/mesh.py: The main code to generate a MAS mesh in python.

Overview:
The process of building an optimal mesh is divided into 4 steps.
Step 1: input mesh requirements.
Step 2: adjusted_mesh: adjust mesh segments. call the function below called "resolve_mesh_segments()"
Step 3: legacy_mesh: compute the legacy mesh. Call the function below called "build_legacy_mesh()"
Step 4: call fortran mesh and write output.dat and mesh_res.txt files.

In this file, we will compute step 1, 2, and 3.
Step 1: Take in the mesh requirements specified by user and check if they are valid.
        The requirements include mesh domain, periodicity, BG_RATIO, FG_RATIO, and mesh segments.
        Functions used:
         * insert_mesh_segment() - adds mesh segments to the segment_list.
         * is_valid()

Step 2: call "resolve_mesh_segements()". This function will call the following functions (in ascending order):

        * call _resolve_mesh_segments_overlap_region():
        Check if there is overlapping in mesh segments inputted. If so it will always keep the segment with the
        lower resolution. Here is an illustration:
        mesh segments inputted     removed overlapping segments
        ||=======         ||       ||==              ||
        ||    ========    ||   ==> ||    ========    ||
        ||        ========||       ||            ====||
        ||  ==            ||       ||  ==            ||

        * call _resolve_mesh_segments_narrow_region():
        Remove all small mesh segments that are less than 4 points. And instead tag the small segment domain to the
        segment adjacent to it that has the smaller ds.

        * call _resolve_mesh_segments_ds():
        Make the current mesh continuous. Set a ds0 and ds1 for each segment.
        Meaning, ds0 is the beginning resolution and ds1 is the resolution at the end of the segment.
        Here is an illustration:
        mesh segments pre            mesh segments post
        ||==   ===        ||       ||==\\   //===\\    ||
        ||   ==           ||   ==> ||   \\==//   \\    ||
        ||            ====||       ||            \\====||
        ||                ||       ||                  ||

        * if mesh is periodic the call self.periodic_case():
        adjust the begin and last segments so the adjusted mesh will be periodic.
        Here is an illustration:
        mesh segments pre-periodic  mesh segments post-periodic
        ||\\                  ||       ||                    ||
        || \\      //==\\     ||   ==> ||         //==\\     ||
        || \\    //     \\  //||       ||\\     //     \\  //||
        ||  ====         ===  ||       ||  ====         ===  ||

Step 3: build legacy mesh. Here we take the adjusted_mesh segments and calculate the segments total number of points,
        domain (length), and ratio. The calculations to solve legacy mesh segments are in src/mesh_segments.
        Here we call build_legacy_mesh() which adds a layer of complexity since it solves the legacy mesh iteratively.
        Each time a mesh segment is *undershooting* the legacy mesh is recalculated.
"""
import json
import numpy
from .legacy_mesh import LegacyMesh
from .legacy_mesh_segment import LegacyMeshSegment
from .mesh_segment import MeshSegment

EPSILON = 1 / numpy.power(10, 5)


class Mesh:
    """
    Mesh object is the mesh in stages 1 and 2. Stage three is in legacy_mesh.py.
    The functions below include the most important functions to build a mesh.
    """

    def __init__(self, lower_bnd, upper_bnd, periodic=False, phi_shift=0.0):
        self.lower_bnd = numpy.float64(lower_bnd)
        self.upper_bnd = numpy.float64(upper_bnd)
        self.periodic = periodic
        self.phi_shift = numpy.float64(phi_shift)
        self.BG_RATIO = MeshSegment.DEFAULT_BG_REGION_RATIO
        # self.FG_RATIO = MeshSegment.DEFAULT_FG_REGION_RATIO
        self.segment_list = numpy.array([MeshSegment(self.lower_bnd, self.upper_bnd)])

    def __str__(self):
        return json.dumps(
            self.json_dict(), indent=2, default=lambda o: o.json_dict())

    def json_dict(self):
        return {
            'lower_bnd': self.lower_bnd,
            'upper_bnd': self.upper_bnd,
            'periodic': self.periodic,
            'phi_shift': self.phi_shift,
            'BG_RATIO': self.BG_RATIO,
            # 'FG_RATIO': self.FG_RATIO,
            'segment_list': [segment.json_dict() for segment in self.segment_list.tolist()]
        }

    def is_valid(self):
        """
        Check if inputted mesh is valid. Step 1 of building a mesh.
        Otherwise, print a Error message.
        """
        if self.lower_bnd >= self.upper_bnd:
            print("Error: lower_bnd >= upper_bnd.")
            return False

        if self.periodic and self.lower_bnd != 0.0:
            print("Error: If mesh is periodic, it requires lower_bnd=0.")
            return False

        if self.segment_list is None:
            print("Error: segment_list is empty. Input at least one mesh segment requirements.")
            return False

        for segment in self.segment_list:
            if segment.s0 < self.lower_bnd or segment.s1 > self.upper_bnd:
                if segment.s0 < self.lower_bnd:
                    print("Error: segment.s0 < lower_bnd.", segment.json_dict())
                if segment.s1 > self.upper_bnd:
                    print("Error: segment.s1 > upper_bnd.", segment.json_dict())
                return False
            elif not segment.segment_is_valid():
                print("Error: mesh segment is invalid.", segment.json_dict())
                return False
        return True

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
        if new_segment.validate_bnd(s0=new_segment.s0, s1=new_segment.s1):
            if self.periodic and (new_segment.s0 < 0 or new_segment.s1 > self.upper_bnd):
                self.make_mesh_segment_periodic(new_segment)
            else:
                new_segment, segment_valid = self.force_mesh_segment_in_mesh_domain(new_segment)
                if segment_valid:
                    index = self.get_mesh_segment_index(mesh_segment=new_segment, beg_index=beg_index)
                    self.segment_list = numpy.insert(self.segment_list, index, new_segment)
        else:
            print("segment is invalid. s0 >= s1", new_segment.json_dict())

    def force_mesh_segment_in_mesh_domain(self, segment):
        """ force the non periodic mesh segments to be in the main mesh domain. """
        segment_is_valid = True
        if segment.s1 > self.upper_bnd and segment.s0 > self.upper_bnd:
            print("segment is out of main mesh bounds. ", segment.json_dict())
            segment_is_valid = False
        elif segment.s0 < self.lower_bnd and segment.s1 < self.lower_bnd:
            print("segment is out of main mesh bounds. ", segment.json_dict())
            segment_is_valid = False
        elif segment.s1 > self.upper_bnd >= segment.s0 >= self.lower_bnd:
            print("segment s1 is out of main mesh bounds. Force s1 = upper_bnd ", segment.s1)
            segment.s1 = self.upper_bnd
        elif segment.s0 < self.lower_bnd <= segment.s1 <= self.upper_bnd:
            print("segment s0 is out of main mesh bounds. Force s0 = lower_bnd ", segment.s0)
            segment.s0 = self.lower_bnd
        return segment, segment_is_valid

    def make_mesh_segment_periodic(self, new_segment):
        """ Force periodicity on mesh segments if periodic=True,
        these cases occur when: new_segment.s0 < 0 or new_segment.s1 > 2 * numpy.pi"""
        if 0 < new_segment.s0 < self.upper_bnd < new_segment.s1:
            segment_1 = MeshSegment(s0=new_segment.s0, s1=self.upper_bnd, ds=new_segment.ds0,
                                    var_ds_ratio=new_segment.var_ds_ratio)
            segment_2 = MeshSegment(s0=0, s1=new_segment.s1 - self.upper_bnd, ds=new_segment.ds0,
                                    var_ds_ratio=new_segment.var_ds_ratio)
            index1 = self.get_mesh_segment_index(mesh_segment=segment_1)
            self.segment_list = numpy.insert(self.segment_list, index1, segment_1)
            index2 = self.get_mesh_segment_index(mesh_segment=segment_2)
            self.segment_list = numpy.insert(self.segment_list, index2, segment_2)

        elif self.upper_bnd < new_segment.s0 and self.upper_bnd < new_segment.s1:
            new_segment.s0 = new_segment.s0 - self.upper_bnd
            new_segment.s1 = new_segment.s1 - self.upper_bnd
            index = self.get_mesh_segment_index(mesh_segment=new_segment)
            self.segment_list = numpy.insert(self.segment_list, index, new_segment)

        elif new_segment.s0 < 0 and new_segment.s1 < 0:
            new_segment.s0 = new_segment.s0 + self.upper_bnd
            new_segment.s1 = new_segment.s1 + self.upper_bnd
            index = self.get_mesh_segment_index(mesh_segment=new_segment)
            self.segment_list = numpy.insert(self.segment_list, index, new_segment)

        elif new_segment.s0 < 0 and 0 < new_segment.s1 < self.upper_bnd:
            segment_1 = MeshSegment(s0=0, s1=new_segment.s1, ds=new_segment.ds0, var_ds_ratio=new_segment.var_ds_ratio)
            segment_2 = MeshSegment(s0=new_segment.s0 + self.upper_bnd, s1=self.upper_bnd, ds=new_segment.ds0,
                                    var_ds_ratio=new_segment.var_ds_ratio)
            index1 = self.get_mesh_segment_index(mesh_segment=segment_1)
            self.segment_list = numpy.insert(self.segment_list, index1, segment_1)
            index2 = self.get_mesh_segment_index(mesh_segment=segment_2)
            self.segment_list = numpy.insert(self.segment_list, index2, segment_2)

        elif new_segment.s0 <= 0 and new_segment.s1 >= self.upper_bnd:
            new_segment.s0 = 0
            new_segment.s1 = self.upper_bnd
            index = self.get_mesh_segment_index(mesh_segment=new_segment)
            self.segment_list = numpy.insert(self.segment_list, index, new_segment)

    def get_mesh_segment_index(self, mesh_segment, beg_index=0):
        """ return the index of the mesh segment. """
        for index in range(beg_index, len(self.segment_list)):
            segment = self.segment_list[index]
            if mesh_segment.s0 < segment.s0:
                return index
            elif mesh_segment.s0 == segment.s0:
                if mesh_segment.s1 > segment.s1:
                    index += 1
                return index
        return len(self.segment_list)

    def remove_mesh_segment(self, index):
        """
        Removes and returns a mesh segment at the specified position in the
        list of mesh segments.
        """
        segment = self.segment_list[index]
        self.segment_list = numpy.delete(self.segment_list, index)

        return segment

    def resolve_mesh_segments(self):
        """
        Step 2 of building a mesh. Returns the adjusted mesh.
        """
        self._resolve_mesh_segments_overlap_region()  # deletes overlapping segments
        self._resolve_mesh_segments_narrow_region()  # deletes segments with 4 or less points.
        self._resolve_mesh_segments_ds()  # make adjusted mesh continuous. Every segment has a ds0 and ds1.
        if self.periodic:  # solve for periodic case by adjusting the begin and end segments.
            self._periodic_case()

        return self

    def _resolve_mesh_segments_overlap_region(self):
        """
        Resolves mesh segments with overlapping regions by modifying, removing
        and/or adding segments so that all of the mesh segments combined cover
        the entire domain without any overlapping regions.

        In the illustrations for each case and their possible results, 'a', 'b'
        and 'c' represent the regions of subsequent segments in the list. Note
        that these conditions and results remain true in the case of segment C
        starting and/or ending at the same point as segment B.
        """
        index = 0
        while index < len(self.segment_list) - 1:
            segment_a = self.segment_list[index]
            segment_b = self.segment_list[index + 1]

            if segment_a.s0 == segment_b.s0:
                if segment_a.s1 < segment_b.s1:
                    """
                    aaaa          aaaa
                    bbbbbb    =>     bbb    OR  bbbbbb
                      cccccc        cccccc        cccccc
                    """
                    if segment_a.ds0 <= segment_b.ds0:
                        self.remove_mesh_segment(index + 1)
                        segment_b.s0 = segment_a.s1
                        self.insert_mesh_segment(segment_b, index)
                    else:
                        self.remove_mesh_segment(index)
                elif segment_a.s1 == segment_b.s1:
                    """
                    aaaaaa        aaaaaa
                    bbbbbb    =>            OR  bbbbbb
                      cccccc        cccccc        cccccc
                    """
                    if segment_a.ds0 <= segment_b.ds0:
                        self.remove_mesh_segment(index + 1)
                    else:
                        self.remove_mesh_segment(index)
                else:
                    """
                    aaaaaa        aaaaaa           aaa
                    bbbb      =>            OR  bbbb
                      cccccc        cccccc        cccccc
                    """
                    if segment_a.ds0 <= segment_b.ds0:
                        self.remove_mesh_segment(index + 1)
                    else:
                        self.remove_mesh_segment(index)
                        segment_a.s0 = segment_b.s1
                        self.insert_mesh_segment(segment_a, index)
            else:
                if segment_a.s1 <= segment_b.s0:
                    """
                    aaaa           aaaa
                       bbbb    =>     bbbb
                       cccccc         cccccc
                    """
                    index += 1
                elif segment_a.s1 < segment_b.s1:
                    """
                    aaaaaa          aaaaaa          aaa
                      bbbbbb    =>       bbb    OR    bbbbbb
                        cccccc          cccccc          cccccc
                    """
                    if segment_a.ds0 <= segment_b.ds0:
                        self.remove_mesh_segment(index + 1)
                        segment_b.s0 = segment_a.s1
                        self.insert_mesh_segment(segment_b, index)
                    else:
                        segment_a.s1 = segment_b.s0
                        index += 1
                elif segment_a.s1 == segment_b.s1:
                    """
                    aaaaaa          aaaaaa          aaa
                      bbbb      =>              OR    bbbb
                        cccccc          cccccc          cccccc
                    """
                    if segment_a.ds0 <= segment_b.ds0:
                        self.remove_mesh_segment(index + 1)
                    else:
                        segment_a.s1 = segment_b.s0
                        index += 1
                else:
                    """
                    aaaaaaa          aaaaaaa          aaa aaa
                      bbb        =>               OR    bbb
                        ccccccc          ccccccc          ccccccc
                    """
                    if segment_a.ds0 <= segment_b.ds0:
                        self.remove_mesh_segment(index + 1)
                    else:
                        new_segment = MeshSegment(
                            segment_b.s1, segment_a.s1, segment_a.ds0,
                            segment_a.var_ds_ratio)
                        segment_a.s1 = segment_b.s0
                        self.insert_mesh_segment(new_segment, index + 1)
                        index += 1

    def _resolve_mesh_segments_narrow_region(self):
        """
        Removes mesh segments whose region is too narrow (4 or less points) and covers them with
        the neighboring mesh segments.
        """
        n_min = 4
        index = 0

        while index < len(self.segment_list):
            segment = self.segment_list[index]
            prev_segment = None  # default
            next_segment = None  # default
            n_test = numpy.inf  # default

            if index > 0:
                prev_segment = self.segment_list[index - 1]
            if index < len(self.segment_list) - 1:
                next_segment = self.segment_list[index + 1]

            if segment.ds0 == numpy.inf:
                if index == len(self.segment_list) - 1 and prev_segment:
                    if prev_segment.ds1 != numpy.inf:
                        n_test = numpy.floor(numpy.abs(segment.s1 - segment.s0) / prev_segment.ds1)
                elif index == 0 and next_segment:
                    if next_segment.ds0 != numpy.inf:
                        n_test = numpy.floor(numpy.abs(segment.s1 - segment.s0) / next_segment.ds0)

            elif segment.ds0 != numpy.inf:
                n_test = numpy.floor(numpy.abs(segment.s1 - segment.s0) / segment.ds0)

            # if this segment is too small:
            if n_test <= n_min:
                if index == 0:
                    next_segment.s0 = segment.s0
                elif index == (len(self.segment_list) - 1):
                    prev_segment.s1 = segment.s1
                else:
                    if prev_segment.ds0 >= next_segment.ds0:
                        if prev_segment.ds0 == numpy.inf:
                            next_segment.s0 = segment.s0
                        else:
                            prev_segment.s1 = segment.s1
                    else:
                        if next_segment.ds0 == numpy.inf:
                            prev_segment.s1 = segment.s1
                        else:
                            next_segment.s0 = segment.s0

                self.remove_mesh_segment(index)
                index += -1
            index += 1

    def _resolve_mesh_segments_ds(self):
        """
        Resolves the proper ds values at both ends of each mesh segment.

        In the illustrations for each case, '=' and '|' represent subsequent
        segments regions (prev, curr, next) and their boundaries respectively.
        The original ds values with respect to each other are shown by which
        line they are drawn (y-axis). The starting and ending ds values of a
        segment (curr) are determined by comparing its original ds value with
        its neighbors' (prev, next) original ds value respectively. Lower ds
        value always has higher priority.
        """
        # Stores the original constant ds values of each segment before they
        # are overwritten with the proper values.
        ds_list = []
        for segment in self.segment_list:
            ds_list.append(segment.ds0)

        index = 0
        end_index = len(self.segment_list) - 1
        while index <= end_index:
            segment = self.segment_list[index]

            curr_ds = ds_list[index]
            prev_ds = ds_list[index - 1] if index > 0 else curr_ds
            next_ds = ds_list[index + 1] if index < end_index else curr_ds

            if curr_ds == MeshSegment.BG_REGION_DS:
                if index == 0:
                    segment.set_ds(curr_ds, next_ds)
                elif index == end_index:
                    segment.set_ds(prev_ds, curr_ds)
                else:
                    self.resolve_gap_mid_mesh(segment, index, ds_begin=prev_ds, ds_end=next_ds)
                    if end_index == len(self.segment_list) - 2:  # if gen_resolve_gap inserted a segment
                        end_index = len(self.segment_list) - 1
                        ds_list.insert(index + 1, prev_ds)
                        ds_list[index + 1] = self.segment_list[index + 1].ds0

                        index += 1

                    else:
                        ds_list[index] = self.segment_list[index + 1].ds0

            elif curr_ds <= prev_ds:
                if curr_ds <= next_ds:
                    """
                    |==|  |==|      |==|  |  |      |  |  |==|      |  |  |  |
                    |  |==|  |  OR  |  |==|==|  OR  |==|==|  |  OR  |==|==|==|
                    |  |  |  |      |  |  |  |      |  |  |  |      |  |  |  |
                    """
                    segment.set_ds(curr_ds)
                else:
                    """
                    |==|  |  |      |  |  |  |
                    |  |==|  |  OR  |==|==|  |
                    |  |  |==|      |  |  |==|
                    """
                    segment.set_ds(curr_ds, next_ds)
            else:
                if curr_ds <= next_ds:
                    """
                    |  |  |==|      |  |  |  |
                    |  |==|  |  OR  |  |==|==|
                    |==|  |  |      |==|  |  |
                    """
                    segment.set_ds(prev_ds, curr_ds)
                else:
                    """
                    |  |  |  |
                    |  |==|  |
                    |==|  |==|
                    """
                    dsh, sh = self._check_resolve_gap_mid_mesh(index, prev_ds, next_ds)
                    if dsh - curr_ds <= EPSILON:
                        self.resolve_gap_mid_mesh(segment, index, ds_begin=prev_ds, ds_end=next_ds)
                        if end_index == len(self.segment_list) - 2:  # if gen_resolve_gap inserted a segment
                            end_index = len(self.segment_list) - 1
                            ds_list.insert(index + 1, prev_ds)
                            ds_list[index + 1] = self.segment_list[index + 1].ds0
                            index += 1
                        else:
                            ds_list[index] = self.segment_list[index + 1].ds0
                    else:
                        if segment.s0 < sh < segment.s1:
                            new_segment = MeshSegment(
                                sh, segment.s1, curr_ds, segment.var_ds_ratio)
                            new_segment.set_ds(curr_ds, next_ds)
                            segment.s1 = new_segment.s0
                            segment.set_ds(prev_ds, curr_ds)
                            index += 1
                            self.segment_list = numpy.insert(
                                self.segment_list, index, new_segment)
                            ds_list.insert(index, curr_ds)
                            end_index = len(self.segment_list) - 1

            index += 1

    def _resolve_hat_mesh_segment(self, index):
        """ This function resolves an adjusted mesh segment (step #2) where we have this pattern:
                    |  |  |  |      |  |   == |  |
                    |  |==|  | ---> |  |  //\\|  |
                    |==|  |==|      |==|//  \\|==|

        """

        segment = self.segment_list[index]

        curr_ds = segment.ds0
        prev_ds = self.segment_list[index - 1].ds1
        next_ds = self.segment_list[index + 1].ds0

        dsh, sh = self._check_resolve_gap_mid_mesh(index, prev_ds, next_ds)

        if dsh - curr_ds <= numpy.sqrt(EPSILON):
            self.resolve_gap_mid_mesh(segment, index, ds_begin=prev_ds, ds_end=next_ds)

        else:
            if segment.s0 < sh < segment.s1:
                new_segment = MeshSegment(sh, segment.s1, curr_ds, segment.var_ds_ratio)
                new_segment.set_ds(curr_ds, next_ds)
                segment.s1 = new_segment.s0
                segment.set_ds(prev_ds, curr_ds)
                index += 1
                self.segment_list = numpy.insert(self.segment_list, index, new_segment)

    def _get_ds_begin_and_ds_end(self, num_beg, num_end):
        """ return ds0 of segment begin and ds1 of segment end. This is called to check if periodic condition
        is satisfied. """
        segment_begin = self.segment_list[0]
        segment_end = self.segment_list[-1]

        ds_begin = segment_begin.ds0
        ds_end = segment_end.ds1

        if ds_begin == numpy.inf:
            # this is a fixed length segment so compute ds0 using the legacy function.
            ds_begin = segment_begin.get_ds0_using_num_points(num_beg)
        if ds_end == numpy.inf:
            # this is a fixed length segment so compute ds1 using the legacy function.
            ds_end = segment_end.get_ds1_using_num_points(num_end)

        return ds_begin, ds_end

    def build_legacy_mesh(self, max_iterations=500):
        """
        Builds and returns the legacy mesh using constraints of this mesh.
        """
        legacy_mesh = LegacyMesh(self.lower_bnd, self.upper_bnd, self.periodic, self.phi_shift)

        jj = 0  # the cumulative number of iterations.
        kk = 0  # number of iterations stuck on fixing the periodicity.
        ii = 0  # current mesh segment index.

        while ii < len(self.segment_list) and jj < max_iterations:

            segment = self.segment_list[ii]
            legacy_mesh_segment_list = segment.get_legacy_mesh_segments(self.lower_bnd, self.upper_bnd)

            if legacy_mesh_segment_list[0].s0 == segment.s0 and \
                    legacy_mesh_segment_list[-1].s1 == segment.s1:
                for legacy_segment in legacy_mesh_segment_list:
                    legacy_mesh.insert_mesh_segment(legacy_segment)

                # Update the next segment ds0 if needed OR the previous segment ds1. Ensures a continuous mesh.
                if len(legacy_mesh_segment_list) == 1:
                    if self.update_next_segment(segment, ii, legacy_segment):
                        ii = - 1
                        legacy_mesh.segment_list = numpy.array([], dtype=LegacyMeshSegment)

                if legacy_segment.s1 == self.upper_bnd and self.periodic:
                    # check if periodicity requirement is satisfied, if not adjust either begin or end segment to be
                    # fixed ds. Then, reiterate and solve for legacy mesh.
                    # Note: if kk > 2, this is a sign that we get a round off error since legacy mesh computes the
                    # number of segment points using np.ceil, this can cause the begin and end ds to be slightly off.
                    # In that case, we return the current legacy mesh and exit the while loop.
                    ds_begin, ds_end = self._get_ds_begin_and_ds_end(num_beg=legacy_mesh.segment_list[0].num_points,
                                                                     num_end=legacy_mesh.segment_list[-1].num_points)
                    if abs(ds_begin - ds_end) > EPSILON:
                        if ds_begin > ds_end:
                            self.segment_list[0].ds0 = ds_end
                        else:
                            self.segment_list[-1].ds1 = ds_begin
                        if kk < 2:
                            # this loop is caused by using np.ceil to find the legacy segment num_points.
                            ii = -1
                            legacy_mesh.segment_list = numpy.array([], dtype=LegacyMeshSegment)
                    kk += 1

            else:
                if segment == self.segment_list[-1] and \
                        segment.has_increasing_ds():
                    raise Exception("Fixed DS segment is too long for the " +
                                    "last segment. Aborting.")
                elif segment == self.segment_list[0] and \
                        segment.has_decreasing_ds():
                    raise Exception("Fixed DS segment is too long for the " +
                                    "first segment. Aborting.")

                passes_mult_segment = False
                if segment.has_increasing_ds() and segment.s1 != self.upper_bnd:

                    # Next segment
                    adjacent_segment = self.segment_list[ii + 1]

                    if legacy_mesh_segment_list[-1].s1 >= adjacent_segment.s1:
                        passes_mult_segment = True

                    if not passes_mult_segment and \
                            (not adjacent_segment.is_fixed_length() or not adjacent_segment.has_increasing_ds()):
                        # CASE: PASSES ONE SEGMENT.
                        # CASE: NOT FIXED LENGTH, NOT INCREASING DS.
                        # RECALCULATE MID HAT POINT.
                        if segment.is_fixed_ds() and adjacent_segment.is_fixed_ds() \
                                and adjacent_segment.has_decreasing_ds() and adjacent_segment.s1 != self.upper_bnd:
                            # remove one of the mesh segments.
                            self.segment_list[ii + 1].s0 = segment.s0
                            self.segment_list[ii + 1].ds1 = adjacent_segment.ds0
                            self.remove_mesh_segment(ii)
                            # recalculate the peak between the two segments.
                            self._resolve_hat_mesh_segment(index=ii + 1)

                        else:
                            segment.s1 = legacy_mesh_segment_list[-1].s1
                            adjacent_segment.s0 = legacy_mesh_segment_list[-1].s1

                    else:
                        # CASE: SEGMENT CROSSES MULTIPLE REGIONS
                        # CASE: FIXED LENGTH AND HAS INCREASING DS
                        n = segment.get_num_points_fixed_length_mesh()
                        ds = segment.get_ds1_using_num_points(n)
                        segment.ds1 = segment.BG_REGION_DS
                        adjacent_segment.ds0 = ds

                        if adjacent_segment.s1 != self.upper_bnd and adjacent_segment.is_fixed_length() \
                                and adjacent_segment.has_increasing_ds():
                            if self.segment_list[ii + 2].is_fixed_length() and \
                                    self.segment_list[ii + 2].has_decreasing_ds():
                                if self.segment_list[ii + 2].s1 != self.upper_bnd:
                                    ''''
                                        Undershoot case mid-mesh. Calculate new intersection point. 
                                        Calling resolve gap again. 
                                        ds0      ds1     ds0       ds1
                                        | |  //\\ | |    | |   //\\ | | 
                                        |=| //  \\|=| => | | //   \\|=| 
                                        | |       | |    |=|//      | |

                                    '''
                                    # print("Recalculate resolve gap.")
                                    adjacent_segment.s1 = self.segment_list[ii + 2].s1
                                    # adjacent_segment.var_ds_ratio = segment.DEFAULT_BG_REGION_RATIO
                                    adjacent_segment.ds1 = self.segment_list[ii + 2].ds1
                                    self.remove_mesh_segment(ii + 2)
                                    self.resolve_gap_mid_mesh(adjacent_segment, ii + 1, ds_begin=ds,
                                                              ds_end=adjacent_segment.ds1)

                        if adjacent_segment.s1 == self.upper_bnd and self.periodic and \
                                not adjacent_segment.has_decreasing_ds() and \
                                not self.segment_list[0].has_increasing_ds():
                            '''
                                Undershoot case end-mesh. Calculate new intersection point of resolve_gap periodic case.
                                There will now be a new phi_shift.  
                                ds0      ds1     ds0       ds1
                                | |  //\\ | |    | |   \\  | | 
                                |=| //  \\|=| => |=| // \\ | | 
                                | |       | |    |=|     \\|=|

                                '''
                            # print("Periodic case is recalculated. Last segment adjacent is undershooting.")
                            self.revert_shift()
                            self.segment_list[0].s0 = self.lower_bnd
                            self.segment_list[-1].s1 = self.upper_bnd
                            self._periodic_case()
                            legacy_mesh.phi_shift = self.phi_shift

                if segment.has_decreasing_ds() and segment.s0 != self.lower_bnd:
                    # Previous segment
                    adjacent_segment = self.segment_list[ii - 1]
                    if legacy_mesh_segment_list[-1].s0 <= adjacent_segment.s0:
                        passes_mult_segment = True

                    if not passes_mult_segment and \
                            (not adjacent_segment.is_fixed_length() or not adjacent_segment.has_decreasing_ds()):
                        # CASE: PASSES ONE SEGMENT
                        # CASE: NOT FIXED LENGTH, NOT DECREASING DS
                        # RECALCULATE MID HAT POINT.
                        if segment.is_fixed_ds() and adjacent_segment.is_fixed_ds() \
                                and adjacent_segment.has_increasing_ds() and adjacent_segment.s0 != self.lower_bnd:
                            # remove one of the mesh segments.
                            self.segment_list[ii - 1].s1 = segment.s1
                            self.segment_list[ii - 1].ds0 = adjacent_segment.ds1
                            self.remove_mesh_segment(ii)
                            # recalculate the peak between the two segments.
                            self._resolve_hat_mesh_segment(index=ii - 1)

                        else:
                            # adjust the length of the segment.
                            segment.s0 = legacy_mesh_segment_list[-1].s0
                            adjacent_segment.s1 = legacy_mesh_segment_list[-1].s0
                    else:
                        # CASE: SEGMENT CROSSES MULTIPLE REGIONS
                        # CASE: FIXED LENGTH AND HAS DECREASING DS
                        n = segment.get_num_points_fixed_length_mesh()
                        ds = segment.get_ds0_using_num_points(n)
                        segment.ds0 = segment.BG_REGION_DS
                        adjacent_segment.ds1 = ds

                        if adjacent_segment.s0 != self.lower_bnd and adjacent_segment.is_fixed_length() \
                                and adjacent_segment.has_decreasing_ds():
                            if self.segment_list[ii - 2].is_fixed_length() and \
                                    self.segment_list[ii - 2].has_increasing_ds():
                                '''
                                    Undershoot case mid-mesh. Calculate new intersection point. 
                                    Calling resolve gap again. 
                                    ds0      ds1     ds0       ds1
                                    | |  //\\ | |    | |   \\  | | 
                                    |=| //  \\|=| => |=| // \\ | | 
                                    | |       | |    |=|     \\|=|
    
                                    '''
                                # print("Recalculate resolve gap. ")
                                self.segment_list[ii - 2].s1 = adjacent_segment.s1
                                # self.segment_list[i - 2].var_ds_ratio = segment.DEFAULT_BG_REGION_RATIO
                                self.segment_list[ii - 2].ds1 = adjacent_segment.ds1
                                self.remove_mesh_segment(ii - 1)
                                self.resolve_gap_mid_mesh(self.segment_list[ii - 2], ii - 2,
                                                          ds_begin=self.segment_list[ii - 2].ds0, ds_end=ds)

                        if adjacent_segment.s0 == self.lower_bnd and self.periodic and \
                                not adjacent_segment.has_increasing_ds() and \
                                not self.segment_list[-1].has_decreasing_ds():
                            '''
                                Undershoot case begin segment. Calculate new intersection point of periodic case. 
                                There is a new phi_shift now. 
                                Calling resolve gap periodic case again. 
                                ds0      ds1     ds0       ds1
                                | |  //\\ | |    | |   \\  | | 
                                |=| //  \\|=| => |=| // \\ | | 
                                | |       | |    |=|     \\|=|

                            '''
                            # print("Periodic case is recalculated. First segment adjacent is undershooting.")
                            self.revert_shift()
                            self.segment_list[0].s0 = self.lower_bnd
                            self.segment_list[-1].s1 = self.upper_bnd
                            self._periodic_case()
                            legacy_mesh.phi_shift = self.phi_shift

                ii = -1

                legacy_mesh.segment_list = numpy.array([], dtype=LegacyMeshSegment)

            ii += 1
            jj += 1

        if jj >= max_iterations:
            raise Exception("Error: Legacy mesh failed to find a result. Try adjusting your mesh requirements. ")

        return legacy_mesh

    def update_next_segment(self, segment, i, legacy_segment):
        """
        Enforce continuity.
        If we have multiple undershoots in a row it is important to update the next segments ds0/ds1.
        Now legacy mesh will be continuous.
        """
        need_to_recalculate = False
        if segment.ds1 == numpy.inf:
            segment_ds1 = segment.ds0 * legacy_segment.ratio
            if i != len(self.segment_list) - 1:  # if there is an adjacent segment from the right.
                adjacent_segment_ds0 = self.segment_list[i + 1].ds0
                if adjacent_segment_ds0 != segment_ds1 and adjacent_segment_ds0 != numpy.inf:
                    self.segment_list[i + 1].ds0 = segment_ds1

        if segment.ds0 == numpy.inf:
            segment_ds0 = segment.ds1 / legacy_segment.ratio
            if i > 0:  # if there is an adjacent segment from the left.
                adjacent_segment_ds1 = self.segment_list[i - 1].ds1
                if round(adjacent_segment_ds1, 3) != round(segment_ds0, 3) and adjacent_segment_ds1 != numpy.inf:
                    self.segment_list[i - 1].ds1 = segment_ds0
                    need_to_recalculate = True
        return need_to_recalculate

    @staticmethod
    def get_vectors(ds_begin, ds_end, segment_begin_s1, segment_end_s0, ratio):
        """
        get the vectors to calculate the intersection of two fixed length segments.
        ds0 * R^n0 = ds1 * R^n1
        """
        ln_ratio = numpy.log(ratio)

        num_points = 1000.0
        s = numpy.arange(num_points) / (num_points - 1) * (- segment_begin_s1 + segment_end_s0) + segment_begin_s1
        n0 = numpy.log(ln_ratio * (segment_end_s0 - s) / ds_end + 1) / ln_ratio
        n1 = numpy.log(ln_ratio * (s - segment_begin_s1) / ds_begin + 1) / ln_ratio
        dsn0 = ds_end * numpy.power(ratio, n0)
        dsn1 = ds_begin * numpy.power(ratio, n1)
        return s, n0, n1, dsn0, dsn1

    @staticmethod
    def get_sh(s, dsn1, dsn0):
        """sh is the point in the s interval where the two segments intersect."""
        diff = dsn1 - dsn0
        if diff[0] > diff[len(diff) - 1]:
            diff_reverse = diff[::-1]
            s_reverse = s[::-1]
            sh = numpy.interp(0.0, diff_reverse, s_reverse)

        else:
            sh = numpy.interp(0.0, diff, s)
        return sh

    @staticmethod
    def get_n_test0(ratio0, segment_end_s0, sh, ds_end):
        """ number of points in mesh segment. Used for resolve_gap and periodic_case. """
        ln_ratio_0 = numpy.log(ratio0)
        n_test0 = numpy.ceil(numpy.log(ln_ratio_0 * (segment_end_s0 - sh) / ds_end + 1) / ln_ratio_0)
        return n_test0

    @staticmethod
    def get_n_test1(ratio1, segment_begin_s1, sh, ds_begin):
        """ number of points in mesh segment. Used for resolve_gap and periodic_case. """
        ln_ratio_1 = numpy.log(ratio1)
        n_test1 = numpy.ceil(numpy.log(ln_ratio_1 * (sh - segment_begin_s1) / ds_begin + 1) / ln_ratio_1)
        return n_test1

    def calculate_intersection(self, ds_begin, ds_end, segment_begin_s1, segment_end_s0, ratio):
        """ Find the intersection point for resolve gap. ds0 * R^n0 = ds1 * R^n1 """
        # Now find the position of the solution to the equation ds0 * R^n0 = ds1 * R^n1
        s, n0, n1, dsn0, dsn1 = self.get_vectors(ds_begin, ds_end, segment_begin_s1, segment_end_s0, ratio)

        # Find the point of the s interval where the two segments intersect.
        sh = self.get_sh(s, dsn1, dsn0)

        return s, n0, n1, dsn0, dsn1, sh

    def _check_resolve_gap_mid_mesh(self, index, ds_begin, ds_end):
        """ This is identical to the function below "resolve_gap_mid_mesh" yet it does not perform any actions.
        This is only for diagnostics. """

        segment_begin = self.segment_list[index - 1]
        segment_end = self.segment_list[index + 1]

        ratio = self.segment_list[index].var_ds_ratio
        s, n0, n1, dsn0, dsn1, sh = self.calculate_intersection(ds_begin=ds_begin, ds_end=ds_end,
                                                                segment_begin_s1=segment_begin.s1,
                                                                segment_end_s0=segment_end.s0,
                                                                ratio=ratio)

        if segment_begin.s1 < sh < segment_end.s0:
            '''
            CASE #1: the segment_begin.ds is fairly similar to segment.end_ds.
                        |  |    |  |      |  |     |  |
                        |  |    |  |  ==> |  | //\\|  |
                        |==|    |==|      |==|// \\|==|
            '''
            nh0 = numpy.ceil(numpy.interp(sh, s, n0))
            nh1 = numpy.ceil(numpy.interp(sh, s, n1))
            dsh0 = numpy.interp(sh, s, dsn0)
            dsh1 = numpy.interp(sh, s, dsn1)

            ratio0 = numpy.power((dsh0 / ds_end), (1.0 / nh0))
            ratio1 = numpy.power((dsh1 / ds_begin), (1.0 / nh1))

            # Now make sure it works
            n_test0 = self.get_n_test0(ratio0, segment_end.s0, sh, ds_end)
            n_test1 = self.get_n_test1(ratio1, segment_begin.s1, sh, ds_begin)

            if n_test0 == nh0 and n_test1 == nh1:
                ''' divide the gap segment into two segments. One segment that raises to the peak and
                another that connects the peak to segment_end.ds0'''
                return dsh0, sh
            else:
                print("Error: n_test0 and n_test1 midmesh.")

        if sh == segment_end.s0:  # end ds is much bigger than begin ds
            '''
            CASE #2: the segment_begin.ds is much smaller than segment.end_ds.
                        |  |    |==|      |  |     |==|
                        |  |    |  |  ==> |  |  // |  |
                        |==|    |  |      |==|//   |  |
            '''
            nh1 = numpy.ceil(numpy.interp(sh, s, n1))
            dsh1 = numpy.interp(sh, s, dsn1)
            ratio1 = numpy.power((dsh1 / ds_begin), (1.0 / nh1))
            # check it works
            n_test1 = self.get_n_test1(ratio1, segment_begin.s1, sh, ds_begin)
            if n_test1 == nh1:
                return dsh1, sh
            else:
                print("ERROR: n_test1 mid-mesh.")

        if sh == segment_begin.s1:
            '''
            CASE #3: the segment_begin.ds is much bigger than segment.end_ds.                  
                        |==|    |  |      |==|     |  |
                        |  |    |  |  ==> |  | \\  |  |
                        |  |    |==|      |  |   \\|==|
            '''
            nh0 = numpy.ceil(numpy.interp(sh, s, n0))
            dsh0 = numpy.interp(sh, s, dsn0)
            ratio0 = numpy.power((dsh0 / ds_end), (1.0 / nh0))
            # check it works
            n_test0 = self.get_n_test0(ratio0, segment_end.s0, sh, ds_end)
            if n_test0 == nh0:
                return dsh0, sh
            else:
                print("ERROR: n_test0 mid-mesh.")

    def resolve_gap_mid_mesh(self, segment, index, ds_begin, ds_end):
        """
        Resolves the gap between two segments "segment_begin" and "segment_end" where the segment between the two is
        called "segment_gap" which does not have a specific ds requirement.
        Hence, this function will divide "segment_gap" into two smaller segments
        such that in this gap it will go up and then down as coarsely as possible (case #1).
        If a intersection point is not possible (case #2 and case #3) it will connect begin and
        end segment such that the resulting mesh is continuous.
                    |  |    |  |      |  |     |  |
                    |  |    |  |  ==> |  | //\\|  |
                    |==|    |==|      |==|// \\|==|
        """

        segment_begin = self.segment_list[index - 1]
        segment_end = self.segment_list[index + 1]

        ratio = self.segment_list[index].var_ds_ratio
        s, n0, n1, dsn0, dsn1, sh = self.calculate_intersection(ds_begin=ds_begin, ds_end=ds_end,
                                                                segment_begin_s1=segment_begin.s1,
                                                                segment_end_s0=segment_end.s0,
                                                                ratio=ratio)

        if segment_begin.s1 < sh < segment_end.s0:
            '''
            CASE #1: the segment_begin.ds is fairly similar to segment.end_ds.
                        |  |    |  |      |  |     |  |
                        |  |    |  |  ==> |  | //\\|  |
                        |==|    |==|      |==|// \\|==|
            '''
            nh0 = numpy.ceil(numpy.interp(sh, s, n0))
            nh1 = numpy.ceil(numpy.interp(sh, s, n1))
            dsh0 = numpy.interp(sh, s, dsn0)
            dsh1 = numpy.interp(sh, s, dsn1)

            ratio0 = numpy.power((dsh0 / ds_end), (1.0 / nh0))
            ratio1 = numpy.power((dsh1 / ds_begin), (1.0 / nh1))

            # Now make sure it works
            n_test0 = self.get_n_test0(ratio0, segment_end.s0, sh, ds_end)
            n_test1 = self.get_n_test1(ratio1, segment_begin.s1, sh, ds_begin)

            if n_test0 == nh0 and n_test1 == nh1:
                ''' divide the gap segment into two segments. One segment that raises to the peak and
                another that connects the peak to segment_end.ds0'''
                self.segment_list[index].s1 = sh
                self.segment_list[index].ds0 = ds_begin
                self.segment_list[index].ds1 = segment.BG_REGION_DS
                gap_segment_2 = MeshSegment(sh, segment_end.s0)
                gap_segment_2.set_ds(segment.BG_REGION_DS, ds_end)
                self.segment_list = numpy.insert(self.segment_list, index + 1, gap_segment_2)
                self.segment_list[index].var_ds_ratio = ratio1
                self.segment_list[index + 1].var_ds_ratio = ratio0
            else:
                print("Error: n_test0 and n_test1 midmesh.")

        if sh == segment_end.s0:  # end ds is much bigger than begin ds
            '''
            CASE #2: the segment_begin.ds is much smaller than segment.end_ds.
                        |  |    |==|      |  |     |==|
                        |  |    |  |  ==> |  |  // |  |
                        |==|    |  |      |==|//   |  |
            '''
            nh1 = numpy.ceil(numpy.interp(sh, s, n1))
            dsh1 = numpy.interp(sh, s, dsn1)
            ratio1 = numpy.power((dsh1 / ds_begin), (1.0 / nh1))
            # check it works
            n_test1 = self.get_n_test1(ratio1, segment_begin.s1, sh, ds_begin)
            if n_test1 == nh1:
                self.segment_list[index].set_ds(ds_begin, segment.BG_REGION_DS)
                self.segment_list[index].var_ds_ratio = ratio1
                segment_end.set_ds(dsh1, ds_end)
            else:
                print("ERROR: n_test1 mid-mesh.")

        if sh == segment_begin.s1:
            '''
            CASE #3: the segment_begin.ds is much bigger than segment.end_ds.                  
                        |==|    |  |      |==|     |  |
                        |  |    |  |  ==> |  | \\  |  |
                        |  |    |==|      |  |   \\|==|
            '''
            nh0 = numpy.ceil(numpy.interp(sh, s, n0))
            dsh0 = numpy.interp(sh, s, dsn0)
            ratio0 = numpy.power((dsh0 / ds_end), (1.0 / nh0))
            # check it works
            n_test0 = self.get_n_test0(ratio0, segment_end.s0, sh, ds_end)
            if n_test0 == nh0:
                self.segment_list[index].set_ds(segment.BG_REGION_DS, ds_end)
                self.segment_list[index].var_ds_ratio = ratio0
                segment_begin.set_ds(ds_begin, dsh0)
            else:
                print("ERROR: n_test0 mid-mesh.")

    def solve_periodic_case_both_fixed_length(self, segment_begin, segment_end, ratio):
        """ Solve the periodic case for when both begin and end segments are fixed length. Here we use the
        same logic as resolve gap mid mesh.
        Hence, this function will tag segment begin to the end of the mesh. Now the mesh is shifted.
        "segment_gap" is the domain of segment end and segment begin, such that in this gap it will go up and
        then down as coarsely as possible (case #1).
        If a intersection point is not possible (case #2 and case #3) it will connect begin and
        end segment such that the resulting mesh is continuous.
        After finding sh and dsh we will adjust the position of segment begin and segment end which will result in a
        phi_shift. """
        s, n1, n0, dsn1, dsn0, sh = self.calculate_intersection(ds_begin=segment_end.ds0, ds_end=segment_begin.ds1,
                                                                segment_begin_s1=segment_end.s0,
                                                                segment_end_s0=2 * numpy.pi + segment_begin.s1,
                                                                ratio=ratio)

        if segment_end.s0 < sh < 2 * numpy.pi + segment_begin.s1:
            '''
            CASE #1: the segment_begin.ds1 is fairly similar to segment_end.ds0.
                        |  |    |  |      |  |     |  |
                        |  |    |  |  ==> |  | //\\|  |
                        |==|    |==|      |==|// \\|==|
            '''
            # Now discretize it by choosing the n0 and n1s and then slightly modifying
            # the ratios. This way you can guarantee that the mesh solution fits exactly
            # in this space.
            nh0 = numpy.ceil(numpy.interp(sh, s, n0))
            nh1 = numpy.ceil(numpy.interp(sh, s, n1))
            dsh = numpy.interp(sh, s, dsn1)

            ratio0 = numpy.power((dsh / segment_end.ds0), (1.0 / nh0))
            ratio1 = numpy.power((dsh / segment_begin.ds1), (1.0 / nh1))

            # Now make sure it works
            n_test0 = self.get_n_test0(ratio0, -segment_end.s0, -sh, segment_end.ds0)
            n_test1 = self.get_n_test1(ratio1, -(segment_begin.s1 + 2 * numpy.pi), -sh, segment_begin.ds1)

            # Fill in the first segment
            if n_test0 == nh0 and n_test1 == nh1:
                segment_end.s1 = sh
                segment_end.ds1 = segment_end.BG_REGION_DS  # will later be dsh
                segment_end.var_ds_ratio = ratio0
                segment_begin.s0 = (sh - 2 * numpy.pi)
                segment_begin.ds0 = segment_begin.BG_REGION_DS  # will later be dsh
                segment_begin.var_ds_ratio = ratio1
            else:
                print("Error: nh1 and nh0")

        if sh == 2 * numpy.pi + segment_begin.s1:  # begin ds is much bigger than end ds
            '''
            CASE #2: the segment_begin.ds1 is much bigger than segment_end.ds0.
                        |  |    |==|      |  |     |==|
                        |  |    |  |  ==> |  |  // |  |
                        |==|    |  |      |==|//   |  |
            '''
            nh0 = numpy.ceil(numpy.interp(sh, s, n0))
            dsh = numpy.interp(sh, s, dsn0)
            ratio0 = numpy.power((dsh / segment_end.ds0), (1.0 / nh0))
            n_test0 = self.get_n_test0(ratio0, -segment_end.s0, -sh, segment_end.ds0)
            if n_test0 == nh0:
                segment_end.ds1 = segment_end.BG_REGION_DS
                segment_end.s1 = 2 * numpy.pi + segment_begin.s1
                segment_end.var_ds_ratio = ratio0
                self.segment_list[1].ds0 = dsh
                self.remove_mesh_segment(0)
            else:
                print("Error: ntest0 != nh0 in periodic case. ")

        if sh == segment_end.s0:
            '''
            CASE #3: the segment_begin.ds1 is much smaller than segment_end.ds0.                  
                        |==|    |  |      |==|     |  |
                        |  |    |  |  ==> |  | \\  |  |
                        |  |    |==|      |  |   \\|==|
            '''
            nh1 = numpy.ceil(numpy.interp(sh, s, n1))
            dsh = numpy.interp(sh, s, dsn1)
            ratio1 = numpy.power((dsh / segment_begin.ds1), (1.0 / nh1))
            n_test1 = self.get_n_test1(ratio1, -(segment_begin.s1 + 2 * numpy.pi), -sh, segment_begin.ds1)
            if n_test1 == nh1:
                segment_begin.ds0 = segment_begin.BG_REGION_DS
                segment_begin.s0 = segment_end.s0 - 2 * numpy.pi
                segment_begin.var_ds_ratio = 1 / ratio1
                self.remove_mesh_segment(-1)
                self.segment_list[-1].ds1 = dsh
            else:
                print("Error: ntest1 != nh1 in periodic case. ")

    def _periodic_case(self):
        self._resolve_gap()
        self.remove_shift()

    def _resolve_gap(self):
        """
        solve for periodic case. 9 permutations.
        Assumes the segment begin is constant or decreasing ds and end segment is constant or increasing ds.
        Flow chart is found in mkdocs static site in Q.
        """
        segment_begin = self.segment_list[0]
        segment_end = self.segment_list[-1]

        if (segment_begin.is_constant() and segment_end.is_fixed_length()) or \
                (segment_begin.is_fixed_ds() and segment_end.is_fixed_length()):
            ''' adjust end segment to be fixed ds.'''

            segment_end.ds1 = segment_begin.ds0

        elif segment_begin.is_fixed_length() and segment_end.is_constant() or \
                segment_begin.is_fixed_length() and segment_end.is_fixed_ds():
            ''' adjust segment begin to be fixed ds.'''
            segment_begin.ds0 = segment_end.ds1

        elif (segment_begin.is_constant() and segment_end.is_constant()) or \
                (segment_begin.is_constant() and segment_end.is_fixed_ds()) or \
                (segment_begin.is_fixed_ds() and segment_end.is_constant()):
            ''' adjust to the smallest ds between the two: segment_begin.ds0 or segment_end.ds1. '''
            if segment_begin.ds0 < segment_end.ds1:
                segment_end.ds1 = segment_begin.ds0
            if segment_end.ds1 < segment_begin.ds0:
                segment_begin.ds0 = segment_end.ds1

        elif segment_begin.is_fixed_length() and segment_end.is_fixed_length() and \
                segment_begin.ds0 > segment_begin.ds1 and segment_end.ds0 < segment_end.ds1:
            '''
            Requirements: The first segment in the list should be decreasing and
            fixed length. The last segment should be increasing and fixed length.
            if sh is in the interval we add a phi_shift. 
                        ds0     ds1      ds0        ds1       
                        | |=====| |      | |========| | 
                        | |     | |      | |        | |
                        | |     | |      | |0 //\\ 1| |
                        | |     | | == > |=| //  \\ | |
                        |=|     |=|      | |//    \\|=|
            '''
            # Now find the position of the solution to the equation ds0 * R^n0 = ds1 * R^n1
            ratio = min(segment_begin.var_ds_ratio, segment_end.var_ds_ratio)
            self.solve_periodic_case_both_fixed_length(segment_begin, segment_end, ratio)

        elif segment_begin.is_fixed_ds() and segment_end.is_fixed_ds():
            ''' First and last segments are fixed ds. Then we got to make sure the fixed length 
                segment does not go above the user ds requests. If so, a constant segment will be added.'''

            if segment_begin.ds0 == segment_end.ds1:
                ''' Modify both begin and end segments. (add a phi_shift)'''
                ratio = min(segment_begin.var_ds_ratio, segment_end.var_ds_ratio)
                max_ds = max(segment_end.ds1, segment_begin.ds0)
                s, n1, n0, dsn1, dsn0, sh = self.calculate_intersection(ds_begin=segment_end.ds0,
                                                                        ds_end=segment_begin.ds1,
                                                                        segment_begin_s1=segment_end.s0,
                                                                        segment_end_s0=2 * numpy.pi + segment_begin.s1,
                                                                        ratio=ratio)
                dsh1 = numpy.interp(sh, s, dsn1)
                dsh0 = numpy.interp(sh, s, dsn0)

                if dsh1 > max_ds and dsh0 > max_ds:
                    '''
                    Add a constant segment to optimize the mesh and still remain below user request.
                                ds0     ds1      ds0        ds1
                                | |     | |      | |0 ==== 1| |
                                | |     | | == > | | //  \\ | |
                                |=|     |=|      |=|//    \\|=|
                    '''
                    s, n1, n0, dsn1, dsn0 = self.get_vectors(ds_begin=segment_end.ds0, ds_end=segment_begin.ds1,
                                                             segment_begin_s1=segment_end.s0,
                                                             segment_end_s0=2 * numpy.pi + segment_begin.s1,
                                                             ratio=ratio)

                    # Find sh0 (where dsn0 == max_ds)
                    sh0 = self.get_sh(s, max_ds, dsn0)

                    # Find sh1 (where dsn1 == max_ds)
                    sh1 = self.get_sh(s, max_ds, dsn1)

                    # Now discretize it by choosing the n0 and n1s and then slightly modifying
                    # the ratios. This way you can guarantee that the mesh solution fits exactly
                    # in this space.
                    nh0 = numpy.ceil(numpy.interp(sh0, s, n0))
                    dsh0 = numpy.interp(sh0, s, dsn0)
                    nh1 = numpy.ceil(numpy.interp(sh1, s, n1))
                    dsh1 = numpy.interp(sh1, s, dsn1)
                    ratio0 = numpy.power((dsh0 / segment_end.ds0), (1.0 / nh0))
                    ratio1 = numpy.power((dsh1 / segment_begin.ds1), (1.0 / nh1))

                    # Now make sure it works
                    n_test0 = self.get_n_test0(ratio0, -segment_end.s0, -sh0, segment_end.ds0)
                    n_test1 = self.get_n_test1(ratio1, -(segment_begin.s1 + 2 * numpy.pi), -sh1, segment_begin.ds1)

                    if n_test0 == nh0 and n_test1 == nh1:
                        segment_end.s1 = sh0
                        segment_end.ds1 = dsh0  # segment_end.BG_REGION_DS  # Approximated at dsh0
                        segment_end.var_ds_ratio = ratio0
                        gap_constant_segment = MeshSegment(sh0, sh1)
                        gap_constant_segment.set_ds(dsh0, dsh1)
                        self.segment_list = numpy.insert(self.segment_list, len(self.segment_list),
                                                         gap_constant_segment)
                        segment_begin.s0 = (sh1 - 2 * numpy.pi)
                        segment_begin.ds0 = segment_end.BG_REGION_DS  # Approximated at dsh1
                        segment_begin.var_ds_ratio = ratio1
                    else:
                        print("Error: n_test0 or n_test1")

                else:
                    '''
                    Handle like the fixed length segments, which adds a phi_shift.
                                ds0     ds1      ds0       ds1
                                | |=====| |      | |========| |
                                | |     | |      | |        | |
                                | |     | |      | |0 //\\ 1| |
                                | |     | | == > |=| //  \\ | |
                                |=|     |=|      | |//    \\|=|
                    '''
                    self.solve_periodic_case_both_fixed_length(segment_begin=segment_begin, segment_end=segment_end,
                                                               ratio=ratio)

            elif segment_begin.ds0 < segment_end.ds1:
                # ONLY ADJUST THE LAST SEGMENT SIMILAR TO THE CALCULATIONS IN RESOLVE_GAP
                s, n0, n1, dsn0, dsn1, sh = self.calculate_intersection(ds_begin=segment_end.ds0,
                                                                        ds_end=segment_begin.ds0,
                                                                        segment_begin_s1=segment_end.s0,
                                                                        segment_end_s0=segment_end.s1,
                                                                        ratio=segment_end.var_ds_ratio)
                if sh == segment_end.s0:
                    '''
                    CASE #1: the segment_end.ds0 is much smaller or bigger than segment_begin.ds0.
                    Handle like constant case. Force segment end to end as segment begin ds0. 
                    '''
                    segment_end.ds1 = segment_begin.ds0

                if segment_end.s0 < sh < segment_end.s1:
                    '''
                    CASE #2: the segment_end.ds0 is fairly similar to segment_end_ds1.
                    Segment end:
                    '''
                    nh0 = numpy.ceil(numpy.interp(sh, s, n0))
                    nh1 = numpy.ceil(numpy.interp(sh, s, n1))
                    dsh0 = numpy.interp(sh, s, dsn0)
                    dsh1 = numpy.interp(sh, s, dsn1)

                    if dsh0 < segment_end.ds1 and dsh1 < segment_end.ds1:
                        ''' Then can be treated as resolve gap. '''
                        ratio0 = numpy.power((dsh0 / segment_begin.ds0), (1.0 / nh0))
                        ratio1 = numpy.power((dsh1 / segment_end.ds0), (1.0 / nh1))

                        # Now make sure it works
                        n_test0 = self.get_n_test0(ratio0, segment_end.s1, sh, segment_begin.ds0)
                        n_test1 = self.get_n_test1(ratio1, segment_end.s0, sh, segment_end.ds0)

                        if n_test0 == nh0 and n_test1 == nh1:
                            '''
                            ds0    ds1       ds0     ds1
                            | |    | |      | |1    0| |
                            |=|    | | == > |=|// \\ | |
                            | |    |=|      | |    \\|=|
                            '''
                            gap_segment = MeshSegment(sh, segment_end.s1)
                            segment_end.s1 = sh
                            segment_end.ds1 = segment_end.BG_REGION_DS
                            gap_segment.set_ds(segment_end.BG_REGION_DS, segment_begin.ds0)
                            self.segment_list = numpy.insert(self.segment_list, len(self.segment_list), gap_segment)
                            segment_end.var_ds_ratio = ratio1
                            self.segment_list[-1].var_ds_ratio = ratio0
                        else:
                            print("Error: ntest0 != nh0 and ntest1 !=nh1")
                    else:
                        ''' 
                        Overshoot case need a constant segment added.
                                ds0     ds1      ds0       ds1
                                | |     | |      | |1     0| |        
                                | |     | |      | | ====  | |
                                |=|     | | == > |=|//  \\ | |
                                | |     |=|      | |     \\|=|
                        '''
                        # Find sh1 (where dsn1 == ds_max)
                        sh1 = self.get_sh(s, dsn1, segment_end.ds1)

                        # Find sh0 (where dsn0 == ds_max)
                        sh0 = self.get_sh(s, dsn0, segment_end.ds1)

                        # Now discretize it by choosing the n0 and n1s and then slightly modifying
                        # the ratios. This way you can guarantee that the mesh solution fits exactly
                        # in this space.
                        nh0 = numpy.ceil(numpy.interp(sh0, s, n0))
                        dsh0 = numpy.interp(sh0, s, dsn0)
                        nh1 = numpy.ceil(numpy.interp(sh1, s, n1))
                        dsh1 = numpy.interp(sh1, s, dsn1)
                        ratio0 = numpy.power((dsh0 / segment_begin.ds0), (1.0 / nh0))
                        ratio1 = numpy.power((dsh1 / segment_end.ds0), (1.0 / nh1))

                        # Now make sure it works
                        n_test0 = self.get_n_test0(ratio0, segment_end.s1, sh0, segment_begin.ds0)
                        n_test1 = self.get_n_test1(ratio1, segment_end.s0, sh1, segment_end.ds0)

                        # save segment_end.s1 used later to adjust the segments added.
                        s1_end = segment_end.s1
                        if n_test0 == nh0 and n_test1 == nh1:
                            segment_end.s1 = sh1
                            segment_end.ds1 = dsh0  # segment_end.BG_REGION_DS
                            segment_end.var_ds_ratio = ratio1
                            gap_constant_segment = MeshSegment(sh1, sh0)
                            gap_constant_segment.set_ds(dsh0, dsh1)
                            self.segment_list = numpy.insert(self.segment_list, len(self.segment_list),
                                                             gap_constant_segment)
                            gap_segement_decrease = MeshSegment(sh0, s1_end)
                            gap_segement_decrease.set_ds(dsh1, segment_begin.ds0)
                            self.segment_list = numpy.insert(self.segment_list, len(self.segment_list),
                                                             gap_segement_decrease)
                            self.segment_list[-1].var_ds_ratio = ratio0
                        else:
                            print("Error: n_test0 and n_test1")

            elif segment_begin.ds0 > segment_end.ds1 and segment_begin.ds0 != segment_begin.BG_REGION_DS:
                # ONLY ADJUST THE BEGIN SEGMENT SIMILAR TO THE CALCULATIONS IN RESOLVE_GAP
                s, n0, n1, dsn0, dsn1, sh = self.calculate_intersection(ds_begin=segment_end.ds1,
                                                                        ds_end=segment_begin.ds1,
                                                                        segment_begin_s1=segment_begin.s0,
                                                                        segment_end_s0=segment_begin.s1,
                                                                        ratio=segment_begin.var_ds_ratio)
                if sh == segment_begin.s1:
                    '''
                    CASE #1: the segment_end.ds1 is much smaller/bigger than segment_begin.ds1.
                    Handle like constant segment case. Force the begin segment to begin as segment_end.ds1.
                    Ensures periodicity.  
                    '''
                    segment_begin.ds0 = segment_end.ds1

                if segment_begin.s0 < sh < segment_begin.s1:
                    '''
                    CASE #2: the segment_begin.ds1 is fairly similar to segment_end_ds1.
                    '''
                    nh0 = numpy.ceil(numpy.interp(sh, s, n0))
                    nh1 = numpy.ceil(numpy.interp(sh, s, n1))
                    dsh0 = numpy.interp(sh, s, dsn0)
                    dsh1 = numpy.interp(sh, s, dsn1)

                    if dsh0 < segment_begin.ds0 and dsh1 < segment_begin.ds0:
                        ''''
                            ds0     ds1     ds0     ds1
                            | |    | |      | |1   0| |
                            | |    |=|  ==> | | //\\|=|
                            |=|    | |      |=|//   | |
                
                        '''
                        ratio0 = numpy.power((dsh0 / segment_begin.ds1), (1.0 / nh0))
                        ratio1 = numpy.power((dsh1 / segment_end.ds1), (1.0 / nh1))

                        # Now make sure it works
                        n_test0 = self.get_n_test0(ratio0, segment_begin.s1, sh, segment_begin.ds1)
                        n_test1 = self.get_n_test1(ratio1, segment_begin.s0, sh, segment_end.ds1)

                        if n_test0 == nh0 and n_test1 == nh1:
                            gap_segment = MeshSegment(sh, segment_begin.s1)
                            gap_segment.set_ds(segment_begin.BG_REGION_DS, segment_begin.ds1)
                            segment_begin.ds1 = segment_begin.BG_REGION_DS
                            segment_begin.ds0 = segment_end.ds1
                            segment_begin.s1 = sh
                            self.segment_list = numpy.insert(self.segment_list, 1, gap_segment)
                            segment_begin.var_ds_ratio = ratio1
                            self.segment_list[1].var_ds_ratio = ratio0
                        else:
                            print("Error: n_test0 and n_test1")

                    else:
                        ''''
                            Overshoot case. Need to add a constant segment. 
                            ds0      ds1      ds0       ds1
                            | |      | |      | |1 === 0| |
                            | |      |=|  ==> | | //  \\|=|
                            |=|      | |      |=|//     | |

                        '''

                        # Find sh1 (where dsn1 == ds_max)
                        sh1 = self.get_sh(s, dsn1, segment_begin.ds0)

                        # Find sh0 (where dsn0 == ds_max)
                        sh0 = self.get_sh(s, dsn0, segment_begin.ds0)

                        # Now discretize it by choosing the n0 and n1s and then slightly modifying
                        # the ratios. This way you can guarantee that the mesh solution fits exactly
                        # in this space.
                        nh0 = numpy.ceil(numpy.interp(sh0, s, n0))
                        dsh0 = numpy.interp(sh0, s, dsn0)
                        nh1 = numpy.ceil(numpy.interp(sh1, s, n1))
                        dsh1 = numpy.interp(sh1, s, dsn1)
                        ratio0 = numpy.power((dsh0 / segment_begin.ds1), (1.0 / nh0))
                        ratio1 = numpy.power((dsh1 / segment_end.ds1), (1.0 / nh1))

                        # Now make sure it works
                        n_test0 = self.get_n_test0(ratio0, segment_begin.s1, sh0, segment_begin.ds1)
                        n_test1 = self.get_n_test1(ratio1, segment_begin.s0, sh1, segment_end.ds1)

                        s1_begin = segment_begin.s1
                        ds1_begin = segment_begin.ds1

                        if n_test1 == nh1 and n_test0 == nh0:
                            segment_begin.s1 = sh1
                            segment_begin.ds0 = segment_end.ds1
                            segment_begin.ds1 = dsh1  # segment_begin.BG_REGION_DS  # dsh1
                            segment_begin.var_ds_ratio = ratio1
                            gap_constant_segment = MeshSegment(sh1, sh0)
                            gap_constant_segment.set_ds(dsh1, dsh0)
                            self.segment_list = numpy.insert(self.segment_list, 1, gap_constant_segment)
                            gap_segment_2 = MeshSegment(sh0, s1_begin)
                            gap_segment_2.set_ds(dsh0, ds1_begin)  # segment_begin.BG_REGION_DS
                            self.segment_list = numpy.insert(self.segment_list, 2, gap_segment_2)
                            self.segment_list[2].var_ds_ratio = ratio0
                        else:
                            print("Error: n_test0 and n_test1")

    def remove_shift(self):
        """ determine the shift and shift all segments accordingly. """
        segment_begin = self.segment_list[0]
        phi_shift = segment_begin.s0
        self.phi_shift = phi_shift
        for segments in self.segment_list:  # works for both cases: right and left shift
            segments.s0 = segments.s0 - phi_shift
            segments.s1 = segments.s1 - phi_shift
        return phi_shift

    def revert_shift(self):
        """ determine the previous shift and revert to original mesh without any shifts. """
        for segments in self.segment_list:  # works for both cases: right and left shift
            segments.s0 = segments.s0 + self.phi_shift
            segments.s1 = segments.s1 + self.phi_shift
        self.phi_shift = 0
