#!/usr/bin/env python
# coding=utf-8

"""
Read/write CSV dictionaries.
"""

from __future__ import absolute_import
from io import open

import csv

from penelope.utilities import print_debug
from penelope.utilities import print_error

__author__ = "Alberto Pettarin"
__copyright__ = "Copyright 2012-2016, Alberto Pettarin (www.albertopettarin.it)"
__license__ = "MIT"
__version__ = "3.1.2"
__email__ = "alberto@albertopettarin.it"
__status__ = "Production"

ASCII_ESCAPES = [
    ("\\a", "\a"),
    ("\\b", "\b"),
    ("\\t", "\t"),
    ("\\n", "\n"),
    ("\\v", "\v"),
    ("\\f", "\f"),
    ("\\r", "\r")
]

def escape(string):
    ret = string
    for s, r in ASCII_ESCAPES:
        ret = ret.replace(s, r)
    return ret

def read(dictionary, args, input_file_paths):
    csv_fs = escape(args.csv_fs)
    csv_ls = escape(args.csv_ls)
    for input_file_path in input_file_paths:
        print_debug("Reading from file '%s'..." % (input_file_path), args.debug)
        with open(input_file_path, "rb") as input_file_object:
            input_file_reader = csv.reader(
                input_file_object,
                dialect='excel',
            )
            if args.csv_ignore_first_line:
                input_file_reader.next()
            for row in input_file_reader:
                if len(row) < 2:
                    print_error("invalid csv row: %r"%row)
                    continue
                headword = row[0].decode("utf-8")
                definition = row[1].decode("utf-8")
                if args.ignore_case:
                    headword = headword.lower()
                dictionary.add_entry(headword=headword, definition=definition)
        print_debug("Reading from file '%s'... success" % (input_file_path), args.debug)
    return dictionary

def write(dictionary, args, output_file_path):
    csv_fs = escape(args.csv_fs)
    csv_ls = escape(args.csv_ls)
    try:
        print_debug("Writing to file '%s'..." % (output_file_path), args.debug)
        output_file_obj = open(output_file_path, "wb")
        for index in dictionary.entries_index_sorted:
            entry = dictionary.entries[index]
            string = u"%s%s%s%s" % (
                entry.headword,
                csv_fs,
                entry.definition,
                csv_ls
            )
            output_file_obj.write(string.encode("utf-8"))
        output_file_obj.close()
        print_debug("Writing to file '%s'... success" % (output_file_path), args.debug)
        return [output_file_path]
    except:
        print_error("Writing to file '%s'... failure" % (output_file_path))
        return None



