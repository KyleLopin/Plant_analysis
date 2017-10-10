""" Data class to hold and manipulate data
"""

# standard libraries
import csv
import logging
# installed libraries
import numpy as np
import pandas as pd
import scipy.signal
# import local files
import analysis_functions as funcs

__author__ = 'Kyle Vitautas Lopin'

START_THRESHOLD_RATIO = 0.1


class PyplotData_v2(object):
    def __init__(self):
        self.adjusted_data = []  # panda data frames with the baseline voltage subtracted
        self.decimated_data = []
        self.heavy_decimate_data = []
        self.baselines = []  # save what the baseline of the recordings are
        self.average_max = []  # save the max amplitude of the trace
        self.time_start = []  # save when the action potential starts
        self.normed = False
        self.len = 0

    def append(self, data, label):
        data.index = data.index.map(float)
        for i, data_key in enumerate(data):  # hackish
            if i == 0:
                self._append_single_series(data, data_key)
            else:
                self._append_single_series(data, data_key, time_shift=self.time_start[-1])

        # data.index = data.index.map(float)
        # print('data in append: {0}'.format(data))
        # baseline = funcs.calculate_baseline(data)
        # print('bzselines: ', baseline)
        # for data_series in data:
        #     print('data_series:  {0}'.format(data_series))
        #     self._append_single_series(data[data_series])
        # self.baselines.append(baseline)
        # print('baseline: {0}; type {1}'.format(baseline, type(baseline)))
        # baseline_adjuct = pd.DataFrame()
        # for df_key in data:
        #     print('adding key: ', df_key)
        #     baseline_adjuct[df_key] = data[df_key] - baseline
        #
        # heavy_rolling_mean = baseline_adjuct.rolling(1000).mean()
        # # calculate when the action potential starts
        # max_amps = funcs.calculate_max_amplitudes(baseline_adjuct)  # find the max first
        # self.average_max.extend(max_amps)
        #
        #
        # threshold = max_amps * START_THRESHOLD_RATIO  # calculate the threshold where the AP starts
        # hold = heavy_rolling_mean['voltage'][1:] < threshold  # use heavy roll to eliminate picking
        # # up the transient response from hitting the plant
        # time_shift = hold[hold == True].index[0]  # find where the data first crosses the threhold
        # self.time_start.append(time_shift)
        #
        # time_shifted_data = baseline_adjuct.copy()
        # time_shifted_data.index = time_shifted_data.index - time_shift
        # self.adjusted_data.append(time_shifted_data)
        #
        # self.decimated_data.append(time_shifted_data.rolling(10).mean())
        # self.heavy_decimate_data.append(time_shifted_data.rolling(1000).mean())

    def _append_single_series(self, data, key, time_shift=None):
        """ Take a data frame and append it to raw data anc make the other data structures needed
        :param data:  data frame of the raw acquired data
        """
        # calculate the data with a 0 baseline
        baseline = funcs.calculate_baseline(data[key])
        # data_index = scipy.signal.decimate(raw_data.index, 10)
        # data_voltage = scipy.signal.decimate(raw_data.voltage, 10)
        # data = pd.DataFrame(data=data_voltage, index=data_index)
        self.baselines.append(baseline)
        baseline_adjuct = pd.DataFrame()
        baseline_adjuct[key] = data[key] - baseline

        # calculate a rolling mean of the data

        heavy_rolling_mean = baseline_adjuct.rolling(1000).mean()
        # calculate when the action potential starts
        max_amp = funcs.calculate_max_amplitude(baseline_adjuct, key)  #find the max first
        self.average_max.append(max_amp)
        threshold = max_amp*START_THRESHOLD_RATIO  # calculate the threshold where the AP starts
        hold = heavy_rolling_mean[key][1:] < threshold  # use heavy roll to eliminate picking
        # up the transient response from hitting the plant
        if not time_shift:
            time_shift = hold[hold == True].index[0]  # find where the data first crosses the threhold
        self.time_start.append(time_shift)
        print("made data time_shift: ", time_shift)

        time_shifted_data = baseline_adjuct.copy()
        time_shifted_data.index = time_shifted_data.index - time_shift
        self.adjusted_data.append(time_shifted_data)

        self.decimated_data.append(time_shifted_data.rolling(10).mean())
        self.heavy_decimate_data.append(time_shifted_data.rolling(1000).mean())
        self.len += 1

    def delete_line(self, _index):
        del self.adjusted_data[_index]
        del self.decimated_data[_index]
        del self.heavy_decimate_data[_index]
        del self.baselines[_index]
        del self.average_max[_index]
        del self.time_start[_index]
        self.len -= 1

    def delete_some_data(self, picks):
        print('delete in data: ', picks)
        for index in reversed(picks):
            self.delete_line(index)


