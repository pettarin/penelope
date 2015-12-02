#!/usr/bin/env python
# coding=utf-8

"""
Read/write StarDict dictionaries.

To write a StarDict file, the dictzip executable is required.
"""

from __future__ import absolute_import
from io import open
import gzip
import os
import subprocess
import struct
import zipfile

from penelope.utilities import create_temp_directory
from penelope.utilities import delete_directory
from penelope.utilities import print_debug
from penelope.utilities import print_error
from penelope.utilities import print_info

__author__ = "Alberto Pettarin"
__copyright__ = "Copyright 2012-2015, Alberto Pettarin (www.albertopettarin.it)"
__license__ = "MIT"
__version__ = "3.1.1"
__email__ = "alberto@albertopettarin.it"
__status__ = "Production"

DICTZIP = u"dictzip"

SAMETYPESEQUENCE_SUPPORTED_VALUES = [
    u"m", # pure text
    u"l", # pure text (locale encoding instead of UTF-8, use --input-file-encoding to specify it)
    u"g", # Pango markup
    u"t", # English phonetic
    u"x", # XDXF markup
    u"y", # Chinese YinBiao or Japanese KANA
    u"k", # KingSoft PowerWord markup
    u"w", # MediaWiki markup
    u"h"  # HTML markup
]         # all the above are UTF-8 encoded (except "l") and terminated by \0

