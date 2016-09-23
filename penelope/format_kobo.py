#!/usr/bin/env python
# coding=utf-8

"""
Read/write Kobo dictionaries.

The read function only acquires the index,
as the definition files of the original Kobo dictionaries
are obfuscated/encrypted.

The write function, however, is able to output
fully functional Kobo dictionaries
(provided that their file names match one of the official ones,
probably because they are hard-coded in the Kobo firmware).

The MARISA executables marisa-build and marisa-reverse-lookup
must be installed as the Python module marisa_trie or
as executables in your $PATH.
"""

from __future__ import absolute_import
import gzip
import imp
import io
import os
import subprocess
import zipfile

from penelope.prefix_kobo import get_prefix as get_prefix_kobo
from penelope.utilities import create_temp_directory
from penelope.utilities import create_temp_file
from penelope.utilities import delete_directory
from penelope.utilities import delete_file
from penelope.utilities import print_debug
from penelope.utilities import print_error
from penelope.utilities import print_info
from penelope.utilities import rename_file

__author__ = "Alberto Pettarin"
__copyright__ = "Copyright 2012-2016, Alberto Pettarin (www.albertopettarin.it)"
__license__ = "MIT"
__version__ = "3.1.3"
__email__ = "alberto@albertopettarin.it"
__status__ = "Production"

WORDS_FILE_NAME = u"words"
MARISA_BUILD = u"marisa-build"
MARISA_REVERSE_LOOKUP = u"marisa-reverse-lookup"


def read(dictionary, args, input_file_paths):
    def read_single_file(dictionary, args, input_file_path):
        # result flag
        result = False

        # create a tmp file
        tmp_handler, tmp_path = create_temp_file()

        # copy the index file from the zip to the tmp file
        input_file_obj = zipfile.ZipFile(input_file_path)
        tmp_file_obj = io.open(tmp_path, "wb")
        tmp_file_obj.write(input_file_obj.read(WORDS_FILE_NAME))
        tmp_file_obj.close()
        input_file_obj.close()

        # read index with MARISA
        try:
            # call MARISA with marisa_trie module
            import marisa_trie
            trie = marisa_trie.Trie()
            trie.load(tmp_path)
            for pair in trie.items():
                dictionary.add_entry(headword=pair[0], definition=u"")
            result = True
        except ImportError as exc:
            # call MARISA with subprocess
            print_info("  MARISA cannot be imported as Python module. You might want to install it with:")
            print_info("  $ [sudo] pip install marisa_trie")
            marisa_reverse_lookup_path = MARISA_REVERSE_LOOKUP
            if args.marisa_bin_path is None:
                print_info("  Running '%s' from $PATH" % MARISA_REVERSE_LOOKUP)
            else:
                marisa_reverse_lookup_path = os.path.join(args.marisa_bin_path, MARISA_REVERSE_LOOKUP)
                print_info("  Running '%s' from '%s'" % (MARISA_REVERSE_LOOKUP, args.marisa_bin_path))
            # TODO this is ugly, but it works
            query = (u"\n".join([str(x) for x in range(int(args.marisa_index_size))]) + u"\n").encode("utf-8")

            try:
                proc = subprocess.Popen(
                    [marisa_reverse_lookup_path, tmp_path],
                    stdout=subprocess.PIPE,
                    stdin=subprocess.PIPE,
                    stderr=subprocess.PIPE
                )
                stdout = proc.communicate(input=query)[0].decode("utf-8")
                for line in stdout.splitlines():
                    array = line.split("\t")
                    if len(array) >= 2:
                        key = array[1]
                        if args.ignore_case:
                            key = key.lower()
                        dictionary.add_entry(headword=key, definition=u"")
                result = True
            except OSError as exc:
                print_error("  Unable to run '%s' as '%s'" % (MARISA_REVERSE_LOOKUP, marisa_reverse_lookup_path))
                print_error("  Please make sure '%s':" % MARISA_REVERSE_LOOKUP)
                print_error("    1. is available on your $PATH or")
                print_error("    2. specify its path with --marisa-bin-path or")
                print_error("    3. install the marisa_trie Python module")
        except:
            print_debug("Reading from file '%s'... failed" % (input_file_path))

        # delete the tmp file
        delete_file(tmp_handler, tmp_path)
        return result

    for input_file_path in input_file_paths:
        print_debug("Reading from file '%s'..." % (input_file_path), args.debug)
        result = read_single_file(dictionary, args, input_file_path)
        if result:
            print_debug("Reading from file '%s'... success" % (input_file_path), args.debug)
        else:
            print_error("Reading from file '%s'... failed" % (input_file_path))
            return None
    return dictionary


