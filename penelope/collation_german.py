#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
This is a sample collation function (IcuNoCase) for German.
"""

__author__ = "Alberto Pettarin"
__copyright__ = "Copyright 2012-2015, Alberto Pettarin (www.albertopettarin.it)"
__license__ = "MIT"
__version__ = "3.0.1"
__email__ = "alberto@albertopettarin.it"
__status__ = "Production"

def collate_function(string1, string2):
    """
    Implement IcuNoCase collation for German.

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
    for f in [[u"ä", u"a"], [u"ö", u"o"], [u"ü", u"u"], [u"ß", u"ss"]]:
        b1 = b1.replace(f[0], f[1])
        b2 = b2.replace(f[0], f[1])
    
    if b1.encode("utf-16") == b2.encode("utf-16"):
        if c1.encode("utf-16") == c2.encode("utf-16"):
            return 0
        if c1.encode("utf-16") < c2.encode("utf-16"):
            return -1
    else:
        if b1.encode("utf-16") < b2.encode("utf-16"):
            return -1
    return 1



