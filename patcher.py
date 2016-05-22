""" patcher.py """

__author__ = "Etienne Faisant"
__date__ = "2015-07-02"

import sys
import os
import tkinter
from tkinter import filedialog


class patcher_tk(tkinter.Tk):

    def __init__(self, parent):
        tkinter.Tk.__init__(self, parent)
        self.parent = parent
        self.initialize()

    def initialize(self):
        self.grid()

        fp_label = tkinter.Label(self, text="Filepath")
        fp_label.grid(column=0, row=0, sticky='EW')

        self.filepath = tkinter.StringVar()
        self.entry = tkinter.Entry(self, textvariable=self.filepath)
        self.entry.grid(column=0, row=1, columnspan=3, sticky='EW')

        filediag = tkinter.Button(self, text="...", command=self.OnButtonClick_filedialog)
        filediag.grid(column=3, row=1, sticky='EW')

        add_label = tkinter.Label(self, text="Address")
        add_label.grid(column=0, row=2, sticky="EW")

        self.address = tkinter.StringVar()
        self.entry_add = tkinter.Entry(self, textvariable=self.address)
        self.entry_add.grid(column=0, row=3, sticky="EW")

        oldv_label = tkinter.Label(self, text="Old value")
        oldv_label.grid(column=1, row=2, sticky="EW")

        self.oldvalue = tkinter.StringVar()
        self.entry_old = tkinter.Entry(self, textvariable=self.oldvalue)
        self.entry_old.grid(column=1, row=3, sticky="EW")

        newv_label = tkinter.Label(self, text="New value")
        newv_label.grid(column=2, row=2, sticky="EW")

        self.newvalue = tkinter.StringVar()
        self.entry_new = tkinter.Entry(self, textvariable=self.newvalue)
        self.entry_new.grid(column=2, row=3, sticky="EW")

        patchbtn = tkinter.Button(self, text="patch", command=self.OnButtonClick_patch)
        patchbtn.grid(column=3, row=2, rowspan=2, sticky="NSEW")

        self.labelVariable = tkinter.StringVar()
        label = tkinter.Label(self, textvariable=self.labelVariable, anchor="w", fg="white", bg="blue")
        label.grid(column=0, row=4, columnspan=4, sticky='EW')

        self.resizable(False, False)
        self.update()
        self.geometry(self.geometry())

    def OnButtonClick_filedialog(self):
        self.filepath.set(filedialog.askopenfilename(filetypes=[("All", "*")]))

    def OnButtonClick_patch(self):
        self.labelVariable.set(patch(self.filepath.get(), self.address.get(), self.oldvalue.get(), self.newvalue.get()))


def patch(binfile, address, oldvalue, newvalue):
    print("Patch of", binfile, "at", address, "replacing", oldvalue, "by", newvalue)
    try:
        int(address, 16)
    except:
        return "Address malformed"

    try:
        int(oldvalue, 16)
        if len(oldvalue) % 2 == 1:
            raise ValueError('')
    except:
        return "Old value malformed"

    try:
        int(newvalue, 16)
        if len(newvalue) % 2 == 1:
            raise ValueError('')
    except:
        return "New value malformed"

    if len(oldvalue) < len(newvalue):
        return "Error, new value could not be longer than old value"

    try:
        address = int(address, 16)
        filesize = os.path.getsize(binfile)
        oldvalue = bytes.fromhex(oldvalue)
        newvalue = bytes.fromhex(newvalue)

        if address + len(oldvalue) >= filesize and len(oldvalue) > len(newvalue):
            return "Error, address + old value length > file size"

        with open(binfile, "r+b") as bf:
            if address + len(newvalue) >= filesize:
                bf.seek(0, os.SEEK_END)
                bf.write(b'\0' * (address - filesize + len(newvalue)))

            bf.seek(address)
            testval = bf.read(len(oldvalue))
            if testval == oldvalue:
                bf.seek(address)
                bf.write(newvalue)
            else:
                return "Old value not found"
            return "Ok"
    except FileNotFoundError:
        return "File not found"

if __name__ == '__main__':
    if len(sys.argv) < 2:
        app = patcher_tk(None)
        app.title('Patcher')
        app.mainloop()
    else:
        if sys.argv[1] in ['-c', '-console']:
            if len(sys.argv) < 2:
                binfile = input("File to patch : ")
            else:
                binfile = sys.argv[1]

            if len(sys.argv) > 2:
                address = sys.argv[2]
            else:
                address = input("Address : ")

            if len(sys.argv) > 3:
                oldvalue = sys.argv[3]
            else:
                oldvalue = input("Old value : ")

            if len(sys.argv) > 4:
                newvalue = sys.argv[4]
            else:
                newvalue = input("New value : ")

            print(patch(binfile, address, oldvalue, newvalue))
        else:
            print(sys.argv[0], "[-c] [file [address [oldvalue [newvalue]]]")
            print("-c, -console\tuse console version")
            print("file\t\tfile path")
            print("address\t\taddress where apply patch")
            print("oldvalue\texpected value")
            print("newvalue\tpatch value")
