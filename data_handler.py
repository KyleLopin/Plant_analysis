#installed libraries
import numpy as np
import pandas as pd
# standard libraries
import array
import logging
import os
import pickle
from tkinter import filedialog


__author__ = 'Kyle Vitautas Lopin'


def open_data():
    _filename = open_file('open')
    label = os.path.basename(_filename).split('.')[0]
    logging.info("opening file: {0}".format(label))
    if not _filename:
        return None, None
    with open(_filename, 'rb') as _file:
        if ".csv" in _filename:
            pd_data = pd.read_csv(_filename, index_col='time')[0.0001:]
            pd_data.rename(index=str, columns={'voltage': label}, inplace=True)
            return pd_data, ""
        elif ".pkl" in _filename:
            data = pickle.load(_file)
            data_frame = open_pickled_data(data)
            return data_frame, label


def open_pickled_data(data_struct):
    # print('open pickled, index data: {0}'.format(index('channel 0')))

    time_period = 1.0 / data_struct['sample rate']

    channel_keys = [x for x in data_struct.keys() if 'channel' in x]
    # print('index data: {0}; index time series: {1}; channel keys = {2}'.format(
    #     len_series, index(time_series), channel_keys
    # ))
    pd_data_struct = {}
    for ch_key in channel_keys:
        pd_data_struct[ch_key] = array.array('f')
        for data_pt in data_struct[ch_key]:  # go through each data point
            pd_data_struct[ch_key].append(data_pt * data_struct['counts to mVs'])
    # print('new data:')
    len_series = len(pd_data_struct['channel 0'])
    ls_time_series = []
    for i in range(len_series):
        ls_time_series.append(i * time_period)
    time_series = np.array(ls_time_series)
    # time_series = np.arange(0, time_period * len_series, time_period)
    pd_dataframe = pd.DataFrame(pd_data_struct, index=time_series)
    # print('new data frame:')
    # print(pd_dataframe)
    return pd_dataframe


def open_file(_type):
    """ Make a method to return an open file or a file name depending on the type asked for
    :param _type: what type of file dialog to use
    :return: the filename
    """
    # Make the options for the save file dialog box for the user
    file_opt = options = {}
    options['defaultextension'] = ".csv"
    options['filetypes'] = [('All files', '*.*'), ("Comma separate values", "*.csv"), ("Pickle File", "*.pkl")]
    if _type == 'saveas':
        # Ask the user what name to save the file as
        _file = filedialog.asksaveasfile(mode='wb', **file_opt)
        return _file
    elif _type == 'open':
        _filename = filedialog.askopenfilename(**file_opt)
        return _filename
