""" Graphical User Interface to analyze plant electrophysiological data
"""
# TODO: encapsulation is horrible

# standard libraries
import logging
import tkinter as tk
from tkinter import ttk

# installed libraries

# local files
import analysis_functions as funcs
import change_top
import data_handler as dh
import option_menu_gui as option_menu
import pyplot_data
import tkinter_pyplot


__author__ = 'Kyle Vitautas Lopin'


PROGRAM_NAME = "Data Analysis"

logging.basicConfig(level=logging.DEBUG,
                    format="%(levelname)s %(module)s %(lineno)d: %(message)s")
COLORS = ['firebrick', 'darkgreen', 'navy', 'red', 'green', 'blue', 'lightsalmon', 'lightgreen', 'cornflowerblue']

class PlantAnalysisGUI(tk.Tk):

    def __init__(self, parent=None):
        tk.Tk.__init__(self, parent)
        self.color_index = 0
        self.last_dir = None
        self.display_type = 'decimated'
        self.data = pyplot_data.PyplotData_v2()  # make a list of panda data frames
        # make menu bar
        option_menu.OptionMenu(self)

        # make frame to hold buttons to manipulate the data in
        self.top_frame = tk.Frame(self, height=35)
        self.top_frame.pack(side='top', fill=tk.X)
        self.make_buttons(self.top_frame)

        # make a second frame to hold button to manipulate data
        print('1')
        self.manipulation_frame = tk.Frame(self, height=35)
        self.manipulation_frame.pack(side='top', fill=tk.X)
        self.make_manipulate_buttons(self.manipulation_frame)

        # make graph area to plot later
        self.data_area = tkinter_pyplot.PyplotEmbed(self, self.data)
        self.data_area.pack(side='top', expand=True, fill=tk.BOTH)

        # make frame to show data statistics on the bottom
        print('2')
        self.bottom_frame = tk.Frame(self)
        self.bottom_frame.pack(side='top', fill=tk.X)
        self.data_info_frames = []
        self.data_summary_frames = []

    def make_buttons(self, _frame):
        ttk.Button(_frame, text='Open', command=self.open_and_display_data).pack(side='left')
        ttk.Button(_frame, text='Delete All', command=self.delete_data).pack(side='left')
        ttk.Button(_frame, text='Delete Some Data',
                   command=lambda: change_top.UserDeleteSomeData(self)).pack(side='left')
        ttk.Button(_frame, text='Fit Data', command=self.fit_data).pack(side='left')

    def make_manipulate_buttons(self, frame):
        ttk.Button(frame, text='Current test', command=self.show_currents).pack(side='left')
        self.display_type_button = ttk.Button(frame, text='Regular Data View', command=self.toggle_display_type)
        self.display_type_button.pack(side='left')
        ttk.Button(frame, text='Change Line Style',
                   command=lambda: change_top.ChangeDataLegend(self)).pack(side='left')
        self.norm_button = ttk.Button(frame, text="Shifting turned On", command=self.toggle_data_normalized)
        self.norm_button.pack(side='left')

    def toggle_display_type(self):
        print('setting display tupe')
        if self.display_type == 'heavy':  # button should be pressed already
            print('ll')
            self.display_type_button.config(text='Regular Data View')
            self.display_type = 'decimated'
            self.data_area.toogle_data_decimation(self.data.decimated_data)
        elif self.display_type == 'decimated':
            print('hh')
            self.display_type_button.config(text='Quick Data View')
            self.display_type = 'heavy'
            self.data_area.toogle_data_decimation(self.data.heavy_decimate_data)
        else:
            raise Exception

    def toggle_data_normalized(self):
        if self.data.normed:
            self.data.normed = False
            self.norm_button.config(text="Shifting turned Off")
        else:
            self.data.normed = True
            self.norm_button.config(text="Shifting turned On")

    def show_currents(self):
        pass

    def fit_data(self):
        print('fit data')
        if not self.data.adjusted_data:
            print('no data')
            return
        self.data_area.get_fit_start()

    def delete_data(self):
        self.data = pyplot_data.PyplotData_v2()
        self.data_area.delete_all()
        # delete all the frames
        for _frame in self.data_info_frames:
            _frame.pack_forget()
            _frame.destroy()

    def open_and_display_data(self):
        data, label = dh.open_data()
        self.data.append(data, label)
        num_new_lines_to_add = data.shape[1]
        for i in range(1, num_new_lines_to_add+1):
            if self.display_type == 'decimated':
                self.data_area.plot(self.data.decimated_data[-i], data.keys()[-i]+" "+label,
                                    color=COLORS[self.color_index])
            elif self.display_type == 'heavy':
                self.data_area.plot(self.data.heavy_decimate_data[-i], data.keys()[-i] + " " + label,
                                    color=COLORS[self.color_index])
            self.make_data_summary_frame(self.data, -i, data.keys()[-i]+" "+label)
            self.color_index = (self.color_index + 1) % 9

    def make_data_analysis_frame(self, tk_frame):
        pass

    def make_data_summary_frame(self, data: pyplot_data.PyplotData_v2, _index: int, label: str):
        print('make summery frame index: ', _index)
        print('maxes: ', data.average_max)
        new_frame = tk.Frame(self.bottom_frame, height=25)
        new_frame.pack(side='top', fill=tk.X)
        tk.Label(new_frame, text="baseline = {0:.2f}      maximum amplitude = {1:.2f}"
                 .format(data.baselines[_index], data.average_max[_index])).pack(side='left')

        # make a spinbox to let the user move the time series around
        time_shifter = tk.DoubleVar()
        print("time shifter: ", data.time_start[-1])
        time_shifter.set(data.time_start[_index])
        # time_shifter.trace('w', lambda: self.data_area.time_shift(index-2, time_shifter.get()))
        index = self.data_area.index - _index - 1
        tk.Spinbox(new_frame, textvariable=time_shifter,
                   from_=-100, to=100, increment=0.01,
                   # index - 2 because the numbers start from 1 not 0 and it has been incremented already
                   command=lambda: self.data_area.time_shift(index, time_shifter.get())
                    ).pack(side='left')
        tk.Label(new_frame, text=label).pack(side='left')
        self.data_info_frames.append(new_frame)

    def delete_some_data(self, picks):
        for index in reversed(picks):
            # del self.data_info_frames[index]
            self.data_info_frames[index].pack_forget()
            self.data_info_frames[index].destroy()
        # self.update()


if __name__ == '__main__':
    root = PlantAnalysisGUI()
    root.title(PROGRAM_NAME)
    root.mainloop()
