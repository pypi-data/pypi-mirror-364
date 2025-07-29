""" This is a class to keep track of the legacy mesh parameters in the process of optimizing the total number of
mesh points (step #4 of creating a mesh). """
from mesh_generator.bin.psi_mesh_tool import mesh_coordinate_transforms
import numpy as np
import json
import os


class MeshOptimizer:
    """
    Mesh optimizer class to keep track of mesh results.
    """

    def __init__(self, adjusted_mesh: dict, legacy_mesh: dict, mesh_type: str, output_file_name=None,
                 mesh_res_file_name=None, dir_name=None):
        # dictionary of adjusted mesh parameters.
        self.adjusted_mesh = adjusted_mesh
        # dictionary of legacy mesh parameters.
        self.legacy_mesh = legacy_mesh
        # mesh type = "t"/"p"/"r"
        self.mesh_type = mesh_type
        # file name to save mesh points. default=None, which will not write the mesh results.
        self.mesh_res_file_name = mesh_res_file_name
        # output file name with legacy mesh parameters.
        self.output_file_name = output_file_name
        # total number of mesh points.
        self.total_num_points = 0
        # ratio between s0 and legacy upper bound
        self.ratio_in_s = []
        # ration between ds0 and ds1
        self.ratio_in_ds = []
        # number of filters.
        self.filter = 0
        # main directory to save results.
        self.dir_name = dir_name
        # list of all mesh points location.
        self.s_list = []
        # list of all mesh points resolution.
        self.ds_list = []
        # list of ratio between mesh points.
        self.r_list = []

    def __str__(self):
        return json.dumps(self.json_dict(), indent=2, default=lambda o: o.json_dict())

    def __call__(self):
        """ compute optimal mesh total number of points and save it in mesh files. """
        # compute the legacy mesh segment ratio.
        self.compute_legacy_ratio()

        # compute the list of mesh points.
        self.calculate_mesh_points()

        # check mesh is valid - adjust the mesh points.
        self.check_mesh_valid()

        # write mesh files.
        self.write_files()

    def json_dict(self):
        return {
            'adjusted_mesh': self.adjusted_mesh,
            'legacy_mesh': self.legacy_mesh,
            'mesh_type': self.mesh_type,
            's': self.s_list,
            'ds': self.ds_list,
            'ratio': self.r_list
        }

    def compute_legacy_ratio(self):
        """ compute the legacy mesh segment resolution ratio"""
        for idx in range(0, len(self.legacy_mesh['segment_list'])):
            segments = self.legacy_mesh['segment_list'][idx]
            self.total_num_points += segments["num_points"]
            self.ratio_in_s.append((segments["s0"] - self.legacy_mesh["lower_bnd"]) /
                                   (self.legacy_mesh["upper_bnd"] - self.legacy_mesh["lower_bnd"]))

            if idx == len(self.legacy_mesh['segment_list']) - 1:
                self.ratio_in_s.append(segments["s1"] / self.legacy_mesh["upper_bnd"])
            self.ratio_in_ds.append(segments["ratio"])

        if self.legacy_mesh["periodic"]:
            self.ratio_in_s = self.ratio_in_s[:-1]

    def write_mesh_output_file(self):
        """ write mesh res file. """
        # open .dat file
        output_path = os.path.join(self.dir_name, self.output_file_name)
        with open(output_path, "w") as f:
            f.write("Mesh coordinate label:\n%s \n" % self.mesh_type)
            f.write("Flag to specify a periodic mesh [.true.|.false.]:\n%s \n" %
                    self._is_periodic(self.legacy_mesh['periodic']))
            f.write("Number of mesh points:\n%s\n" % self.total_num_points)
            f.write("Lower and upper mesh limits [X0,X1]:\n %s, %s\n" % (
                "{0:.6E}".format(self.legacy_mesh["lower_bnd"]),
                "{0:.6E}".format(self.legacy_mesh["upper_bnd"])))

            f.write("Position of segments, FRAC [terminated with /]:\n %s" % "{0:.6E}".format(self.ratio_in_s[0]))
            for i in range(1, len(self.ratio_in_s)):
                f.write(', ' + str("{0:.6E}".format(self.ratio_in_s[i])))
            f.write('/\n')

            f.write("Ratio of segments, DRATIO [terminated with /]:\n %s" % "{0:.6E}".format(self.ratio_in_ds[0]))
            for i in range(1, len(self.ratio_in_ds)):
                f.write(', ' + str("{0:.6E}".format(self.ratio_in_ds[i])))
            f.write('/\n')

            f.write("Amount to shift the mesh:\n %s\n" % "{0:.6E}".format(self.legacy_mesh['phi_shift']))
            f.write("Number of times to filter:\n%s" % self.filter)
        return self.total_num_points

    @staticmethod
    def _is_periodic(legacy):
        if not legacy:
            return ".false."
        else:
            return ".true."

    def calculate_mesh_points(self):
        """ compute the location of all mesh points and their corresponding ds."""
        # compute the mesh by fraction ratio and total number of mesh points. This computation is originally done
        # in PSI tool called "Mesh", translated from FORTRAN.
        self.s_list = mesh_coordinate_transforms(label=self.mesh_type, nc=self.total_num_points,
                                                 c0=self.legacy_mesh["lower_bnd"], c1=self.legacy_mesh["upper_bnd"],
                                                 frac=self.ratio_in_s, dratio=self.ratio_in_ds, nfilt=self.filter,
                                                 periodic=self.legacy_mesh["periodic"],
                                                 c_shift=self.legacy_mesh["phi_shift"])

        self.get_lists()  # save the computed lists.

    def get_lists(self):
        """ saves s, ds, ratio vectors. """
        self.ds_list = self.s_list - np.roll(self.s_list, 1)

        if self.legacy_mesh["periodic"]:
            self.ds_list[0] = self.ds_list[-1]
        else:
            self.ds_list[0] = self.ds_list[1]

        self.r_list = self.ds_list / np.roll(self.ds_list, 1)
        if self.legacy_mesh["periodic"]:
            self.r_list[0] = self.r_list[-1]
        else:
            self.r_list[0] = self.r_list[2]
            self.r_list[1] = self.r_list[2]

    def write_mesh_res_file(self):
        """ write mesh_res_[p/t/r].dat file with mesh solution = s/ds/r lists"""
        file_path = os.path.join(self.dir_name, self.mesh_res_file_name)
        with open(file_path, "w") as f:
            f.write("i	" + self.mesh_type + "	d" + self.mesh_type + "	ratio\n")
            if self.legacy_mesh["periodic"]:
                j0 = 1
            else:
                j0 = 3
                f.write('{0: >8}'.format('1') + "\t " + "{:.14E}".format(self.s_list[0]) + "    " +
                        "{:.14E}".format(self.ds_list[1]) + "\t " + "{:.14E}".format(self.r_list[2]) + "\n")
                f.write('{0: >8}'.format('2') + "\t " + "{:.14E}".format(self.s_list[1]) + "\t " +
                        "{:.14E}".format(self.ds_list[1]) + "\t " + "{:.14E}".format(self.r_list[2]) + "\n")
            for j in range(j0, self.total_num_points + 1):
                f.write('{0: >8}'.format(j) + "\t " + "{:.14E}".format(self.s_list[j - 1]) + "\t " +
                        "{:.14E}".format(self.ds_list[j - 1]) + "\t " + "{:.14E}".format(self.r_list[j - 1]) + "\n")

    def check_seg(self):
        """
        This test will check if the mesh is below all constant mesh segments that the user specified.
        It will save all the mesh segments with ds=1 (constant segments) and will read mesh results to see if points are
        below segment requirements.
        Iteratively.
        :return: bool True/False
        """
        epsilon = 1e-8
        exceed_seg = False

        new_constant_list = []  # a list with all constant segments
        phi_shift = self.adjusted_mesh['phi_shift']
        for segments in self.adjusted_mesh['segment_list']:
            if segments['ratio'] == 1.:
                new_constant_list.append(segments)

        ii = 0
        jj = 0
        while ii < len(new_constant_list):
            s0 = (new_constant_list[ii]['s0']) + phi_shift
            s1 = (new_constant_list[ii]['s1']) + phi_shift
            ds = (new_constant_list[ii]['ds0'])
            while jj < len(self.s_list):
                x = self.s_list[jj]  # s
                y = self.ds_list[jj]  # ds
                if s0 < x < s1:
                    if y > ds + epsilon:
                        # mesh is above user requests! -> break then call add_num.
                        exceed_seg = True
                        return exceed_seg
                if x > s1:
                    # break -> move to the next constant mesh segment.
                    break
                jj += 1
            ii += 1
        return exceed_seg

    def check_ratio(self):
        """
        Check if the the new legacy mesh exceeds 100.5% of BG_RATIO
        :return: bool True/False
        """
        percent = 0.005
        exceed_ratio = False
        ratio_max = self.adjusted_mesh['BG_RATIO'] * (1 + percent)
        ratio_min = (1. / self.adjusted_mesh['BG_RATIO']) * (1 - percent)

        for ii in range(len(self.r_list)):
            if self.r_list[ii] > ratio_max:
                exceed_ratio = True
                return exceed_ratio
            if self.r_list[ii] < ratio_min:
                exceed_ratio = True
                return exceed_ratio
        return exceed_ratio

    def reduce_num(self):
        """
        Iteratively find the optimized number of points for mesh by reducing the total number of points (-1).
        """
        idx = 0
        if not self.check_ratio():
            while idx <= self.total_num_points:
                self.total_num_points += - 1
                self.calculate_mesh_points()
                if self.check_seg() is False and self.check_ratio() is False:
                    idx += 1
                else:
                    self.total_num_points += 1
                    break

    def add_num(self):
        """
        Mesh is exceeding the user requests more points are needed (+1).
        """

        self.total_num_points += 1  # increase total number of points.
        self.calculate_mesh_points()
        idx = 0

        while idx <= self.total_num_points:
            if self.check_seg():
                self.total_num_points += 1
                self.calculate_mesh_points()
                idx += 1
            else:
                break

    def check_mesh_valid(self):
        """adding or subtracting points from legacy mesh total number of points which will move the mesh up or down.
        This is done iteratively.Checks if the mesh exceeds the user constant mesh segment requirements - if so, it
        will add points to the mesh to lower its ds. """
        if self.check_seg():
            # need to optimize your mesh by adding points (+1).
            self.add_num()
        else:
            # need to optimize your mesh by deleting points (-1).
            self.reduce_num()

        # apply filter of 5.
        self.filter = 5

        # compute the mesh points with filter.
        self.calculate_mesh_points()

    def write_files(self):
        """ write mesh results to mesh_res and output files. """
        if self.mesh_res_file_name is not None:
            self.write_mesh_res_file()  # write mesh_res_[p/t/r].dat file with s/ds/r lists.
        if self.output_file_name is not None:
            self.write_mesh_output_file()  # write mesh parameters file.


if __name__ == "__main__":
    from tests.test_results import phi_test_1_adj, phi_test_1_legacy

    step4 = MeshOptimizer(adjusted_mesh=phi_test_1_adj, legacy_mesh=phi_test_1_legacy, mesh_type="p",
                          output_file_name="mesh_test_p.dat", mesh_res_file_name="mesh_res_p_test.dat",
                          dir_name=os.getcwd())
    step4.write_mesh_output_file()
