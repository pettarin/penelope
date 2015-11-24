#!/usr/bin/env python
# coding=utf-8

"""
The Dictionary class is the internal representation of a dictionary.

It is a (multi)dictionary, with a reverse lookup index.

It supports merging definitions for the same headword, and sorting
by headword and/or definition, possibly reversing or ignoring the case.

It also has support for associating synonyms (i.e., headword strings)
to each entry, and to "flatten them" (i.e., creating new headwords,
one for each synonym, with the definition of the original entry).
"""

from __future__ import absolute_import
from io import open
import os

from penelope.utilities import get_uuid
from penelope.utilities import print_error

__author__ = "Alberto Pettarin"
__copyright__ = "Copyright 2012-2015, Alberto Pettarin (www.albertopettarin.it)"
__license__ = "MIT"
__version__ = "3.0.1"
__email__ = "alberto@albertopettarin.it"
__status__ = "Production"

def read_dictionary(args):
    """
    Read the input dictionary from the input files specified
    in the given arguments.

    Return a Dictionary, or None if failed.
    """
    metadata = DictionaryMetadata(
        identifier_string=args.identifier,
        author_string=args.author,
        email_string=args.email,
        website_string=args.website,
        title_string=args.title,
        copyright_string=args.copyright,
        license_string=args.license,
        year_string=args.year,
        language_from=args.language_from,
        language_to=args.language_to,
        description_string=args.description
    )
    dictionary = Dictionary(metadata=metadata)
    input_format = args.input_format
    if input_format == "bookeen":
        # NOTE
        # for bookeen format we cannot prepare the file paths
        # as for the other formats, since we might have a compressed .install file
        # or an uncompressed pair (.dict.idx and .dict)
        # this is dealt with directly in format_bookeen.py
        import penelope.format_bookeen
        return penelope.format_bookeen.read(dictionary, args, args.input_file)
    elif input_format == "csv":
        input_file_paths = prepare_file_paths(args.input_file, ".csv")
        if input_file_paths is None:
            return None
        import penelope.format_csv
        return penelope.format_csv.read(dictionary, args, input_file_paths)
    elif input_format == "kobo":
        input_file_paths = prepare_file_paths(args.input_file, ".zip")
        if input_file_paths is None:
            return None
        import penelope.format_kobo
        return penelope.format_kobo.read(dictionary, args, input_file_paths)
    elif input_format == "stardict":
        input_file_paths = prepare_file_paths(args.input_file, ".zip")
        if input_file_paths is None:
            return None
        import penelope.format_stardict
        return penelope.format_stardict.read(dictionary, args, input_file_paths)
    elif input_format == "xml":
        input_file_paths = prepare_file_paths(args.input_file, ".xml")
        if input_file_paths is None:
            return None
        import penelope.format_xml
        return penelope.format_xml.read(dictionary, args, input_file_paths)
    return dictionary

def write_dictionary(dictionary, args):
    """
    Write the dictionary to file.

    Return a list of paths, or None if failed.
    """
    output_format = args.output_format
    if output_format == "bookeen":
        # NOTE
        # for bookeen format we cannot add the file extension
        # as for the other formats, since we might have to generate
        # a compressed .install file or an uncompressed pair (.dict.idx and .dict)
        # this is dealt with directly in format_bookeen.py
        import penelope.format_bookeen
        return penelope.format_bookeen.write(dictionary, args, args.output_file)
    elif output_format == "csv":
        output_file_path = add_extension(args.output_file, ".csv")
        import penelope.format_csv
        return penelope.format_csv.write(dictionary, args, output_file_path)
    elif output_format == "epub":
        output_file_path = add_extension(args.output_file, ".epub")
        import penelope.format_epub
        return penelope.format_epub.write(dictionary, args, output_file_path)
    elif output_format == "kobo":
        output_file_path = get_kobo_file_path(args)
        import penelope.format_kobo
        return penelope.format_kobo.write(dictionary, args, output_file_path)
    elif output_format == "mobi":
        output_file_path = add_extension(args.output_file, ".mobi")
        import penelope.format_mobi
        return penelope.format_mobi.write(dictionary, args, output_file_path)
    elif output_format == "stardict":
        output_file_path = add_extension(args.output_file, ".zip")
        import penelope.format_stardict
        return penelope.format_stardict.write(dictionary, args, output_file_path)
    elif output_format == "xml":
        output_file_path = add_extension(args.output_file, ".xml")
        import penelope.format_xml
        return penelope.format_xml.write(dictionary, args, output_file_path)
    return False

