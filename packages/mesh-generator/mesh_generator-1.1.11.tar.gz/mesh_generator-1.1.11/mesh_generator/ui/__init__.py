""" UI Mesh python modules.
The MainWindow module: tkinter_main_app.py
The FirstWindow: upload_magnetogram.py

To start the Main UI:

from mesh_generator.ui.upload_magnetogram import MeshGeneratorUI

MeshGeneratorUI() # then call the UI first window.
"""

from mesh_generator.ui.upload_magnetogram import MeshGeneratorUI
from mesh_generator.ui.tkinter_mainapp import MeshApp
from mesh_generator.ui.auto_mesh_from_dict import MeshRes