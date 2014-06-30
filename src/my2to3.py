#!/usr/bin/env python
# -*- coding: utf-8 -*-

__license__     = 'MIT'
__author__      = 'Alberto Pettarin (alberto albertopettarin.it)'
__copyright__   = '2012-2014 Alberto Pettarin (alberto albertopettarin.it)'
__version__     = 'v2.0.0'
__date__        = '2014-06-30'
__description__ = 'Convert code from Python 2 to Python 3, using code comments'

import re, sys, unicodedata
### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ###
def main():
    fileIn = open(sys.argv[1], 'r')
    text = fileIn.read()
    fileIn.close()
    print convert(text)
### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ###


### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ###
def convert(text):

    text2 = re.sub(r"#Python2#\n", "#Python2#", text)
    text2 = re.sub(r"#Python3#", "#Python3#\n", text2)

    return text2
### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ###

### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ###
if __name__ == '__main__':

    reload(sys)
    sys.setdefaultencoding("utf-8")
    
    main()
### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ###
