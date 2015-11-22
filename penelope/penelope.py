#!/usr/bin/env python
# coding=utf-8

"""
This is the main Penelope script.
"""

from __future__ import absolute_import
import argparse
import sys

from command_line import COMMAND_LINE_PARAMETERS
from command_line import DESCRIPTION
from command_line import EPILOG
from command_line import INPUT_FORMATS
from command_line import OUTPUT_FORMATS
from command_line import REQUIRED_PARAMETERS
from command_line import USAGE
from command_line import check_arguments
from command_line import set_default_values
from dictionary import read_dictionary
from dictionary import write_dictionary
from utilities import get_uuid
from utilities import load_input_parser
from utilities import print_debug
from utilities import print_error
from utilities import print_info

__author__ = "Alberto Pettarin"
__copyright__ = "Copyright 2012-2015, Alberto Pettarin (www.albertopettarin.it)"
__license__ = "MIT"
__version__ = "3.0.0"
__email__ = "alberto@albertopettarin.it"
__status__ = "Production"

def main():
    parser = argparse.ArgumentParser(
        usage=USAGE,
        description=DESCRIPTION,
        epilog=EPILOG,
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    for param in COMMAND_LINE_PARAMETERS:
        if param["short"] is None:
            parser.add_argument(
                param["long"],
                help=param["help"],
                action=param["action"],
                default=argparse.SUPPRESS
            )
        else:
            parser.add_argument(
                param["short"],
                param["long"],
                help=param["help"],
                action=param["action"],
                default=argparse.SUPPRESS
            )
    arguments = parser.parse_args()

    # no arguments: show help and exit
    if len(sys.argv) < 2:
        parser.print_help()
        sys.exit(0)

    # print version and exit
    if "version" in arguments:
        print_info("Penelope v%s" % (__version__))
        sys.exit(0)

    # check we have all the required arguments
    # if not, it will sys.exit() with some error code
    check_arguments(arguments)

    # set default values
    set_default_values(arguments)
    print_debug(u"Running with the command line arguments:\n%s" % (str(arguments)), arguments.debug)

    # read raw dictionary
    print_info(u"Reading input file(s)...")
    dictionary = read_dictionary(arguments)
    if dictionary is None:
        print_error("Unable to read the input file(s)")
        sys.exit(8)
    print_info(u"Reading input file(s)... done")

    # apply custom input parser, if specified
    if arguments.input_parser is not None:
        input_parser = load_input_parser(arguments.input_parser)
        if input_parser is not None:
            print_info(u"Applying the specified input parser...")
            dictionary = input_parser.parse(dictionary, arguments)
            print_info(u"Applying the specified input parser... done")

    # sort dictionary before, if requested
    if arguments.sort_before:
        print_info(u"Sorting before...")
        dictionary.sort(
            arguments.sort_by_headword,
            arguments.sort_by_definition,
            arguments.sort_reverse,
            arguments.sort_ignore_case
        )
        print_info(u"Sorting before... done")

    # merge definitions, if requested
    if arguments.merge_definitions:
        print_info(u"Merging...")
        dictionary.merge_definitions(merge_separator=arguments.merge_separator)
        print_info(u"Merging... done")

    # flatten synonyms, if requested
    if arguments.flatten_synonyms:
        print_info(u"Flattening synonyms...")
        dictionary.flatten_synonyms()
        print_info(u"Flattening synonyms... done")

    # sort dictionary after, if requested
    if arguments.sort_after:
        print_info(u"Sorting after...")
        dictionary.sort(
            arguments.sort_by_headword,
            arguments.sort_by_definition,
            arguments.sort_reverse,
            arguments.sort_ignore_case
        )
        print_info(u"Sorting after... done")

    # output dictionary
    print_info(u"Writing output file(s)...")
    output_paths = write_dictionary(dictionary, arguments)
    if output_paths is None:
        print_error("Unable to write the output file(s)")
        sys.exit(16)
    print_info(u"Writing output file(s)... done")
    print_info(u"The following file(s) have been created:")
    for op in output_paths:
        print_info(u"  %s" % op)

    sys.exit(0)



if __name__ == '__main__':
    main()



