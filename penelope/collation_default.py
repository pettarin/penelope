#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
This is the default collation function (IcuNoCase).
"""

__author__ = "Alberto Pettarin"
__copyright__ = "Copyright 2012-2015, Alberto Pettarin (www.albertopettarin.it)"
__license__ = "MIT"
__version__ = "3.1.0"
__email__ = "alberto@albertopettarin.it"
__status__ = "Production"

def collate_function(string1, string2):
    """
    Implement default IcuNoCase collation,
    by simply lowercasing the UTF-8 encoded versions
    of the two strings.

    :param string1: first string
    :type  string1: unicode
    :param string2: second string
    :type  string2: unicode
    :rtype: int
    """
    b1 = string1.encode("utf-8").lower()
    b2 = string2.encode("utf-8").lower()
    if b1 == b2:
        return 0
    if b1 < b2:
        return -1
    return 1



