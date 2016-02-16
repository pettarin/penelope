#!/usr/bin/env python
# coding=utf-8

"""
Read/write Bookeen dictionaries.
"""

from __future__ import absolute_import
from io import open
import imp
import os
import sqlite3
import zipfile

from penelope.collation_default import collate_function as collate_function_default
from penelope.utilities import print_debug
from penelope.utilities import print_error
from penelope.utilities import print_info
from penelope.utilities import create_temp_directory
from penelope.utilities import copy_file
from penelope.utilities import delete_directory

__author__ = "Alberto Pettarin"
__copyright__ = "Copyright 2012-2016, Alberto Pettarin (www.albertopettarin.it)"
__license__ = "MIT"
__version__ = "3.1.2"
__email__ = "alberto@albertopettarin.it"
__status__ = "Production"

CHUNK_FILE_PREFIX = "c_"
CHUNK_SIZE = 262144 # 2^18
EMPTY_FILE_PATH = os.path.join(os.path.split(os.path.abspath(__file__))[0], "res/empty.idx")
HEADER = "<!DOCTYPE html PUBLIC \"-//W3C//DTD XHTML 1.0 Strict//EN\"  \"http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd\" [<!ENTITY ns \"&#8226;\">]><html xml:lang=\"%s\" xmlns=\"http://www.w3.org/1999/xhtml\"><head><title></title></head><body>"

def read(dictionary, args, input_file_string):
    def read_single_dict(dictionary, args, single_dict):
        # create tmp directory
        tmp_path = create_temp_directory()
        print_debug("Working in temp dir '%s'" % (tmp_path), args.debug)

        if len(single_dict) == 1:
            print_debug("Unzipping .install file...", args.debug)
            zip_file_path = single_dict[0]
            idx_file_path = os.path.join(tmp_path, "d.dict.idx")
            dict_file_path = os.path.join(tmp_path, "d.dict")
            zip_file_obj = zipfile.ZipFile(zip_file_path, "r")
            for entry in zip_file_obj.namelist():
                if entry.endswith(".dict.idx"):
                    zip_entry = zip_file_obj.open(entry)
                    idx_file_obj = open(idx_file_path, "wb")
                    idx_file_obj.write(zip_entry.read())
                    idx_file_obj.close()
                    zip_entry.close()
                elif entry.endswith(".dict"):
                    zip_entry = zip_file_obj.open(entry)
                    dict_file_obj = open(dict_file_path, "wb")
                    dict_file_obj.write(zip_entry.read())
                    dict_file_obj.close()
                    zip_entry.close()
            zip_file_obj.close()
            print_debug("Unzipping .install file... done", args.debug)
        else:
            print_debug("Files .dict.idx and .dict already uncompressed...", args.debug)
            idx_file_path = single_dict[0]
            dict_file_path = single_dict[1]
            for file_path in [idx_file_path, dict_file_path]:
                if not os.path.exists(file_path):
                    print_error("File '%s' does not exist" % file_path)
                    return False
            print_debug("Files .dict.idx and .dict already uncompressed... done", args.debug)

        # unzip .dict file into tmp_path
        print_debug("Unzipping .dict file...", args.debug)
        zip_file_obj = zipfile.ZipFile(dict_file_path, "r")
        for entry in zip_file_obj.namelist():
            if not entry.endswith("/"):
                zip_entry = zip_file_obj.open(entry)
                entry_file_path = os.path.join(tmp_path, os.path.basename(entry))
                entry_file_obj = open(entry_file_path, "wb")
                entry_file_obj.write(zip_entry.read())
                entry_file_obj.close()
                zip_entry.close()
        zip_file_obj.close()
        print_debug("Unzipping .dict file... done", args.debug)

        # read .dict.idx
        print_debug("Reading .dict.idx file...", args.debug)
        sql_connection = sqlite3.connect(idx_file_path)
        sql_cursor = sql_connection.cursor()
        sql_cursor.execute("select * from T_DictIndex")
        index_data = sql_cursor.fetchall()
        chunk_index_to_entries = {}
        max_chunk_index = 1
        for index_entry in index_data:
            headword = index_entry[1]
            if args.ignore_case:
                headword = headword.lower()
            offset = index_entry[2]
            size = index_entry[3]
            chunk_index = index_entry[4]
            if not chunk_index in chunk_index_to_entries:
                chunk_index_to_entries[chunk_index] = []
            if chunk_index > max_chunk_index:
                max_chunk_index = chunk_index
            chunk_index_to_entries[chunk_index].append([headword, offset, size])
        sql_cursor.close()
        sql_connection.close()
        print_debug("Reading .dict.idx file... done", args.debug)

        # read c_* files
        print_debug("Reading c_* files...", args.debug)
        for chunk_index in range(1, max_chunk_index + 1):
            print_debug("  Reading c_%d file..." % (chunk_index), args.debug)
            chunk_file_path = os.path.join(tmp_path, "%s%d" % (CHUNK_FILE_PREFIX, chunk_index))
            chunk_file_obj = open(chunk_file_path, "rb")
            for entry in chunk_index_to_entries[chunk_index]:
                headword = entry[0]
                offset = entry[1]
                size = entry[2]
                chunk_file_obj.seek(offset)
                definition_bytes = chunk_file_obj.read(size)
                definition_unicode = definition_bytes.decode(args.input_file_encoding)
                dictionary.add_entry(headword=headword, definition=definition_unicode)
            chunk_file_obj.close()
            print_debug("  Reading c_%d file... done" % (chunk_index), args.debug)
        print_debug("Reading c_* files... done", args.debug)

        # delete tmp directory
        if args.keep:
            print_info("Not deleting temp dir '%s'" % (tmp_path))
        else:
            delete_directory(tmp_path)
            print_debug("Deleted temp dir '%s'" % (tmp_path), args.debug)
        return True 

    single_dicts = []
    for prefix in input_file_string.split(","):
        if prefix.endswith(".install"):
            single_dicts.append([prefix])
        elif prefix.endswith(".dict"):
            tentative_dict_path = prefix
            tentative_idx_path = tentative_dict_path + u".idx"
            if (os.path.exists(tentative_idx_path)) and (os.path.exists(tentative_dict_path)):
                single_dicts.append([tentative_idx_path, tentative_dict_path])
        else:
            tentative_dict_path = prefix + u".dict"
            tentative_idx_path = tentative_dict_path + u".idx"
            if (os.path.exists(tentative_idx_path)) and (os.path.exists(tentative_dict_path)):
                single_dicts.append([tentative_idx_path, tentative_dict_path])
    
    if len(single_dicts) == 0:
        print_error("Cannot find .install or .dict.idx/.dict files")
        return None

    for single_dict in single_dicts:
        print_debug("Reading from file '%s'..." % (single_dict), args.debug)
        result = read_single_dict(dictionary, args, single_dict)
        if result:
            print_debug("Reading from file '%s'... success" % (single_dict), args.debug)
        else:
            print_error("Reading from file '%s'... failed" % (single_dict))
            return None
    return dictionary

