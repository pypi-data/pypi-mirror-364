"""
User Interface (UI) main window to create a mesh generation by uploading a hdf file magnetogram
plotting it using matplotlib and interactively specifying the mesh requirement. This is a great way to develop more
tests for test/unit_test.py and detect bugs in the src mesh code.
"""

import tkinter as tk
import numpy as np
import matplotlib as mpl
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure
from matplotlib.widgets import RectangleSelector
from matplotlib.patches import Rectangle
from mesh_generator.bin.call_psi_mesh_tool import create_psi_mesh
from mesh_generator.src.mesh_segment import MeshSegment
from mesh_generator.src.mesh import Mesh
from mesh_generator.ui.mesh_info import MeshInfo
from mesh_generator.ui.mesh_box import MeshBox
from mesh_generator.ui.read_hdf import plot_hdf
from mesh_generator.bin.tmp_mas_template import write_tmp_mas_file
from mesh_generator.bin.mesh_header_template import write_mesh_header
from mesh_generator.hdf.read_mesh_res import read_tmp_file
from mesh_generator.hdf.write_1d_hdf_files import write_1d_mesh_hdf
from mesh_generator.ui.save_dict import SaveDict
from mesh_generator.ui.restrictor_pan import RestrictPan
from mesh_generator.ui.my_axes import My_Axes
from mesh_generator.ui.mesh_num_points import get_num_points
from mesh_generator.ui.scroll_bar import VerticalScrolledFrame
from mesh_generator.ui.table_chart import TableChart

import os


