"""
Matplotlib tkinter example modified to plot a magnetogram with pcolorfast.

see https://matplotlib.org/gallery/user_interfaces/embedding_in_tk_sgskip.html

and https://matplotlib.org/api/_as_gen/matplotlib.axes.Axes.pcolorfast.html

NOTE:
    - This worked great (fast) on my computer with MPL 3.2.1, python 3.7.6, and tk 8.6.8 from conda.
    - BUT it worked way SLOWER on the same machine with MPL 3.2.1, python 3.8.2, and tk 8.6.10 from conda.
    - I have no idea why, but this suggests that something isn't robust and versions might be important... DOH!
"""
import tkinter

from matplotlib.backends.backend_tkagg import (
    FigureCanvasTkAgg, NavigationToolbar2Tk)
# Implement the default Matplotlib key bindings.
from matplotlib.backend_bases import key_press_handler
from matplotlib.figure import Figure

import numpy as np

root = tkinter.Tk()
root.wm_title("Embedding in Tk")

# -----------------------------------------------------------------------------
# Begin Custom Changes
# -----------------------------------------------------------------------------
from mesh_generator.ui.psihdf import rdhdf_2d

# Choose the files to read, point the base_path to where you put the MapPipeline folder
pipeline_example_folder = '/Users/opalissan/Downloads/MagnetogramExamples'
base_path = pipeline_example_folder + '/Oct2011'

# You can really tell a speed difference loading in a giant hdf file or not
UseBigHdf = True

# This one is 2451 x 1130.
if UseBigHdf:
    hdf_file_path = base_path + '/br_example_2011_10_01_raw.hdf'
    plot_b_width = 100.

# This one is 511 x 376.
else:
    hdf_file_path = base_path + '/br_input_fb_diffused.hdf'
    plot_b_width = 20.

p, t, br_pt = rdhdf_2d(hdf_file_path)

# NOTE: pcolorfast and pcolormesh want the coords of pixel corners not centers --> build a "half mesh" for p & t.
# - This means making an array that is n+1 size and has the midpoint positions of the original.
# - I choose to clip the endpoints of the half mesh to the original bounds, vs extrapolate.
# - see also https://matplotlib.org/api/_as_gen/matplotlib.pyplot.pcolormesh.html .
ph = np.concatenate([[p[0]], 0.5*(p[1:] + p[:-1]), [p[-1]]])
th = np.concatenate([[t[0]], 0.5*(t[1:] + t[:-1]), [t[-1]]])

# Make the canvas decently large.
fig = Figure(figsize=(10, 5), dpi=100)

# Put the plot somewhere arbitrary on the canvas.
rect = [0.1, 0.1, 0.8, 0.8]
ax = fig.add_axes(rect)

# Set the x,y limits and the aspect to equal length (this will flip the theta axis in the plot as desired)
ax.set_xlim(0, np.pi*2)
ax.set_ylim(np.pi, 0.0)
ax.set_aspect('equal')

# Set the color scaling values
cmin = -plot_b_width
cmax = plot_b_width
cmap = 'RdBu'

# Compare pcolorfast vs. pcolormesh (use comments)
pcolor_object = ax.pcolorfast(ph, th, br_pt, cmap=cmap, vmin=cmin, vmax=cmax)


# Optional colorbar
fig.colorbar(pcolor_object, ax=ax)

# -----------------------------------------------------------------------------
# End Custom Changes
# -----------------------------------------------------------------------------

canvas = FigureCanvasTkAgg(fig, master=root)  # A tk.DrawingArea.
canvas.draw()

toolbar = NavigationToolbar2Tk(canvas, root)
toolbar.update()


def on_key_press(event):
    print("you pressed {}".format(event.key))
    key_press_handler(event, canvas, toolbar)


canvas.mpl_connect("key_press_event", on_key_press)

button = tkinter.Button(master=root, text="Quit", command=root.quit)

# Packing order is important. Widgets are processed sequentially and if there
# is no space left, because the window is too small, they are not displayed.
# The canvas is rather flexible in its size, so we pack it last which makes
# sure the UI controls are displayed as long as possible.
button.pack(side=tkinter.BOTTOM)
canvas.get_tk_widget().pack(side=tkinter.TOP, fill=tkinter.BOTH, expand=1)

tkinter.mainloop()