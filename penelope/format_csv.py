#!/usr/bin/env python
# coding=utf-8

"""
Read/write CSV dictionaries.
"""

from io import open

from utilities import print_debug
from utilities import print_error

__author__ = "Alberto Pettarin"
__copyright__ = "Copyright 2012-2015, Alberto Pettarin (www.albertopettarin.it)"
__license__ = "MIT"
__version__ = "3.0.0"
__email__ = "alberto@albertopettarin.it"
__status__ = "Production"

def read(dictionary, args, input_file_paths):
    for input_file_path in input_file_paths:
        print_debug("Reading from file '%s'..." % (input_file_path), args.debug)
        input_file_object = open(input_file_path, "rb")
        data_bytes = input_file_object.read() # bytes
        data_unicode = data_bytes.decode(args.input_file_encoding) # unicode
        input_file_object.close()
        lines = data_unicode.split(args.csv_ls)
        if args.csv_ignore_first_line:
            lines = lines[1:]
        for line in lines:
            array = line.split(args.csv_fs)
            if len(array) >= 2:
                headword = array[0]
                definition = line[len(headword) + 1:]
                if args.ignore_case:
                    headword = headword.lower()
                dictionary.add_entry(headword=headword, definition=definition)
        print_debug("Reading from file '%s'... success" % (input_file_path), args.debug)
    return dictionary

def write(dictionary, args, output_file_path):
    try:
        print_debug("Writing to file '%s'..." % (output_file_path), args.debug)
        output_file_obj = open(output_file_path, "wb")
        for index in dictionary.entries_index_sorted:
            entry = dictionary.entries[index]
            string = u"%s%s%s%s" % (
                entry.headword,
                args.csv_fs,
                entry.definition,
                args.csv_ls
            )
            output_file_obj.write(string.encode("utf-8"))
        output_file_obj.close()
        print_debug("Writing to file '%s'... success" % (output_file_path), args.debug)
        return [output_file_path]
    except:
        print_error("Writing to file '%s'... failure" % (output_file_path))
        return None