def write(dictionary, args, output_file_path):
    # result to be returned
    result = None

    # get absolute path
    output_file_path_absolute = os.path.abspath(output_file_path)

    # create tmp directory
    cwd = os.getcwd()
    tmp_path = create_temp_directory()
    print_debug("Working in temp dir '%s'" % (tmp_path), args.debug)
    os.chdir(tmp_path)

    # sort by headword
    dictionary.sort(by_headword=True)

    # group by prefix
    files_to_compress = []
    prefix_length = int(args.group_by_prefix_length)
    special_group, group_keys, group_dict = dictionary.group(
        prefix_function=get_prefix_kobo,
        prefix_length=prefix_length,
        merge_min_size=int(args.group_by_prefix_merge_min_size),
        merge_across_first=args.group_by_prefix_merge_across_first
    )
    if special_group is not None:
        special_group_key = u"1" * prefix_length
        group_dict[special_group_key] = special_group
        group_keys = [special_group_key] + group_keys

    # write files
    for key in group_keys:
        # write html file
        file_html_path = key + u".html"
        file_html_obj = io.open(file_html_path, "wb")
        file_html_obj.write(u"<?xml version=\"1.0\" encoding=\"utf-8\"?><html>".encode("utf-8"))
        for entry in group_dict[key]:
            headword = entry.headword
            definition = entry.definition
            file_html_obj.write((u"<w><a name=\"%s\"/><div><b>%s</b><br/>%s</div></w>" % (headword, headword, definition)).encode("utf-8"))
        file_html_obj.write((u"</html>").encode("utf-8"))
        file_html_obj.close()

        # compress in gz format
        file_html_obj = io.open(file_html_path, "rb")
        file_gz_path = file_html_path + u".gz"
        file_gz_obj = gzip.open(file_gz_path, "wb")
        file_gz_obj.writelines(file_html_obj)
        file_gz_obj.close()
        file_html_obj.close()

        # delete .html file
        delete_file(None, file_html_path)
        # rename .html.gz file into .html
        rename_file(file_gz_path, file_html_path)
        files_to_compress.append(file_html_path)

    # write words
    file_words_path = WORDS_FILE_NAME
    keys = sorted(dictionary.entries_index.keys())
    try:
        import marisa_trie
        trie = marisa_trie.Trie(keys)
        trie.save(file_words_path)
        result = [file_words_path]
    except ImportError as exc:
        # call MARISA with subprocess
        print_info("  MARISA cannot be imported as Python module. You might want to install it with:")
        print_info("  $ [sudo] pip install marisa_trie")
        marisa_build_path = MARISA_BUILD
        if args.marisa_bin_path is None:
            print_info("  Running '%s' from $PATH" % MARISA_BUILD)
        else:
            marisa_build_path = os.path.join(args.marisa_bin_path, MARISA_BUILD)
            print_info("  Running '%s' from '%s'" % (MARISA_BUILD, args.marisa_bin_path))
        # TODO this is ugly, but it works
        query = (u"\n".join([x for x in keys]) + u"\n").encode("utf-8")

        try:
            proc = subprocess.Popen(
                [marisa_build_path, "-l", "-o", file_words_path],
                stdout=subprocess.PIPE,
                stdin=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            proc.communicate(input=query)[0].decode("utf-8")
            result = [file_words_path]
        except OSError as exc:
            print_error("  Unable to run '%s' as '%s'" % (MARISA_BUILD, marisa_build_path))
            print_error("  Please make sure '%s':" % MARISA_BUILD)
            print_error("    1. is available on your $PATH or")
            print_error("    2. specify its path with --marisa-bin-path or")
            print_error("    3. install the marisa_trie Python module")
            result = None

    if result is not None:
        # add file_words_path to files to compress
        files_to_compress.append(file_words_path)
        # create output zip file
        try:
            print_debug("Writing to file '%s'..." % (output_file_path_absolute), args.debug)
            file_zip_obj = zipfile.ZipFile(output_file_path_absolute, "w", zipfile.ZIP_DEFLATED)
            for file_to_compress in files_to_compress:
                file_to_compress = os.path.basename(file_to_compress)
                file_zip_obj.write(file_to_compress)
            file_zip_obj.close()
            result = [output_file_path]
            print_debug("Writing to file '%s'... success" % (output_file_path_absolute), args.debug)
        except:
            print_error("Writing to file '%s'... failure" % (output_file_path_absolute))

    # delete tmp directory
    os.chdir(cwd)
    if args.keep:
        print_info("Not deleting temp dir '%s'" % (tmp_path))
    else:
        delete_directory(tmp_path)
        print_debug("Deleted temp dir '%s'" % (tmp_path), args.debug)

    return result
