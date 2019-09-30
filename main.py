# -*- coding: utf-8 -*-

from tkinter import filedialog
import tkinter as tk
from PIL import Image, ImageTk

class Window():
    def __init__(self):
        self.root = tk.Tk()
        
        # set up for the photo - create a scrollable canvas
        self.photo_frame = tk.Frame(self.root)
        self.photo_frame.grid()
        
        self.canvas = tk.Canvas(self.photo_frame, width=500, height=500)

        # create and set horizontal scrollbar for the photo
        self.scroll_x = tk.Scrollbar(self.photo_frame, orient="horizontal",
                                     command=self.canvas.xview)
        self.scroll_x.pack(side="bottom", fill="x")

        # create and set vertical scrollbar for the photo
        self.scroll_y = tk.Scrollbar(self.photo_frame, orient="vertical",
                                     command=self.canvas.yview)
        self.scroll_y.pack(side="right", fill="y")
        
        self.canvas.configure(yscrollcommand=self.scroll_y.set,
                              xscrollcommand=self.scroll_x.set)
        self.canvas.pack(side="left", fill="both", expand=True)


        self.load_photo()
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))


        again_button = tk.Button(self.root, text="Load photo",
                                 command=self.load_photo)
        again_button.grid()
#        again_button.pack()

        self.root.mainloop()

    def load_photo(self):
        try:
            image_path = filedialog.askopenfilename(title="Select photo of a receipt",
                                                    filetypes=(("jpeg files", "*.jpg"),
                                                               ("all files", "*.*")))
            self.image = ImageTk.PhotoImage(Image.open(image_path))
            self.canvas.create_image(0, 0, anchor="nw", image=self.image)
        except OSError:
            self.canvas.configure(text="File is not an image")
        except AttributeError:
            self.canvas.configure(text="File not chosen")

def main():
    window = Window()


if __name__ == "__main__":
    main()
