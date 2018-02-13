class ImageDisplayer(tk.Canvas):
    """
    Displays an image.
    Supports scaling, scrolling, and adding overlays.
    """
    
    
    def __init__(self, *args, **kwargs):
        """
        Create an ImageDisplayer.
        args, and kwargs are the same as the ones for `tkinter.Canvas` with the addition of the following:
        
        `width` and `height` are used to size the canvas on the screen 
        but the image size is used to calculate the size of the canvas.
        
        - `image`: a PIL image to display
        
        """
        
        try:
            img = kwargs["image"]
            del kwargs["image"]
        except KeyError:
            img = TkImage()
        self.img = img # resizes
        self.orig_img = img # retains it's original size
        self.tk_image = ImageTk.PhotoImage(self.img.convert())
        
        kwargs["scrollregion"] = (0, 0, img.width, img.height)
        
        super().__init__(*args, **kwargs)
        
        self.scale_factor = 1
        
        self.image_id = self.create_image(0, 0, anchor="nw", image=self.tk_image)
        
    def scale_down(self, amount=0.1):
        """
        Scale down the image by an amount (the minimum is 0.001).
        :param amount: the amount. Defaults to 0.1
        """
        
        self.scale_factor -= amount
        if self.scale_factor <= 0: self.scale_factor = 0.001
        print(f"scale factor: {self.scale_factor}")
        self.config(scrollregion=(0, 0, 
            self.orig_img.width * self.scale_factor,
            self.orig_img.height * self.scale_factor))
        
        # resize the image
        self.img = self.orig_img.resize((
            int(self.orig_img.width * self.scale_factor),
            int(self.orig_img.height * self.scale_factor)))
        self.tk_image = ImageTk.PhotoImage(self.img)
        # redraw the image
        self.delete(self.image_id)
        self.image_id = self.create_image(0, 0, anchor="nw", image=self.tk_image)
        
    def scale_up(self, amount=0.1):
        """
        Same as `scale_down(-amount)`.
        """
        self.scale_down(-amount)
        