class MeshApp:
    """The User Interface main app to develop a 3D mesh. """

    def __init__(self, hdf_file_path, ui_session_data, save_mesh_file_path, UseExistingInput=False):
        root = tk.Tk()
        root.wm_title("MainApp")  # title of the window.
        root.config(background="white")  # background color of the window.
        width_screen_mm = root.winfo_screenmmwidth()
        width_screen_pxl = root.winfo_screenwidth()
        height_screen_mm = root.winfo_screenmmheight()
        height_screen_pxl = root.winfo_screenheight()
        self.hdf_file_path = hdf_file_path

        for ii in range(3):
            root.grid_columnconfigure(ii, weight=1)  # the text and entry frames column
        for jj in range(3):
            root.grid_rowconfigure(jj, weight=1)  # all frames row
        # assign the mesh results folder
        self.mesh_results_folder = save_mesh_file_path

        # frame with instructions on how to use gui includes step 1 and step 2.
        # (submitting the boxes and input respective ds.)
        self.leftFrame = VerticalScrolledFrame(root, relief=tk.SUNKEN, width=width_screen_pxl/4,
                                               height=height_screen_pxl/5)
        self.leftFrame.grid(row=0, column=0, sticky=tk.NSEW,  rowspan=2)

        # label with step 1 instruction
        tk.Label(self.leftFrame, text="Step 1: Draw each box, when box is finalized click save latest box button.").\
            grid(row=0, column=0, columnspan=5, sticky=tk.NW, pady=10)

        # save latest box button
        tk.Button(self.leftFrame, text='save latest box', activeforeground='navy',
                  command=self.save_latest_box).grid(row=1, column=1, pady=10)

        # reset latest box button
        tk.Button(self.leftFrame, text='Reset', activeforeground='navy', command=self.reset) \
            .grid(row=4, column=1, pady=10)

        # delete drop-box
        tk.Label(self.leftFrame, text="Remove box #:").grid(row=3, column=0, sticky=tk.E)
        self.del_tb_variable = tk.StringVar(self.leftFrame)
        self.del_tb_variable.set(' ')
        self.del_tb_opt = tk.OptionMenu(self.leftFrame, self.del_tb_variable, ' ')
        self.del_tb_opt.grid(row=3, column=1, sticky=tk.NSEW)
        self.del_tb_variable.trace("w", self.drop_box_delete_box_get_val)
        tk.Button(self.leftFrame, text='apply', command=self.delete_box).grid(row=3, column=2, sticky=tk.W)

        # redraw drop-box
        tk.Label(self.leftFrame, text="Redraw box #:").grid(row=2, column=0, sticky=tk.E)
        self.redraw_variable = tk.StringVar(self.leftFrame)
        self.redraw_variable.set(' ')
        self.redraw_opt = tk.OptionMenu(self.leftFrame, self.redraw_variable, ' ')
        self.redraw_opt.grid(row=2, column=1, sticky=tk.NSEW)
        self.del_tb_variable.trace("w", self.redraw_drop_box_get_val)

        tk.Button(self.leftFrame, text='apply', command=self.redraw_box_apply).grid(row=2, column=2, sticky=tk.W)
        tk.Button(self.leftFrame, text='submit', command=self.redraw_submit).grid(row=2, column=2, sticky=tk.E)

        # optional edit box table manually in a new window.
        tk.Label(self.leftFrame, text="(Optional) Enter box coordinates manually").grid(row=5, column=0,
                                                                                        sticky=tk.W, columnspan=3,
                                                                                        pady=10)
        tk.Button(self.leftFrame, text='Box Chart', command=self.box_chart).grid(row=6, column=1)

        # step 2- enter ds values
        tk.Label(self.leftFrame, text="Step 2: After submitting each box indicate desired ds in textbox below.")\
            .grid(row=7, column=0, columnspan=7, sticky=tk.W, pady=10)

        # enter BG ratio
        tk.Label(self.leftFrame, text="BG ratio:").grid(row=8, column=0, sticky=tk.E, pady=10)
        self.bg_ratio = tk.Entry(self.leftFrame, width=5)
        self.bg_ratio.insert(tk.END, '1.06')
        self.bg_ratio.grid(row=8, column=1, sticky=tk.W)

        # enter FG ratio
        tk.Label(self.leftFrame, text="FG ratio:").grid(row=8, column=2, sticky=tk.E, pady=10)
        self.fg_ratio = tk.Entry(self.leftFrame, width=5)
        self.fg_ratio.insert(tk.END, '1.03')
        self.fg_ratio.grid(row=8, column=3, sticky=tk.W)

        tk.Label(self.leftFrame, text="ds", relief=tk.RIDGE, bg='lightgray', bd=2, width=10). \
            grid(row=9, column=1, sticky=tk.NSEW)
        tk.Label(self.leftFrame, text="ratio", relief=tk.RIDGE, bg='lightgray', bd=2, width=10). \
            grid(row=9, column=2, sticky=tk.NSEW)

        # second frame: includes step 3, 4 and building a radial mesh manually.
        self.rightFrame = VerticalScrolledFrame(root, relief=tk.SUNKEN, width=width_screen_pxl/4,
                                                height=height_screen_pxl/5)
        self.rightFrame.grid(row=0, column=2, rowspan=2, sticky=tk.NSEW)

        # step 4- get total number of points in theta and phi
        tk.Button(self.rightFrame, text='\u03B8 number of points', command=self.num_points_theta) \
            .grid(row=2, column=0, columnspan=1, pady=10)
        tk.Button(self.rightFrame, text='\u03C6 number of points', command=self.num_points_phi) \
            .grid(row=3, column=0, columnspan=1, pady=10)

        tk.Label(self.rightFrame, text="     ").grid(row=2, column=1, pady=10, sticky=tk.W)
        tk.Label(self.rightFrame, text="     ").grid(row=3, column=1, pady=10, sticky=tk.W)

        # step 4- get plots of phi and theta mesh results
        tk.Label(self.rightFrame, text="Step 3: Get mesh results").grid(row=1, column=0, sticky=tk.W,
                                                                                pady=10)
        tk.Button(self.rightFrame, text='\u03B8 mesh plot', command=self.get_theta_results). \
            grid(row=2, column=2, sticky=tk.W, columnspan=2, pady=10)
        tk.Button(self.rightFrame, text='\u03C6 mesh plot', command=self.get_phi_results). \
            grid(row=3, column=2, sticky=tk.W, columnspan=2, pady=10)

        # step 5- radial mesh table
        tk.Label(self.rightFrame, text="Step 4: Input radial mesh segments").grid(row=4, column=0,
                                                                                          columnspan=2, pady=10,
                                                                                          sticky=tk.W)
        # get radial total number of mesh points
        tk.Button(self.rightFrame, text='r number of points', command=self.num_points_r). \
            grid(row=5, column=0, columnspan=1, pady=10)
        tk.Label(self.rightFrame, text="     ").grid(row=5, column=1, pady=10, sticky=tk.W)

        # get radial mesh resulted plot
        tk.Button(self.rightFrame, text='r mesh plot', command=self.get_radial_results). \
            grid(row=5, column=2, sticky=tk.W, columnspan=2, pady=10)

        # total number of points of all mesh (t x p x r):
        tk.Label(self.rightFrame, text="Compute total number of points:").grid(row=6, column=0, pady=10,
                                                                                       sticky=tk.W, columnspan=2)
        tk.Button(self.rightFrame, text='\u03B8 x \u03C6 x r', command=self.total_num_points). \
            grid(row=6, column=2, sticky=tk.NSEW, pady=10)

        # RADIAL_BG_TEXTBOX
        tk.Label(self.rightFrame, text="Radial BG ratio:").grid(row=7, column=0, sticky=tk.E)
        self.radial_bg_ratio = tk.Entry(self.rightFrame, width=5, bg='white')
        self.radial_bg_ratio.insert(tk.END, '1.06')
        self.radial_bg_ratio.grid(row=7, column=1, sticky=tk.W)

        # RADIAL_FG_TEXTBOX
        tk.Label(self.rightFrame, text="Radial FG ratio:").grid(row=7, column=2, sticky=tk.E, columnspan=2)
        self.radial_fg_ratio = tk.Entry(self.rightFrame, width=5, bg='white')
        self.radial_fg_ratio.insert(tk.END, '1.03')
        self.radial_fg_ratio.grid(row=7, column=4, sticky=tk.W)

        # R0_TEXTBOX
        tk.Label(self.rightFrame, text="rMin:").grid(row=8, column=0, sticky=tk.E)
        self.rMin = tk.Entry(self.rightFrame, width=5, bg='white')
        self.rMin.insert(tk.END, '1')
        self.rMin.grid(row=8, column=1, sticky=tk.W)

        # R1_TEXTBOX
        tk.Label(self.rightFrame, text="rMax:").grid(row=9, column=0, sticky=tk.E)
        self.rMax = tk.Entry(self.rightFrame, width=5, bg='white')
        self.rMax.insert(tk.END, '2.5')
        self.rMax.grid(row=9, column=1, sticky=tk.W)

        # # RADIAL TABLE
        tk.Label(self.rightFrame, text='r0', relief=tk.RIDGE, bg='lightgray', bd=2, width=6).grid(row=10, column=1,
                                                                                                  sticky=tk.NSEW,
                                                                                                  columnspan=1)
        tk.Label(self.rightFrame, text='r1', relief=tk.RIDGE, bg='lightgray', bd=2, width=6).grid(row=10, column=2,
                                                                                                  sticky=tk.NSEW,
                                                                                                  columnspan=1)
        tk.Label(self.rightFrame, text='dr', relief=tk.RIDGE, bg='lightgray', bd=2, width=6).grid(row=10, column=3,
                                                                                                  sticky=tk.NSEW,
                                                                                                  columnspan=1)
        tk.Label(self.rightFrame, text='ratio', relief=tk.RIDGE, bg='lightgray', bd=2, width=9).grid(row=10,
                                                                                                            column=4,
                                                                                                            sticky=tk.NSEW,
                                                                                                            columnspan=1)

        # save patch of rect drawn on canvas
        self.rect_data = 0
        # save all boxes drawn on the plot in a list
        self.patch_list = []
        # if the button redraw rectangle is pressed then keep track if the new rectangle is drawn on plot.
        self.redraw_box_submit = False
        # if the box number passed in redraw textbox
        self.box_num = 0
        # ds textbox widgets saved in a list
        self.ds_tab_array = []
        # var ds textbox widgets saved in a list
        self.var_ds_tab_array = []
        # radial textbox specifications saved in a list
        self.radial_table_tb = []

        # pan only left and right
        mpl.projections.register_projection(My_Axes)

        # frame containing the canvas
        self.midFrame = tk.Frame(root, background="white")  # , width=300, height=200,
        self.midFrame.grid(row=0, column=1, rowspan=2)
        # Make the canvas decently large.
        self.fig = Figure(figsize=(width_screen_mm/(3*25.4), height_screen_mm/(3*25.4))) # figsize=(8, 4), dpi=100
        #self.fig.subplots_adjust(left=0.02, bottom=0.1, right=0.96, top=0.92, wspace=0, hspace=0)
        self.ax = self.fig.add_subplot(111, projection="My_Axes")
        self.hdf_file_path = hdf_file_path
        cmin = self.setup_magnetogram_plot(self.fig, self.hdf_file_path)

        # save ui_session button.
        self.bottomFrame = tk.Frame(root) # width=1830, height=10
        self.bottomFrame.grid(row=2, column=1, columnspan=1)
        tk.Label(self.bottomFrame, text="Step #5: Save all mesh files:").grid(row=1, column=0, columnspan=2)
        tk.Button(self.bottomFrame, text="Save session", command=self.save_ui_session).grid(row=1, column=2)
        tk.Label(self.bottomFrame, text="Colorbar min/max:").grid(row=0, column=0)
        self.cmax_value = tk.Entry(self.bottomFrame, width=5)
        self.cmax_value.insert(tk.END, str(abs(cmin)))
        self.cmax_value.grid(row=0, column=1, sticky=tk.W)
        tk.Button(self.bottomFrame, text="apply", command=self.apply_new_scale).grid(row=0, column=2)

        self.canvas = FigureCanvasTkAgg(self.fig, master=self.midFrame)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(side=tk.BOTTOM, fill=tk.BOTH, expand=1, anchor=tk.CENTER)

        def line_select_callback(eclick, erelease):
            """ draw rectangle boxes on matplotlib figure """
            x1, y1 = eclick.xdata, eclick.ydata
            x2, y2 = erelease.xdata, erelease.ydata
            rect = Rectangle((min(x1, x2), min(y1, y2)), np.abs(x1 - x2), np.abs(y1 - y2), fill=False)
            self.rect_data = rect

        rs = RectangleSelector(self.ax, line_select_callback,
                               drawtype='box', useblit=False, button=[1],
                               minspanx=5, minspany=5, spancoords='pixels',
                               interactive=True)

        toolbar = NavigationToolbar2Tk(self.canvas, self.midFrame)
        toolbar.update()
        # canvas._tkcanvas.pack(side=tk.TOP)

        # read dictionary / MeshInfo object
        if UseExistingInput is False:
            print("new ui_session!")
            self.ui_session = ui_session_data
        if UseExistingInput is True:
            print("uploading json!")
            self.read_ui_session(ui_session_data)

        root.mainloop()

    def read_ui_session(self, ui_session_data):
        # copy information from dictionary to MeshInfo object that can later be edited & saved while using the UI.
        self.ui_session = MeshInfo(lower_bnd_t=ui_session_data["lower_bnd_t"],
                                   upper_bnd_t=ui_session_data["upper_bnd_t"],
                                   lower_bnd_p=ui_session_data["lower_bnd_p"],
                                   upper_bnd_p=ui_session_data["upper_bnd_p"],
                                   lower_bnd_r=ui_session_data["lower_bnd_r"],
                                   upper_bnd_r=ui_session_data["upper_bnd_r"],
                                   BG_RATIO=ui_session_data["BG_RATIO"],
                                   FG_RATIO=ui_session_data["FG_RATIO"],
                                   RADIAL_BG_RATIO=ui_session_data["RADIAL_BG_RATIO"],
                                   RADIAL_FG_RATIO=ui_session_data["RADIAL_FG_RATIO"])

        if len(ui_session_data["box_list"]) != 0:
            self.ui_session.box_list = ui_session_data["box_list"]

        i = 0
        while i < len(self.ui_session.box_list):
            box = self.ui_session.box_list[i]
            self.ui_session.box_list[i] = MeshBox(t0=box['t0'], t1=box['t1'], p0=box['p0'],
                                                  p1=box['p1'], r0=box['r0'], r1=box['r1'], ds=box['ds'],
                                                  radial_ds=box['radial_ds'], radial_var_ds=box['radial_var_ds'],
                                                  tp_var_ds=box['tp_var_ds'])
            i += 1

        # draw boxes on the image
        i = 1
        for rect in self.ui_session.box_list:
            rect_patch = mpl.patches.Rectangle((min(rect.p0, rect.p1), min(rect.t0, rect.t1)),
                                               np.abs(rect.p0 - rect.p1),
                                               np.abs(rect.t0 - rect.t1), fill=False)
            label_box = "Box # %s" % i
            self.ax.text(rect.p0, rect.t0, label_box)
            self.ax.add_patch(rect_patch)
            self.patch_list.append(rect_patch)

            # ds text box
            tk.Label(self.leftFrame, text=label_box, relief=tk.RIDGE, bg='lightgray', bd=2). \
                grid(row=9 + i, column=0, sticky=tk.NSEW)
            self.ds_tab_array.append(tk.Entry(self.leftFrame, width=10, bg='white'))
            self.var_ds_tab_array.append(tk.Entry(self.leftFrame, width=10, bg='white'))
            self.ds_tab_array[-1].insert(tk.END, str(rect.ds))
            if rect.tp_var_ds is not None:
                self.var_ds_tab_array[-1].insert(tk.END, str(rect.tp_var_ds))
            else:
                self.var_ds_tab_array[-1].insert(tk.END, str(self.ui_session.FG_RATIO))
            self.ds_tab_array[-1].grid(row=9 + i, column=1, sticky=tk.NSEW)
            self.var_ds_tab_array[-1].grid(row=9 + i, column=2, sticky=tk.NSEW)

            # add r table with textbox
            tk.Label(self.rightFrame, text=label_box, relief=tk.RIDGE, bg='lightgray', bd=2) \
                .grid(row=10 + i, column=0, sticky=tk.NSEW)
            cols = []
            for j in range(4):
                e = tk.Entry(self.rightFrame, width=5)
                if j == 0 and rect.r0 is not None:
                    e.insert(tk.END, str(rect.r0))
                elif j == 1 and rect.r1 is not None:
                    e.insert(tk.END, str(rect.r1))
                elif j == 2 and rect.radial_ds is not None:
                    e.insert(tk.END, str(rect.radial_ds))
                elif j == 3 and rect.radial_var_ds is not None:
                    e.insert(tk.END, str(rect.radial_var_ds))
                else:
                    e.insert(tk.END, str(self.ui_session.RADIAL_FG_RATIO))
                e.grid(row=10 + i, column=j + 1, sticky=tk.NSEW)
                cols.append(e)
            self.radial_table_tb.append(cols)
            i += 1

        # add BG_RATIO value to textbox
        self.bg_ratio.delete(0, tk.END)
        self.bg_ratio.insert(0, str(self.ui_session.BG_RATIO))

        # add FG_RATIO value to textbox
        self.fg_ratio.delete(0, tk.END)
        self.fg_ratio.insert(0, str(self.ui_session.FG_RATIO))

        # add BG_RATIO_RADIAL value to textbox
        self.radial_bg_ratio.delete(0, tk.END)
        self.radial_bg_ratio.insert(0, str(self.ui_session.RADIAL_BG_RATIO))

        # add FG_RATIO_RADIAL value to textbox
        self.radial_fg_ratio.delete(0, tk.END)
        self.radial_fg_ratio.insert(0, str(self.ui_session.RADIAL_FG_RATIO))

        # add rMin value to textbox
        self.rMin.delete(0, tk.END)
        self.rMin.insert(0, str(self.ui_session.lower_bnd_r))

        # add rMax value to textbox
        self.rMax.delete(0, tk.END)
        self.rMax.insert(0, str(self.ui_session.upper_bnd_r))

        # add drop-box for deleting mesh boxes, options.
        self.remove_menu_option_delete_dropbox()
        self.remove_menu_option_redraw_dropbox()

    def reset(self):
        """ delete all the boxes drawn on matplotlib figure and clear ui_session box_list."""
        for i in range(0, len(self.ui_session.box_list)):
            # delete the lastest ds textbox and label
            tk.Label(self.leftFrame, text="             ").grid(row=10 + i,
                                                                column=0, sticky=tk.NSEW)
            self.ds_tab_array[i].destroy()
            self.var_ds_tab_array[i].destroy()

            # delete box label in radial table
            tk.Label(self.rightFrame, text="       ", bd=2).grid(row=11 + i, column=0, sticky=tk.NSEW)

        # delete the entry boxes in radial table
        for row in self.radial_table_tb:
            for entry in row:
                entry.destroy()

        self.radial_table_tb = []
        self.ds_tab_array = []
        self.var_ds_tab_array = []
        self.ds_tab_array = []
        # delete all boxes in dictionary
        self.ui_session.box_list = np.array([], dtype=MeshBox)

        # remove rectangles from plot
        for box in self.patch_list:
            box.remove()
        self.patch_list.clear()

        # delete all text on plot
        self.ax.texts.clear()

        # remove all dropbox options
        self.reset_delete_box_drop_box()
        self.reset_redraw_box_drop_box()

    def num_points_theta(self):
        """ return the total number of points in current theta mesh. """
        self.get_bg_ratio()
        self.get_fg_ratio()
        self.add_ds()
        try:
            self.get_mesh_theta_1(False)
            num_points_t = get_num_points(os.path.join(self.mesh_results_folder, "tmp_mesh_t.dat"))
        except:
            num_points_t = "n/a"
        tk.Label(self.rightFrame, text=str(num_points_t)).grid(row=2, column=1, sticky=tk.SW)
        return num_points_t

    def num_points_phi(self):
        """ return the total number of points in current phi mesh. """
        self.get_bg_ratio()
        self.get_fg_ratio()
        self.add_ds()
        try:
            self.get_mesh_phi_1(False)
            num_points_p = get_num_points(os.path.join(self.mesh_results_folder, "tmp_mesh_p.dat"))
        except:
            num_points_p = "n/a"
        tk.Label(self.rightFrame, text=str(num_points_p)).grid(row=3, column=1, sticky=tk.SW)
        return num_points_p

    def num_points_r(self):
        """ return the total number of points in current radial mesh. """
        self.get_radial_bg_ratio()
        self.get_radial_rMin()
        self.get_radial_rMax()
        try:
            self.get_mesh_r_1(False)
            num_points_r = get_num_points(os.path.join(self.mesh_results_folder, "tmp_mesh_r.dat"))
        except:
            num_points_r = "n/a"
        tk.Label(self.rightFrame, text=str(num_points_r)).grid(row=5, column=1, sticky=tk.SW)
        return num_points_r

    def total_num_points(self):
        """ return the total number of points in 3d mesh: np_t x np_p x np_r """
        try:
            np_t = self.num_points_theta()
            np_p = self.num_points_phi()
            np_r = self.num_points_r()
            total_np = int(np_t) * int(np_p) * int(np_r)
            tk.Label(self.rightFrame, text=str('{:.2e}'.format(total_np))).grid(row=6, column=3, sticky=tk.W,
                                                                                columnspan=2)
        except:
            total_np = "n/a"
            tk.Label(self.rightFrame, text=total_np).grid(row=6, column=3, sticky=tk.W, columnspan=2)

    def write_tmp_mas_files(self):
        """write a tmp mas files"""
        all_tmp_mesh_files_exist = True
        if os.path.exists(path=os.path.join(self.mesh_results_folder, "tmp_mesh_t.dat")):
            write_tmp_mas_file(mesh_type="t",
                               tmp_mesh_dir_name=os.path.join(self.mesh_results_folder, "tmp_mesh_t.dat"),
                               tmp_mas_dir_name=os.path.join(self.mesh_results_folder, "tmp_mas_t.dat"))
        else:
            all_tmp_mesh_files_exist = False

        if os.path.exists(path=os.path.join(self.mesh_results_folder, "tmp_mesh_p.dat")):
            write_tmp_mas_file(mesh_type="p",
                               tmp_mesh_dir_name=os.path.join(self.mesh_results_folder, "tmp_mesh_p.dat"),
                               tmp_mas_dir_name=os.path.join(self.mesh_results_folder, "tmp_mas_p.dat"))
        else:
            all_tmp_mesh_files_exist = False

        if os.path.exists(path=os.path.join(self.mesh_results_folder, "tmp_mesh_r.dat")):
            write_tmp_mas_file(mesh_type="r",
                               tmp_mesh_dir_name=os.path.join(self.mesh_results_folder, "tmp_mesh_r.dat"),
                               tmp_mas_dir_name=os.path.join(self.mesh_results_folder, "tmp_mas_r.dat"))
        else:
            all_tmp_mesh_files_exist = False

        return all_tmp_mesh_files_exist

    def write_header_file(self):
        """ write a mesh_header.dat file in folder. """
        write_mesh_header(tmp_mas_p_file=os.path.join(self.mesh_results_folder, "tmp_mas_p.dat"),
                          tmp_mas_t_file=os.path.join(self.mesh_results_folder, "tmp_mas_t.dat"),
                          tmp_mas_r_file=os.path.join(self.mesh_results_folder, "tmp_mas_r.dat"),
                          mesh_header_file_path=os.path.join(self.mesh_results_folder, "mesh_header.dat"))

    def write_hdf_files(self):
        """ write 1d mesh spacing hdf5 files and half mesh. """
        if os.path.exists(path=os.path.join(self.mesh_results_folder, "mesh_res_t.txt")) and \
                os.path.exists(path=os.path.join(self.mesh_results_folder, "mesh_res_p.txt")) and \
                os.path.exists(path=os.path.join(self.mesh_results_folder, "mesh_res_r.txt")):
            t, dt, t_ratio = read_tmp_file(name_of_tmp_file=os.path.join(self.mesh_results_folder, "mesh_res_t.txt"))
            p, dt, p_ratio = read_tmp_file(name_of_tmp_file=os.path.join(self.mesh_results_folder, "mesh_res_p.txt"))
            r, rt, r_ratio = read_tmp_file(name_of_tmp_file=os.path.join(self.mesh_results_folder, "mesh_res_r.txt"))
            if self.hdf_file_path[-3:] == ".h5":
                write_1d_mesh_hdf(outdir=self.mesh_results_folder, mesh_name="1x", t=t, p=p, r=r, type=".h5")
            else:
                write_1d_mesh_hdf(outdir=self.mesh_results_folder, mesh_name="1x", t=t, p=p, r=r, type=".hdf")

    def get_all_tabs_info(self):
        """ copy all tabs information to the ui dictionary. this step is done before saving the json file. """
        # radial information.
        self.get_radial_rMin()
        self.get_radial_rMax()
        self.get_radial_fg_ratio()
        self.get_radial_bg_ratio()
        row_num = 1
        for row in self.radial_table_tb:
            self.read_radial_textbox_row(row, row_num)
            row_num += 1

        # theta and phi information.
        self.get_fg_ratio()
        self.get_bg_ratio()
        self.add_ds()

    def save_ui_session(self):
        """ save the current 3d mesh results in bin/mesh_header.dat and in a txt/json file in the ui folder. """
        # recalculate theta, phi, and radial mesh.
        try:
            self.theta(show_plot=False)
        except:
            print("Theta mesh is invalid.")
        try:
            self.phi(show_plot=False)
        except:
            print("Phi mesh is invalid.")
        try:
            self.radial(show_plot=False)
        except:
            print("Radial mesh is invalid. ")

        # write a tmp mas files:
        all_mas_files_exist = self.write_tmp_mas_files()

        # write_mesh_header file.
        if all_mas_files_exist:
            self.write_header_file()

        # write 1d hdf5 files with mesh spacing and half spacing.
        self.write_hdf_files()

        # save json ui_session in a txt/json file:
        root = tk.Tk()
        SaveDict(master=root, ui_session=self.ui_session, save_json_folder=self.mesh_results_folder)
        root.mainloop()

    def get_theta_results(self):
        try:
            self.theta()
        except:
            print("Theta mesh requirements are not valid. ")

    def get_phi_results(self):
        try:
            self.phi()
        except:
            print("Phi mesh requirements are not valid. ")

    def get_radial_results(self):
        try:
            self.radial()
        except:
            print("Radial mesh requirements are not valid. ")

    def theta(self, show_plot=True):
        """ generate a theta mesh. """
        self.get_bg_ratio()
        self.get_fg_ratio()
        self.add_ds()
        try:
            self.get_mesh_theta_1(show_plot)
        except Exception:
            print("Theta mesh failed. ")

    def get_mesh_theta_1(self, show_plot):
        """ include 4 steps of building a theta mesh. """
        if self.ui_session.BG_RATIO != 1.06:
            MeshSegment.DEFAULT_BG_REGION_RATIO = self.ui_session.BG_RATIO
        if self.ui_session.FG_RATIO != 1.03:
            MeshSegment.DEFAULT_FG_REGION_RATIO = self.ui_session.FG_RATIO
        mesh = Mesh(self.ui_session.lower_bnd_t, self.ui_session.upper_bnd_t, False)
        for box in self.ui_session.box_list:
            if 0 <= box.t0 <= np.pi and 0 <= box.t1 <= np.pi:
                mesh.insert_mesh_segment(MeshSegment(box.t0, box.t1, box.ds, var_ds_ratio=box.tp_var_ds))
        if mesh.is_valid():
            input_mesh = mesh.json_dict()
            adj_mesh = mesh.resolve_mesh_segments().json_dict()
            legacy_mesh = mesh.build_legacy_mesh(max_iterations=250).json_dict()
            mpl.pyplot.close("all")
            create_psi_mesh(adj_mesh, legacy_mesh, 't', self.mesh_results_folder, output_file_name="tmp_mesh_t.dat",
                            mesh_res_file_name="mesh_res_t.txt", show_plot=show_plot,
                            save_plot_path=self.mesh_results_folder,
                            save_plot=True, plot_file_name="theta_mesh_spacing.png", input_mesh=input_mesh)

    def phi(self, show_plot=True):
        """ generate a phi mesh."""
        self.get_bg_ratio()
        self.get_fg_ratio()
        self.add_ds()
        try:
            self.get_mesh_phi_1(show_plot)
        except Exception:
            print("Phi mesh failed.")

    def get_mesh_phi_1(self, show_plot):
        """ include 4 steps of building a phi mesh. """
        if self.ui_session.BG_RATIO != 1.06:
            MeshSegment.DEFAULT_BG_REGION_RATIO = self.ui_session.BG_RATIO
        if self.ui_session.FG_RATIO != 1.03:
            MeshSegment.DEFAULT_FG_REGION_RATIO = self.ui_session.FG_RATIO

        mesh = Mesh(self.ui_session.lower_bnd_p, self.ui_session.upper_bnd_p, True)
        for box in self.ui_session.box_list:
            mesh.insert_mesh_segment(MeshSegment(box.p0, box.p1, box.ds, var_ds_ratio=box.tp_var_ds))

        if mesh.is_valid():
            input_mesh = mesh.json_dict()
            adj_mesh = mesh.resolve_mesh_segments().json_dict()  # adjusted mesh as a dictionary
            legacy_mesh = mesh.build_legacy_mesh(max_iterations=250).json_dict()  # legacy mesh as a dictionary
            mpl.pyplot.close("all")
            create_psi_mesh(adj_mesh, legacy_mesh, 'p', self.mesh_results_folder, output_file_name="tmp_mesh_p.dat",
                            mesh_res_file_name="mesh_res_p.txt", show_plot=show_plot, save_plot=True,
                            save_plot_path=self.mesh_results_folder, plot_file_name="phi_mesh_spacing.png",
                            input_mesh=input_mesh)
        else:
            print("Phi input fails to build a mesh. Mesh is not valid.")

    def radial(self, show_plot=True):
        """ generate a radial mesh. """
        self.get_radial_bg_ratio()
        self.get_radial_fg_ratio()
        self.get_radial_rMin()
        self.get_radial_rMax()
        try:
            self.get_mesh_r_1(show_plot)
        except Exception:
            print("Radial mesh failed. ")

    def read_radial_textbox_row(self, row, row_num):
        """ check if radial input textbox content is valid."""
        try:
            s0 = float(row[0].get())
        except ValueError:
            s0 = None
        self.ui_session.box_list[row_num - 1].r0 = s0

        try:
            s1 = float(row[1].get())
        except ValueError:
            s1 = None
        self.ui_session.box_list[row_num - 1].r1 = s1

        try:
            ds = float(row[2].get())
        except ValueError:
            ds = None
        self.ui_session.box_list[row_num - 1].radial_ds = ds

        try:
            var_ds = float(row[3].get())
        except ValueError:
            var_ds = None
        self.ui_session.box_list[row_num - 1].radial_var_ds = var_ds

    def get_mesh_r_1(self, show_plot):
        """ include the 4 steps of building a mesh. """
        MeshSegment.DEFAULT_BG_REGION_RATIO = self.ui_session.RADIAL_BG_RATIO
        MeshSegment.DEFAULT_FG_REGION_RATIO = self.ui_session.RADIAL_FG_RATIO
        mesh = Mesh(self.ui_session.lower_bnd_r, self.ui_session.upper_bnd_r, False)
        row_num = 1
        for row in self.radial_table_tb:
            self.read_radial_textbox_row(row, row_num)
            s0 = self.ui_session.box_list[row_num - 1].r0
            s1 = self.ui_session.box_list[row_num - 1].r1
            ds = self.ui_session.box_list[row_num - 1].radial_ds
            var_ds = self.ui_session.box_list[row_num - 1].radial_var_ds
            if s0 is not None and s1 is not None:
                mesh.insert_mesh_segment(MeshSegment(s0, s1, ds=ds, var_ds_ratio=var_ds))
            row_num += 1
        if mesh.is_valid():
            input_mesh = mesh.json_dict()
            adj_mesh = mesh.resolve_mesh_segments().json_dict()
            legacy_mesh = mesh.build_legacy_mesh(max_iterations=250).json_dict()
            mpl.pyplot.close("all")
            create_psi_mesh(adj_mesh, legacy_mesh, 'r', self.mesh_results_folder, output_file_name="tmp_mesh_r.dat",
                            mesh_res_file_name="mesh_res_r.txt", show_plot=show_plot, save_plot=True,
                            save_plot_path=self.mesh_results_folder, plot_file_name="r_mesh_spacing.png",
                            input_mesh=input_mesh)

    def add_ds(self):
        """ check if ds textbox content in theta/phi are valid."""
        i = 0
        for ds_box in self.ds_tab_array:
            try:
                ds_val = float(ds_box.get())
            except ValueError:
                ds_val = None
            self.ui_session.box_list[i].ds = ds_val
            i += 1

        i = 0
        for var_ds_box in self.var_ds_tab_array:
            try:
                var_ds_val = float(var_ds_box.get())
            except ValueError:
                var_ds_val = None
            self.ui_session.box_list[i].tp_var_ds = var_ds_val
            i += 1

    def get_bg_ratio(self):
        """ get the content in step 3 BG_RATIO textbox. (theta+phi)"""
        try:
            bg_ratio = float(self.bg_ratio.get())
        except ValueError:
            return
        self.ui_session.BG_RATIO = float(bg_ratio)

    def get_fg_ratio(self):
        """ get the content in step 3 FG_RATIO textbox. (theta+phi)"""
        try:
            fg_ratio = float(self.fg_ratio.get())
        except ValueError:
            return
        self.ui_session.FG_RATIO = float(fg_ratio)

    def get_radial_bg_ratio(self):
        """ get the content in RADIAL_BG_RATIO textbox. (radial)"""
        try:
            radial_bg_ratio = float(self.radial_bg_ratio.get())
        except ValueError:
            return
        self.ui_session.RADIAL_BG_RATIO = float(radial_bg_ratio)

    def get_radial_fg_ratio(self):
        """ get the content in RADIAL_FG_RATIO textbox. (radial)"""
        try:
            radial_fg_ratio = float(self.radial_fg_ratio.get())
        except ValueError:
            return
        self.ui_session.RADIAL_FG_RATIO = float(radial_fg_ratio)

    def get_radial_rMin(self):
        """ get the content in lower_bnd_r textbox. Radial mesh domain."""
        try:
            rMin = float(self.rMin.get())
        except ValueError:
            return
        self.ui_session.lower_bnd_r = float(rMin)

    def get_radial_rMax(self):
        """ get the content in upper_bnd_r textbox. Radial mesh domain."""
        try:
            rMax = float(self.rMax.get())
        except ValueError:
            return
        self.ui_session.upper_bnd_r = float(rMax)

    def redraw_submit(self):
        """submit the new coordinates of the redrawn box"""
        if self.box_num != 0:
            if len(self.ui_session.box_list) >= self.box_num:
                self.ax.add_patch(self.rect_data)
                rect_position = mpl.patches.Rectangle.get_bbox(self.rect_data)
                label_box = "Box # %s" % self.box_num
                self.ax.text(rect_position.x0, rect_position.y0, label_box)

                self.ui_session.box_list[self.box_num - 1].t0 = min(rect_position.y0, rect_position.y1)
                self.ui_session.box_list[self.box_num - 1].t1 = max(rect_position.y0, rect_position.y1)
                self.ui_session.box_list[self.box_num - 1].p0 = min(rect_position.x0, rect_position.x1)
                self.ui_session.box_list[self.box_num - 1].p1 = max(rect_position.x0, rect_position.x1)

                self.patch_list.insert(self.box_num - 1, self.rect_data)
                self.box_num = 0
                self.redraw_box_submit = False
                self.canvas.draw()
        else:
            print("First click apply button to remove the box from image, then redraw the same box and click submit.")

    def redraw_box_apply(self):
        """ Remove the txt box number and patch of box. """
        if self.redraw_box_submit is False:
            try:
                box_num = self.redraw_drop_box_get_val()
            except ValueError:
                print("Input must be an integer")
                return

            if len(self.ui_session.box_list) < box_num or box_num <= 0:
                print("Index is out of range.")
            else:
                self.box_num = box_num
                i = 0
                while i < len(self.ax.texts):
                    if self.ax.texts[i].get_text() == "Box # " + str(box_num):  # remove txt of box number
                        self.ax.texts[i].remove()
                        break
                    i += 1

                current_box = self.patch_list[int(box_num) - 1]
                current_box.remove()
                self.patch_list.remove(current_box)
                self.redraw_box_submit = True
                self.canvas.draw()
        else:
            print("Please redraw the box and then click submit.")

    def save_latest_box(self):
        """ Save the latest box drawn on the plot and append to ui_session box_list. """
        if self.box_num == 0:
            if self.rect_data == 0:
                print("First draw a rectangle on plot.")
                return
            else:
                self.ax.add_patch(self.rect_data)
                rect_position = mpl.patches.Rectangle.get_bbox(self.rect_data)
                i = (len(self.ui_session.box_list) + 1)
                label_box = "Box # %s" % i
                self.ax.text(rect_position.x0, rect_position.y0, label_box)
                self.ui_session.insert_mesh_box(i - 1, MeshBox(t0=min(rect_position.y0, rect_position.y1),
                                                               t1=max(rect_position.y0, rect_position.y1),
                                                               p0=min(rect_position.x0, rect_position.x1),
                                                               p1=max(rect_position.x0, rect_position.x1)))
                self.patch_list.append(self.rect_data)

                # add a ds text box for step #2
                tk.Label(self.leftFrame, text=label_box, relief=tk.RIDGE, bg='lightgray', bd=2). \
                    grid(row=9 + len(self.ui_session.box_list), column=0, sticky=tk.NSEW)
                self.ds_tab_array.append(tk.Entry(self.leftFrame, width=10, bg='white'))
                self.var_ds_tab_array.append(tk.Entry(self.leftFrame, width=10, bg='white'))
                self.ds_tab_array[-1].insert(tk.END, '')
                self.var_ds_tab_array[-1].insert(tk.END, str(self.ui_session.FG_RATIO))
                self.ds_tab_array[-1].grid(row=9 + len(self.ui_session.box_list), column=1, sticky=tk.NSEW)
                self.var_ds_tab_array[-1].grid(row=9 + len(self.ui_session.box_list), column=2, sticky=tk.NSEW)

                # add a radial textbox
                tk.Label(self.rightFrame, text=label_box, relief=tk.RIDGE, bg='lightgray', bd=2) \
                    .grid(row=10 + len(self.ui_session.box_list), column=0, sticky=tk.NSEW)
                cols = []
                i = len(self.ui_session.box_list) - 1
                for j in range(4):
                    e = tk.Entry(self.rightFrame, width=5, bg='white')
                    if j == 3:
                        e.insert(tk.END, str(self.ui_session.RADIAL_FG_RATIO))
                    else:
                        e.insert(tk.END, "")
                    e.grid(row=10 + len(self.ui_session.box_list), column=j + 1, sticky=tk.NSEW)
                    cols.append(e)
                self.radial_table_tb.append(cols)

                # add option to dropbox in remove and redraw.
                self.update_delete_box_drop_box()
                self.update_redraw_box_drop_box()
                self.canvas.draw()

    def delete_box(self):
        """ Delete a box drawn on canvas. """
        try:
            box_id = int(self.drop_box_delete_box_get_val())  # check if input is valid
        except ValueError:
            print("The dropbox box number is invalid.")
            return

        if self.box_num == 0:
            if len(self.ui_session.box_list) < box_id or box_id <= 0:
                print("Index is out of range.")
            else:
                i = 0
                while i < len(self.ax.texts):
                    if self.ax.texts[i].get_text() == "Box # " + str(box_id):  # remove txt of box number
                        self.ax.texts[i].remove()
                        i += - 1
                    i += 1

                if int(box_id) < len(self.ui_session.box_list):  # adjust all text box numbers and ds boxes
                    idx = 0
                    for box in range(int(box_id) + 1, len(self.ui_session.box_list) + 1):
                        self.ds_tab_array[box - 2].delete(0, tk.END)
                        self.var_ds_tab_array[box - 2].delete(0, tk.END)
                        self.ds_tab_array[box - 2].insert(0, str(self.ds_tab_array[box - 1].get()))
                        self.var_ds_tab_array[box - 2].insert(0, str(self.var_ds_tab_array[box - 1].get()))
                        self.radial_table_tb[box - 2][0].delete(0, tk.END)
                        self.radial_table_tb[box - 2][1].delete(0, tk.END)
                        self.radial_table_tb[box - 2][2].delete(0, tk.END)
                        self.radial_table_tb[box - 2][3].delete(0, tk.END)
                        self.radial_table_tb[box - 2][0].insert(0, str(self.radial_table_tb[box - 1][0].get()))
                        self.radial_table_tb[box - 2][1].insert(0, str(self.radial_table_tb[box - 1][1].get()))
                        self.radial_table_tb[box - 2][2].insert(0, str(self.radial_table_tb[box - 1][2].get()))
                        self.radial_table_tb[box - 2][3].insert(0, str(self.radial_table_tb[box - 1][3].get()))
                        while idx < len(self.ax.texts):
                            if self.ax.texts[idx].get_text() == "Box # " + str(box):
                                self.ax.texts[idx].set_text("Box # " + str(box - 1))
                                break
                            idx += 1

                self.ui_session.box_list = np.delete(self.ui_session.box_list, int(box_id) - 1)
                current_box = self.patch_list[int(box_id) - 1]
                current_box.remove()
                self.patch_list.remove(current_box)

                # delete the lastest ds textbox and label
                tk.Label(self.leftFrame, text="             ").grid(row=10 + len(self.ui_session.box_list),
                                                                    column=0, sticky=tk.NSEW)
                self.ds_tab_array[-1].destroy()
                self.ds_tab_array.pop()
                self.var_ds_tab_array[-1].destroy()
                self.var_ds_tab_array.pop()

                # delete box label in radial table
                tk.Label(self.rightFrame, text="       ", bg='gray92', bd=2) \
                    .grid(row=11 + len(self.ui_session.box_list), column=0, sticky=tk.NSEW)
                for tab in self.radial_table_tb[-1]:
                    tab.destroy()
                self.radial_table_tb.pop()

                # delete the box option from dropbox in remove and redraw mesh.
                self.remove_menu_option_delete_dropbox()
                self.remove_menu_option_redraw_dropbox()
                self.canvas.draw()

    def box_chart(self):
        """ Window to edit the boxes coordinates manually. """
        root = tk.Tk()
        TableChart(root, self.ui_session, self.ax, self.patch_list)
        root.mainloop()

    def update_delete_box_drop_box(self):
        """ update delete box dropbox. """
        if len(self.ui_session.box_list) == 1:
            self.reset_delete_box_drop_box()
        choice = str(len(self.ui_session.box_list))
        self.del_tb_opt['menu'].add_command(label=choice, command=tk._setit(self.del_tb_variable, choice))

    def reset_delete_box_drop_box(self):
        """ reset the dropbox in delete box. """
        self.del_tb_variable.set('')
        self.del_tb_opt['menu'].delete(0, 'end')

    def drop_box_delete_box_get_val(self, *args):
        """ get the dropdown menu selected for delete box. """
        try:
            return int(self.del_tb_variable.get())
        except Exception:
            return 0

    def remove_menu_option_delete_dropbox(self):
        """ remove a box number from dropbox. """
        self.reset_delete_box_drop_box()
        for ii in range(1, len(self.ui_session.box_list) + 1):
            self.del_tb_opt['menu'].add_command(label=str(ii), command=tk._setit(self.del_tb_variable, str(ii)))

    def redraw_drop_box_get_val(self, *args):
        """ get the dropdown menu selected for redraw box. """
        try:
            return int(self.redraw_variable.get())
        except Exception:
            return 0

    def update_redraw_box_drop_box(self):
        """ update redraw box dropbox. """
        if len(self.ui_session.box_list) == 1:
            self.reset_redraw_box_drop_box()
        choice = str(len(self.ui_session.box_list))
        self.redraw_opt['menu'].add_command(label=choice, command=tk._setit(self.redraw_variable, choice))

    def reset_redraw_box_drop_box(self):
        """ reset the dropbox in redraw box. """
        self.redraw_variable.set('')
        self.redraw_opt['menu'].delete(0, 'end')

    def remove_menu_option_redraw_dropbox(self):
        """ once a box is deleted the options of boxes to redraw will change. """
        self.reset_redraw_box_drop_box()
        for ii in range(1, len(self.ui_session.box_list) + 1):
            self.redraw_opt['menu'].add_command(label=str(ii), command=tk._setit(self.redraw_variable, str(ii)))

    @staticmethod
    def set_colorbar(fig, im):
        """ add a colorbar to magnetogram plot. """
        position = fig.add_axes([0.94, 0.1, 0.01, 0.8])
        cb = fig.colorbar(im, cax=position, shrink=1.5, orientation="vertical")
        cb.ax.tick_params(labelsize=7)

    def setup_magnetogram_plot(self, fig, hdf_file_path):
        """ setup the plot in midframe. """
        self.set_axis_limits()

        cmin, im = self.read_hdf_file(hdf_file_path)

        # set a colorbar.
        self.set_colorbar(fig=fig, im=im)

        self.restrict_panning()
        return cmin

    def restrict_panning(self):
        """ restrict panning in x axis beyond limits. """
        RestrictPan(self.ax, x=lambda t: t <= 4 * np.pi)
        RestrictPan(self.ax, x=lambda t: t >= -2 * np.pi)

    def set_axis_limits(self):
        """set the x and y axis limits. """
        # Set the x,y limits and the aspect to equal length (this will flip the theta axis in the plot as desired)
        self.ax.set_xlim(0, np.pi * 2)
        self.ax.set_ylim(np.pi, 0.0)
        self.ax.set_aspect('equal')

    def read_hdf_file(self, hdf_file_path):
        """ read hdf magnetogram file. """
        # read the hdf file u
        hdfdata = plot_hdf(hdf_file_path)
        # Set the color scaling values
        cmin = self.initial_cmin_scale(hdfdata)
        self.im1 = self.plot_hdf_file(cmin, hdfdata)

        return cmin, self.im1

    @staticmethod
    def initial_cmin_scale(hdfdata):
        """ get initial hdf scaling. """
        cmin = np.min(hdfdata[2])
        cmax = np.max(hdfdata[2])

        if abs(cmin) > abs(cmax):
            cmax = cmax / 25
            cmin = -abs(cmax)
        if abs(cmax) > abs(cmin):
            cmin = cmin / 25

        return int(cmin)

    def plot_hdf_file(self, cmin, hdfdata):
        """ plot magnetogram."""
        self.im1 = self.ax.pcolorfast(hdfdata[0], hdfdata[1], hdfdata[2], cmap='RdBu', vmin=cmin, vmax=abs(cmin))
        self.im2 = self.ax.pcolorfast(2 * np.pi * np.ones(len(hdfdata[0])) + hdfdata[0], hdfdata[1], hdfdata[2],
                                      cmap='RdBu', vmin=cmin, vmax=abs(cmin))
        self.im3 = self.ax.pcolorfast(-2 * np.pi * np.ones(len(hdfdata[0])) + hdfdata[0], hdfdata[1], hdfdata[2],
                                      cmap='RdBu', vmin=cmin, vmax=abs(cmin))
        return self.im1

    def apply_new_scale(self):
        """ plot the magnetogram with new scaling. """
        new_value = self.read_new_cmax()
        if new_value == 0:
            print("cmin value is not valid.")
        else:
            self.im1.set_clim(-abs(new_value), abs(new_value))
            self.im2.set_clim(-abs(new_value), abs(new_value))
            self.im3.set_clim(-abs(new_value), abs(new_value))
            self.canvas.draw()

    def read_new_cmax(self):
        """ get the new cmin value from textbox"""
        try:
            return float(self.cmax_value.get())
        except Exception:
            return 0


if __name__ == "__main__":
    # Choose the files to read, point the base_path to where you put the MapPipeline folder

    hdf_file_path1 = "/Users/opalissan/Downloads/MagnetogramExamples/Oct2011/br_example_2011_10_01_raw.hdf"
    hdf_file_path2 = "/Users/opalissan/Desktop/br_caplan_shine_fill_pt.h5"
    # ui dictionary
    my_ui_session = MeshInfo(lower_bnd_t=0, upper_bnd_t=np.pi, lower_bnd_p=0, upper_bnd_p=2 * np.pi,
                             lower_bnd_r=0, upper_bnd_r=2.5)

    app = MeshApp(hdf_file_path=hdf_file_path2, ui_session_data=my_ui_session, UseExistingInput=False,
                  save_mesh_file_path="/Users/opalissan/Desktop/mesh_folder")
