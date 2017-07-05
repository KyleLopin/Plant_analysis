""" Option menu for plant electrophysiological data analysis GUI
"""

# standard libraries
import tkinter as tk

__author__ = 'Kyle Vitatuas Lopin'


class OptionMenu(tk.Menu):

    def __init__(self, master):
        tk.Menu.__init__(self, master=master)
        # Make the main menu to put all the submenus on
        menubar = tk.Menu(master)
        # Make a menus along the top of the gui
        file_menu = tk.Menu(menubar, tearoff=0)
        options_menu = tk.Menu(menubar, tearoff=0)
        data_menu = tk.Menu(menubar, tearoff=0)

        # make the drop down options for the user
        # make_option_menu(options_menu, master)
        make_file_option_menu(file_menu, master)
        # make_data_menu(data_menu, master)
        # make_developer_menu(developer_menu, master)

        menubar.add_cascade(label="File", menu=file_menu)
        menubar.add_cascade(label="Data", menu=data_menu)
        menubar.add_cascade(label="Options", menu=options_menu)

        master.config(menu=menubar)


def make_file_option_menu(file_menu, master):
    """ Make command to add to the "File" option in the menu
    :param file_menu: tk.Menu to add the commands to
    :param master: menu master
    """
    file_menu.add_command(label="Open",
                          command=master.open_and_display_data)

    # file_menu.add_command(label="Select Data to Save",
    #                       command=master.save_selected_data)
    file_menu.add_separator()
    file_menu.add_command(label="Quit",
                          command=master.quit)