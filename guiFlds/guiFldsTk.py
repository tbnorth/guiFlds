"""Tkinter implementation of guiFlds
"""

# pgSSDRtktb_ui.py $Id$
# Author: Terry Brown
# Created: Mon Jul 09 2007


import tkinter as tk
from tkinter import filedialog


class msg:
    """class with write method, guiFlds uses this to redirect output to
    gui, in this case self.txt, a Tkinter Text"""

    def __init__(self, txt, root):
        self.txt = txt
        self.root = root
        # make readonly
        self.txt.configure(state=tk.DISABLED)

    def write(self, txt):
        self.txt.configure(state=tk.NORMAL)
        self.txt.insert(tk.END, txt)
        self.txt.configure(state=tk.DISABLED)
        self.txt.see(tk.END)
        self.root.update()


class callOn:
    """callback wrapper class, handles buttons that feed file/directory
    names into text entry fields, as well as parameterless button press
    commands"""

    def __init__(self, ui, owner, funcName, special=None, target=None):
        self.ui = ui
        self.owner = owner
        self.funcName = funcName
        self.special = special
        self.target = target

    def __call__(self, *args):
        """Keyword arguments:
        args -- may contain event arguments from Tkinter"""
        self.ui.readFlds(self.owner.fldDict())
        f = None
        if hasattr(self.owner, self.funcName):
            f = getattr(self.owner, self.funcName)
        if self.special is None:
            f()
        if self.special == "__OPENDIR__":
            t = None
            if self.target:
                t = self.target.get()
            fileName = filedialog.askdirectory(
                parent=self.ui.master, title="Select Folder", initialdir=t
            )
            if fileName:
                if self.target:
                    self.target.set(fileName)
                else:
                    f(fileName)
        if self.special == "__OPENFILE__":
            fileName = filedialog.askopenfilename(
                parent=self.ui.master,
                filetypes=[("Any File", "*.*")],
                title="Open File",
            )
            if fileName:
                if self.target:
                    self.target.set(fileName)
                else:
                    f(fileName)
        if self.special == "__SAVEFILE__":
            fileName = filedialog.asksaveasfilename(
                parent=self.ui.master,
                filetypes=[("Any File", "*.*")],
                title="Save File",
            )
            if fileName:
                if self.target:
                    self.target.set(fileName)
                else:
                    f(fileName)
        if not self.target:
            self.ui.writeFlds(self.owner.fldDict())


