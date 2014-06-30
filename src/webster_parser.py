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
#def parse(data):
#    parsed_data = []
#    for d in data:
#        parsed_data += [ [ d[0], True, [], [], d[1] ] ]
#    return parsed_data

def parse(data, type_sequence, ignore_case):
    parsed_data = []

    global_dictionary = dict()
    for d in data:
        word = d[0]
        definition = clean_definition(word, d[1])

        par = word.find('(')
        if par > -1:
            word = word[:par].strip()
        
        if word in global_dictionary:
            global_dictionary[word] += [ definition ]
        else:
            global_dictionary[word] = [ definition ]

    for word in global_dictionary:
        definitions = assemble(word, global_dictionary[word])
        parsed_data += [ [ word, True, [], [], definitions ] ]

    return parsed_data
### END parse ###

### BEGIN assemble ###
# assemble(word, definitions)
# assemble together several definitions for word
def assemble(word, definitions):
    cleaned = "<b>" + word + "</b>"
    if len(definitions) == 1:
        return cleaned + "<f>&nbsp;&ns;&nbsp;</f>" + definitions[0]
    else:
        i = 1
        for d in definitions:
            cleaned += "<f>&nbsp;&ns;&nbsp;</f>" + "<b>("+ str(i) + ")</b>&nbsp;" + d
            i += 1
        return cleaned
### END assemble ###

### BEGIN clean_definition ###
# clean_definition(word, definition)
# clean the current definition for word
def clean_definition(word, definition):
    pos = definition.find('</k>')
    if pos > -1:
        return definition[pos+len('</k>'):].strip()
    else:
        return definition
### END clean ###
