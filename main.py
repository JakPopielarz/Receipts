# -*- coding: utf-8 -*-

from tkinter import filedialog
import tkinter as tk
from PIL import Image, ImageTk

class Window():
    def __init__(self):
        self.root = tk.Tk()

        self.selection_topleft_coords = []

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

        # load photo and set scrollregion so the scrollbars can work properly
        self.load_photo()
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))


        # set up canvas for selecting with drawing a rectangle
        self.canvas.bind("<Button-1>", self.draw_selection)
        self.canvas.bind("<B1-Motion>", self.update_selection)
        # that is deleted on mouse button release
        self.canvas.bind("<ButtonRelease-1>", self.delete_selection)

        again_button = tk.Button(self.root, text="Load photo",
                                 command=self.load_photo)
        again_button.grid()

        self.root.mainloop()

    def load_photo(self):
        try:
            image_path = filedialog.askopenfilename(title="Select photo of a receipt",
                                                    filetypes=(("jpeg files", "*.jpg"),
                                                               ("all files", "*.*")))
            self.image = ImageTk.PhotoImage(Image.open(image_path))
            self.canvas.create_image(0, 0, anchor="nw", image=self.image)
        except OSError: # if user chose a file which is not an image
            self.canvas.configure(text="File is not an image")
        except AttributeError: # if nothing was chosen
            self.canvas.configure(text="File not chosen")

    def draw_selection(self, event):
        # convert coordinates of mouse on window to coordinates on canvas
        canvas_x, canvas_y = self.canvas.canvasx(0), self.canvas.canvasy(0)

        self.selection_topleft_coords = [canvas_x+event.x, canvas_y+event.y]

        # create a rectangle on canvas with top left coner in place of the click
        self.canvas.create_rectangle(self.selection_topleft_coords[0],
                                     self.selection_topleft_coords[1],
                                     self.selection_topleft_coords[0],
                                     self.selection_topleft_coords[1],
                                     outline="red", tags="selection")

    def update_selection(self, event):
        # convert coordinates of mouse on window to coordinates on canvas
        canvas_x, canvas_y = self.canvas.canvasx(0), self.canvas.canvasy(0)

        # delete old selection
        self.canvas.delete("selection")

        # create new selection - from place clicked to current mouse position (if LMB held)
        self.canvas.create_rectangle(self.selection_topleft_coords[0],
                                     self.selection_topleft_coords[1],
                                     canvas_x+event.x,
                                     canvas_y+event.y,
                                     outline="red", tags="selection")
        

    def delete_selection(self, event):
        self.canvas.delete("selection")

def main():
    window = Window()


if __name__ == "__main__":
    main()
