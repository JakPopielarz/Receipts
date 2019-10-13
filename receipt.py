#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Oct 10 11:21:47 2019

@author: jakub
"""

class Receipt():
    def __init__(self, date, amount):
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

    def __str__(self):

        return "Date: " + self.get_printable_date() + "; Amount: " + str(self.amount)

    def get_printable_date(self):
        date = self.date.values()
        date = [str(x) for x in date]

        return ".".join(date)

    def to_list(self):
        arr = list(self.date.values())
        arr.append(self.amount)

        return arr
