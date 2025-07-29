""" This is the first window of the mesh UI. Here the user will upload magnetogram, upload existing json with previous
UI session info. """
import tkinter as tk
import tkinter.filedialog
import os
import json
from mesh_generator.ui.auto_mesh_from_dict import MeshRes
from mesh_generator.ui.tkinter_mainapp import MeshApp
from mesh_generator.ui.mesh_info import MeshInfo
import numpy as np


class MeshGeneratorUI:
    def __init__(self):
        # main window.
        self.root = tk.Tk()
        self.root.wm_title("PSI Mesh Generator")  # title of the window.

        for ii in range(12):
            self.root.grid_columnconfigure(ii, weight=1)  # the text and entry frames column
        for jj in range(12):
            self.root.grid_rowconfigure(jj, weight=1)  # all frames row

        # hdf file path that will be passed to the MainApp, there the magnetogram will be plotted using matplotlib.
        self.hdf_file_path = None
        # json file containing previous session mesh requirements.
        self.json_file_path = None
        # folder where mesh results will be saved:
        self.save_folder_path = None

        # print instructions on window.
        tk.Label(self.root, text="Step 1: Upload Magnetogram 2D hdf/h5 file, input path:").grid(row=0, column=0,
                                                                                                sticky=tk.W,
                                                                                                columnspan=2)

        tk.Label(self.root, text="Step 2: (Optional) Upload a json file constaining previous session mesh "
                                 "requirements, otherwise will start a new UI session. "). \
            grid(row=2, column=0, sticky=tk.W, columnspan=6, rowspan=2)

        tk.Label(self.root, text="Step 3: Provide a folder path where mesh results will be saved. "). \
            grid(row=6, column=0, sticky=tk.W, columnspan=6, rowspan=2)

        tk.Label(self.root, text="Step 4: If json file is provided then you can skip interactive UI main window and "
                                 "directly compute mesh results. "). \
            grid(row=10, column=0, sticky=tk.W, columnspan=6, rowspan=2)

        # create a textbox for user to input hdf file path.
        self.upload_mag_path = tk.Entry(self.root, width=70)
        self.upload_mag_path.insert(tk.END, '')
        self.upload_mag_path.grid(row=1, column=0, columnspan=5, sticky=tk.W)
        tk.Button(self.root, text='browse', command=self.find_path_hdf).grid(row=1, column=4, sticky=tk.W)

        # create a textbox for user to input json file path.
        self.upload_json_path = tk.Entry(self.root, width=70)
        self.upload_json_path.insert(tk.END, '')
        self.upload_json_path.grid(row=5, column=0, columnspan=4, sticky=tk.W)
        tk.Button(self.root, text='browse', command=self.find_path_json).grid(row=5, column=4, sticky=tk.W)

        # create a textbox for user to input dir path where files will be saved.
        self.save_dir = tk.Entry(self.root, width=70)
        self.save_dir.insert(tk.END, '')
        self.save_dir.grid(row=8, column=0, columnspan=4, sticky=tk.W)
        tk.Button(self.root, text='browse', command=self.find_dir).grid(row=8, column=4, sticky=tk.W)

        # skip interactive and open main ui window.
        tk.Button(self.root, text="Generate mesh from json", command=self.skip_interactive). \
            grid(row=12, column=1, sticky=tk.NSEW)
        tk.Button(self.root, text="Mesh UI main window", command=self.main_app_window_activate). \
            grid(row=12, column=2, sticky=tk.NSEW)

        self.root.mainloop()

    def find_path_hdf(self):
        """ hdf file browser function. """
        if self.check_hdf_path_is_valid():
            self.hdf_file_path = tk.filedialog.askopenfilename(parent=self.root, title='Select a File',
                                                               initialdir=os.path.dirname(self.hdf_file_path),
                                                               filetypes=[('hdf file', '.hdf'),
                                                                          ('h5 file', '.h5')])
        else:
            self.hdf_file_path = tk.filedialog.askopenfilename(parent=self.root, title='Select a File',
                                                               initialdir="/",
                                                               filetypes=[('hdf file', '.hdf'),
                                                                          ('h5 file', '.h5')])
        if self.hdf_file_path != "":
            self.upload_mag_path.delete("0", "end")
            self.upload_mag_path.insert(tk.END, self.hdf_file_path)

    def find_path_json(self):
        """ json file browser function. """
        if self.check_json_path_is_valid():
            self.json_file_path = tk.filedialog.askopenfilename(parent=self.root, title='Select a File',
                                                                initialdir=os.path.dirname(self.json_file_path),
                                                                filetypes=[('json file', '.json')])
        else:
            self.json_file_path = tk.filedialog.askopenfilename(parent=self.root, title='Select a File',
                                                                initialdir="/", filetypes=[('json file', '.json')])
        if self.json_file_path != "":
            self.upload_json_path.delete("0", "end")
            self.upload_json_path.insert(tk.END, self.json_file_path)

    def find_dir(self):
        """ json file browser function. """
        if self.check_save_dir_path_is_valid():
            self.save_folder_path = tk.filedialog.askdirectory(parent=self.root, title='Select a Folder',
                                                               initialdir=self.save_folder_path)
        else:
            self.save_folder_path = tk.filedialog.askdirectory(parent=self.root, title='Select a Folder',
                                                               initialdir="/")

        if self.save_folder_path != "":
            self.save_dir.delete("0", "end")
            self.save_dir.insert(tk.END, self.save_folder_path)

    def get_save_dir_path(self):
        """ return the latest save dir path. """
        self.save_folder_path = self.save_dir.get()

    def get_hdf_path(self):
        """ return the latest hdf file path. """
        self.hdf_file_path = self.upload_mag_path.get()

    def get_json_path(self):
        """ return the latest json file path. """
        self.json_file_path = self.upload_json_path.get()

    def check_hdf_path_is_valid(self):
        """ check if user hdf path input is valid."""
        try:
            self.get_hdf_path()
            return os.path.exists(path=self.hdf_file_path)
        except:
            return False

    def check_json_path_is_valid(self):
        """ check if user json path input is valid."""
        try:
            self.get_json_path()
            return os.path.exists(path=self.json_file_path)
        except:
            return False

    def check_save_dir_path_is_valid(self):
        """ check if user save dir path input is valid."""
        try:
            self.get_save_dir_path()
            return os.path.exists(path=self.save_folder_path)
        except:
            try:
                print("Save folder path is not a current directory, hence creating this folder.")
                os.makedirs(path=self.save_folder_path, exist_ok=True)
                return True
            except:
                return False

    def skip_interactive(self):
        """ skip interative button function,
        this will call a save in directory window and will do all the calculation in the backend.
        """
        # make sure the json file provided is valid
        if self.check_json_path_is_valid() is False:
            print("The json file path provided is invalid. Use the browser button to find the exact location of the "
                  "previous session json file.")
            return 0

        # make sure the json file provided is valid
        if self.check_save_dir_path_is_valid() is False:
            print("The save folder path provided is invalid. Use the browser button to find the exact location of the "
                  "folder where mesh results will be saved.")
            return 0

        elif self.check_json_path_is_valid() and self.check_save_dir_path_is_valid():
            # calculate the mesh given the requirements in the json file.

            MeshRes(save_mesh_dir=self.save_folder_path, json_file_path=self.json_file_path)
            print("Mesh files are written successfully.")

    def main_app_window_activate(self):
        """ activate the main app window. """
        if self.check_hdf_path_is_valid():
            if self.check_save_dir_path_is_valid():
                if self.check_json_path_is_valid():
                    self.open_main_window_with_existing_req()
                else:
                    self.open_main_window_without_existing_req()
            else:
                print("save folder path is not valid. Please re-enter the folder path.",
                      self.save_folder_path)
        else:
            print("hdf file is not valid. Please re-enter the hdf file path.",
                  self.hdf_file_path)

    def open_main_window_with_existing_req(self):
        """ if hdf file and json file are valid then open the main window with existing mesh requirements. """
        with open(self.json_file_path, 'r') as data:
            ui_dict = json.load(data)
            MeshApp(hdf_file_path=self.hdf_file_path, save_mesh_file_path=self.save_folder_path,
                    ui_session_data=ui_dict, UseExistingInput=True)

    def open_main_window_without_existing_req(self):
        """Generate the GUI without any previous mesh requirements. """
        my_ui_session = MeshInfo(lower_bnd_t=0, upper_bnd_t=np.pi, lower_bnd_p=0, upper_bnd_p=2 * np.pi,
                                 lower_bnd_r=1.0, upper_bnd_r=2.5)
        MeshApp(hdf_file_path=self.hdf_file_path, save_mesh_file_path=self.save_folder_path,
                ui_session_data=my_ui_session, UseExistingInput=False)


if __name__ == "__main__":
    MeshGeneratorUI()