class guiFldsTk:
    """Tkinter GUI for guiFlds.

    Reverse engineered from tk_happy file."""

    def __init__(self, owner):
        """owner -- the guiFlds descendant that owns this interface"""
        self.owner = owner
        self.closing = False

        master = tk.Tk()
        self.initialize(master)
        # self.master = master # done in initialize
        self.owner.setUpdate(self.master.update)  # _idletasks)
        master.mainloop()

    def exiting(self):
        """window closed - but wait for one last click to show
        terminal output, if any"""
        if not self.closing and hasattr(self.owner, "WindowClosed"):
            self.closing = True
            self.readFlds(self.owner.fldDict())
            self.owner.WindowClosed()
            for i in self.entry.itervalues():
                for t in ["label", "entry", "helper", "button"]:
                    if t in i:
                        i[t].destroy()
            self.menuBar.destroy()
            print("Final messages from application above.")
            print("Click close again to close window.")
        else:
            self.master.destroy()

    def initialize(self, master):
        """layout gui, set up callbacks"""
        w = 440
        h = 550

        # START: tk_happy did this
        self.initComplete = 0
        frame = tk.Frame(master, width=w, height=h)
        frame.pack()
        self.master = master
        self.x, self.y, self.w, self.h = -1, -1, -1, -1

        # bind master to <Configure> in order to handle any resizing, etc.
        # postpone self.master.bind("<Configure>", self.Master_Configure)
        self.master.bind("<Enter>", self.bindConfigure)
        # END: tk_happy did this

        # use class name of owner for window title
        self.master.title(str(self.owner.__class__).split(".")[-1])

        # bind window closing callback
        master.protocol("WM_DELETE_WINDOW", self.exiting)

        lw = 120  # label width
        lh = 22  # label height
        ew = 220  # entry width
        cw = 120  # checkbox width
        cr = 3  # checkbox columns
        r = 0  # current column
        bh = 24  # button height
        fbw = 30  # file chooser button width

        px, py = 4, 4  # padding
        x, y = px, py  # initial values

        self.entry = {}  # various widgets
        self.radio = {}  # shared StringVars for radio buttons

        # entry fields
        for fName, fType, fDesc, fDef, fSpec in self.owner.fld_iter():
            if fType == str:
                self.entry[fName] = {}
                e = self.entry[fName]
                e["label"] = tk.Label(
                    self.master,
                    text=fDesc,
                    justify="right",
                    anchor="e",
                    width=lw,
                    height=lh,
                )

                e["label"].place(x=x, y=y, width=lw, height=lh)

                x += lw + px

                e["entry"] = tk.Entry(self.master, relief="sunken", width="15")
                e["entry"].place(x=x, y=y, width=ew, height=lh)
                e["value"] = tk.StringVar()
                e["value"].set(self.owner.fldDict()[fName])
                e["entry"].configure(textvariable=e["value"])
                # e['traceName'] = e['value'].trace_variable('w', e['trace'])

                if fSpec:  # add button to select file / directory in this entry
                    x += ew + px
                    e["helper"] = tk.Button(
                        self.master,
                        text=" .. ",
                        justify="center",
                        relief="raised",
                        width="15",
                    )
                    e["helper"].place(x=x, y=y, width=fbw, height=bh)
                    e["helper"].bind(
                        "<ButtonRelease-1>",
                        callOn(
                            self, self.owner, fName, special=fSpec, target=e["value"]
                        ),
                    )
                y += py + lh
                x = px

        # check buttons
        for fName, fType, fDesc, fDef, fSpec in self.owner.fld_iter():
            if fType == bool and not fSpec:
                self.entry[fName] = {}
                e = self.entry[fName]
                e["entry"] = tk.Checkbutton(
                    self.master, text=fDesc, justify="left", relief="flat", width="15"
                )
                e["entry"].place(x=x, y=y, width=cw, height=lh)
                e["value"] = tk.StringVar()
                e["value"].set(self.owner.fldDict()[fName])
                e["entry"].configure(variable=e["value"], onvalue="yes", offvalue="no")

                e["entry"].bind("<ButtonRelease-1>", lambda e: self.readFlds())
                x += cw + px
                r += 1
                if r == cr:
                    r = 0
                    y += lh
                    x = px

        if r != 0:
            r = 0
            y += lh
        x = px

        # radio buttons
        for fName, fType, fDesc, fDef, fSpec in self.owner.fld_iter():
            if fType == bool and fSpec == "__RADIO__":
                self.entry[fName + ":" + fDef] = {}
                e = self.entry[fName + ":" + fDef]
                e["entry"] = tk.Radiobutton(
                    self.master,
                    text=fDesc,
                    justify="left",
                    relief="flat",
                    width="15",
                    value=fDef,
                )
                e["entry"].place(x=x, y=y, width=cw, height=lh)
                sv = self.radio.setdefault(fName, tk.StringVar())
                sv.set(self.owner.fldDict()[fName])
                e["entry"].configure(variable=sv)

                x += cw + px
                r += 1
                if r == cr:
                    r = 0
                    y += lh
                    x = px

        if r != 0:
            r = 0
            y += lh
        x = px

        # action buttons
        for fName, fType, fDesc, fDef, fSpec in self.owner.fld_iter():
            if fType is None and "-->" not in fDesc:
                self.entry[fName] = {}
                e = self.entry[fName]
                e["button"] = tk.Button(
                    self.master,
                    text=fDesc,
                    justify="center",
                    relief="raised",
                    width="15",
                )
                e["button"].place(x=x, y=y, width=cw, height=bh)
                e["button"].bind(
                    "<ButtonRelease-1>", callOn(self, self.owner, fName, special=fSpec)
                )

                x += cw + px
                r += 1
                if r == cr:
                    r = 0
                    y += bh
                    x = px

        if r != 0:
            r = 0
            y += lh
        x = px

        # menus
        # only one supported currently
        menuName = ""
        menuList = []
        for fName, fType, fDesc, fDef, fSpec in self.owner.fld_iter():
            if fType is None and "-->" in fDesc:
                menuName = fDesc.split("-->")[0]
                menuList.append((fDesc.split("-->")[1], fDef, fName))

        if menuName:
            self.menuBar = tk.Menu(master, relief="raised", bd=2)

            top_File = tk.Menu(self.menuBar, tearoff=0)

            for i, s, n in menuList:
                top_File.add("command", label=i, command=callOn(self, self.owner, n, s))

            self.menuBar.add("cascade", label="File", menu=top_File)
            # self.menuBar.add("command", label = "Help", command = self.menu_Help)
            master.config(menu=self.menuBar)

        # message area, text with scroll bar
        y += py
        lbframe = tk.Frame(self.master)
        self.Text_1_frame = lbframe
        scrollbar = tk.Scrollbar(lbframe, orient=tk.VERTICAL)
        self.Text_1 = tk.Text(
            lbframe, width="40", height="12", yscrollcommand=scrollbar.set
        )
        scrollbar.config(command=self.Text_1.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.Text_1.pack(side=tk.LEFT, fill=tk.BOTH, expand=1)

        self.Text_1_frame.place(x=x, y=y, width=400, height=200)

        self.msg = msg(self.Text_1, master)
        self.owner.setMessage(self.msg)
        self.owner.setUpdate(self.master.update)

    def readFlds(self, fDict=None):
        """read values from gui to owner's parameter dictionary"""
        if fDict is None:
            fDict = self.owner.fldDict()
        for fName, fType, fDesc, fDef, fSpec in self.owner.fld_iter():
            if fType:
                if not (fType == bool and fSpec):
                    fDict[fName] = self.entry[fName]["value"].get()
                else:
                    fDict[fName] = self.radio[fName].get()

    def writeFlds(self, fDict):
        """write valuess from owner's parameter dictionary to gui"""
        for fName, fType, fDesc, fDef, fSpec in self.owner.fld_iter():
            if fType:
                if not (fType == bool and fSpec):
                    self.entry[fName]["value"].set(fDict[fName])
                else:
                    self.radio[fName].set(fDict[fName])

    # probably useless debris from tk_happy reverse engineering
    def bindConfigure(self, event):
        if not self.initComplete:
            # TNB self.master.bind("<Configure>", self.Master_Configure)
            self.initComplete = 1

    # probably useless debris from tk_happy reverse engineering
    # unaltered from tk_happy
    def Master_Configure(self, event):
        pass
        # >>>>>>insert any user code below this comment for section "Master_Configure"
        # replace, delete, or comment-out the following
        if event.widget != self.master:
            if self.w != -1:
                return
        x = int(self.master.winfo_x())
        y = int(self.master.winfo_y())
        w = int(self.master.winfo_width())
        h = int(self.master.winfo_height())
        if (self.x, self.y, self.w, self.h) == (-1, -1, -1, -1):
            self.x, self.y, self.w, self.h = x, y, w, h

        if self.w != w or self.h != h:
            print("Master reconfigured... make resize adjustments")
            self.w = w
            self.h = h
