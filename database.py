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
                    tags = row[-1]
                    tags = tags[1:-1]
                    tags = tags.replace("'", "")
                    tags = tags.split(", ")
                    self.receipts.append(Receipt(row[:-2], row[-2], tags))

        except FileNotFoundError:
            self.receipts = []
            new_csv = True

        with open("receipts_summation.csv", "a") as file:
            csv_file = csv.writer(file)
            if new_csv:
                csv_file.writerow(["day", "month", "year", "amount", "tags"])

        self.available_tags = []
        for receipt in self.receipts:
            self.available_tags = self.available_tags + receipt.tags

    def __str__(self):
        string = ""
        for bill in self.receipts:
            string += str(bill) + "\n"

        return string

    def add_receipt(self, bill):
        self.receipts.append(bill)
        self.available_tags = self.available_tags + bill.tags
        with open("receipts_summation.csv", "a") as file:
            csv_file = csv.writer(file)
            csv_file.writerow(bill.to_list())

    def get_tags(self):
        return ", ".join(set(self.available_tags))
#        return ", ".join(self.available_tags)
