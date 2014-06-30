#!/usr/bin/env python
# -*- coding: utf-8 -*-

__license__     = 'MIT'
__author__      = 'Alberto Pettarin (alberto albertopettarin.it)'
__copyright__   = '2012-2014 Alberto Pettarin (alberto albertopettarin.it)'
__version__     = 'v2.0.0'
__date__        = '2014-06-30'
__description__ = 'Default collation function for penelope.py'

### BEGIN collate_function ###
# collate_function(string1, string2)
# compare string1 to string2
# return  0 if string1 == string2
#        -1 if string1 < string2
#         1 if string1 > string2
def collate_function(string1, string2):
    b1 = bytearray(string1, 'utf-8').lower()
    b2 = bytearray(string2, 'utf-8').lower()
    if (b1 == b2):
        return 0
    else:
        return -1 if (b1 < b2) else 1
### END collate_function ###

