
# standard libraries
from tkinter import filedialog



__author__ = 'Kyle Vitautas Lopin'








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



