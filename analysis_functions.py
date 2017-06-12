""" Functions to help analyze a data trace
"""
# standard libraries
import logging
import pickle
import os
import tkinter as tk
from tkinter import filedialog
import sys
#installed libraries
import pandas as pd

__author__ = 'Kyle Vitautas Lopin'


def calculate_baseline(data_frame):
    """ Calculate the baseline voltage of a data trace by
    :param data_frame: panda data frame
    :return: float - average voltage for the time between 1-4 seconds
    """
    baseline_splice = data_frame[1.0:4.0].mean()
    return float(baseline_splice)


def calculate_max_amplitudes(data: pd.DataFrame):
    max_amps = []
    for df_key in data:

        max = data[df_key].min()
        max_id = data[df_key].idxmin()
        max_range = [max_id - 0.025, max_id + 0.025]  # get data 25 millisec before or after max point
    max_amps.append(float(data[max_range[0]:max_range[1]].mean()))
    return max_amps

def calculate_max_amplitude(data: pd.DataFrame, df_key):
    max = data[df_key].min()
    max_id = data[df_key].idxmin()
    max_range = [max_id - 0.025, max_id + 0.025]  # get data 25 millisec before or after max point
    return float(data[max_range[0]:max_range[1]].mean())


def pd_decimation(data, downsampling_factor):
    """ Take a pandas 
    :param data: Pandas dataframe with the index being the time stamp
    :return: new pandas dataframe with the signal decimated
    """
    time_series = data.index
    data_series = data.voltage
    print('decimateion types: {0}; ========== \n {1}'.format(time_series, data_series))
