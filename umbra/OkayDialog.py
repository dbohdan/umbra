from tkinter import *
import tkinter.messagebox
from . import Global, util
import os

DIALOG_GEOMETRY="+32+32"

OK="OK"
CANCEL="Cancel"

YESNO_YES="yes"
YESNO_NO="no"

INPUT_WIDTH=32
MENU_WIDTH=40
MENU_MAX_HEIGHT=27
TEXT_WIDTH=40
TEXT_HEIGHT=20

if os.name=="nt":
    MONO_FONT=("Courier", 10, "bold")
    MENU_FONT=("Courier", 12, "bold")
else:
    MONO_FONT=("Courier", 12)
    MENU_FONT=("Courier", 12, "bold")

#________________________________________
def alert(master, title, msg, type=Global.ALERT_WARNING):
    if type==Global.ALERT_ERROR:
        return tkinter.messagebox.showerror(title, msg)
    elif type==Global.ALERT_INFO:
        return tkinter.messagebox.showinfo(title, msg)
    elif type==Global.ALERT_WARNING:
        return tkinter.messagebox.showwarning(title, msg)
    elif type==Global.ALERT_YESNO:
        return tkinter.messagebox.askyesno(title, msg, default=YESNO_NO)
    else:
        assert 0, "Unknown alert type '%s'"%type

#________________________________________
class OkayDialog:
    def __init__(self, master, title, geometry, **args):
        self.top = Toplevel(master)
        self.top.transient(master)
        self.top.bind("<Destroy>", self.event)
        self.top.bind("<Key-Return>", self.event)
        self.top.bind("<Key-Escape>", self.event)
        self.top.geometry(geometry)

        self.dlg = Frame(self.top)
        self.top.title(title)
        body = Frame(self.dlg)
        body.pack(anchor=N)

        self.buttonbar = Frame(self.dlg)
        self.ok = self.addButton(OK)
        self.buttonbar.pack(anchor=S)

        self.button = None
        self.__firstTime=1

        # user initialization
        self.makeBody(body, args)

        self.dlg.pack()

        master.lower(belowThis=self.top)
        self.top.tkraise(aboveThis=master)

        self.top.mainloop()

    def __okayCommand(self, selected):
        if self.__firstTime:
            self.__firstTime=0
            self.button=selected
            self.okay()
            self.top.withdraw()
            self.top.destroy()
            self.top.quit()

    def addButton(self, text, key=None, side=LEFT, fill=None, anchor=CENTER, **opts):
        if key and len(key) == 1:
            label = "[%s] %s" % (key, text)
        else:
            label = text
        b = Button(self.buttonbar, text=label, takefocus=0, anchor=anchor,
            command=lambda s=self, t=text: s.__okayCommand(t), **opts)
        if key:
            self.top.bind(key, lambda e, s=self, t=text: s.__okayCommand(t))
        b.pack(side=side, anchor=NW, fill=fill)
        return b

    def event(self, event):
        self.__okayCommand(event.keysym)

    def makeBody(self, body, args):
        """Override with your GUI construction to go in the body frame; any
        user-named constructor parameters are in args as a dictionary"""
        pass

    def okay(self):
        """Called when a button is pressed, or when the window is closed."""
        pass

    def title(self, title):
        self.top.title(title)

#________________________________________
class InputDialog(OkayDialog):
    def makeBody(self, body, args):
        prompts = args["prompts"]
        self.fields = []
        i=0
        for p in prompts:
            Label(body, text=p).grid(row=i, sticky=W)
            entry = Entry(body, width=INPUT_WIDTH, bg="white", fg="black")
            entry.bind("<Key-Return>", self.event)
            self.fields.append(entry)
            entry.grid(row=i, column=1, sticky=W)
            i = i+1
        self.fields[0].focus_set()
        self.answers = None

        self.addButton(CANCEL, key="<Key-Escape>")

    def okay(self):
        if self.button != CANCEL:
            self.answers = []
            for entry in self.fields:
                self.answers.append( entry.get() )
        else:
            self.answers=None

    def getAnswer(self, i):
        if self.answers: return self.answers[i]
        return None

    def getAnswers(self):
        return self.answers

