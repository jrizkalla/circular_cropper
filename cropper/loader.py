import tkinter as tk
import tkinter.filedialog
import tkinter.simpledialog
from tkinter import ttk
from os import path
from functools import partial
import io

from PIL import Image

import requests as http

from urllib.parse import urlparse, urlunparse

class LoadingDialog(tk.Toplevel):
    """
    A dialog that displays a progress bar and, if an error occurs, an error message.
    Use `report_error` to hide the progress bar and display a text error.
    """
    
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.transient(parent)
        
        main_frame = ttk.Frame(self)
        main_frame.grid(row=0, column=0, sticky="nsew")
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        
        self.info_label = ttk.Label(main_frame, text="Loading...")
        self.info_label.grid(row=0, column=0)
        
        self.prog_bar = ttk.Progressbar(main_frame, mode="indeterminate")
        self.prog_bar.grid(row=1, column=0, sticky="nsew")
        self.prog_bar.start()
        
        
    def report_error(self, desc=""):
        """
        Remove the progress bar and report an error.
        :param desc: the error to report
        """
        
        self.prog_bar.destroy()
        del self.prog_bar
        
        self.info_label.configure(text="Error: ")
        
        self.error_label = ttk.Label(self, text=desc)
        self.error_label.grid(row=1, column=0, sticky="nsew")
        print("Reporting error")
        
        
        
        

class ImageTable(tk.Canvas):
    """
    A table of URLs mapped to IDs.
    """
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.bind("<Configure>", self._on_configure)
        self.columnconfigure(0, weight=1)
        self.entry_frames = []
        
    def _on_configure(self, *args):
        self["scrollregion"] = (0, 0, self.winfo_reqwidth(), self.winfo_reqheight())
        
    def add_entry(self, url=None, id_=None):
        """
        Add a new entry to the table.
        """
        url = url if url is not None else ""
        id_ = id_ if id_ is not None else ""
        
        entry = ttk.Frame(self, relief="ridge")
        url_box = ttk.Entry(entry, name="url_field")
        id_box = ttk.Entry(entry, name="id_field")
        arrow_label = ttk.Label(entry, text="\u2192")
        crop_button = ttk.Button(entry, name="crop_button", text="     crop     ",
                command=partial(self._on_crop, len(self.entry_frames)))
        
        url_box.grid(row=0, column=0, sticky="nswe")
        id_box.grid(row=0, column=2, sticky="nswe")
        arrow_label.grid(row=0, column=1, sticky="nsew")
        crop_button.grid(row=0, column=3)
        
        self.entry_frames.append(entry)
        entry.columnconfigure(0, weight=1)
        entry.grid(row=len(self.entry_frames)-1, column=0,
                sticky="nsew")
        
        # also update the scrollregion to make it bigger
        self._on_configure()
        
        # placeholders for the inputs
        url_box.insert(0, "File path or URL")
        id_box.insert(0, "output filename")
        def _remove_placeholder(box, *args, **kwargs):
            box.delete(0, "end")
            box.unbind("<FocusIn>")
        url_box.bind("<FocusIn>", partial(_remove_placeholder, url_box))
        id_box.bind("<FocusIn>", partial(_remove_placeholder, id_box))
    
        
        
    def _on_crop(self, idx):
        url_or_filename = self.entry_frames[idx].children["url_field"].get()
        id_ = self.entry_frames[idx].children["id_field"].get().strip()
        ld = LoadingDialog(self)
        
        def _get_response():
            try:
                # is it a filename
                if path.isfile(url_of_filename):
                    img = Image.open(url_or_filename)
                else:
                    if url.scheme == "":
                        url = url._replace(scheme="http")
                    response = http.get(urlunparse(url))
                    response.raise_for_status()
                    
                    # is the reponse an image
                    img = Image.open(io.BytesIO(response.content))
                    
                img.show()
                
                ld.destroy()
                self.entry_frames[idx].children["crop_button"].configure(text="crop again")
            except http.ConnectionError:
                ld.report_error("Unable to connect. Please check the URL and your internet connection")
            except Exception as e:
                print(type(e))
                ld.report_error(str(e))
        
        if id_ == "":
            ld.report_error("ID is empty")
        else:
            self.after(100, _get_response)
        
        
    def yview(self, *args):
        print("yview")
        super().yview(*args)
        

class ImageLoader(ttk.Frame):
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        dir_var = tk.StringVar()
        
        text_entry_style = ttk.Style()
        text_entry_style.configure("DirInput.TEntry",
                background="white"
                )
        
        sources_label = ttk.Label(self, text="Image Sources")
        
        mapping = ImageTable(self)
        mapping_scroll = ttk.Scrollbar(self, orient="vertical",
                command=mapping.yview)
        mapping["yscrollcommand"] = mapping_scroll.set
        
        out_dir_label = ttk.Label(self, text="Output directory: ")
        out_dir_input = ttk.Entry(self, 
                style="DirInput.TEntry",
                textvariable=dir_var)
        dir_var.set(path.expanduser("~"))
        dir_var.trace("w", self._on_dir_change)
        
        # buttons
#?        help_button = ttk.Button(self, text="?")
        add_button= ttk.Button(self, text="+", command=lambda: mapping.add_entry())
        choose_button = ttk.Button(self, text="choose",
                command=lambda: dir_var.set(tk.filedialog.askdirectory()))
        
        # positioning:
        self.rowconfigure(1, weight=1)
        self.rowconfigure(2, weight=1)
        self.rowconfigure(3, weight=1)
        self.columnconfigure(0, pad=10)
        self.columnconfigure(1, weight=1)
        
        sources_label.grid(row=0, column=0, sticky="w")
#?        help_button.grid(row=0, column=2, sticky="nsew")
        
        mapping.grid(row=1, column=0, columnspan=2, rowspan=3, sticky="nesw")
        mapping_scroll.grid(row=1, column=2, rowspan=3, sticky="ns")
        add_button.grid(row=1, column=3, sticky="n")
        add_button.focus_set()
        
        out_dir_label.grid(row=4, column=0, sticky="e", pady=10)
        out_dir_input.grid(row=4, column=1, sticky="ew")
        choose_button.grid(row=4, column=3, sticky="w")
        
        self.dir_var = dir_var
        self.text_entry_style = text_entry_style
        
        self.after(100, lambda: mapping.add_entry())
        
    def _on_dir_change(self, *args):
        # validate it
        valid = path.isdir(self.dir_var.get())
        print(f"Directory {'is' if valid else 'isnt'} valid")
        self.text_entry_style.configure("DirInput.TEntry",
                background="white" if valid else "#ffddd8")
