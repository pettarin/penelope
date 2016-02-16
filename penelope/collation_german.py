#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
This is a collation function (IcuNoCase) for German.
"""

__author__ = "Alberto Pettarin"
__copyright__ = "Copyright 2012-2016, Alberto Pettarin (www.albertopettarin.it)"
__license__ = "MIT"
__version__ = "3.1.2"
__email__ = "alberto@albertopettarin.it"
__status__ = "Production"

REPLACEMENTS = [
    [u"ä", u"a"],
    [u"ö", u"o"],
    [u"ü", u"u"],
    [u"ß", u"ss"]
]

def collate_function(string1, string2):
    """
    Implement IcuNoCase collation for German.
    (I do not remember where the procedure comes from.)

    :param string1: first string
    :type  string1: unicode
    :param string2: second string
    :type  string2: unicode
    :rtype: int
    """
    b1 = string1.lower()
    b2 = string2.lower()
    c1 = b1
    c2 = b2
    for repl in REPLACEMENTS:
        b1 = b1.replace(repl[0], repl[1])
        b2 = b2.replace(repl[0], repl[1])
    if b1.encode("utf-16") == b2.encode("utf-16"):
        if c1.encode("utf-16") == c2.encode("utf-16"):
            return 0
        if c1.encode("utf-16") < c2.encode("utf-16"):
            return -1
    else:
        if b1.encode("utf-16") < b2.encode("utf-16"):
            return -1
    return 1



