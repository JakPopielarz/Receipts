#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Oct 10 11:21:47 2019

@author: jakub
"""

class Receipt():
    def __init__(self, date, amount):
        date = date.split(".")
        self.date = {"day": int(date[0]),
                     "month": int(date[1]),
                     "year": int(date[2])}

        self.amount = amount

    def __str__(self):
        date = self.date.values()
        date = [str(x) for x in date]

        return "Date: " + ".".join(date) + "; Amount: " + str(self.amount)
