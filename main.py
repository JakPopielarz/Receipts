# -*- coding: utf-8 -*-

from tkinter import filedialog
import tkinter as tk
from PIL import Image, ImageTk

window = tk.Tk()

imagefile = filedialog.askopenfilename(title = "Select photo of a receipt",
                                       filetypes = (("jpeg files","*.jpg"),
                                                    ("all files","*.*")))
img = ImageTk.PhotoImage(Image.open(imagefile))
lbl = tk.Label(window, image = img).pack()

window.mainloop()