def get_kobo_file_path(args):
    if (args.language_from == args.language_to) and (args.language_from == "en"):
        output_file_name = "dicthtml.zip"
    else:
        output_file_name = "dicthtml-%s" % (args.language_from)
        if args.language_from != args.language_to:
            output_file_name += "-%s" % (args.language_to)
        output_file_name += ".zip"
    output_file_path = os.path.split(args.output_file)[0]
    output_file_path = os.path.join(output_file_path, output_file_name)
    return output_file_path

def add_extension(file_path, extension):
    if not file_path.endswith(extension):
        file_path += extension
    return file_path

def prepare_file_paths(string, extension):
    file_paths = []
    for prefix in string.split(","):
        file_path = add_extension(prefix, extension)
        if not os.path.exists(file_path):
            print_error("File '%s' does not exist" % file_path)
            return None
        file_paths.append(file_path)
    return file_paths



class DictionaryEntry(object):
    def __init__(
            self,
            headword,
            definition
    ):
        self.headword = headword
        self.definition = definition
        self.clear_synonyms()

    def clear_synonyms(self):
        self.synonyms = []

    def add_synonym(self, synonym):
        self.synonyms.append(synonym)

    def get_synonyms(self):
        return self.synonyms

    def __len__(self):
        if self.headword is None:
            return 0
        return len(self.headword)

    def __str__(self):
        return u"""DictionaryEntry
    Headword: '%s'
    Definition: '%s'""" % (self.headword, self.definition)

    def prefix(self, prefix_length):
        if len(self) < prefix_length:
            return self.headword
        return self.headword[0:prefix_length]

class DictionaryMetadata(object):
    def __init__(
            self,
            identifier_string=None,
            author_string=None,
            email_string=None,
            website_string=None,
            title_string=None,
            copyright_string=None,
            license_string=None,
            year_string=None,
            language_from=None,
            language_to=None,
            description_string=None
    ):
        self.identifier_string = identifier_string
        self.author_string = author_string
        self.email_string = email_string
        self.website_string = website_string
        self.title_string = title_string
        self.copyright_string = copyright_string
        self.license_string = license_string
        self.year_string = year_string
        self.language_from = language_from
        self.language_to = language_to
        self.description_string = description_string
        if self.identifier_string is None:
            self.identifier_string = get_uuid()

    def __str__(self):
        return u"""DictionaryMetadata
    Identifier:    '%s'
    Language from: '%s'
    Language to:   '%s'
    Title:         '%s'
    Author:        '%s'
    Copyright:     '%s'
    License:       '%s'
    Year:          '%s'
    Email:         '%s'
    Website:       '%s'
    Description:   '%s'""" % (
        self.identifier_string,
        self.language_from,
        self.language_to,
        self.title_string,
        self.author_string,
        self.copyright_string,
        self.license_string,
        self.year_string,
        self.email_string,
        self.website_string,
        self.description_string
    )

    @property
    def is_monolingual(self):
        if self.language_from is None:
            return False
        return self.language_from == self.language_to

    @property
    def is_bilingual(self):
        if self.language_from is None:
            return False
        return self.language_from != self.language_to

