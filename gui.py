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

        # create a container for all screens
        container = tk.Frame(self)
        container.pack(side="top", fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.database = database.Database()

        # create and prepare all the screens
        self.frames = {}

        self.frames["MainMenu"] = MainMenu(container, self)
        self.frames["PhotoSelection"] = PhotoSelection(container, self)
        self.frames["DatabaseEntryForm"] = DatabaseEntryForm(container, self)

        self.frames["MainMenu"].grid(row=0, column=0, sticky="nsew")
        self.frames["PhotoSelection"].grid(row=0, column=0, sticky="nsew")
        self.frames["DatabaseEntryForm"].grid(row=0, column=0, sticky="nsew")

        # display the first screen
        self.show_frame("MainMenu")

    def show_frame(self, frame_name):
        frame = self.frames[frame_name]
        frame.tkraise()

        if frame_name == "PhotoSelection":
            frame.load_photo()

    def pass_amount_to(self, receiver_frame_name, amount):
        frame = self.frames[receiver_frame_name]
        frame.amount = amount
        frame.amount_label.config(text="Amount: "+amount)

class MainMenu(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller

        instructions = """---INSTRUCTIONS---

- select a photo to analyze -
- click, hold and drag to select area with the sum (cannot change the selection after releasing LMB) -
- approve or rectify the recognition -
- choose a date for the receipt, add it to the database -
- repeat, if you wish -
"""

        self.about = tk.Label(self, text=instructions)
        self.about.pack()

        self.go_button = tk.Button(self, text="Load photo",
                                   command=lambda: self.controller.show_frame("PhotoSelection"))
        self.go_button.pack()

class PhotoSelection(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        self.selection_coords = []

        # set up for the photo - create a scrollable canvas
        self.photo_frame = tk.Frame(self)
        self.photo_frame.grid()

        self.canvas = tk.Canvas(self.photo_frame, width=800, height=600)

        self.create_scrollbars()

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

        if self.canvas.find_withtag("photo"):
            self.canvas.delete("photo")

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

        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

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
        chose_selection = tk.messagebox.askyesno("Are you sure?",
                                                 "Are you sure you want to select this region?")

        if chose_selection:
            self.analyze_selection()
        else:
            self.canvas.delete("selection")

    def analyze_selection(self):
        if self.canvas.find_withtag("photo"):
            self.rectify_selection_coords()

            # crop and swap the image stored
            self.image.select_fragment(self.selection_coords)
            self.image.create_contours()
#            self.image.draw_contours()
            self.image.create_bounding_rectangles()

            # gather responses and learning material
# UNCOMMENT if you want to create a new set of samples for the algorithm to learn
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

            # change to False if you do not want the app to create new samples
            will_teach = False
            if will_teach:
                if correct:
                    # add samples to the knowledge-base
                    self.image.save_correct_recognition(recognized)
                else:
                    # gather correct input and save it to the knowledge-base
                    recognized = self.teach()
            else:
                recognized = self.get_correct_recognition()

            self.canvas.delete("photo")
            if recognized:
                self.controller.pass_amount_to("DatabaseEntryForm", recognized)
                self.controller.show_frame("DatabaseEntryForm")

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

    def get_correct_recognition(self):
        # collect correct input from user
        amount = ""
        message=""
        number_of_rectangles = len(self.image.bounding_rectangles)+1

        while len(amount) != number_of_rectangles:
            amount = simpledialog.askstring("Correct amount",
                                            message +\
                                            "Enter correct amount [always with 2 digits after coma]")
            if not amount:
                self.controller.show_frame("PhotoSelection")
                break
            elif len(amount) < number_of_rectangles:
                message = "Too few characters entered"
            else:
                message = "Too many characters entered"

        return amount

    def teach(self):
        amount = self.get_correct_recognition()
        if amount:
            self.image.save_correct_recognition(amount)

        return amount

class DatabaseEntryForm(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller

        row_index = 0
        self.saved = False

        # create a space for messages for the user
        self.message = tk.Label(self)
        self.message.grid(row=row_index, column=0, columnspan=4)

        row_index += 1

        # display the recognized amount
        self.amount = ""
        self.amount_label = tk.Label(self, text="Amount: "+ self.amount)
        self.amount_label.grid(row=row_index, column=0, columnspan=2)

        # instruct the user how to enter tags
        self.tags_disclaimer = tk.Label(self, text="ENTER TAGS SEPARATED WITH A COMA AND SPACE",
                                        fg="blue")
        self.tags_disclaimer.grid(row=row_index, column=2, columnspan=2)

        row_index += 1

        # create a field to enter the year value and a validation function for it
        self.year_label = tk.Label(self, text="Year:")
        year_vcmd = (self.register(self.validate_year))
        self.year_field = tk.Entry(self, validate="all", validatecommand=(year_vcmd, "%P"),
                                   exportselection=False)
        self.year_field.insert("end", "2019")

        self.year_label.grid(row=row_index, column=0)
        self.year_field.grid(row=row_index, column=1)

        # display available tags
        self.current_tags_label = tk.Label(self, text="Current tags: ")
        self.current_tags_listed = tk.Label(self, text=self.controller.database.get_tags(),
                                            justify="left")

        self.current_tags_label.grid(row=row_index, column=2)
        self.current_tags_listed.grid(row=row_index, column=3, rowspan=2, sticky="n")
        self.current_tags_listed["wraplength"] = 500 - self.current_tags_listed.winfo_rootx()

        row_index += 1

        # create a field to chose the month
        self.month_label = tk.Label(self, text="Month:")
        self.month_field = tk.Listbox(self, height=12, selectbackground="light blue")
        for month in ("January", "February", "March", "April", "May", "June",
                      "July", "August", "September", "October", "November",
                      "December"):
            self.month_field.insert("end", month)
        self.month_field.selection_set(0)

        self.month_label.grid(row=row_index, column=0)
        self.month_field.grid(row=row_index, column=1)

        row_index += 1

        # create a field to enter the day value and a validation function for it
        self.day_label = tk.Label(self, text="Day:")
        day_vcmd = (self.register(self.validate_day))
        self.day_field = tk.Entry(self, validate="all", validatecommand=(day_vcmd, "%P"),
                                  exportselection=False)
        self.day_field.insert("end", "1")

        self.day_label.grid(row=row_index, column=0)
        self.day_field.grid(row=row_index, column=1)

        # create a field for tags
        self.tags_entry_label = tk.Label(self, text="Tags:")
        self.tags_field = tk.Entry(self, exportselection=False)

        self.tags_entry_label.grid(row=row_index, column=2)
        self.tags_field.grid(row=row_index, column=3)

        row_index += 1

        self.add_button = tk.Button(self, text="Add receipt to database",
                                    command=self.add_receipt)
        self.add_button.grid(row=row_index, columnspan=4, sticky="nsew")

        row_index += 1

        self.load_photo_button = tk.Button(self, text="Load another photo",
                                           command=self.load_photo)
        self.load_photo_button.grid(row=row_index, columnspan=4, sticky="nsew")

        row_index += 1

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
        # ask if user wants to save receipt again (if was savd before)
        if self.saved:
            self.saved = not(tk.messagebox.askyesno("Are you sure?",
                                                    "Looks like you already did that. Save again?"))

        # save recceipt if validated
        if self.validate_year(self.year_field.get()) and\
        self.validate_day(self.day_field.get()) and not self.saved:
            date = self.day_field.get() + "." + str(self.month_field.curselection()[0]+1)
            date += "." + self.year_field.get()

            tags = self.tags_field.get().split(", ")

            self.controller.database.add_receipt(Receipt(date, self.amount, tags))
            self.update_tags()
            self.saved = True
            self.message.config(text="Receipt saved succesfully!", fg="green")

        # if not validate put feedback in appropriate field
        elif not self.validate_day(self.day_field.get()):
            self.day_field.config(fg="red")
        elif not self.validate_year(self.year_field.get()):
            self.year_field.config(fg="red")

        elif self.saved:
            pass

        # shouldn't really reach this point ever
        # but in case it does display something for the user
        else:
            messagebox.showinfo("Ooops", "Something went wrong")

    def load_photo(self):
        # if receipt was saved - select another one
        if self.saved:
            self.controller.show_frame("PhotoSelection")

        # if receipt was not saved - ask if user is sure he wants to proceed
        # then act accordingly
        else:
            sure = tk.messagebox.askyesno("Are you sure?",
                                          """You didn't save data to the database.
                                          Do you want to continue?""")
            if sure:
                self.controller.show_frame("PhotoSelection")
            else:
                pass
        self.saved = False

    def update_tags(self):
        self.current_tags_listed["text"] = self.controller.database.get_tags()
