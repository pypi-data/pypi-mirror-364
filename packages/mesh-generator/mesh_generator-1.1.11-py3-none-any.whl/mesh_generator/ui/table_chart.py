""" sub window for tkinter_mainapp.py to adjust the theta and phi mesh segment coordinates manually. """
import tkinter as tk
import numpy as np
import matplotlib as mpl
from mesh_generator.ui.scroll_bar import VerticalScrolledFrame


class TableChart:
    """
    Table chart of mesh_box 3d coordinates. This table can be changed manually from tkinter_mainapp.py.
    The change of coordinates will also show in the matplotlib rectangle patches.
    """

    def __init__(self, root, ui_session, ax, patch_list):
        self.root = root
        self.ui_session = ui_session
        self.ax = ax
        self.patch_list = patch_list

        self.root.geometry("650x250")  # size of tkinter window.
        self.root.minsize(width=620, height=250)  # minimum size of tkinter window.
        self.root.config(background="light gray")
        self.root.wm_title("Box Chart")
        self.text_box_list = []
        self.mainFrame = VerticalScrolledFrame(self.root, width=550, height=200, borderwidth=2, relief=tk.SUNKEN,
                                               background="gray")
        self.mainFrame.pack(fill=tk.BOTH)
        tk.Button(self.root, text='Apply Changes', highlightbackground='gray', activeforeground='navy',
                  command=self.try_submit_changes).pack(side=tk.BOTTOM)

        # BOX TABLE
        self.box_table()

    def box_table(self):
        tk.Label(self.mainFrame, text='t0', relief=tk.RIDGE, bg='lightgray', bd=2, width=12).grid(row=1, column=1,
                                                                                                  sticky=tk.NSEW,
                                                                                                  columnspan=1)
        tk.Label(self.mainFrame, text='t1', relief=tk.RIDGE, bg='lightgray', bd=2, width=12).grid(row=1, column=2,
                                                                                                  sticky=tk.NSEW,
                                                                                                  columnspan=1)
        tk.Label(self.mainFrame, text='p0', relief=tk.RIDGE, bg='lightgray', bd=2, width=12).grid(row=1, column=3,
                                                                                                  sticky=tk.NSEW,
                                                                                                  columnspan=1)
        tk.Label(self.mainFrame, text='p1', relief=tk.RIDGE, bg='lightgray', bd=2, width=12).grid(row=1, column=4,
                                                                                                  sticky=tk.NSEW,
                                                                                                  columnspan=1)

        for i in range(1, len(self.ui_session.box_list) + 1):
            label = "Box # " + str(i)
            tk.Label(self.mainFrame, text=label, relief=tk.RIDGE, bg='lightgray', bd=2, width=12).grid(row=i + 1,
                                                                                                       column=0,
                                                                                                       sticky=tk.NSEW)
            rect = self.ui_session.box_list[i - 1]
            cols = []
            for j in range(4):
                e = tk.Entry(self.mainFrame, width=12)
                if j == 0 and rect.t0 is not None:
                    e.insert(tk.END, str(rect.t0))
                elif j == 1 and rect.t1 is not None:
                    e.insert(tk.END, str(rect.t1))
                elif j == 2 and rect.p0 is not None:
                    e.insert(tk.END, str(rect.p0))
                elif j == 3 and rect.p1 is not None:
                    e.insert(tk.END, str(rect.p1))
                else:
                    e.insert(tk.END, '')
                e.grid(row=i + 1, column=j + 1, sticky=tk.NSEW)
                cols.append(e)
            self.text_box_list.append(cols)

    def get_entry(self, row, row_num):
        try:
            t0 = float(row[0].get())
        except ValueError:
            t0 = None
            print("Error: t0 is not a number.")

        try:
            t1 = float(row[1].get())
        except ValueError:
            t1 = None
            print("Error: t1 is not a number.")

        try:
            p0 = float(row[2].get())
        except ValueError:
            p0 = None
            print("Error: p0 is not a number.")

        try:
            p1 = float(row[3].get())
        except ValueError:
            p1 = None
            print("Error: p1 is not a number.")

        self.check_valid(t0, t1, row_num, 't')
        self.check_valid(p0, p1, row_num, 'p')

    def check_valid(self, s0, s1, row_num, mesh_type: str):
        if s0 is not None and s1 is not None:
            if s0 < s1:
                if mesh_type == 't' and 0 <= s0 <= np.pi and 0 <= s1 <= np.pi:
                    self.ui_session.box_list[row_num - 1].t0 = s0
                    self.ui_session.box_list[row_num - 1].t1 = s1
                if mesh_type == 'p' and -2 * np.pi <= s0 <= 4 * np.pi and -2 * np.pi <= s0 <= 4 * np.pi:
                    self.ui_session.box_list[row_num - 1].p0 = s0
                    self.ui_session.box_list[row_num - 1].p1 = s1
            else:
                print("s0 needs to be less than s1.")

        if s0 is None and s1 is not None:
            if mesh_type == 't':
                if self.ui_session.box_list[row_num - 1].t0 < s1 and 0 <= s1 <= np.pi:
                    self.ui_session.box_list[row_num - 1].t1 = s1
                else:
                    print("t0 needs to be less than t1.")
            if mesh_type == 'p':
                if self.ui_session.box_list[row_num - 1].p0 < s1 and -2 * np.pi <= s1 <= 4 * np.pi:
                    self.ui_session.box_list[row_num - 1].p1 = s1
                else:
                    print("p0 needs to be less than p1.")

        if s0 is not None and s1 is None:
            if mesh_type == 't':
                if self.ui_session.box_list[row_num - 1].t1 > s0 and 0 <= s0 <= np.pi:
                    self.ui_session.box_list[row_num - 1].t0 = s0
                else:
                    print("t0 needs to be less than t1.")
            if mesh_type == 'p':
                if self.ui_session.box_list[row_num - 1].p1 > s0 and -2 * np.pi <= s0 <= 4 * np.pi:
                    self.ui_session.box_list[row_num - 1].p0 = s0
                else:
                    print("p0 needs to be less than p1.")

    def try_submit_changes(self):
        try:
            self.submit_changes()
        except:
            print("Failed to submit changes. ")

    def submit_changes(self):
        row_num = 1
        for row in self.text_box_list:
            self.get_entry(row, row_num)
            row_num += 1

        # remove rectangles from plot
        for box in self.patch_list:
            box.remove()
        self.patch_list.clear()

        # delete all text on plot
        self.ax.texts.clear()

        # # draw new boxes on the image
        ii = 1
        for rect in self.ui_session.box_list:
            rect_patch = mpl.patches.Rectangle((min(rect.p0, rect.p1), min(rect.t0, rect.t1)),
                                               np.abs(rect.p0 - rect.p1),
                                               np.abs(rect.t0 - rect.t1), fill=False)
            label_box = "Box # %s" % ii
            self.ax.text(rect.p0, rect.t0, label_box)
            self.ax.add_patch(rect_patch)
            self.patch_list.append(rect_patch)
            ii += 1

        # close the window
        self.root.destroy()
