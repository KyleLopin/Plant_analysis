""" Graphical User Interface to analyze plant electrophysiological data
"""
# TODO: encapsulation is horrible

# standard libraries
import array
import logging
import pickle
import os
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
import sys
#installed libraries
print('1')
import numpy as np
print('2')
import pandas as pd
print('3')

#local files
import analysis_functions as funcs
import option_menu_gui as option_menu
print('4')
import pyplot_data
print('5')
import tkinter_pyplot
print('6')

__author__ = 'Kyle Vitautas Lopin'


PROGRAM_NAME = "Data Analysis"

logging.basicConfig(level=logging.DEBUG,
                    format="%(levelname)s %(module)s %(lineno)d: %(message)s")

class PlantAnalysisGUI(tk.Tk):

    def __init__(self, parent=None):
        tk.Tk.__init__(self, parent)
        self.last_dir = None
        self.display_type = 'decimated'
        self.data = pyplot_data.PyplotData_v2()  # make a list of panda data frames
        # make menu bar
        option_menu.OptionMenu(self)

        # make frame to hold buttons to manipulate the data in
        self.top_frame = tk.Frame(self, height=35)
        self.top_frame.pack(side='top', fill=tk.X)
        self.make_buttons(self.top_frame)

        #make a second frame to hold buttont to manipulate data
        print('1')
        self.manip_frame = tk.Frame(self, height=35)
        self.manip_frame.pack(side='top', fill=tk.X)
        self.make_manip_buttons(self.manip_frame)

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
        ttk.Button(_frame, text='Delete all', command=self.delete_data).pack(side='left')

        ttk.Button(_frame, text='Fit Data', command=self.fit_data).pack(side='left')

    def make_manip_buttons(self, frame):
        ttk.Button(frame, text='Current test', command=self.show_currents).pack(side='left')
        self.display_type_button = ttk.Button(frame, text='Regular Data View', command=self.toggle_display_type)
        self.display_type_button.pack(side='left')

    def toggle_display_type(self):
        print('setting display tupe')
        if self.display_type == 'heavy':  # button should be pressed already
            print('ll')
            self.display_type_button.config(text='Regular Data View')
            self.display_type = 'decimated'
        elif self.display_type == 'decimated':
            print('hh')
            self.display_type_button.config(text = 'Quick Data View')
            self.display_type = 'heavy'
        else:
            raise Exception

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
        data, label = self.open_data()
        self.data.append(data, label)
        num_new_lines_to_add = data.shape[1]
        for i in range(1, num_new_lines_to_add+1):
            # print('last label: ', self.last_label)
            if self.display_type == 'decimated':
                self.data_area.plot(self.data.decimated_data[-i], data.keys()[-i]+" "+self.last_label)
            elif self.display_type == 'heavy':
                self.data_area.plot(self.data.heavy_decimate_data[-i], data.keys()[-i] + " " + self.last_label)
            self.make_data_summary_frame(self.data, i-1)

    def make_data_analysis_frame(self, tk_frame):
        pass

    def make_data_summary_frame(self, data: pyplot_data.PyplotData_v2, _index: int):
        new_frame = tk.Frame(self.bottom_frame, height=25)
        new_frame.pack(side='top', fill=tk.X)
        tk.Label(new_frame, text="baseline = {0:.2f}      maximum amplitude = {1:.2f}"
                 .format(data.baselines[- _index], data.average_max[- _index])).pack(side='left')

        # make a spinbox to let the user move the time series around
        time_shifter = tk.DoubleVar()
        print("time shifter: ", data.time_start[-1])
        time_shifter.set(data.time_start[_index])
        # time_shifter.trace('w', lambda: self.data_area.time_shift(index-2, time_shifter.get()))
        index = self.data_area.index - _index - 1
        tk.Spinbox(new_frame, textvariable=time_shifter,
                   from_=-100, to=100, increment=0.01,
                   # index - 2 because the numbers start from 1 not 0 and it has been incremented already
                   command=lambda: self.data_area.time_shift(index-2, time_shifter.get())
                    ).pack(side='left')

        self.data_info_frames.append(new_frame)

    def open_data(self):
        _filename = open_file('open', self.last_dir)
        # _filename = '/Users/Prattana_Nut/Documents/DATA2017/170410/A170410_002.csv'
        self.last_dir = os.path.dirname(_filename)
        label = os.path.basename(_filename).split('.')[0]
        self.last_label = label
        # print('filename: ', _filename)
        logging.info("opening file: {0}".format(label))
        if _filename:
            # remember last directory
            with open(_filename, 'rb') as _file:

                if ".csv" in _filename:
                    pd_data = pd.read_csv(_filename, index_col='time')[0.0001:]
                    pd_data.rename(index=str, columns={'voltage': label}, inplace=True)
                    return pd_data, ""
                elif ".pkl" in _filename:
                    data = pickle.load(_file)
                    return self.open_pickled_data(data), label

    def open_pickled_data(self, data_struct):
        # print('open pickled, len data: {0}'.format(len('channel 0')))

        time_period = 1.0 / data_struct['sample rate']

        channel_keys = [x for x in data_struct.keys() if 'channel' in x]
        # print('len data: {0}; len time series: {1}; channel keys = {2}'.format(
        #     len_series, len(time_series), channel_keys
        # ))
        pd_data_struct = {}
        for ch_key in channel_keys:
            pd_data_struct[ch_key] = array.array('f')
            for data_pt in data_struct[ch_key]:  # go through each data point
                pd_data_struct[ch_key].append(data_pt*data_struct['counts to mVs'])
        # print('new data:')
        len_series = len(pd_data_struct['channel 0'])
        ls_time_series = []
        for i in range(len_series):
            ls_time_series.append(i*time_period)
        time_series = np.array(ls_time_series)
        # time_series = np.arange(0, time_period * len_series, time_period)
        pd_dataframe = pd.DataFrame(pd_data_struct, index=time_series)
        # print('new data frame:')
        # print(pd_dataframe)
        return pd_dataframe


def open_file(_type, last_dir=None):
    """ Make a method to return an open file or a file name depending on the type asked for
    :param _type: what type of file dialog to use
    :return: the filename
    """
    # Make the options for the save file dialog box for the user
    file_opt = options = {}
    options['defaultextension'] = ".csv"
    if last_dir:
        options['initialdir'] = last_dir
    options['filetypes'] = [('All files', '*.*'), ("Comma separate values", "*.csv"), ("Pickle File", "*.pkl")]
    if _type == 'saveas':
        # Ask the user what name to save the file as
        _file = filedialog.asksaveasfile(mode='wb', **file_opt)
    elif _type == 'open':
        _filename = filedialog.askopenfilename(**file_opt)
        return _filename
    return _file


if __name__ == '__main__':
    root = PlantAnalysisGUI()
    root.title(PROGRAM_NAME)
    root.mainloop()
