# -*- coding: utf-8 -*-
"""
This is where the input data such as Username and Password are stored. It calls
up a graphical user interface to input the data. The main reason you would need
to edit this is to set default values or to add an additional input.

This file gets every needed input except for gps coordinates, date/time, and 
species name. 
"""


import sys
import tkinter as tk
from tkinter import Tk, Frame, Entry, TOP, X, Button, Label

def input_data():
    # The fields which are collected by the gui. This is what is displayed next
    # to the entry box.
    fields = ['Username', 'Password', 'APP ID', 'APP Secret', 'Folder', 
              'Time Zone', 'Accuracy of Position  (m)']
    
    # Here is where the preset values are set. These should be edited to match
    # the photos being imported. 
    
    # Your user name and password on the iNaturalist website. 
    Username = ''
    Password = ''
    
    # You will need to make an app to be able to use this code 
    # https://www.inaturalist.org/oauth/applications/new
    app = 'e4d9505ef7e814513d0a225e2e6555846765a84ceda7034eb454722e8047b68b'
    secret = 'b3766331e211b4a3e5fe34d4b51dd67f96d5deabd87c5837d823ce326a7bd0cd'
    
    # Every photo contained in subfolders in this folder will be uploaded. The
    # species will be the name of the folder the photo was placed in. 
    folder_name = 'E:/My Documents/Pictures/a6300/Test Folder'
    
    # It appears all the time zones here are accepted:
    # https://gist.github.com/mjrulesamrat/0c1f7de951d3c508fb3a20b4b0b33a98
    time_zone = 'America/Los_Angeles'
    accuracy = 10 #Accuracy in meters
    default_text = [Username, Password, app, secret, folder_name,
                    time_zone, accuracy]
    
    # Had to use a class here rather than a function to get data out of this
    # and back to the main script.
    class GetEntry():
        def __init__(self, master, fields, default_text):
            self.master=master
            self.entry_contents=None
            self.entries = []        
            
            # the different entry boxes are labeled e1, e2, e3... They are 
            # defined here
            self.e1 = tk.Entry(master, width = 75)
            self.entries.append(self.e1)
            Label(master, text=fields[0]).grid(row=0)
            self.e1.insert(0, default_text[0])
            self.e1.grid(row=0, column=1)
            self.e1.focus_set()
                
            self.e2 = tk.Entry(master, width = 75)
            self.entries.append(self.e2)
            Label(master, text=fields[1]).grid(row=1)
            self.e2.insert(0, default_text[1])
            self.e2.grid(row=1, column=1)
            self.e2.focus_set()    
    
            self.e3 = tk.Entry(master, width = 75)
            self.entries.append(self.e3)
            Label(master, text=fields[2]).grid(row=2)
            self.e3.insert(0, default_text[2])
            self.e3.grid(row=2, column=1)
            self.e3.focus_set() 
            
            self.e4 = tk.Entry(master, width = 75)
            self.entries.append(self.e4)
            Label(master, text=fields[3]).grid(row=3)
            self.e4.insert(0, default_text[3])
            self.e4.grid(row=3, column=1)
            self.e4.focus_set() 
            
            self.e5 = tk.Entry(master, width = 75)
            self.entries.append(self.e5)
            Label(master, text=fields[4]).grid(row=4)
            self.e5.insert(0, default_text[4])
            self.e5.grid(row=4, column=1)
            self.e5.focus_set() 
            
            self.e6 = tk.Entry(master, width = 75)
            self.entries.append(self.e6)
            Label(master, text=fields[5]).grid(row=5)
            self.e6.insert(0, default_text[5])
            self.e6.grid(row=5, column=1)
            self.e6.focus_set() 
            
            self.e7 = tk.Entry(master, width = 75)
            self.entries.append(self.e7)
            Label(master, text=fields[6]).grid(row=6)
            self.e7.insert(0, default_text[6])
            self.e7.grid(row=6, column=1)
            self.e7.focus_set()
            
            # The upload button is defined here
            tk.Button(master, text="Upload", width=10, bg="yellow",
                   command=self.callback).grid(row=10, column=0)
    
                # This function pulls what is typed out of the entry boxes when
            # the button is pushed. 
        def callback(self):
            self.entry_contents = []
            self.entry_contents.append(self.e1.get())
            self.entry_contents.append(self.e2.get())
            self.entry_contents.append(self.e3.get())
            self.entry_contents.append(self.e4.get())
            self.entry_contents.append(self.e5.get())
            self.entry_contents.append(self.e6.get())
            self.entry_contents.append(self.e7.get())
            
            # This closes the window after the data has been obtained
            self.master.destroy()
    
    
    master = tk.Tk()
    
    # This calls up the box with the inputs
    GE=GetEntry(master, fields, default_text)
    
    tk.Button(master, text="Quit", width=10, bg="yellow",
           command=master.destroy).grid(row=10, column=1)
    
    master.mainloop()
    
    # This extracts the text out of those boxes and returns it. 
    text_entered = GE.entry_contents
    return text_entered