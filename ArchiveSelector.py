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
            self.conn = sqlite3.connect(self.window.filename)
            chats = self.conn.execute("select distinct chat.display_name from chat where not chat.display_name='';")
            # self.setupDates()
            self.setupListbox()
            for idx, row in enumerate(chats):
                print(idx)
                print(str.encode(row[0]))
                self.chatListbox.insert(idx, str.encode(row[0]))

    def chatSelected(self, selection):
        print(selection)
        # print(self.startDateEntry.get())
        # print(self.endDateEntry.get())
        chatIndex = self.conn.execute("SELECT chat.ROWID FROM chat WHERE chat.display_name='"+selection.decode('utf-8')+"';")
        chatIndex = chatIndex.fetchone()[0]
        print(chatIndex)
        messages = self.conn.execute("SELECT message.text, handle.id FROM chat, message, handle, chat_handle_join, chat_message_join WHERE chat.ROWID=chat_handle_join.chat_id AND chat.ROWID=chat_message_join.chat_id AND handle.ROWID=chat_handle_join.handle_id AND message.ROWID=chat_message_join.message_id AND message.handle_id=handle.ROWID AND (chat.ROWID="+str(chatIndex)+");")
        for idx, row in enumerate(messages):
            print(str(idx)+": "+str(row[1])+"- "+str(row[0]))

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