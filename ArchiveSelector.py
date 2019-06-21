from tkinter import Tk, Button, Label, filedialog, messagebox, Listbox, Entry
import sqlite3
import os
import getpass
from pathlib import Path
import glob


class ArchiveSelector:
    def __init__(self):
        self.window = Tk()
        self.window.title("TabBack Analyzer")
        self.window.geometry("500x450")

        label = Label(self.window, text="Tab Back Analyzer")
        label.pack(pady=10, padx=10)

        autoButton = Button(text="Choose messages file...", command=self.autoButtonClicked)
        autoButton.pack()
        self.window.mainloop()


    def autoButtonClicked(self):

        print("auto button")
        self.window.filename = filedialog.askopenfilename(initialdir="/", title="Select chat.db file")
        print(self.window.filename)
        if(not self.window.filename.endswith("chat.db")):
            messagebox.showerror("Error", "Bad File Selection")
        else:
            conn = sqlite3.connect(self.window.filename)
            chats = conn.execute("select distinct chat.display_name from chat where not chat.display_name='';")
            self.setupDates()
            self.setupListbox()
            for idx, row in enumerate(chats):
                print(idx)
                print(str.encode(row[0]))
                self.chatListbox.insert(idx, str.encode(row[0]))

    def chatSelected(self, selection):
        print(selection)
        print(self.startDateEntry.get())
        print(self.endDateEntry.get())

    def setupListbox(self):
        self.chatListbox = Listbox(self.window)
        self.chatListbox.bind('<Double-Button-1>', lambda x: self.chatSelected(self.chatListbox.get(self.chatListbox.curselection())))
        self.chatListbox.pack()

    def setupDates(self):
        self.startDateLabel = Label(self.window, text="Start Date: mm/dd/yy")
        self.startDateLabel.pack()
        self.startDateEntry = Entry(self.window)
        self.startDateEntry.pack()
        self.endDateLabel = Label(self.window, text="End Date: mm/dd/yy")
        self.endDateLabel.pack()
        self.endDateEntry = Entry(self.window)
        self.endDateEntry.pack()