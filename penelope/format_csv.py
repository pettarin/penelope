#!/usr/bin/env python
# coding=utf-8

"""
Read/write CSV dictionaries.
"""

from __future__ import absolute_import
import io

from penelope.utilities import print_debug
from penelope.utilities import print_error

__author__ = "Alberto Pettarin"
__copyright__ = "Copyright 2012-2016, Alberto Pettarin (www.albertopettarin.it)"
__license__ = "MIT"
__version__ = "3.1.3"
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


# TODO should use csv module instead
def read(dictionary, args, input_file_paths):
    csv_fs = escape(args.csv_fs)
    csv_ls = escape(args.csv_ls)
    for input_file_path in input_file_paths:
        print_debug("Reading from file '%s'..." % (input_file_path), args.debug)
        input_file_object = io.open(input_file_path, "rb")
        data_bytes = input_file_object.read()                       # bytes
        data_unicode = data_bytes.decode(args.input_file_encoding)  # unicode
        input_file_object.close()
        lines = data_unicode.split(csv_ls)
        if args.csv_ignore_first_line:
            lines = lines[1:]
        for line in lines:
            array = line.split(csv_fs)
            if len(array) >= 2:
                headword = array[0]
                definition = line[len(headword) + 1:]
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
        output_file_obj = io.open(output_file_path, "wb")
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