class Dictionary(object):
    def __init__(
            self,
            metadata=None
    ):
        # metadata object
        self.metadata = metadata
        if self.metadata is None:
            self.metadata = DictionaryMetadata()
        # actual dictionary entries
        self.entries = []
        # maps headword -> list of indices of self.entries with that headword
        self.entries_index = {}
        # list of indices (unsorted or sorted by headword and/or definition)
        self.entries_index_sorted = []
        self.has_synonyms = False

    def __str__(self):
        return """Dictionary
Number of entries:          %d
Number of unique headwords: %d
Has synonyms:               %s
%s""" % (len(self), self.unique_headwords, str(self.has_synonyms), str(self.metadata))

    def __len__(self):
        return len(self.entries)

    def clear(self):
        self.entries = []
        self.entries_index = {}
        self.entries_index_sorted = []
        self.has_synonyms = False

    @property
    def unique_headwords(self):
        return len(self.entries_index)

    @property
    def has_unique_headwords_only(self):
        return len(self) == self.unique_headwords

    def add_synonym(self, synonym, headword_index):
        if headword_index < len(self):
            entry = self.entries[headword_index]
            entry.add_synonym(synonym)
            self.has_synonyms = True

    def add_entry(self, entry=None, headword=None, definition=None):
        if entry is None:
            entry = DictionaryEntry(headword, definition)
        self.entries.append(entry)
        if not entry.headword in self.entries_index:
            self.entries_index[entry.headword] = []
        index = len(self.entries) - 1
        self.entries_index[entry.headword].append(index)
        self.entries_index_sorted.append(index)

    def has_headword(self, headword):
        return headword in self.entries_index

    def get_definitions(self, headword):
        if not self.has_headword(headword):
            return []
        definitions = []
        for index in self.entries_index[headword]:
            definitions.append(self.entries[index].definition)
        return definitions

    def get_synonyms(self):
        syn_with_index = []
        if self.has_synonyms:
            for index in self.entries_index_sorted:
                entry = self.entries[index]
                for synonym in entry.get_synonyms():
                    syn_with_index.append([synonym, index])
        return syn_with_index

    def sort(self, by_headword=True, by_definition=False, reverse=False, ignore_case=False):
        if (not by_headword) and (not by_definition):
            self.entries_index_sorted = range(len(self.entries))
            return
        tmp = []
        i = 0
        for entry in self.entries:
            first = entry.headword if by_headword else u""
            if ignore_case:
                first = first.lower()
            second = entry.definition if by_definition else u""
            if ignore_case:
                second = second.lower()
            tmp.append([
                first,
                second,
                i
            ])
            i += 1
        tmp = sorted(tmp, reverse=reverse)
        self.entries_index_sorted = []
        for t in tmp:
            self.entries_index_sorted.append(t[2])

    def flatten_synonyms(self):
        """
        Add a new entry for each synonym,
        using the definition of the original headword.
        At the end, reset the current sort order.
        (You will need to sort it later, if interested in having
        the dictionary sorted by headword and/or definition.)
        """
        if not self.has_synonyms:
            # nothing to do
            return

        for entry in self.entries:
            for synonym in entry.get_synonyms():
                self.add_entry(headword=synonym, definition=entry.definition)

        self.sort(False, False, False, False)

    def merge_definitions(self, merge_function=None, merge_separator=None):
        """
        Merge definitions of entries with the same headword,
        using merge_function or merge_separator to create the merged definition.

        Note that this function destroys the current dictionary,
        and re-populate its entries (with the new "merged" entries).

        As a consequence, it resets the current sort order.
        (You will need to sort it later, if interested in having
        the dictionary sorted by headword and/or definition.)
        """

        def default_merge_function(headword, definitions):
            """
            Merge definitions for the same headword in a custom way:
            1 def   => definition
            2+ defs => definition<SEP>definition<SEP>...
            """
            return merge_separator.join(definitions)

        if (self.has_unique_headwords_only) or ((merge_function is None) and (merge_separator is None)):
            # nothing to do
            return

        if merge_function is None:
            # use the default merge function, joining using the merge_separator string
            merge_function = default_merge_function

        # copy previous data
        original_entries = self.entries
        original_entries_index = self.entries_index
        # delete all
        self.clear()
        # for all (unique) headwords
        for headword in original_entries_index:
            original_entries_index_headword = original_entries_index[headword]
            definitions_to_be_merged = [original_entries[i].definition for i in original_entries_index_headword]
            merged_definition = merge_function(headword, definitions_to_be_merged)
            self.add_entry(headword=headword, definition=merged_definition)
            new_headword_index = len(self) - 1
            # add synonyms to this new entry, by adding all synonyms of the original entries
            # merged into this new entry (with index new_headword_index in self.entries)
            for i in original_entries_index_headword:
                original_entry_synonyms = original_entries[i].get_synonyms()
                for synonym in original_entry_synonyms:
                    self.add_synonym(synonym=synonym, headword_index=new_headword_index)

        # not needed, since we called self.clear()
        #self.sort(False, False, False, False)



