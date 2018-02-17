import tkinter as tk
from tkinter import ttk

from PIL import Image, ImageTk, ImageDraw
import math

class ImageDisplayerWrapper(ttk.Frame):
    """
    Provides a wrapper around `ImageDisplayer` for zooming, scrolling, and cropping.
    """
    
    def __init__(self, parent, *args, **kwargs):
        
        try:
            image = kwargs["image"]
            self.out_file = kwargs["out_file"]
            del kwargs["image"]
            del kwargs["out_file"]
        except KeyError as e:
            raise TypeError(f"missing {e.args[0]} keyword argument") from None
        
        try:
            self.out_format = kwargs["out_format"]
            del kwargs["out_format"]
        except KeyError:
            self.out_format = "png"
        try:
            self._crop_command = kwargs["command"]
            del kwargs["command"]
        except KeyError:
            self._crop_command = lambda self: ...
        
        super().__init__(parent, *args, **kwargs)
        
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)
        self.rowconfigure(0, weight=1)
        self.rowconfigure(1, weight=0)
        
        displayer = ImageDisplayer(self, image=image, width=100, height=100)
        displayer.grid(row=0, column=0, sticky="nsew", columnspan=2)
        
        vscroll = ttk.Scrollbar(self,
                orient="vertical", 
                command=displayer.yview)
        hscroll = ttk.Scrollbar(self,
                orient="horizontal", 
                command=displayer.xview)
        vscroll.grid(row=0, column=2, sticky="ns")
        hscroll.grid(row=1, column=0, sticky="ew", columnspan=2)
        displayer["yscrollcommand"] = vscroll.set
        displayer["xscrollcommand"] = hscroll.set
        
        scale_down_button = ttk.Button(self, text="-",
                command=lambda: displayer.scale_down())
        scale_up_button = ttk.Button(self, text="+",
                command=lambda: displayer.scale_up())
        scale_down_button.grid(row=2, column=0, sticky="ew")
        scale_up_button.grid(row=2, column=1, sticky="ew")
        gen_img_button = ttk.Button(self, text="crop",
                command=self._on_crop)
        gen_img_button.grid(row=3, column=0, sticky="ew", columnspan=2)
        
        self.displayer = displayer
        
    def _on_crop(self, *args):
        # crop the image and save it
        image = self.displayer.generate_image()
        image.save(self.out_file, format=self.out_format)
        self._crop_command()
        
    

