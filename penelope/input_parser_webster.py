#!/usr/bin/env python
# coding=utf-8

"""
This is an example of an input parser, acting on a real-world dictionary,
the Webster 1913.
"""

__author__ = "Alberto Pettarin"
__copyright__ = "Copyright 2012-2015, Alberto Pettarin (www.albertopettarin.it)"
__license__ = "MIT"
__version__ = "3.1.0"
__email__ = "alberto@albertopettarin.it"
__status__ = "Production"

def parse(dictionary, arguments):
    """
    Given the input dictionary and arguments,
    return a (possibly, modified) dictionary.

    The returned dictionary might be the same (input) instance,
    or a new one.

    :param dictionary: the (raw) input dictionary
    :type  dictionary: Dictionary
    :param arguments: the command line arguments
    :type  arguments: Namespace from argparse
    :rtype: Dictionary
    """

    def clean_definition(entry):
        """
        Remove any prefix of type "<k>...</k>"
        from the entry.definition string.
        """
        pos = entry.definition.find("</k>")
        if pos > -1:
            entry.definition = entry.definition[pos+len("</k>"):].strip()

    def custom_merge_function(headword, definitions):
        """
        Merge definitions for the same headword in a custom way:
        1 def   => <b>word<b>
                    <f>&nbsp;&ns;&nbsp;</f>definition
        2+ defs => <b>word<b>
                    <f>&nbsp;&ns;&nbsp;</f><b>(1)&nbsp;definition
                    <f>&nbsp;&ns;&nbsp;</f><b>(2)&nbsp;definition...
        """
        if len(definitions) > 1:
            clean = u"<b>%s<b>" % (headword)
            for i in range(len(definitions)):
                clean += "<f>&nbsp;&ns;&nbsp;</f><b>(%d)</b>&nbsp;%s" % (i+1, definitions[i])
            return clean
        if len(definitions) == 1:
            return u"<b>%s<b><f>&nbsp;&ns;&nbsp;</f>%s" % (headword, definitions[0])
        return u""

    if dictionary is None:
        return None
    for entry in dictionary.entries:
        clean_definition(entry)
    dictionary.merge_definitions(merge_function=custom_merge_function)
    return dictionary



