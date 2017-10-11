# standard libraries
import logging
import tkinter as tk
from tkinter import font
from tkinter import ttk


__author__ = 'Kyle Vitautas Lopin'


COLOR_CHOICES = ['black', 'gray', 'red', 'green', 'blue', 'orange', 'magenta',
                 'darkred', 'lawngreen', 'forestgreen', 'mediumblue', 'darkslateblue',
                 'darkviolet', 'darkorchid']
LINE_STYLES = ['solid', 'dashed', 'dashdot', 'dotted']

class UserDeleteSomeData(tk.Toplevel):
    def __init__(self, master):
        tk.Toplevel.__init__(self, master)
        big_font = font.Font(family="Helvetica", size=14)
        small_font = font.Font(family="Helvetica", size=12)
        size = master.data.index
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


class ChangeDataLegend(tk.Toplevel):
    """ Make a toplevel that will allow the user to change the color of the data in the legend
    """

    def __init__(self, master):
        graph = master.data_area
        tk.Toplevel.__init__(self, master=master)
        self.legend_entries = []
        self.color_picks = []
        self.line_styles = []
        self.custom_colors = []
        tk.Label(self, text="Configure Data Legend").pack(side="top")
        # make a section to modify each line plotted so far
        for i in range(master.data.index):
            horizontal_frame = tk.Frame(self)
            horizontal_frame.pack(side="top")
            bottom_frame = tk.Frame(horizontal_frame)
            bottom_frame.pack(side="bottom")
            tk.Label(horizontal_frame, text="Chose color:").pack(side='left')
            self.color_picks.append(tk.StringVar())
            self.color_picks[i].set(master.data_area.colors[i])
            drop_menu = tk.OptionMenu(horizontal_frame,
                                      self.color_picks[i],
                                      *COLOR_CHOICES)
            drop_menu.pack(side='left')
            tk.Label(horizontal_frame,
                     text="Change data label:").pack(side='left')
            self.legend_entries.append(tk.StringVar())
            self.legend_entries[i].set(master.data_area.labels[i])
            tk.Entry(horizontal_frame, width=40,
                     textvariable=self.legend_entries[i]).pack(side="left")
            # tk.Label(bottom_frame, text="Line style:").pack(side='left')
            # self.line_styles.append(tk.StringVar())
            # self.line_styles[i].set('solid')
            # drop_menu2 = tk.OptionMenu(bottom_frame, self.line_styles[i], *LINE_STYLES)
            # drop_menu2.pack(side='left')
        bottom_frame = tk.Frame(self)
        bottom_frame.pack(side='bottom')
        tk.Button(bottom_frame,
                  text='Save',
                  width=10,
                  command=lambda: self.save(master, graph)).pack(side='left', padx=10,
                                                                 fill=tk.X, expand=1)
        tk.Button(bottom_frame,
                  text='Exit',
                  width=10,
                  command=self.destroy).pack(side='left', padx=10, fill=tk.X, expand=1)

    def save(self, _master, graph):
        """  The user wants to save changes to the data style and legend, impliment it here
        :param _master: master where the data is stored
        :param graph: graph area
        """
        for i, pick in enumerate(self.color_picks):
            _master.data_area.colors[i] = pick.get()
            graph.change_line_color(pick.get(), i)
            graph.change_line_style(self.line_styles[i].get(), i)
            _master.data_area.labels[i] = self.legend_entries[i].get()
        graph.update_legend()

        self.destroy()