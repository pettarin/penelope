#!/usr/bin/env python
# -*- coding: utf-8 -*-

__license__     = 'MIT'
__author__      = 'Alberto Pettarin (alberto albertopettarin.it)'
__copyright__   = '2012-2014 Alberto Pettarin (alberto albertopettarin.it)'
__version__     = 'v2.0.0'
__date__        = '2014-06-30'
__description__ = 'Parse the given definition list for penelope.py'

### BEGIN parse ###
# parse(data, type_sequence, ignore_case)
# parse the given list of pairs
# data = [ [word, definition] ]
# with type_sequence and ignore_case options,
# and outputs the following list:
# parsed = [ word, include, synonyms, substitutions, definition ]
#
# where:
#        word is the sorting key
#        include is a boolean saying whether the word should be included
#        synonyms is a list of alternative strings for word
#        substitutions is a list of pairs [ word_to_replace, replacement ]
#        definition is the definition of word

# default implementation, just copy the content of the stardict dictionary
def parse(data, type_sequence, ignore_case):
    parsed_data = []
    for d in data:
        parsed_data += [ [ d[0], True, [], [], d[1] ] ]
    return parsed_data
### END parse ###

