""" sub window to save the ui session with the 3d mesh requirements in a txt/json file. """
import tkinter as tk
from mesh_generator.ui.mesh_info import MeshInfo


class SaveDict:
    """
    Window for tk.tkinter_mainapp.py to save the ui_session dictionary in a txt or json file, which can later be
    uploaded again to the UI.
    """

    def __init__(self, master, ui_session, save_json_folder):
        self.ui_session = ui_session
        self.save_json_folder = save_json_folder

        self.master = master
        w = 800  # width for the Tk root
        h = 100  # height for the Tk root

        # get screen width and height
        ws = self.master.winfo_screenwidth()  # width of the screen
        hs = self.master.winfo_screenheight()  # height of the screen

        # calculate x and y coordinates for the Tk root window
        x = (ws / 2) - (w / 2)
        y = (hs / 2) - (h / 2)

        # set the dimensions of the screen
        # and where it is placed
        self.master.geometry('%dx%d+%d+%d' % (w, h, x, y))

        tk.Label(self.master, text="File path:").grid(row=0)
        self.master.title("Input json file path")
        self.e1 = tk.Entry(self.master, width=70)
        self.e1.insert(tk.END, str(self.save_json_folder) + "/mesh_requirements.json")
        self.e1.grid(row=0, column=1)

        tk.Button(self.master, text='Save', command=self.save_dict).grid(row=3, column=1, sticky=tk.W, pady=4)

    @staticmethod
    def save_session(ui_session, file_name):
        with open(file_name, 'w') as output:
            output.write(ui_session.__str__())

    def save_dict(self):
        file_name = self.e1.get()
        self.save_session(self.ui_session, file_name)
        self.master.destroy()


if __name__ == "__main__":
    import numpy as np

    my_ui_session = MeshInfo(lower_bnd_t=0, upper_bnd_t=np.pi, lower_bnd_p=0, upper_bnd_p=2 * np.pi,
                             lower_bnd_r=0, upper_bnd_r=2.5)

    root = tk.Tk()
    my_gui = SaveDict(root, my_ui_session, save_json_folder="/")
    root.mainloop()
