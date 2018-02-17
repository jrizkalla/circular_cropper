import tkinter as tk
from tkinter import ttk

from . import *

root = tk.Tk()
root.columnconfigure(0, weight=1)
root.rowconfigure(0, weight=1)


def crop_image(img, out_file):
    new_win = tk.Toplevel()
    new_win.transient(root)
    
    disp = ImageDisplayerWrapper(new_win,
            image=img,
            out_file=out_file,
            command=lambda: new_win.destroy())
    disp.grid(row=0, column=0, sticky="nsew")
    
    new_win.columnconfigure(0, weight=1)
    new_win.rowconfigure(0, weight=1)
    
loader = ImageLoader(root, command=crop_image)
loader.grid(row=0, column=0, sticky="nsew")
    

while True:
    try:
        root.mainloop()
        break
    except UnicodeDecodeError: pass
