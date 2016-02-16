#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
This is the prefix function for grouping headwords for Kobo format.
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

    Note that the procedure implemented here is the result
    of reverse engineering, since no official specification
    has been published by Kobo so far. YMMV.

    :param headword: the headword string
    :type  headword: unicode
    :param length: prefix length
    :type  length: int
    :rtype: unicode
    """
    def is_allowed(character):
        # all non-ascii (x > 127) are ok
        # all ASCII lowercase letters (97 <= x <= 122) are ok
        # everything else is not ok
        try:
            code = ord(character)
            return (code > 127) or ((code >= 97) and (code <= 122))
        except:
            pass
        return True

    # defaults to u"SPECIAL", it will be mapped to u"11...1" later
    prefix = u"SPECIAL"
    headword = headword.lower()
    if len(headword) > 0:
        while len(headword) < length:
            # for headwords shorter than length, append an 'a' at the end
            # e.g. length=3, "xy" => "xya"
            headword += u"a"
        # TODO maybe the check should be done only for the first character
        is_ok = True
        for character in headword:
            if not is_allowed(character):
                is_ok = False
                break
        if is_ok:
            prefix = headword[0:length]
    return prefix



