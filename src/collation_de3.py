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
    # conversion to unicode and lower case (only for Python 2)
    #Python2#    b1 = string1.decode('utf-8')
    #Python3#
    b1 = string1
    #Python2#    b2 = string2.decode('utf-8')
    #Python3#
    b2 = string2
    b1 = b1.lower()
    b2 = b2.lower()
    # store strings with original accents for 2nd level collation
    c1 = b1
    c2 = b2

    # replace german accent characters by base characters for 1st level collation
    #Python2#    for f in [ [u'ä', u'a'], [u'ö', u'o'], [u'ü', u'u'], [u'ß', u'ss'] ]:
    #Python3#
    for f in [ ['ä', 'a'], ['ö', 'o'], ['ü', 'u'], ['ß', 'ss'] ]:
        b1 = b1.replace(f[0], f[1])
        b2 = b2.replace(f[0], f[1])

    # 1st level collation
    if b1.encode('utf-16') == b2.encode('utf-16'):
        # 2nd level collation
        if c1.encode('utf-16') == c2.encode('utf-16'):
            return 0
        else:
            return -1 if c1.encode('utf-16') < c2.encode('utf-16') else 1
    # 1st level collation
    else:
        return -1 if b1.encode('utf-16') < b2.encode('utf-16') else 1
### END collate_function ###


