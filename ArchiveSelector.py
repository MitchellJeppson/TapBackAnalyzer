from sqlite3.dbapi2 import Cursor
from tkinter import Tk, Button, Label, filedialog, messagebox, Listbox, Entry
import sqlite3
import os
import getpass
from pathlib import Path
import glob
import re
from json import JSONEncoder
import plotly.plotly as py
import plotly.graph_objs as go



RE_EMOJI=re.compile('[\U00010000-\U0010ffff]|\U0000FFFC', flags=re.UNICODE)


class StatsTracker(JSONEncoder):
    def __init__(self, name="Default Name"):
        self.name = name
        self.loves = 0
        self.thumbs_up = 0
        self.thumbs_down = 0
        self.lols = 0
        self.emphasis = 0
        self.questions = 0
        self.messages = []

    def addToMessages(self, message):
        message = RE_EMOJI.sub(r'', message)
        if len(self.messages) >= 10:
            self.messages = self.messages[1:10]
        self.messages.append(message)

    def containsMessage(self, message):
        message = RE_EMOJI.sub(r'', message)
        return message in self.messages

    def incrementLoves(self):
        self.loves = self.loves + 1

    def incrementThumbsUp(self):
        self.thumbs_up = self.thumbs_up + 1

    def incrementThumbsDown(self):
        self.thumbs_down = self.thumbs_down + 1

    def incrementLols(self):
        self.lols = self.lols + 1

    def incrementEmphasis(self):
        self.emphasis = self.emphasis + 1

    def incrementQuestions(self):
        self.questions = self.questions + 1


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
        chatIndex = self.conn.execute("SELECT chat.ROWID FROM chat WHERE chat.display_name='"+selection.decode('utf-8')+"';")
        chatIndex = chatIndex.fetchone()[0]
        print(chatIndex)
        allMessages = self.conn.execute("select t1.text, datetime(t1.date/1000000000+strftime('%s', '2001-01-01'), 'unixepoch', 'localtime') as date, id from message t1 inner join chat_message_join t2 on t2.chat_id=" + str(chatIndex) + " and t1.rowid=t2.message_id left join handle on t1.handle_id=handle.ROWID order by t1.date;").fetchall()
        print("got all messages!")
        allRecipients = self.conn.execute("select handle.id from chat, chat_handle_join, handle where chat.ROWID=chat_handle_join.chat_id AND chat_handle_join.handle_id=handle.ROWID AND chat.ROWID=" + str(chatIndex) + ";").fetchall()
        allRecipients.append(["Me"])
        print(chatIndex)
        self.recipients = []
        for recipient in allRecipients:
            self.recipients.append(StatsTracker(recipient[0]))

        # TODO: Currently has issues with emojies and likes on emoji text.
        # TODO: Currently does not take into account images and "Laughed at an image".
        for message in allMessages:
            if message[0] == None: # i think this happends for like images or just blank texts?
                continue
            if message[0].startswith("Laughed at “") :
                print("Found lol")
                recipient = self.whichRecipientGetsThis(message[0][12:len(message[0])-1])
                if recipient is None:
                    print("break")
                    continue
                recipient.incrementLols()
                continue
            elif message[0].startswith("Liked “"):
                print("Found Thumbsup")
                recipient = self.whichRecipientGetsThis(message[0][7:len(message[0])-1])
                if recipient is None:
                    print("break")
                    continue
                recipient.incrementThumbsUp()
                continue
            elif message[0].startswith("Disliked “"):
                print("Found Thumbsdown")
                recipient = self.whichRecipientGetsThis(message[0][10:len(message[0])-1])
                if recipient is None:
                    print("break")
                    continue
                recipient.incrementThumbsDown()
                continue
            elif message[0].startswith("Loved “"):
                print("Found love")
                recipient = self.whichRecipientGetsThis(message[0][7:len(message[0])-1])
                if recipient is None:
                    print("break")
                    continue
                recipient.incrementLoves()
                continue
            elif message[0].startswith("Emphasized “"):
                print("Found emphasis")
                recipient = self.whichRecipientGetsThis(message[0][12:len(message[0])-1])
                if recipient is None:
                    print("break")
                    continue
                recipient.incrementEmphasis()
                continue
            elif message[0].startswith("Questioned “"):
                print("Found QuestionMark")
                recipient = self.whichRecipientGetsThis(message[0][12:len(message[0])-1])
                if recipient is None:
                    print("break")
                    continue
                recipient.incrementQuestions()
                continue

            rec = self.getRecipientById(message[2])
            if rec is None:
                print("bad getRecipientById")
                print(message)
                continue
            rec.addToMessages(message[0])

        self.plotThatShit()


    def getRecipientById(self, id):
        if id == None:
            id = "Me"
        for recipient in self.recipients:
            if recipient.name == id:
               return recipient

        print("getRecipientById: no valid id found")
        rec = StatsTracker(id)
        self.recipients.append(rec)
        return rec

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

    def whichRecipientGetsThis(self, message):
        message = RE_EMOJI.sub(r'', message)
        for recipient in self.recipients:
            if recipient.containsMessage(message):
                return recipient

        print("No recipient found? ")
        return None


    def plotThatShit(self):
        print("pts")
        recipientsNames = []
        loves = []
        likes = []
        dislikes = []
        laughs = []
        emphasis = []
        questions = []
        for recipient in self.recipients:
            if recipient.name == "+18018567377":
                recipientsNames.append("Josh")
            elif recipient.name == "+18013582230" or recipient.name == "austinemail@msn.com":
                recipientsNames.append("Austin")
            elif recipient.name == "+18019157142":
                recipientsNames.append("Jordan")
            elif recipient.name == "+13854398755":
                recipientsNames.append("Tanner")
            elif recipient.name == "+18018369681":
                recipientsNames.append("Jeremy")
            elif recipient.name == "+18014722033":
                recipientsNames.append("Trevor")
            elif recipient.name == "+18019608123":
                recipientsNames.append("Connor")
            elif recipient.name == "Me":
                recipientsNames.append("Mitchell")

            loves.append(recipient.loves)
            likes.append(recipient.thumbs_up)
            dislikes.append(recipient.thumbs_down)
            laughs.append(recipient.lols)
            emphasis.append(recipient.emphasis)
            questions.append(recipient.questions)

        # trace1 = go.Bar(
        #     x=['giraffes', 'orangutans', 'monkeys'],
        #     y=[20, 14, 23],
        #     name='SF Zoo'
        # )
        # trace2 = go.Bar(
        #     x=['giraffes', 'orangutans', 'monkeys'],
        #     y=[12, 18, 29],
        #     name='LA Zoo'
        # )
        trace1 = go.Bar(
            x=recipientsNames,
            y=loves,
            name='Loves'
        )
        trace2 = go.Bar(
            x=recipientsNames,
            y=likes,
            name='Likes'
        )
        trace3 = go.Bar(
            x=recipientsNames,
            y=dislikes,
            name='Dislikes'
        )
        trace4 = go.Bar(
            x=recipientsNames,
            y=laughs,
            name='Laughs'
        )
        trace5 = go.Bar(
            x=recipientsNames,
            y=emphasis,
            name='Emphasis'
        )
        trace6 = go.Bar(
            x=recipientsNames,
            y=questions,
            name='Questions'
        )

        data = [trace1, trace2, trace3, trace4, trace5, trace6]
        layout = go.Layout(barmode='group')

        fig = go.Figure(data=data, layout=layout)
        m = py.plot(fig, filename='grouped-bar')
        print(m)
        print("done plotting")