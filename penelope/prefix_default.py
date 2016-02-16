#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
This is the default prefix function for grouping headwords.
"""

__author__ = "Alberto Pettarin"
__copyright__ = "Copyright 2012-2016, Alberto Pettarin (www.albertopettarin.it)"
__license__ = "MIT"
__version__ = "3.1.2"
__email__ = "alberto@albertopettarin.it"
__status__ = "Production"

def get_prefix(headword, length):
    """
    Return the prefix for the given headword,
    of length length.

    :param headword: the headword string
    :type  headword: unicode
    :param length: prefix length
    :type  length: int
    :rtype: unicode
    """
    if headword is None:
        return None
    lowercased = headword.lower()
    if ord(lowercased[0]) < 97:
        return u"SPECIAL"
    if len(lowercased) < length:
        return lowercased
    return lowercased[0:length]


