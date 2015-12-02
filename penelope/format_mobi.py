#!/usr/bin/env python
# coding=utf-8

"""
Write MOBI (Kindle) dictionaries.

It creates a .opf and .html file, and invokes kindlegen to compile it.
"""

from __future__ import absolute_import
from io import open
import os
import subprocess

from penelope.dictionary_ebook import DictionaryEbook
from penelope.utilities import print_debug
from penelope.utilities import print_error
from penelope.utilities import print_info
from penelope.utilities import create_temp_directory
from penelope.utilities import copy_file
from penelope.utilities import delete_directory

__author__ = "Alberto Pettarin"
__copyright__ = "Copyright 2012-2015, Alberto Pettarin (www.albertopettarin.it)"
__license__ = "MIT"
__version__ = "3.1.1"
__email__ = "alberto@albertopettarin.it"
__status__ = "Production"

KINDLEGEN = u"kindlegen"

def read(dictionary, args, input_file_paths):
    print_error("Read function not implemented for MOBI dictionaries")
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

    # create mobi object
    mobi = DictionaryEbook(ebook_format=DictionaryEbook.MOBI, args=args)

    # add groups
    for key in all_group_keys:
        if key == u"SPECIAL":
            group_entries = special_group
        else:
            group_entries = group_dict[key]
        mobi.add_group(key, group_entries)

    # create output file
    print_debug("Writing to file '%s'..." % (output_file_path_absolute), args.debug)
    mobi.write(output_file_path_absolute, compress=False)
    result = [output_file_path]
    print_debug("Writing to file '%s'... done" % (output_file_path_absolute), args.debug)

    # run kindlegen
    tmp_path = mobi.get_tmp_path()
    if args.mobi_no_kindlegen:
        print_info("Not running kindlegen, the raw files are located in '%s'" % tmp_path)
        result = [tmp_path]
    else:
        try:
            print_debug("Creating .mobi file with kindlegen...", args.debug)
            kindlegen_path = KINDLEGEN
            opf_file_path_absolute = os.path.join(tmp_path, "OEBPS", "content.opf")
            mobi_file_path_relative = u"content.mobi"
            mobi_file_path_absolute = os.path.join(tmp_path, "OEBPS", mobi_file_path_relative)
            if args.kindlegen_path is None:
                print_info("  Running '%s' from $PATH" % KINDLEGEN)
            else:
                kindlegen_path = args.kindlegen_path
                print_info("  Running '%s' from '%s'" % (KINDLEGEN, kindlegen_path))
            proc = subprocess.Popen(
                [kindlegen_path, opf_file_path_absolute, "-o", mobi_file_path_relative],
                stdout=subprocess.PIPE,
                stdin=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            output = proc.communicate()
            if args.debug:
                output_unicode = (output[0]).decode("utf-8")
                print_debug(output_unicode, args.debug)
            copy_file(mobi_file_path_absolute, output_file_path_absolute)
            result = [output_file_path]
            print_debug("Creating .mobi file with kindlegen... done", args.debug)
        except OSError as exc:
            print_error("  Unable to run '%s' as '%s'" % (KINDLEGEN, kindlegen_path))
            print_error("  Please make sure '%s':" % KINDLEGEN)
            print_error("    1. is available on your $PATH or")
            print_error("    2. specify its path with --kindlegen-path")

    # delete tmp directory
    tmp_path = mobi.get_tmp_path()
    if args.keep:
        print_info("Not deleting temp dir '%s'" % (tmp_path))
    else:
        mobi.delete()
        print_debug("Deleted temp dir '%s'" % (tmp_path), args.debug)

    return result



