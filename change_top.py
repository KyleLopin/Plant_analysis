# standard libraries
import logging
import tkinter as tk
from tkinter import font
from tkinter import ttk


__author__ = 'Kyle Vitautas Lopin'


class UserDeleteSomeData(tk.Toplevel):
    def __init__(self, master):
        tk.Toplevel.__init__(self, master)
        big_font = font.Font(family="Helvetica", size=14)
        small_font = font.Font(family="Helvetica", size=12)
        size = master.data.len
        length = 50 * size
        self.geometry("400x{0}".format(length))
        self.title("Select data to delete")
        tk.Label(self,
                 text="Select data to delete",
                 font=big_font).pack(side='top')
        frames = []
        choices = []
        index = 0
        for _label in master.data_area.labels:
            frames.append(tk.Frame(self))
            choices.append(tk.IntVar())
            tk.Checkbutton(frames[index],
                           text=_label,
                           font=small_font,
                           variable=choices[index]).pack(padx=5)

            frames[index].pack(side='top', fill=tk.X, expand=1)
            index += 1

        tk.Label(self, text="Delete on selected data?")

        button_frame = tk.Frame(self)
        tk.Button(button_frame,
                  text="Yes",
                  width=10,
                  command=lambda: self.send_delete_selection(master, choices)
                  ).pack(side='left', padx=10, fill=tk.X, expand=1)

        tk.Button(button_frame,
                  text="No",
                  width=10,
                  command=self.destroy
                  ).pack(side='left', padx=10, fill=tk.X, expand=1)

        button_frame.pack(side='top', fill=tk.X, expand=1)

    def send_delete_selection(self, master, picks):
        """ Decode the check boxes the user selected and send the list to master to delete the data
        :param master: root application
        :param picks: list of the checkboxes the user choose from
        """
        _list = []
        _index = 0
        for pick in picks:
            if pick.get() == 1:
                _list.append(_index)
            _index += 1
        master.data.delete_some_data(_list)
        master.data_area.delete_some_data(_list)
        master.delete_some_data(_list)
        self.destroy()