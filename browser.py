# created on 5/9/22 at 23:13

import json
from tkinter import *
import tkinter as tk
from tkinter import ttk, filedialog
import webbrowser



class nestedSelector():
    # tkinter combobox that update its options when the value of its parent combobox changed

    def __init__(self, options=None, default=None, disabled=True, updator=None, *args, **kwargs):

        self.child = None  # the child that is supposed to change when *this* box changes
        self.disabled = disabled  # whether if the box starts disabled
        self.selector_var = StringVar(root)  # the variable of the box, for tracing
        self.selector_var.trace_add("write", self.demand_child)

        self.updator = updator  # function that returns the list of updated options upon demand

        self.default = default  # defaulted value
        if options is not None:  # wrangling with the default states...
            if default is not None:
                if isinstance(default,int):  # default is given as the index in the options list
                    self.default = options[default]
                    self.selector_var.set(options[default])
                elif default not in options:  # given explicit default, but not included
                    options = [default] + options
                    self.selector_var.set(options[0])
                else:  # given explicit default, and is included in the options
                    self.selector_var.set(default)

        # the combobox itself
        self.selector = ttk.Combobox(root, textvariable=self.selector_var, width=30)
        self.selector['values'] = options
        self.selector.configure(state="disabled" if disabled else 'readonly')  # readonly = typing not allowed
        self.selector.grid(*args, **kwargs)

    def demand_child(self,*args):  # asks the child to do stuff
        if self.child is not None:
            self.child.obey_parent(instruction=self.value)

    def obey_parent(self,instruction):  # receiving signal from parent, along with an instruction
        self.enable()
        self.update_options(instruction=instruction)

    def enable(self):  # de-disable the box
        self.disabled = False
        self.selector.configure(state="readonly")

    def update_options(self, instruction):  # update the options of the box when the parent demands
        if self.updator is not None:
            try:
                self.selector['values'] = tuple()
                default = [self.default] if self.default is not None else []
                new_options = default + self.updator(instruction)
                self.selector['values'] = new_options
                if self.default is not None:
                    self.selector.set(new_options[self.default])
                else: self.selector.set(new_options[0])
            except: pass

    def add_child(self, child):
        self.child = child
        self.demand_child()

    @property
    def value(self):
        return self.selector_var.get()

    @property
    def specified(self):
        return not self.value == self.default


class respondingDictionary():
    # tkinter Treeview with two columns, representing a dictionary with key:value in each row
    # updates the values when a parent demands

    def __init__(self, columns, updator, widths=None, *args, **kwargs):
        self.updator = updator

        # columns: the names of columns
        # updator: same as nestedSelectors
        # widths: a list of numbers, indicating the width of each column

        # the Treeview table
        self.table = ttk.Treeview(root, columns=tuple(columns))
        self.table.column("#0", width=0, stretch=False)
        for i, col in enumerate(columns):
            self.table.heading(col, text=col, anchor=CENTER)
            if widths is None:
                self.table.column(col, stretch=True)
            else:
                self.table.column(col, minwidth=widths[i], width=widths[i], stretch=True)
        self.table.grid(*args, **kwargs)

        # opens link upon double click or ENTER key
        self.table.bind("<Double-1>", self.open_link)
        self.table.bind("<Return>", self.open_link)

    def update(self,instruction):  # update the entries in the table
        try:
            new_data = self.updator(instruction)  # get the new entries from the updator function
            self.table.delete(*self.table.get_children())  # delete all entries
            new_keys = list(new_data.keys())
            new_keys.sort(key = lambda x: ('RESIT' not in x, x), reverse = True)
            for id,key in enumerate(new_keys):
                self.table.insert(parent='', index='end', text='', values=(key, new_data[key]))
        except Exception as e: print(e)

    def obey_parent(self,instruction):
        self.update(instruction=instruction)

    def open_link(self,*args):
        selections = self.table.selection()  # get the selected items in the Treeview
        selections = tuple(selections)
        for selection in selections:
            url = self.table.item(selection, 'values')[1]
            webbrowser.open(str(url))

root = Tk()

def main():

    root.title('Paper Browser')
    root.geometry('400x300')
    root.grid_columnconfigure(0, weight=1)
    root.grid_columnconfigure(1, weight=2)

    # read in the json file
    with open('paper_links.json', 'r') as file:
        data = json.load(file)
    # print(json.dumps(data, sort_keys=True, indent=4))

    # instructions
    inst1 = Label(root, text='Open with link with a double click, or select')
    inst1.grid(row=0,column=0,columnspan=3)
    inst2 = Label(root, text='any number of files and press ENTER to open all.')
    inst2.grid(row=1,column=0,columnspan=3)

    # dropdown menu for selecting the term
    # papers = [f'M{i+1}' for i in range(5)]
    papers = ['M1 - Linear Algebra | Groups',
            'M2 - Analysis',
            'M3 - Intro. Calc. | Prob. | Stats.',
            'M4 - Geometry | Dynamics | Construtive',
            'M5 - MVC | FS/PDE']
    paper_selector = nestedSelector(options=papers, disabled=False, row=2, column=1)  # default is the Trinity
    paper_label = Label(root, text='Paper')
    paper_label.grid(row=2,column=0)

    # list of papers
    link_updator = lambda sheet: data[paper_selector.value[0:2]]  # slices the 'M1' from the full title
    link_display = respondingDictionary(columns=('File','Link'),widths=[200,100], updator=link_updator,
                                        row=5, column=0, columnspan=2, sticky='we')
    paper_selector.add_child(link_display)

    root.mainloop()


if __name__ == '__main__':
    main()