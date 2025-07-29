"""
Restrict panning matplotlib plot only right and left (disable panning up and down).
"""

import matplotlib as mpl


class My_Axes(mpl.axes.Axes):
    name = "My_Axes"

    def drag_pan(self, button, key, x, y):
        mpl.axes.Axes.drag_pan(self, button, 'x', x, y)  # pretend key=='x'
