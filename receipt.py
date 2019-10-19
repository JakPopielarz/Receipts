#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Oct 10 11:21:47 2019

@author: jakub
"""

class Receipt():
    def __init__(self, date, amount, tags):
        if type(date) == str:
            date = date.split(".")
            self.date = {"day": int(date[0]),
                         "month": int(date[1]),
                         "year": int(date[2])}
        elif type(date) == list:
            self.date = {"day": int(date[0]),
                         "month": int(date[1]),
                         "year": int(date[2])}

        self.amount = float(amount)
        
        months = ["", "January", "February", "March", "April", "May", "June",
                  "July", "August", "September", "October", "November",
                  "December"]
        self.tags = [months[self.date["month"]]]
        
        if type(tags) == str and tags != "":
            self.tags.append(tags)

        elif type(tags) == list:
            for tag in tags:
                if tag == "":
                    tags.remove(tag)

            self.tags = self.tags + tags

    def __str__(self):
        return "Date: " + self.get_printable_date() + "; Amount: " + str(self.amount) +\
                "; Tags: " + ", ".join(self.tags) 

    def get_printable_date(self):
        date = self.date.values()
        date = [str(x) for x in date]

        return ".".join(date)

    def to_list(self):
        arr = list(self.date.values())
        arr.append(self.amount)
        tags_str = " ".join(self.tags)
        arr.append(tags_str)

        return arr
