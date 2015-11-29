#!/usr/bin/env python
# coding=utf-8

"""
Write EPUB dictionaries.

NOTE: this file needs refactoring.
"""

from __future__ import absolute_import
from io import open
import os
import zipfile

from penelope.dictionary_ebook import DictionaryEbook 
from penelope.utilities import create_temp_directory
from penelope.utilities import delete_directory
from penelope.utilities import print_debug
from penelope.utilities import print_error
from penelope.utilities import print_info

__author__ = "Alberto Pettarin"
__copyright__ = "Copyright 2012-2015, Alberto Pettarin (www.albertopettarin.it)"
__license__ = "MIT"
__version__ = "3.1.0"
__email__ = "alberto@albertopettarin.it"
__status__ = "Production"

def read(dictionary, args, input_file_paths):
    print_error("Read function not implemented for EPUB dictionaries")
    return None

def write(dictionary, args, output_file_path):
    # result to be returned
    result = None

    # get absolute path
    output_file_path_absolute = os.path.abspath(output_file_path)

    # sort by headword, optionally ignoring case
    dictionary.sort(by_headword=True, ignore_case=args.sort_ignore_case)

    # create groups
    special_group, group_keys, group_dict = dictionary.group(
        prefix_function_path=args.group_by_prefix_function,
        prefix_length=int(args.group_by_prefix_length),
        merge_min_size=int(args.group_by_prefix_merge_min_size),
        merge_across_first=args.group_by_prefix_merge_across_first
    )
    all_group_keys = group_keys
    if special_group is not None:
        all_group_keys += [u"SPECIAL"]

    # create epub object
    epub = DictionaryEbook(ebook_format=DictionaryEbook.EPUB2, args=args)
   
    # add groups
    for key in all_group_keys:
        if key == u"SPECIAL":
            group_entries = special_group
        else:
            group_entries = group_dict[key]
        epub.add_group(key, group_entries)

    # create output file
    if args.epub_no_compress:
        print_debug("Not compressing the EPUB container")
        epub.write(output_file_path_absolute, compress=False)
    else:
        print_debug("Writing to file '%s'..." % (output_file_path_absolute), args.debug)
        epub.write(output_file_path_absolute, compress=True)
        result = [output_file_path]
        print_debug("Writing to file '%s'... done" % (output_file_path_absolute), args.debug)

    # delete tmp directory
    tmp_path = epub.get_tmp_path()
    if args.epub_no_compress:
        print_info("The uncompressed EPUB is inside dir '%s'" % (tmp_path))
        result = [tmp_path]
    elif args.keep:
        print_info("Not deleting temp dir '%s'" % (tmp_path))
        if result is None:
            result = [tmp_path]
    else:
        epub.delete()
        print_debug("Deleted temp dir '%s'" % (tmp_path), args.debug)

    return result



