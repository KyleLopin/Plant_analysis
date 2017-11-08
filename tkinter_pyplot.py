""" Module to make a tkinter frame with an embedded pyplot
"""

# standard libraries
import tkinter as tk
# installed libraries
import matplotlib
matplotlib.use("TkAgg")
from matplotlib import pyplot as plt
import matplotlib.animation as animation
from matplotlib.widgets import Cursor
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.backends.backend_tkagg import NavigationToolbar2TkAgg as NavToolbar
import numpy as np
from scipy.optimize import curve_fit

__author__ = 'Kyle Vitautas Lopin'

LEGEND_SPACE_RATIO = 0.9


class PyplotEmbed(tk.Frame):
    """ Class that will make a tkinter frame with a matplotlib plot area embedded in the frame
    """
    def __init__(self, master, data):
        tk.Frame.__init__(self, master=master)
        self.index = 1
        self.lines = []
        self.labels = []
        self.colors = []
        self.vert_line = None
        self.data = data
        self.cursor_connect = None

        self.graph_area = tk.Frame(self)
        self.figure_bed = plt.figure(figsize=(6,4))
        self.axis = self.figure_bed.add_subplot(111)

        self.canvas = FigureCanvasTkAgg(self.figure_bed, master=self)
        self.canvas._tkcanvas.config(highlightthickness=0)
        self.toolbar = NavToolbar(self.canvas, self)  # TODO: check this
        # self.toolbar.pack_forget()
        self.toolbar.pack()

        self.canvas.draw()
        self.canvas.get_tk_widget().pack(side='left', fill=tk.BOTH, expand=1)

    def plot(self, data, _label):
        # self.data.plot(ax=self.graph_area.axis, label='channel {0}'.format(self.index))
        # line = self.axis.plot(data.index, data['voltage'], label=_label)[0]
        line = self.axis.plot(data.index, data, label=_label)[0]
        self.colors.append(line.get_color())
        self.labels.append(_label)
        self.lines.append(line)
        self.axis.legend()
        self.index += 1
        self.canvas.show()

    def delete_all(self):
        while self.lines:
            l = self.lines.pop()
            l.remove()
            del l
        self.canvas.draw()
        self.index = 1
        self.axis.legend()

    def delete_some_data(self, picks):
        print('delete in graph: ', picks)
        for index in reversed(picks):
            self.delete_line(index)

    def delete_line(self, _index):
        self.index -= 1
        del self.labels[_index]
        line = self.lines.pop(_index)
        line.remove()
        del line
        self.update_legend()

    def change_line_color(self, _color, index):
        print('change line:', index, _color)
        self.lines[index].set_color(_color)
        self.colors[index] = _color

    def change_line_style(self, style, index):
        if style != 'solid':
            self.lines[index].set_linestyle(style)
            self.lines[index].set_dashes((1, 5))

    def update_legend(self):
        """ Update the legend and redraw the graph """
        handle, labels = self.axis.get_legend_handles_labels()

        self.axis.legend(handle, self.labels,
                                    loc='best',
                                    # bbox_to_anchor=(1, 0.5),
                                    # title='Data series',
                                    prop={'size': 10},
                                    fancybox=True)  # not adding all this screws it up
        # up for some reason
        self.canvas.show()  # update the canvas where the data is being shown

    def time_shift(self, data_index: int, time_to_shift: float):
        adj_time_shift = time_to_shift - self.data.time_start[data_index]

        x_data = self.data.adjusted_data[data_index].index - adj_time_shift
        self.lines[data_index].set_xdata(x_data)
        self.canvas.draw()

    def get_fit_start(self):
        print('make cursor')
        # cursor = self.axis.axvline(color='r')
        self.cursor_connect = self.canvas.mpl_connect('motion_notify_event', self.onMouseMove)
        self.canvas.mpl_connect('button_press_event', self.onclick)
        self.canvas.show()

    def onMouseMove(self, event):
        if not event.xdata:  # mouse is not over the plot area
            return
        if self.vert_line:
            self.vert_line.remove()
            del self.vert_line
            self.vert_line = None
        self.vert_line = self.axis.axvline(x=event.xdata, color='r', linewidth=2)
        self.canvas.show()

    def onclick(self, event):
        if event.dblclick == 1:
            full_data_set = self.data.adjusted_data[-1]
            start_index = full_data_set.index.get_loc(event.xdata, 'nearest')
            # start_index = pd.Index(self.data.adjusted_data[-1]).get_loc(event.xdata, 'nearest')
            start_num = full_data_set.index[start_index]
            data_to_fit = self.data.adjusted_data[-1][start_num:start_num+20]

            self.fit_data(data_to_fit, start_num)

    def fit_data(self, _data, starting_place):
        print('fitting')
        self.canvas.mpl_disconnect(self.cursor_connect)
        t = _data.index - starting_place # change the time so t=0 at the start of the recording
        amplitude_guess = -_data.voltage.min()
        time_shift = 0
        bounds = (
        0.0, [1.2*amplitude_guess, 1.2*amplitude_guess, 1.2*amplitude_guess, 1.2*amplitude_guess, 0.2, 2, 100, 100])
        initial_guess = (
        2. * amplitude_guess / 3, amplitude_guess / 3., amplitude_guess / 2., amplitude_guess / 2., 0.2, 2, 2, 15)

        fitted_parameters, _ = curve_fit(fitting_func_2a_2i_exp, t, _data.voltage,
                                         p0=initial_guess, bounds=bounds,
                                         ftol=0.0000005, xtol=0.0000005)
        # fitted_parameters, _ = curve_fit(fitting_func_2a_2i_exp, t, _data.voltage, p0=initial_guess)
        print('fitting params: {0}'.format(fitted_parameters))

        # make a new line with the fitted parameters and draw it
        y_fitted = fitting_func_2a_2i_exp(t, *fitted_parameters)
        # plt.plot(t + _data.index, y_fitted, linewidth=2, label="Check")
        fitted_line = self.axis.plot(_data.index,  y_fitted, linewidth=2, label='fitted')[0]

    def toogle_data_decimation(self, data):
        # line: matplotlib.lines.Line2D  # type hint the for loop variable
        for i, line in enumerate(self.lines):
            line.set_xdata(data[i].index.values)
            line.set_ydata(data[i])
        self.canvas.show()


def fitting_func_2a_2i_exp(t, amp1, amp2, amp3, amp4, tau1, tau2, tau3, tau4):
    return amp1*np.exp(-t/tau1) + amp2*np.exp(-t/tau2) - amp3*np.exp(-t/tau3) - amp4*np.exp(-t/tau4)