#________________________________________
class TextDialog(OkayDialog):
    def makeBody(self, body, args):
        msg = args["text"]
        text = Text(body, width=TEXT_WIDTH, height=TEXT_HEIGHT, takefocus=0,
            wrap=WORD)
        text.bind("<Key>", self.event)
        scroll = Scrollbar(body, command=text.yview)
        scroll.bind("<Key-Return>", self.event)
        text.configure(yscrollcommand=scroll.set)
        text.insert(END, msg)
        text.pack(side=LEFT, fill=BOTH, expand=YES)
        scroll.pack(side=RIGHT, fill=Y)

        self.ok.focus_set()

#________________________________________
class MenuDialog(OkayDialog):
    def makeBody(self, body, args):
        prompts = args["prompts"]
        self.keys=args.get("keys", None)
        if "banner" in args:
            Label(body, text=args["banner"], width=MENU_WIDTH, justify=LEFT,
                    font=MONO_FONT).pack(anchor=W)
        height = min(MENU_MAX_HEIGHT, len(prompts))
        if height < len(prompts): scrollbar = 1
        else: scrollbar = 0
        self.list = Listbox(body, width=MENU_WIDTH, height=height,
            selectmode=BROWSE, font=MENU_FONT )
        self.list.bind("<Key-Return>", self.event)
        self.list.bind("<Double-Button-1>", self.event)
        if self.keys:
            for k in self.keys:
                if k:
                    self.list.bind(k, self.keyEvent)
        if scrollbar:
            scroll = Scrollbar(body, command=self.list.yview)
            scroll.bind("<Key-Return>", self.event)
            self.list.configure(yscrollcommand=scroll.set)
        for i in range(len(prompts)):
            item = prompts[i]
            if self.keys and self.keys[i]:
                item = "[%s] %s" % (self.keys[i], item)
            self.list.insert(END, item)
        self.list.pack(side=LEFT, fill=BOTH, expand=YES)
        if scrollbar:
            scroll.pack(side=RIGHT, fill=Y)
        self.list.focus_set()

        self.list.selection_set(0)
        self.index=0

    def keyEvent(self, event):
        k = event.keysym
        i = util.indexOf(k, self.keys)
        if i >= 0:
            self.list.selection_clear( self.list.curselection() )
            self.index = i
            self.list.activate(i)
            self.list.selection_set(i)
            self.event(event)

    def okay(self):
        sels=self.list.curselection()
        if not sels:
            self.index=0
        else:
            self.index=int(sels[0])

    def getSelected(self):
        return self.index

#________________________________________
def testTk(master):
    Button(master, text="input", command=testInput).pack(side=LEFT)
    Button(master, text="alert", command=testAlert).pack(side=LEFT)
    Button(master, text="text", command=testText).pack(side=LEFT)
    Button(master, text="menu", command=testMenu).pack(side=LEFT)
    master.mainloop()

def testAlert():
    print("before alerts")
    alert(master, "Default", "This is a test of the emergency alertbox system.")
    alert(master, "warning", "warning", "warning")
    alert(master, "error", "error", "error")
    alert(master, "info", "info", "info")
    print("after alerts")

def testText():
    print("before text")
    TextDialog(master, "Title", DIALOG_GEOMETRY, text="""
Only two kinds of witnesses exist.  The first live in a neighborhood where
a crime has been committed and in no circumstances have ever seen anything
or even heard a shot.  The second category are the neighbors of anyone who
happens to be accused of the crime.  These have always looked out of their
windows when the shot was fired, and have noticed the accused person standing
peacefully on his balcony a few yards away.
                -- Sicilian police officer""")
    print("after text")

def testInput():
    dlg = InputDialog(master, "Title", DIALOG_GEOMETRY, prompts=("One", "Two") )
    print(dlg.getAnswers())

def testMenu():
    dlg = MenuDialog(master, "Title", DIALOG_GEOMETRY, prompts=list(range(20)) )
    print(dlg.getSelected())

if __name__ == "__main__":
    master = Tk()
    testTk(master)