def write(dictionary, args, output_file_path):
    # result to be returned
    result = None

    # get absolute path
    output_file_path_absolute = os.path.abspath(output_file_path)

    # get absolute path for collation function file 
    bookeen_collation_function_path = None
    if args.bookeen_collation_function is not None:
        bookeen_collation_function_path = os.path.abspath(args.bookeen_collation_function)

    # create tmp directory
    cwd = os.getcwd()
    tmp_path = create_temp_directory()
    print_debug("Working in temp dir '%s'" % (tmp_path), args.debug)
    os.chdir(tmp_path)

    # get the basename
    base = os.path.basename(output_file_path)
    if base.endswith(".zip"):
        base = base[:-4]

    # copy empty.idx into tmp_path
    idx_file_path = base + u".dict.idx"
    dict_file_path = base + u".dict"
    copy_file(EMPTY_FILE_PATH, idx_file_path)

    # open index
    sql_connection = sqlite3.connect(idx_file_path)

    # install collation in the index
    collation_function = collate_function_default
    if bookeen_collation_function_path is not None:
        try:
            collation_function = imp.load_source("", bookeen_collation_function_path).collate_function
            print_debug("Using collation function from '%s'" % (bookeen_collation_function_path), args.debug)
        except:
            print_error("Unable to load collation function from '%s'. Using the default collation function instead." % (bookeen_collation_function_path))
    sql_connection.create_collation("IcuNoCase", collation_function)
    sql_connection.text_factory = str

    # get a cursor and delete any data from the index file
    sql_cursor = sql_connection.cursor()
    sql_cursor.execute("delete from T_DictIndex")

    # write c_* files
    # each c_* file has MAX_CHUNK_SIZE < size <= (MAX_CHUNK_SIZE * 2) bytes (tentatively)
    print_debug("Writing c_* files...", args.debug)
    files_to_compress = []
    current_offset = 0
    chunk_index = 1
    chunk_file_path = "%s%d" % (CHUNK_FILE_PREFIX, chunk_index)
    files_to_compress.append(chunk_file_path)
    chunk_file_obj = open(chunk_file_path, "wb")
    for entry_index in dictionary.entries_index_sorted:
        entry = dictionary.entries[entry_index]
        definition_bytes = entry.definition.encode("utf-8")
        definition_size = len(definition_bytes)
        chunk_file_obj.write(definition_bytes)
        # insert headword into index file
        sql_tuple = (0, entry.headword, current_offset, definition_size, chunk_index)
        sql_cursor.execute("insert into T_DictIndex values (?,?,?,?,?)", sql_tuple)
        # insert synonyms into index file
        if not args.ignore_synonyms:
            for synonym in entry.get_synonyms():
                sql_tuple = (0, synonym[0], current_offset, definition_size, chunk_index)
                sql_cursor.execute("insert into T_DictIndex values (?,?,?,?,?)", sql_tuple)
        # update offset
        current_offset += definition_size
        # if we reached CHUNK_SIZE, open the next c_* file
        if current_offset > CHUNK_SIZE:
            chunk_file_obj.close()
            chunk_index += 1
            chunk_file_path = "%s%d" % (CHUNK_FILE_PREFIX, chunk_index)
            files_to_compress.append(chunk_file_path)
            chunk_file_obj = open(chunk_file_path, "wb")
            current_offset = 0
    chunk_file_obj.close()
    print_debug("Writing c_* files... done", args.debug)

    # compress
    print_debug("Compressing c_* files...", args.debug)
    file_zip_obj = zipfile.ZipFile(dict_file_path, "w", zipfile.ZIP_DEFLATED)
    for file_to_compress in files_to_compress:
        file_to_compress = os.path.basename(file_to_compress)
        file_zip_obj.write(file_to_compress)
    file_zip_obj.close()
    print_debug("Compressing c_* files... done", args.debug)

    # update index metadata
    print_debug("Updating index metadata...", args.debug)
    header = HEADER % (args.language_from)
    sql_cursor.execute("update T_DictInfo set F_xhtmlHeader=?", (header,))
    sql_cursor.execute("update T_DictInfo set F_LangFrom=?", (args.language_from,))
    sql_cursor.execute("update T_DictInfo set F_LangTo=?", (args.language_to,))
    sql_cursor.execute("update T_DictInfo set F_Licence=?", (args.license,))
    sql_cursor.execute("update T_DictInfo set F_Copyright=?", (args.copyright,))
    sql_cursor.execute("update T_DictInfo set F_Title=?", (args.title,))
    sql_cursor.execute("update T_DictInfo set F_Description=?", (args.description,))
    sql_cursor.execute("update T_DictInfo set F_Year=?", (args.year,))
    # the meaning of the following is unknown 
    sql_cursor.execute("update T_DictInfo set F_Alphabet=?", ("Z",))
    sql_cursor.execute("update T_DictInfo set F_CollationLevel=?", ("1",))
    sql_cursor.execute("update T_DictVersion set F_DictType=?", ("stardict",))
    sql_cursor.execute("update T_DictVersion set F_Version=?", ("11",))
    print_debug("Updating index metadata... done", args.debug)

    # compact and close
    sql_cursor.execute("vacuum")
    sql_cursor.close()
    sql_connection.close()

    # create .install file or copy .dict.idx and .dict into requested output directory
    parent_output_directory = os.path.split(output_file_path_absolute)[0]
    if args.bookeen_install_file:
        print_debug("Creating .install file...", args.debug)
        file_zip_path = os.path.join(parent_output_directory, base + u".install")
        file_zip_obj = zipfile.ZipFile(file_zip_path, "w", zipfile.ZIP_DEFLATED)
        for file_to_compress in [dict_file_path, idx_file_path]:
            file_to_compress = os.path.basename(file_to_compress)
            file_zip_obj.write(file_to_compress)
        file_zip_obj.close()
        result = [file_zip_path]
        print_debug("Creating .install file... done", args.debug)
    else:
        print_debug("Copying .dict.idx and .dict files...", args.debug)
        dict_file_path_final = os.path.join(parent_output_directory, os.path.basename(dict_file_path))
        idx_file_path_final = os.path.join(parent_output_directory, os.path.basename(idx_file_path))
        copy_file(dict_file_path, dict_file_path_final)
        copy_file(idx_file_path, idx_file_path_final)
        result = [idx_file_path_final, dict_file_path_final]
        print_debug("Copying .dict.idx and .dict files... done", args.debug)

    # delete tmp directory
    os.chdir(cwd)
    if args.keep:
        print_info("Not deleting temp dir '%s'" % (tmp_path))
    else:
        delete_directory(tmp_path)
        print_debug("Deleted temp dir '%s'" % (tmp_path), args.debug)

    return result



