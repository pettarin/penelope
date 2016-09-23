#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
This is a collation function (IcuNoCase) for German.
"""

from __future__ import absolute_import

from penelope.utilities import PY2
from penelope.utilities import utf_lower

__author__ = "Alberto Pettarin"
__copyright__ = "Copyright 2012-2016, Alberto Pettarin (www.albertopettarin.it)"
__license__ = "MIT"
__version__ = "3.1.3"
__email__ = "alberto@albertopettarin.it"
__status__ = "Production"


REPLACEMENTS = [
    [u"ä", u"a"],
    [u"ö", u"o"],
    [u"ü", u"u"],
    [u"ß", u"ss"]
]
if PY2:
    REPLACEMENTS = [(r.encode("utf-8"), s.encode("utf-8")) for (r, s) in REPLACEMENTS]


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
    for (r, s) in REPLACEMENTS:
        b1 = b1.replace(r, s)
        b2 = b2.replace(r, s)
    b1 = utf_lower(b1, encoding="utf-8", lower=True)
    b2 = utf_lower(b2, encoding="utf-8", lower=True)
    c1 = utf_lower(string1, encoding="utf-8", lower=True)
    c2 = utf_lower(string2, encoding="utf-8", lower=True)
    d1 = utf_lower(b1, encoding="utf-16", lower=False)
    d2 = utf_lower(b2, encoding="utf-16", lower=False)
    if d1 == d2:
        e1 = utf_lower(c1, encoding="utf-16", lower=False)
        e2 = utf_lower(c2, encoding="utf-16", lower=False)
        if e1 == e2:
            return 0
        if e1 < e2:
            return -1
    if d1 < d2:
        return -1
    return 1
