import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
from cropper import *
from PIL import Image, ImageTk
from random import randint

root = tk.Tk()
        
#?image = Image.open("img.jpg").convert()
#?disp = ImageDisplayer(root, ImageTk.PhotoImage(image))
frame = ttk.Frame(root)
frame.grid(row=0, column=0, stick="NWES")
frame.columnconfigure(0, weight=1)
frame.columnconfigure(1, weight=1)
frame.rowconfigure(0, weight=1)
frame.rowconfigure(1, weight=0)



class RandomGrid:
    @staticmethod
    def make_text_changer(label_text):
        def change_text(*args):
            text = str(randint(1, 1000))
            label_text.set(text)
        return change_text
    
    def __init__(self, root, num_rows=10, num_cols=10):
        cell_width = "60p"
        self.callbacks = []

        for rowi in range(num_rows):
            for coli in range(num_cols):
                label_text = tk.StringVar()
                label = ttk.Label(root,
                        textvariable=label_text,
                        width=cell_width,
                        font="TkFixedFont",
                        foreground="green",
                        background="#000000")
                label.grid(row=rowi, column=coli)
                self.callbacks.append(RandomGrid.make_text_changer(label_text))
                
        for callback in self.callbacks: callback()
    
    
    def bind_motion(self, root):
        def call_everything(*args): 
            for callback in self.callbacks: callback(args)
        root.bind("<Motion>", call_everything)



class ScrolledImage:
    def __init__(self, root):
        lst = tk.Listbox(root, height=5)
        lst.grid(row=0, column=0, sticky="nsew")
        
        scroll = tk.Scrollbar(root, orient=tk.VERTICAL, command=lst.yview)
        scroll.grid(row=0, column=1, sticky="ns")
        lst.config(yscrollcommand=scroll.set)
        
        for i in range(1, 101):
            lst.insert("end", f"Line {i} of 100")
            
class ScrolledEnglishDict:
    def __init__(self, root):
        txt = tk.Text(root, wrap="none")
        txt.grid(row=0, column=0, sticky="nsew")
        with open("/usr/share/dict/words", "r") as words_file:
            txt.insert(1.0, words_file.read())
        
        scrolly = tk.Scrollbar(root, orient=tk.VERTICAL, command=txt.yview)
        scrolly.grid(row=0, column=1, sticky="ns")
        scrollx = tk.Scrollbar(root, orient=tk.HORIZONTAL, command=txt.xview)
        scrollx.grid(row=1, column=0, sticky="ew")
        txt["yscrollcommand"] = scrolly.set
        txt["xscrollcommand"] = scrollx.set


        
        

#?rand_grid = RandomGrid(frame)
#?rand_grid.bind_motion(root)

#?sc = ScrolledImage(frame)
#ScrolledEnglishDict(root)
#id = ImageDisplayer(frame, image=Image.open("img.jpg"),
#        width=100,
#        height=100)
#id.grid(row=0, column=0, sticky="nsew", columnspan=2)
#
#vscroll = tk.Scrollbar(frame, orient=tk.VERTICAL, command=id.yview)
#hscroll = ttk.Scrollbar(frame, orient=tk.HORIZONTAL, command=id.xview)
#vscroll.grid(row=0, column=2, sticky="ns")
#hscroll.grid(row=1, column=0, sticky="ew", columnspan=2)
#id["yscrollcommand"] = vscroll.set
#id["xscrollcommand"] = hscroll.set
#
#scale_down_button = ttk.Button(frame, text="-", command=lambda: id.scale_down())
#scale_up_button = ttk.Button(frame, text="+", command=lambda: id.scale_up())
#scale_down_button.grid(row=2, column=0, sticky="ew")
#scale_up_button.grid(row=2, column=1, sticky="ew")
#gen_img_button = ttk.Button(frame, text="crop", command=lambda: id.generate_image().show())
#gen_img_button.grid(row=3, column=0, sticky="ew", columnspan=2)


#?loader = ImageLoader(root)
#?loader.grid(row=0, column=0, sticky="NSEW")
img = Image.open("img.jpg")
disp = ImageDisplayerWrapper(root, image=img,
        out_file="/Users/johnrizkalla/Documents/image_extractor/test.png",
        command=lambda: disp.destroy())
disp.grid(row=0, column=0, sticky="nsew", columnspan=2)


root.columnconfigure(0, weight=1)
root.rowconfigure(0, weight=1)
# Bug fix for UnicodeDecodeError
while True:
    try:
        root.mainloop()
        break
    except UnicodeDecodeError: pass
