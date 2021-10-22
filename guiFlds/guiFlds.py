"""Class that exposes parameters in simple gui interface
"""

# guiFlds.py $Id$
# Author: Terry Brown
# Created: Tue Jul 10 2007

import sys, subprocess, time, os

class msgStd:
    """pass through message handler, doesn't really do anything"""
    def __init__(self, stdout):
        self.stdout = stdout
    def write(self, txt):
        self.stdout.write(txt)

class guiFlds:
    """Class that exposes parameters in simple gui interface

    Driven by a list of fields or parameters specified by:

      - name - (required)
      - type - defaults to str.  None is used for command buttons and menus
      - guitxt - defaults to name, indicates a menu entry if it includes '-->'
      - default value - defaults to None
      - special - __OPENFILE__, __SAVEFILE__, and __OPENDIR__ add helper
        buttons for entry (str) fields, __RADIO__ on a bool field indicates
        a radio button.
    """

    # standard options for loading the owner objects parameter
    # dictionary
    stdFldList = (
            ('Open', None, 'File-->Open', '__OPENFILE__'),
            ('Save', None, 'File-->Save As', '__SAVEFILE__'),
            )

    def varTypDsc(self, fld):
        """Expand short field description tuples as described above"""
        if isinstance(fld, str):
            return fld, str, fld, None, None
        if len(fld) == 2:
            return fld+(fld[0], None, None)
        if len(fld) == 3:
            return fld+(None, None)
        if len(fld) == 4:
            return fld+(None,)
        return fld
    
    def fld_iter(self):
        """iterate field descriptions"""
        for i in (self.fldList + self.stdFldList):
            yield self.varTypDsc(i)
            
    def __init__(self):
        self._fldDict = {}
        self.update = lambda: None

        self.setMessage(msgStd(sys.stdout))
        
        self.msgPat = {}

        # load defaults
        for fName, fType, fDesc, fDef, fSpec in self.fld_iter():
            if fType and fName not in self._fldDict:
                # take default radio button value as first seen
                self._fldDict[fName] = fDef

        self.parseCommandLine()
        
    def fldDict(self):
        """access parameter dictionary"""
        return self._fldDict

    def Save(self, fn):
        """save parameter dictionary to fn, from __SAVEFILE__ special"""
        f = file(fn, 'w')
        self.write(f)
        
    def Open(self, fn):
        """load parameter dictionary to fn, from __LOADFILE__ special"""
        f = file(fn)
        self.read(f)

    def read(self, f):
        """read dictionary with simple <fieldname>:<anything to eol> format"""
        for l in f:
            k,v = l.split(':', 1)
            self.fldDict()[k.strip()] = v.strip()

    def write(self, f):
        """write dictionary with simple <fieldname>:<anything to eol> format"""
        for k, v in self.fldDict().iteritems():
            f.write('%s: %s\n' % tuple(map(str, (k, v))))

    def parseCommandLine(self):
        """check for '--file filename' sequence to load"""
        for n,i in enumerate(sys.argv[1:-1]):
            if i == '--file':
                self.read(file(sys.argv[n+2]))
                break
            
    def setMessage(self, dest):
        """set message recipient"""
        self.msg = dest
        sys.stdout = self.msg
        sys.stderr = self.msg

    def messagePatterns(self):
        """access dictionary of patterns for hightlighting"""
        return self.msgPat

    def setUpdate(self, update):
        """set update function for GUI implementation

        In pWrapper() output from subprocesses is read every 0.1 secs
        while the subprocess is running, GUI may need an update method
        called to show output before suprocess ends and control returns
        to gui loop."""
        self.update = update

    def pWrapper(self, *args, **kargs):
        """Popen wrapper to feed output to "class with write()" rather
        than "real os level file" required by Popen.  The
        "class with write()" is at sys.stdout"""
        kargs.update({'stdout': subprocess.PIPE,
                      'stderr': subprocess.PIPE})
        command = subprocess.Popen(*args, **kargs)

        pollInterval = 0.1 # seconds
        maxWait = 30 # seconds
        polls = maxWait / pollInterval

        def ioPopen(command):
            """Send all available output from subprocess to sys.stdout.

            Uses os.read because it's non-blocking"""
            for f in [command.stdout.fileno(), command.stderr.fileno()]:
                while True:
                    s = os.read(f, 1024)
                    if s:
                        sys.stdout.write(s)
                    else:
                        break
        while polls:
            polls -= 1
            ioPopen(command)
            if self.update: self.update()
            if command.poll() != None: break
            time.sleep(pollInterval)

        ioPopen(command)
