#!/usr/bin/env python
# coding=utf-8

"""
This is a (trivial) example of an input parser,
just to show the parse() interface.

This parser simply returns the (raw) input dictionary, unchanged.
"""

__author__ = "Alberto Pettarin"
__copyright__ = "Copyright 2012-2015, Alberto Pettarin (www.albertopettarin.it)"
__license__ = "MIT"
__version__ = "3.0.1"
__email__ = "alberto@albertopettarin.it"
__status__ = "Production"

def parse(dictionary, arguments):
    """
    Given the input dictionary and arguments,
    return a (possibly, modified) dictionary.

    The returned dictionary might be the same (input) instance,
    or a new one.

    :param dictionary: the (raw) input dictionary
    :type  dictionary: Dictionary
    :param arguments: the command line arguments
    :type  arguments: Namespace from argparse
    :rtype: Dictionary
    """
    return dictionary



