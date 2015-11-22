#!/usr/bin/env python
# coding=utf-8

"""
Read/write XML dictionaries.
"""

from io import open
from lxml import etree

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
        input_file_object.close()
        root = etree.fromstring(data_bytes)
        for entry in root.iter("entry"):
            headword = None
            definition = None
            for child in entry:
                if child.tag == "key":
                    headword = child.text
                if child.tag == "def":
                    definition = child.text
            if (headword is not None) and (definition is not None):    
                dictionary.add_entry(headword=headword, definition=definition)
        print_debug("Reading from file '%s'... success" % (input_file_path), args.debug)
    return dictionary

def write(dictionary, args, output_file_path):
    try:
        print_debug("Creating XML tree...", args.debug)
        dictionary_elem = etree.Element("dictionary")
        for index in dictionary.entries_index_sorted:
            entry = dictionary.entries[index]
            entry_elem = etree.SubElement(dictionary_elem, "entry")
            key_elem = etree.SubElement(entry_elem, "key")
            key_elem.text = entry.headword
            def_elem = etree.SubElement(entry_elem, "def")
            def_elem.text = entry.definition
        tree = etree.ElementTree(dictionary_elem)
        print_debug("Creating XML tree... done", args.debug)
        print_debug("Writing to file '%s'..." % (output_file_path), args.debug)
        tree.write(
            output_file_path,
            pretty_print=True,
            xml_declaration=True
        )
        print_debug("Writing to file '%s'... success" % (output_file_path), args.debug)
        return [output_file_path]
    except:
        print_error("Writing to file '%s'... failure" % (output_file_path))
        return None



