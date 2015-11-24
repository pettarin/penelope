#!/usr/bin/env python
# coding=utf-8

"""
Write MOBI (Kindle) dictionaries.

It creates a .opf and .html file, and invokes kindlegen to compile it.
"""

from __future__ import absolute_import
from io import open
import os
import subprocess

from penelope.utilities import print_debug
from penelope.utilities import print_error
from penelope.utilities import print_info
from penelope.utilities import create_temp_directory
from penelope.utilities import copy_file
from penelope.utilities import delete_directory
from penelope.utilities import rename_file

__author__ = "Alberto Pettarin"
__copyright__ = "Copyright 2012-2015, Alberto Pettarin (www.albertopettarin.it)"
__license__ = "MIT"
__version__ = "3.0.1"
__email__ = "alberto@albertopettarin.it"
__status__ = "Production"

KINDLEGEN = u"kindlegen"

HTML_HEADER = u"""<html>
 <head>
  <meta http-equiv="Content-Type" content="text/html;charset=utf-8" />
  <title>%s</title>
 </head>
 <body topmargin="0" bottommargin="0" leftmargin="5" rightmargin="5">
  <center>
   <hr />
   <font size="+4">%s</font>
   <hr />
  </center>
  <mbp:pagebreak />
"""

HTML_FOOTER = u""" </body>
</html>"""

HTML_WORD = u"""
  <idx:entry>
   <h1><idx:orth>%s</idx:orth></h1>
   <p>%s</p>
  </idx:entry>
  <mbp:pagebreak />
"""

OPF_TEMPLATE = u"""<?xml version="1.0" encoding="utf-8"?>
<package unique-identifier="uid">
    <metadata>
        <dc-metadata xmlns:dc="http://purl.org/metadata/dublin_core" xmlns:oebpackage="http://openebook.org/namespaces/oeb-package/1.0/">
            <dc:Title>%s</dc:Title>
            <dc:Language>%s</dc:Language>
            <dc:Identifier id="uid">%s</dc:Identifier>
            <dc:Creator>%s</dc:Creator>
            <dc:Rights>%s</dc:Rights>
            <dc:Subject BASICCode="REF008000">Dictionaries</dc:Subject>
        </dc-metadata>
        <x-metadata>
            <output encoding="utf-8"></output>
            <DictionaryInLanguage>%s</DictionaryInLanguage>
            <DictionaryOutLanguage>%s</DictionaryOutLanguage>
            <EmbeddedCover>%s</EmbeddedCover>
        </x-metadata>
    </metadata>
    <manifest>
        <item id="item1" media-type="text/x-oeb1-document" href="words.html"></item>
    </manifest>
    <spine>
        <itemref idref="item1"/>
    </spine>
    <tours></tours>
    <guide></guide>
</package>"""

def read(dictionary, args, input_file_paths):
    print_error("Read function not implemented for MOBI dictionaries")
    return None

def write(dictionary, args, output_file_path):
    # result to be returned
    result = None

    # sort by headword, optionally ignoring case
    dictionary.sort(by_headword=True, ignore_case=args.sort_ignore_case)

    # create tmp directory
    tmp_path = create_temp_directory()

    # get the basename
    base = os.path.basename(output_file_path)
    if base.endswith(".mobi"):
        base = base[:-5]
    file_mobi_rel_path = base + u".mobi"
    file_html_path = os.path.join(tmp_path, file_mobi_rel_path)

    # copy cover
    file_cover_rel_path = u"cover"
    file_cover_path = os.path.join(tmp_path, file_cover_rel_path)
    if args.cover_path is not None:
        if os.path.exists(args.cover_path):
            file_cover_rel_path = os.path.basename(args.cover_path)
            file_cover_path = os.path.join(tmp_path, file_cover_rel_path)
            copy_file(args.cover_path, file_cover_path)
        else:
            print_error("Unable to read cover file '%s'" % (args.cover_path))
    else:
        print_error("No cover image file specified: generating MOBI without cover")
        print_error("Use --cover-path to specify a cover image file")

    # TODO split over multiple files?
    # write .html file
    print_debug("Writing .html file...", args.debug)
    file_html_rel_path = u"words.html"
    file_html_path = os.path.join(tmp_path, file_html_rel_path)
    file_html_obj = open(file_html_path, "wb")
    file_html_obj.write((HTML_HEADER % (args.title, args.title)).encode("utf-8"))
    for index in dictionary.entries_index_sorted:
        entry = dictionary.entries[index]
        file_html_obj.write((HTML_WORD % (entry.headword, entry.definition)).encode("utf-8"))
    file_html_obj.write((HTML_FOOTER).encode("utf-8"))
    file_html_obj.close()
    print_debug("Writing .html file... done", args.debug)

    # write .opf file
    print_debug("Writing .opf file...", args.debug)
    file_opf_rel_path = base + u".opf"
    file_opf_path = os.path.join(tmp_path, file_opf_rel_path)
    file_opf_obj = open(file_opf_path, "wb")
    opf_content = OPF_TEMPLATE % (
        args.title,
        args.language_from,
        args.identifier,
        args.author,
        args.copyright,
        args.language_from,
        args.language_to,
        file_cover_rel_path
    )
    file_opf_obj.write((opf_content).encode("utf-8"))
    file_opf_obj.close()
    print_debug("Writing .opf file... done", args.debug)

    # run kindlegen
    if args.mobi_no_kindlegen:
        print_info("Not running kindlegen, the raw files are located in '%s'" % tmp_path)
        result = [tmp_path]
    else:
        try:
            print_debug("Creating .mobi file with kindlegen...", args.debug)
            kindlegen_path = KINDLEGEN
            if args.kindlegen_path is None:
                print_info("  Running '%s' from $PATH" % KINDLEGEN)
            else:
                kindlegen_path = args.kindlegen_path
                print_info("  Running '%s' from '%s'" % (KINDLEGEN, kindlegen_path))
            proc = subprocess.Popen(
                [kindlegen_path, file_opf_path, "-o", file_mobi_rel_path],
                stdout=subprocess.PIPE,
                stdin=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            output = proc.communicate()
            if args.debug:
                output_unicode = (output[0]).decode("utf-8")
                print_debug(output_unicode, args.debug)
            rename_file(file_html_path, output_file_path)
            result = [output_file_path]
            print_debug("Creating .mobi file with kindlegen... done", args.debug)
        except OSError as exc:
            print_error("  Unable to run '%s' as '%s'" % (KINDLEGEN, kindlegen_path))
            print_error("  Please make sure '%s':" % KINDLEGEN)
            print_error("    1. is available on your $PATH or")
            print_error("    2. specify its path with --kindlegen-path")
            result = None

        # delete tmp directory
        if args.keep:
            print_info("Not deleting temp dir '%s'" % (tmp_path))
        else:
            delete_directory(tmp_path)
            print_debug("Deleted temp dir '%s'" % (tmp_path), args.debug)

    return result



