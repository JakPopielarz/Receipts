#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Oct 10 11:23:32 2019

@author: jakub
"""

class Database():
    def __init__(self, receipts=[]):
        self.receipts = receipts

    def __str__(self):
        string = ""
        for bill in self.receipts:
            string += str(bill) + "\n"

        return string

    def add_receipt(self, bill):
        self.receipts.append(bill)