def read(dictionary, args, input_file_paths):
    def find_files(entries):
        found = {}
        for entry in entries:
            if entry.endswith(".ifo"):
                found["d.ifo"] = entry
                break
        if not "d.ifo" in found:
            print_error("Cannot find .ifo file in the given StarDict file (see StarDict spec)")
            return {}
        # remove .ifo extension
        base = found["d.ifo"][:-4]
        # attempt to find these ones
        tentative_idx = base + ".idx"
        tentative_idx_gz = base + ".idx.gz"
        tentative_dict = base + ".dict"
        tentative_dict_dz = base + ".dict.dz"
        tentative_dz = base + ".dz"
        if tentative_idx in entries:
            found["d.idx"] = tentative_idx
        if tentative_idx_gz in entries:
            found["d.idx.gz"] = tentative_idx_gz
        if not (("d.idx" in found) or ("d.idx.gz" in found)):
            print_error("Cannot find .idx or .idx.gz file in the given StarDict file (see StarDict spec)")
            return {}
        if tentative_dict in entries:
            found["d.dict"] = tentative_dict
        if tentative_dict_dz in entries:
            found["d.dict.dz"] = tentative_dict_dz
        if tentative_dz in entries:
            found["d.dz"] = tentative_dz
        if not (("d.dict" in found) or ("d.dict.dz" in found) or ("d.dz" in found)):
            print_error("Cannot find .dict, .dict.dz, or .dz file in the given StarDict file (see StarDict spec)")
            return {}
        # syn is optional
        tentative_syn = base + ".syn"
        if tentative_syn in entries:
            found["d.syn"] = tentative_syn
        return found

    def uncompress_file(compressed_path, tmp_path, key):
        uncompressed_path = os.path.join(tmp_path, key)
        u_obj = open(uncompressed_path, "wb")
        c_obj = gzip.open(compressed_path, "rb")
        u_obj.write(c_obj.read())
        c_obj.close()
        u_obj.close()
        print_debug("Uncompressed %s" % (uncompressed_path), args.debug)
        return uncompressed_path

    def read_ifo(ifo_path, has_syn, args):
        ifo_dict = {}
        ifo_obj = open(ifo_path, "rb")
        ifo_bytes = ifo_obj.read() # bytes
        ifo_unicode = ifo_bytes.decode("utf-8") # unicode, always utf-8 by spec
        ifo_obj.close()
        for line in ifo_unicode.splitlines():
            array = line.split("=")
            if len(array) >= 2:
                key = array[0]
                val = "=".join(array[1:])
                ifo_dict[key] = val
        
        if not "version" in ifo_dict:
            print_error("No 'version' found in the .ifo file (see StarDict spec)")
            return None
        if ifo_dict["version"] not in ["2.4.2", "3.0.0"]:
            print_error("The .ifo file must have a 'version' value equal to '2.4.2' or '3.0.0' (see StarDict spec)")
            return None

        required_keys = ["bookname", "wordcount", "idxfilesize"]
        if has_syn:
            required_keys.append("synwordcount")
        # TODO not used => disabling this
        #if ifo_dict["version"] == "3.0.0":
        #    required_keys.append("idxoffsetbits")
        for key in required_keys:
            if not key in ifo_dict:
                print_error("No '%s' found in the .ifo file (see StarDict spec)" % key)
                return None

        ifo_dict["wordcount"] = int(ifo_dict["wordcount"])
        ifo_dict["idxfilesize"] = int(ifo_dict["idxfilesize"])
        if has_syn:
            ifo_dict["synwordcount"] = int(ifo_dict["synwordcount"])
        # TODO not used => disabling this
        #if ifo_dict["version"] == "3.0.0":
        #    ifo_dict["idxoffsetbits"] = int(ifo_dict["idxoffsetbits"])

        if args.sd_ignore_sametypesequence:
            print_debug("Ignoring sametypesequence value", args.debug)
        else:
            # TODO limitation: we require sametypesequence to be present
            if not "sametypesequence" in ifo_dict:
                print_error("The .ifo file must have a 'sametypesequence' value (see README).")
                return None
            # TODO limitation: we require sametypesequence to have a value in SAMETYPESEQUENCE_SUPPORTED_VALUES
            if not ifo_dict["sametypesequence"] in SAMETYPESEQUENCE_SUPPORTED_VALUES:
                print_error("The .ifo file must have a 'sametypesequence' value of %s (see README)." % "|".join(SAMETYPESEQUENCE_SUPPORTED_VALUES))
                return None

        return ifo_dict

    def read_single_file(dictionary, args, input_file_path):
        # result flag
        result = False

        # create a tmp directory
        tmp_path = create_temp_directory()
        print_debug("Working in temp dir '%s'" % (tmp_path), args.debug)

        # find .ifo, .idx, .dict[.dz] and .syn files inside the zip
        # and extract them to tmp_path
        input_file_obj = zipfile.ZipFile(input_file_path)
        found_files = find_files(input_file_obj.namelist())
        extracted_files = {}
        if len(found_files) > 0:
            for key in found_files:
                entry = found_files[key]
                ext_file_path = os.path.join(tmp_path, key)
                ext_file_obj = open(ext_file_path, "wb")
                zip_entry = input_file_obj.open(entry)
                ext_file_obj.write(zip_entry.read())
                zip_entry.close()
                ext_file_obj.close()
                print_debug("Extracted %s" % (ext_file_path), args.debug)
                extracted_files[key] = ext_file_path
                # extract from compressed file, but only if ".idx" is not present as well
                if (key == "d.idx.gz") and ("d.idx" not in found_files):
                    extracted_files["d.idx"] = uncompress_file(ext_file_path, tmp_path, "d.idx")
                # extract from compressed file, but only if ".dict" is not present as well
                if ((key == "d.dict.dz") or (key == "d.dz")) and ("d.dict" not in found_files):
                    extracted_files["d.dict"] = uncompress_file(ext_file_path, tmp_path, "d.dict")
        input_file_obj.close()

        # here we have d.ifo, d.idx and d.dict (all uncompressed) and possibly d.syn

        has_syn = "d.syn" in extracted_files
        if (has_syn) and (args.ignore_synonyms):
            has_syn = False
            print_debug("Dictionary has synonyms, but ignoring them (--ignore-synonym)", args.debug)
        ifo_dict = read_ifo(extracted_files["d.ifo"], has_syn, args)
        print_debug("Read .ifo file with values:\n%s" % (str(ifo_dict)), args.debug)

        # read dict file
        dict_file_obj = open(extracted_files["d.dict"], "rb")
        dict_file_bytes = dict_file_obj.read()
        dict_file_obj.close()

        # read idx file
        idx_file_obj = open(extracted_files["d.idx"], "rb")
        byte_read = idx_file_obj.read(1)
        headword = b""
        while byte_read:
            if byte_read == b"\0":
                # end of current word: read offset and size
                offset_bytes = idx_file_obj.read(4)
                offset_int = int((struct.unpack('>i', offset_bytes))[0])
                size_bytes = idx_file_obj.read(4)
                size_int = int((struct.unpack('>i', size_bytes))[0])
                definition = dict_file_bytes[offset_int:offset_int+size_int].decode(args.input_file_encoding)
                headword = headword.decode("utf-8")
                if args.ignore_case:
                    headword = headword.lower()
                dictionary.add_entry(headword=headword, definition=definition)
                headword = b""
            else:
                # read next byte
                headword += byte_read
            byte_read = idx_file_obj.read(1)
        idx_file_obj.close()
        result = True

        # read syn file, if present
        if has_syn:
            print_debug("The input StarDict file contains a .syn file, parsing it...", args.debug)
            result = False
            syn_file_obj = open(extracted_files["d.syn"], "rb")
            byte_read = syn_file_obj.read(1)
            synonym = b""
            while byte_read:
                if byte_read == b"\0":
                    # end of current synonym: read index of original word
                    index_bytes = syn_file_obj.read(4)
                    index_int = int((struct.unpack('>i', index_bytes))[0])
                    synonym = synonym.decode("utf-8")
                    if index_int < len(dictionary):
                        dictionary.add_synonym(synonym=synonym, headword_index=index_int)
                    else:
                        # emit a warning?
                        print_debug("Synonym '%s' points to index %d >= len(dictionary), skipping it" % (index_int, synonym), args.debug)
                    synonym = b""
                else:
                    # read next byte
                    synonym += byte_read
                byte_read = syn_file_obj.read(1)
            syn_file_obj.close()
            result = True
            print_debug("The input StarDict file contains a .syn file, parsing it... done", args.debug)
        else:
            print_debug("The input StarDict file does not contain a .syn file", args.debug)

        # delete tmp directory
        if args.keep:
            print_info("Not deleting temp dir '%s'" % (tmp_path))
        else:
            delete_directory(tmp_path)
            print_debug("Deleted temp dir '%s'" % (tmp_path), args.debug)

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

    # get the basename and compute output file paths
    base = os.path.basename(output_file_path)
    if base.endswith(".zip"):
        base = base[:-4]
    ifo_file_path = base + ".ifo"
    idx_file_path = base + ".idx"
    dict_file_path = base + ".dict"
    dict_dz_file_path = base + ".dict.dz"
    syn_file_path = base + ".syn"

    # TODO by spec, the index should be sorted
    # TODO using the comparator stardict_strcmp() defined in the spec
    # TODO (it calls g_ascii_strcasecmp() and/or strcmp() ),
    # TODO or with a user-defined collation function
    #
    # From https://developer.gnome.org/glib/2.28/glib-String-Utility-Functions.html#g-ascii-strcasecmp
    # gint g_ascii_strcasecmp (const gchar *s1, const gchar *s2);
    # Compare two strings, ignoring the case of ASCII characters.
    # Unlike the BSD strcasecmp() function, this only recognizes standard ASCII letters and ignores the locale, treating all non-ASCII bytes as if they are not letters.
    # This function should be used only on strings that are known to be in encodings where the bytes corresponding to ASCII letters always represent themselves. This includes UTF-8 and the ISO-8859-* charsets, but not for instance double-byte encodings like the Windows Codepage 932, where the trailing bytes of double-byte characters include all ASCII letters. If you compare two CP932 strings using this function, you will get false matches. 
    #
    # using Python's builtin lower() and sort() by headword
    # should be equivalent for UTF-8 encoded dictionaries (and it is fast)
    #
    dictionary.sort(by_headword=True, ignore_case=True)

    # write .idx and .dict files
    print_debug("Writing .idx and .dict files...", args.debug)
    idx_file_obj = open(idx_file_path, "wb")
    dict_file_obj = open(dict_file_path, "wb")
    current_offset = 0
    current_idx_size = 0
    for entry_index in dictionary.entries_index_sorted:
        entry = dictionary.entries[entry_index]
        headword_bytes = entry.headword.encode("utf-8")
        definition_bytes = entry.definition.encode("utf-8")
        definition_size = len(definition_bytes)
        # write .idx
        idx_file_obj.write(headword_bytes)
        idx_file_obj.write(b"\0")
        idx_file_obj.write(struct.pack('>i', current_offset))
        idx_file_obj.write(struct.pack('>i', definition_size))
        current_idx_size += (len(headword_bytes) + 1 + 4 + 4)
        # write .dict
        dict_file_obj.write(definition_bytes)
        current_offset += definition_size
    idx_file_obj.close()
    dict_file_obj.close()
    print_debug("Writing .idx and .dict files... done", args.debug)

    # list files to compress
    files_to_compress = []
    files_to_compress.append(ifo_file_path)
    files_to_compress.append(idx_file_path)

    # write .syn file
    dict_syns_len = 0
    if dictionary.has_synonyms:
        if args.ignore_synonyms:
            print_debug("Dictionary has synonyms, but ignoring them", args.debug)
        else:
            print_debug("Dictionary has synonyms, writing .syn file...", args.debug)
            syn_file_obj = open(syn_file_path, "wb")
            dict_syns = dictionary.get_synonyms()
            dict_syns_len = len(dict_syns)
            for pair in dict_syns:
                synonym_bytes = pair[0].encode("utf-8")
                index = pair[1]
                syn_file_obj.write(synonym_bytes)
                syn_file_obj.write(b"\0")
                syn_file_obj.write(struct.pack('>i', index))
            syn_file_obj.close()
            files_to_compress.append(syn_file_path)
            print_debug("Dictionary has synonyms, writing .syn file... done", args.debug)

    # compress .dict file
    if args.sd_no_dictzip:
        print_debug("Not compressing .dict file with dictzip", args.debug)
        files_to_compress.append(dict_file_path)
        result = [dict_file_path] 
    else:
        try:
            print_debug("Compressing .dict file with dictzip...", args.debug)
            dictzip_path = DICTZIP
            if args.dictzip_path is None:
                print_info("  Running '%s' from $PATH" % DICTZIP)
            else:
                dictzip_path = args.dictzip_path
                print_info("  Running '%s' from '%s'" % (DICTZIP, dictzip_path))
            proc = subprocess.Popen(
                [dictzip_path, "-k", dict_file_path],
                stdout=subprocess.PIPE,
                stdin=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            proc.communicate()
            result = [dict_dz_file_path] 
            files_to_compress.append(dict_dz_file_path)
            print_debug("Compressing .dict file with dictzip... done", args.debug)
        except OSError as exc:
            print_error("  Unable to run '%s' as '%s'" % (DICTZIP, dictzip_path))
            print_error("  Please make sure '%s':" % DICTZIP)
            print_error("    1. is available on your $PATH or")
            print_error("    2. specify its path with --dictzip-path or")
            print_error("    3. specify --no-dictzip to avoid compressing the .dict file")
            result = None 

    if result is not None:
        # create ifo file
        ifo_file_obj = open(ifo_file_path, "wb")
        ifo_file_obj.write((u"StarDict's dict ifo file\n").encode("utf-8"))
        ifo_file_obj.write((u"version=2.4.2\n").encode("utf-8"))
        ifo_file_obj.write((u"wordcount=%d\n" % (len(dictionary))).encode("utf-8"))
        ifo_file_obj.write((u"idxfilesize=%d\n" % (current_idx_size)).encode("utf-8"))
        ifo_file_obj.write((u"bookname=%s\n" % (args.title)).encode("utf-8"))
        ifo_file_obj.write((u"date=%s\n" % (args.year)).encode("utf-8"))
        ifo_file_obj.write((u"sametypesequence=m\n").encode("utf-8"))
        ifo_file_obj.write((u"description=%s\n" % (args.description)).encode("utf-8"))
        ifo_file_obj.write((u"author=%s\n" % (args.author)).encode("utf-8"))
        ifo_file_obj.write((u"email=%s\n" % (args.email)).encode("utf-8"))
        ifo_file_obj.write((u"website=%s\n" % (args.website)).encode("utf-8"))
        if dict_syns_len > 0:
            ifo_file_obj.write((u"synwordcount=%d\n" % (dict_syns_len)).encode("utf-8"))
        ifo_file_obj.close()

        # create output zip file
        try:
            print_debug("Writing to file '%s'..." % (output_file_path_absolute), args.debug)
            file_zip_obj = zipfile.ZipFile(output_file_path_absolute, "w", zipfile.ZIP_DEFLATED)
            for file_to_compress in files_to_compress:
                file_to_compress = os.path.basename(file_to_compress)
                file_zip_obj.write(file_to_compress)
                print_debug("Written %s" % (file_to_compress), args.debug)
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