class ImageDisplayer(tk.Canvas):
    """
    Displays an image.
    Supports scaling, scrolling, and adding overlays.
    """
    
    
    def __init__(self, *args, **kwargs):
        """
        Create an ImageDisplayer.
        
        `width` and `height` are used to size the canvas on the screen 
        but the image size is used to calculate the size of the canvas.
        
        `args`, and `kwargs` are the same as the ones for `tkinter.Canvas` with the addition of the following:
        
        - `image`: a PIL image to display
        - `bindmousewheel`: if False, don't bind `<MouseWheel>` to resizing the image (defaults to `True`)
        - `bindmousedrag`: if False, don't scroll with mouse motion (defaults to `True`)
        - `overlaycircle`: if False, don't draw an overlay circle (defaults to `True`)
        - `extend_image`: if False, don't draw extra white space around the image (defaults to `True`)
        
        """
        
        try:
            img = kwargs["image"].convert("RGBA")
            del kwargs["image"]
        except KeyError:
            img = Image.new("RGBA", 500, 500, fill=(255, 255, 255))
        try:
            extend_image = kwargs["extend_image"]
            del kwargs["extend_image"]
        except KeyError: extend_image = True
        
        # pad the image with whitespace on 4 sides
        if extend_image:
            self.img = Image.new("RGBA", (img.width * 2, img.height * 2), "white")
            self.img.paste(img, box=(img.width//2, img.height//2))
        else:
            self.img = img
        
        self.orig_img = self.img # retains it's original size
        kwargs["scrollregion"] = (0, 0, self.img.width, self.img.height)
        
        try:
            bind_mousewheel = kwargs["bind_mousewheel"]
            del kwargs["bind_mousewheel"]
        except KeyError: bind_mousewheel = True
        
        try:
            bind_mousedrag = kwargs["bind_mousedrag"]
            del kwargs["bind_mousedrag"]
        except KeyError: bind_mousedrag = True
        
        try:
            overlay_circle = kwargs["overlaycircle"]
            del kwargs["overlaycircle"]
        except KeyError: overlay_circle = True
        
        super().__init__(*args, **kwargs)
        
        self._scale_factor = 1
        self._xoffset = 0
        self._yoffset = 0
        
        if not overlay_circle:
            # delete _draw_overlay_circle
            self._draw_overlay_circle = lambda: ...
        
        self._draw_overlay_circle()
        self.tk_image = ImageTk.PhotoImage(self.img)
        self.create_image(0, 0, anchor="nw", image=self.tk_image)
        
        self.bind("<Configure>", self._on_resize)
        if bind_mousedrag:
            self.bind("<ButtonPress-1>", self._on_mouse_press)
            self.bind("<ButtonRelease-1>", self._on_mouse_release)
            self.bind("<B1-Motion>", self._on_mouse_motion)
        self.bind("<MouseWheel>", self._on_scroll)
        self.__mouse_pressed = False
        
            
    def _on_resize(self, event):
        self.scale_down(0)
    
    def _on_mouse_press(self, event):
        self.__mouse_pressed = True
        self.__mouse_loc = (event.x, event.y)
        
    def _on_mouse_release(self, event):
        self.__mouse_pressed = False
    
    def _on_mouse_motion(self, event):
        if self.__mouse_pressed:
            # do the drag
            xdelta = event.x - self.__mouse_loc[0]
            ydelta = event.y - self.__mouse_loc[1]
            self.__mouse_loc = (event.x, event.y)
            xmoveto = self._xoffset / self.img.width - xdelta / self.img.width
            ymoveto = self._yoffset / self.img.height - ydelta / self.img.height
            if xmoveto < 0: xmoveto = 0
            if ymoveto < 0: ymoveto = 0
            
            if xdelta != 0: self.xview("moveto", xmoveto)
            if ydelta != 0: self.yview("moveto", ymoveto)
        
    def _on_scroll(self, event):
        print(f"Scroll: {event.delta}")
            
    
    def xview(self, command, what):
        assert command == "moveto", "scroll command not supported"
        self._xoffset = int(float(what) * float(self.img.width))
        ret = super().xview(command, what)
        self.scale_down(0)
        return ret
    
    def yview(self, command, what):
        assert command == "moveto", "scroll command not supported"
        self._yoffset = int(float(what) * float(self.img.height))
        ret = super().yview(command, what)
        self.scale_down(0)
        return ret
    
    def calculate_radius(self, width, height):
        """
        Calculate the radius of the circle inside.
        
        Override to change how the radius is calculated::
        
            >>> ic = ImageDisplayer(...)
            >>> ic.calculate_radius = lambda s, w, h: min(w, h) // 4
        
        :param w: the width of the window
        :param h: the height of the window
        :return: the radius of the circle
        """
        return min(width, height) // 4
    
    def _circle_radius(self):
        width, height = (self.winfo_width(), self.winfo_height())
        return int(self.calculate_radius(width, height))

    def _draw_overlay_circle(self):
        width, height = (self.winfo_width(), self.winfo_height())
        radius = self._circle_radius()
        
        x1 = (width - 2 * radius) // 2 + self._xoffset
        y1 = (height - 2 * radius) // 2 + self._yoffset
        x2 = x1 + 2 * radius
        y2 = y1 + 2 * radius
        
        # radius of the circle should
        foreground = Image.new("RGBA", (self.img.width, self.img.height), (0, 0, 0, 100))
        draw = ImageDraw.Draw(foreground)
        draw.ellipse((x1, y1, x2, y2), fill=(255, 255, 255, 0), outline="white")
        self.img = Image.alpha_composite(self.img, foreground)
        
        
    def generate_image(self):
        """
        Generate a cropped image based on the current window size and zoom level.
        The image is cropped to a circle with the standard radius.
        
        :see calculate_radius:
        """
        
        # work on the original image to avoid resize losses
        # scale offsets and width height for the original image
        xo = int(self._xoffset // self._scale_factor)
        yo = int(self._yoffset // self._scale_factor)
        # use the width and height of the window to know where to crop (also scaled)
        width = int(self.winfo_width() // self._scale_factor)
        height = int(self.winfo_height() // self._scale_factor)
        
        img = self.orig_img.crop((xo, yo, xo + width, yo + height))
        
        # create a completely transparent mask
        mask = Image.new("1", (width, height), 0)
        # and draw a non-transparent circle in the middle (also scale the radius)
        diam = 2*self._circle_radius() // self._scale_factor
        draw = ImageDraw.Draw(mask)
        x1 = (width - diam) // 2
        y1 = (height - diam) // 2
        draw.ellipse((x1, y1, x1 + diam, y1 + diam), fill=1)
        
        # use the mask as the new alpha for img
        img.putalpha(mask)
        
        return img
        
        
        
    def scale_down(self, amount=0.1):
        """
        Scale down the image by an amount (the minimum is 0.001).
        :param amount: the amount. Defaults to 0.1
        """
        
        self._scale_factor -= amount
        if self._scale_factor <= 0: self._scale_factor = 0.001
        self.config(scrollregion=(0, 0, 
            self.orig_img.width * self._scale_factor,
            self.orig_img.height * self._scale_factor))
        
        # resize the image
        self.img = self.orig_img.resize((
            int(self.orig_img.width * self._scale_factor),
            int(self.orig_img.height * self._scale_factor)))
        self._draw_overlay_circle()
        
        
        self.tk_image = ImageTk.PhotoImage(self.img)
        # redraw the image
        self.delete("image")
        
        self.create_image(0, 0, anchor="nw", image=self.tk_image, tag="image")
        
    def scale_up(self, amount=0.1):
        """
        Same as `scale_down(-amount)`.
        """
        self.scale_down(-amount)
        
