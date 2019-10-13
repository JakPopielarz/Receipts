# -*- coding: utf-8 -*-

from tkinter import filedialog, simpledialog, messagebox
import tkinter as tk
from PIL import ImageTk
import photo
import database
from receipt import Receipt

class Window(tk.Tk):
    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)
        self.title("Receipts")

        container = tk.Frame(self)
        container.pack(side="top", fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.database = database.Database()

        self.frames = {}

        self.frames["PhotoSelection"] = PhotoSelection(container, self)
        self.frames["DatabaseEntryForm"] = DatabaseEntryForm(container, self)

        self.frames["PhotoSelection"].grid(row=0, column=0, sticky="nsew")
        self.frames["DatabaseEntryForm"].grid(row=0, column=0, sticky="nsew")

        self.show_frame("PhotoSelection")
#        self.show_frame("DatabaseEntryForm")

    def show_frame(self, frame_name):
        frame = self.frames[frame_name]
        frame.tkraise()

    def pass_amount_to(self, receiver_frame_name, amount):
        frame = self.frames[receiver_frame_name]
        frame.amount = amount
        frame.amount_label.config(text="Amount: "+amount)

class PhotoSelection(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        self.selection_coords = []
#        receipts = [Receipt("3.09.2019", "10.00"), Receipt("1.09.2019", "1000.52")]
#        self.database = database.Database(receipts)

        # set up for the photo - create a scrollable canvas
        self.photo_frame = tk.Frame(self)
        self.photo_frame.grid()

        self.canvas = tk.Canvas(self.photo_frame, width=800, height=600)

        self.create_scrollbars()

        # load photo and set scrollregion so the scrollbars can work properly
        self.load_photo()
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

        self.bind_selection_events()

        again_button = tk.Button(self, text="Load photo",
                                 command=self.load_photo)
        again_button.grid()

    def create_scrollbars(self):
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

    def load_photo(self):
        self.canvas.delete("text")
        try:
            image_path = filedialog.askopenfilename(title="Select photo of a receipt",
                                                    filetypes=(("jpeg files", "*.jpg"),
                                                               ("png files", "*.png"),
                                                               ("all files", "*.*")))
            self.image = photo.Photo(image_path)
            self.set_canvas_photo()
            self.canvas.focus_set()
        except OSError: # if user chose a file which is not an image
            self.canvas.delete("photo")
            self.canvas.create_text(400, 300, tag="text",
                                    text="File is not an image")
        except AttributeError: # if nothing was chosen
            if not self.canvas.find_withtag("photo"):
                self.canvas.create_text(400, 300, tag="text",
                                        text="File not chosen")

    def set_canvas_photo(self):
        canvas_img = ImageTk.PhotoImage(self.image.get_PIL())
        self.canvas.create_image(0, 0, anchor="nw", tag="photo",
                                 image=canvas_img)
        self.canvas.image = canvas_img

        self.canvas.configure(scrollregion=self.canvas.bbox("photo"))

    def bind_selection_events(self):
        # set up canvas for selecting with drawing a rectangle
        self.canvas.bind("<Button-1>", self.draw_selection)
        self.canvas.bind("<B1-Motion>", self.update_selection)
        # that is deleted on mouse button release
        self.canvas.bind("<ButtonRelease-1>", self.select)

        # set up a shortcut to select the whole image
        self.canvas.bind("a", self.select_all)

    def draw_selection(self, event):
        if self.canvas.find_withtag("photo"):
            # convert coordinates of mouse on window to coordinates on canvas
            canvas_x, canvas_y = self.canvas.canvasx(0), self.canvas.canvasy(0)

            self.selection_coords = [canvas_x+event.x, canvas_y+event.y, 0, 0]

            # create a rectangle on canvas with top left coner in place of the click
            self.canvas.create_rectangle(self.selection_coords[0],
                                         self.selection_coords[1],
                                         self.selection_coords[0],
                                         self.selection_coords[1],
                                         outline="red", tags="selection")

    def update_selection(self, event):
        if self.canvas.find_withtag("photo"):
            # convert coordinates of mouse on window to coordinates on canvas
            canvas_x, canvas_y = self.canvas.canvasx(0), self.canvas.canvasy(0)

            self.selection_coords[2] = canvas_x+event.x
            self.selection_coords[3] = canvas_y+event.y

            # delete old selection
            self.canvas.delete("selection")

            # create new selection - from place clicked to current mouse position (if LMB held)
            self.canvas.create_rectangle(self.selection_coords[0],
                                         self.selection_coords[1],
                                         canvas_x+event.x,
                                         canvas_y+event.y,
                                         outline="red", tags="selection")

    def select_all(self, event):
        self.selection_coords = [0, 0,
                                 self.canvas.image.width(),
                                 self.canvas.image.height()]
        self.select(event)

    def select(self, _):
        if self.canvas.find_withtag("photo"):
            self.rectify_selection_coords()

            # crop and swap the image stored
            self.image.crop_image(self.selection_coords)
            self.image.resize_photo()
            self.image.create_contours()
#            self.image.draw_contours()
            self.image.create_bounding_rectangles()

            # gather responses and learning material
#            self.teach()

            self.image.draw_bounding_rectangles()
            recognized = self.image.recognize_digits()

            # swap displayed image
            self.canvas.delete("photo")
            self.set_canvas_photo()

            # move scrollbars to the upmost(vertical)/leftmost(horizontal) position
            self.canvas.yview_moveto(0)
            self.canvas.xview_moveto(0)

            # delete the selection rectangle
            self.canvas.delete("selection")

            # ask the user if digits were recognized correctly and act accordingly
            correct = tk.messagebox.askyesno("Digit recognition",
                                             """Were the digits recognized correctly?\n
                                             Recognized: """+recognized)

#            if correct:
#                # add samples to the knowledge-base
#                self.image.save_correct_recognition(recognized)
#            else:
#                # gather correct input and save it to the knowledge-base
#                recognized = self.teach()
#
            self.controller.pass_amount_to("DatabaseEntryForm", recognized)
            self.controller.show_frame("DatabaseEntryForm")
##            self.database.add_receipt(Receipt("10.09.2019", recognized))
##            print(self.database)

    def rectify_selection_coords(self):
        # if needed swap coordinates so they define a rectanle in order:
        # [top_left_x, top_left_y, bottom_right_x, bottom_right_y]
        if self.selection_coords[0] > self.selection_coords[2]:
            self.selection_coords[0], self.selection_coords[2] =\
            self.selection_coords[2], self.selection_coords[0]
        if self.selection_coords[1] > self.selection_coords[3]:
            self.selection_coords[1], self.selection_coords[3] =\
            self.selection_coords[3], self.selection_coords[1]

        # don't allow selecting outside the image
        self.selection_coords[2] = min(self.selection_coords[2],
                                       self.canvas.image.width())
        self.selection_coords[3] = min(self.selection_coords[3],
                                       self.canvas.image.height())

        # delete the image if whole selection outside of it
        if self.selection_coords[0] > self.canvas.image.width() or \
        self.selection_coords[1] > self.canvas.image.height():
            self.canvas.delete("photo")
            self.canvas.create_text(400, 300, tag="text",
                                    text="File not chosen")

    def teach(self):
        # collect correct input from user and add it to the knowledge-base
        amount = simpledialog.askstring("Correct amount",
                                        "Enter correct amount [always with 2 digits after coma]")
        if amount and len(amount) == len(self.image.bounding_rectangles)+1:
            self.image.save_correct_recognition(amount)

        return amount

class DatabaseEntryForm(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller

        self.amount = ""
        self.amount_label = tk.Label(self, text="Amount: "+ self.amount)
        self.amount_label.grid(row=0, column=0, columnspan=2)

        # create a field to enter the year value and a validation function for it
        self.year_label = tk.Label(self, text="Year:")
        year_vcmd = (self.register(self.validate_year))
        self.year_field = tk.Entry(self, validate="all", validatecommand=(year_vcmd, "%P"),
                                   exportselection=False)
        self.year_field.insert("end", "2019")

        self.year_label.grid(row=1, column=0)
        self.year_field.grid(row=1, column=1)

        # create a field to chose the month
        self.month_label = tk.Label(self, text="Month:")
        self.month_field = tk.Listbox(self, height=12, selectbackground="light blue")
        for month in ("January", "February", "March", "April", "May", "June",
                      "July", "August", "September", "October", "November",
                      "December"):
            self.month_field.insert("end", month)
        self.month_field.selection_set(0)

        self.month_label.grid(row=2, column=0)
        self.month_field.grid(row=2, column=1)

        # create a field to enter the day value and a validation function for it
        self.day_label = tk.Label(self, text="Day:")
        day_vcmd = (self.register(self.validate_day))
        self.day_field = tk.Entry(self, validate="all", validatecommand=(day_vcmd, "%P"),
                                  exportselection=False)
        self.day_field.insert("end", "1")

        self.day_label.grid(row=3, column=0)
        self.day_field.grid(row=3, column=1)

        self.add_button = tk.Button(self, text="Add receipt to database",
                                    command=self.add_receipt)
        self.add_button.grid(row=4, columnspan=2)

    def validate_year(self, text):
        return str.isdigit(text) or text == ""

    def validate_day(self, text):
        days_in_month = {"January": 31, "February": 29, "March": 31, "April": 30,
                         "May": 31, "June": 30, "July": 31, "August":31,
                         "September": 30, "October": 31, "November": 30,
                         "December": 31}
        month = self.month_field.get("active")

        if (str.isdigit(text) and 0 < int(text) <= days_in_month[month]) or\
        text == "":
            return True
        return False

    def add_receipt(self):
        if self.validate_year(self.year_field.get()) and\
        self.validate_day(self.day_field.get()):
            date = self.day_field.get() + "." + str(self.month_field.curselection()[0]+1)
            date += "." + self.year_field.get()

            self.controller.database.add_receipt(Receipt(date, self.amount))
        elif not self.validate_day(self.day_field.get()):
            self.day_field.config(fg="red")
        elif not self.validate_year(self.year_field.get()):
            self.year_field.config(fg="red")
        else:
            messagebox.showinfo("Ooops", "Something went wrong")
