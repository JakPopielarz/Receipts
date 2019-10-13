#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Oct 10 11:23:32 2019

@author: jakub
"""

import csv
from receipt import Receipt

class Database():
    def __init__(self):
        self.receipts = []
        new_csv = False

        try:
            with open("receipts_summation.csv", "r") as csv_file:
                read_file = csv.reader(csv_file)

                for row in list(read_file)[1:]:
                    self.receipts.append(Receipt(row[:-1], row[-1]))

        except FileNotFoundError:
            self.receipts = []
            new_csv = True

        with open("receipts_summation.csv", "a") as file:
            csv_file = csv.writer(file)
            if new_csv:
                csv_file.writerow(["day", "month", "year", "amount"])

    def __str__(self):
        string = ""
        for bill in self.receipts:
            string += str(bill) + "\n"

        return string

    def add_receipt(self, bill):
        self.receipts.append(bill)
        with open("receipts_summation.csv", "a") as file:
            csv_file = csv.writer(file)
            csv_file.writerow(bill.to_list())
