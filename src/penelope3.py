#!/usr/bin/env python
# -*- coding: utf-8 -*-

__license__     = 'MIT'
__author__      = 'Alberto Pettarin (alberto albertopettarin.it)'
__copyright__   = '2012-2014 Alberto Pettarin (alberto albertopettarin.it)'
__version__     = 'v2.0.0'
__date__        = '2014-06-30'
__description__ = 'Penelope is a multi-tool for creating, editing and converting dictionaries, especially for eReader devices'

### BEGIN changelog ###
#
# 2.0.0 2014-06-30 Moved to GitHub
# 1.21             Added encoding="utf-8" to Python3 open(..., "w") calls
# 1.20             Added XML escaping/unescaping via xml.sax.saxutils
# 1.19             Added merging multiple dictionaries
# 1.18             Added -l switch to MARISA_BUILD call, added F_CollationLevel to Odyssey output
# 1.17             Changed the sqlite collation function, to mimic NOCASE (see: http://www.sqlite.org/datatype3.html), and added support for custom collation support.
# 1.16             Added a command line option for specifying the field and/or line separator for CSV input/output
# 1.15             Added read from CSV (courtesy of Wolfgang Miller-Reichling). Code clean-up
# 1.14             Added read from Kobo and Odyssey format, write to XML format, and output EPUB dictionary
# 1.13             Fixed a bug (?) on Python 3.3 under Windows
# 1.12             StarDict and Kobo output with multiset index (multiple occurrences of the same keyword)
# 1.11             Support for non-ASCII characters in filenames for Kobo output
# 1.10             penelope3.py works under Linux with Python 3.2.3
# 1.09             Added "b" to open() calls and added unlink(): now penelope works under Windows with Python 2.7.3
# 1.08             Better management of Kobo output
# 1.07             Added Kobo output
# 1.06             Missing
# 1.05             Added StarDict output
# 1.04             Code refactoring before uploading to Google Code
# 1.03             Fixed a bug when using --xml and --parser
# 1.02             Added XML dictionary input
# 1.01             Initial release
#
### END changelog ###

import collections, getopt, gzip, imp, os, sqlite3, struct, subprocess, sys, zipfile, xml.sax.saxutils
#Python2#from dictEPUB import dictEPUB
#Python3#
from dictEPUB3 import dictEPUB3

### Path to working MARISA executables ###
#
# Please modify according to your OS and installation path.
# Remember that each of the following variables
# points directly to the respective executable,
# not to the directory containing it.
#
# Examples:
# MARISA_BUILD_PATH="/home/alberto/.bin/marisa-0.2.0/tools/marisa-build"
# MARISA_BUILD_PATH="C:\kobo\marisa\marisa-build.exe"
#
MARISA_BUILD_PATH="/home/alberto/.bin/marisa-0.2.0/tools/marisa-build"
MARISA_REVERSE_LOOKUP_PATH="/home/alberto/.bin/marisa-0.2.0/tools/marisa-reverse-lookup"
### Path to working MARISA executables ###


### BEGIN collate_function_default ###
# collate_function_default(string1, string2)
# define the string comparison function for the index file
def collate_function_default(string1, string2):
    b1 = bytearray(string1, 'utf-8').lower()
    b2 = bytearray(string2, 'utf-8').lower()
    if (b1 == b2):
        return 0
    else:
        return -1 if (b1 < b2) else 1
#
# OLD VERSION
#def collate_function(string1, string2):
#    if (string1.lower() == string2.lower()):
#        return 0
#    else:
#        return -1 if (string1.lower() < string2.lower()) else 1
#
### END collate_function_default ###


### BEGIN read_from_stardict_format ###
# read_from_stardict_format(idx_input_filename,
#   dict_input_filename, ignore_case)
# read data from the given stardict dictionary
# and return a list of [ [word, definition] ]
# if ignore_case = True, lowercase all the index word
def read_from_stardict_format(idx_input_filename, dict_input_filename, ignore_case):

    data = []

    # open files
    idx_input_file = open(idx_input_filename, "rb")
    dict_input_file = open(dict_input_filename, "rb")

    # read the whole dictionary in memory
    dict_input = dict_input_file.read()

    # read the index file byte-by-byte
    #Python2#    word = ""
    #Python3#
    word = b''
    byte = idx_input_file.read(1)
    while byte:
        #Python2#        if (byte == '\0'):
        #Python3#
        if (byte == b'\0'):    
            # end of current word: read offset and size
            o = idx_input_file.read(4)
            oi = int((struct.unpack('>i', o))[0])
            s = idx_input_file.read(4)
            si = int((struct.unpack('>i', s))[0])

            # if ignore_case = True, lowercase word
            #Python3#
            word = word.decode("utf-8")
            if ignore_case:
                word = word.lower()

            # extract the proper definition for word
            # and append it to current data
            #Python2#            data += [ [word, dict_input[oi:oi+si] ] ]
            #Python3#
            defs = dict_input[oi:oi+si].decode("utf-8")
            #Python3#
            data += [ [word, defs] ]

            # reset current word
            #Python2#            word = ""
            #Python3#
            word = b''
        else:
            # append current character to current word
            #Python2#            word += str(byte)
            #Python3#
            word += byte

        byte = idx_input_file.read(1)

    idx_input_file.close()
    dict_input_file.close()

    return data
### END read_from_stardict_format ###


### BEGIN read_from_xml_format ###
# read_from_xml_format(xml_input_filename, ignore_case)
# read data from the given XML dictionary
# and return a list of [ [word, definition] ]
# if ignore_case = True, lowercase all the index word
def read_from_xml_format(xml_input_filename, ignore_case):

    data = []

    # open file
    #Python2#    xml_input_file = open(xml_input_filename, "rb")
    #Python3#
    xml_input_file = open(xml_input_filename, "r")

    # read the whole dictionary in memory
    xml_input = xml_input_file.read()

    entry_pos = 0
    entry_pos = xml_input.find('<entry>', entry_pos)
    while entry_pos > -1:
        pos = xml_input.find('<key>', entry_pos)
        end_pos = xml_input.find('</key>', pos)
        key = xml_input[pos + len('<key>'): end_pos].strip()

        if ignore_case:
            key = key.lower()

        pos = xml_input.find('<def>', entry_pos)
        end_pos = xml_input.find('</def>', pos)
        definition = xml_input[pos + len('<def>'): end_pos].strip()

        data += [ [ xml.sax.saxutils.unescape(key), xml.sax.saxutils.unescape(definition) ] ]

        entry_pos = xml_input.find('<entry>', entry_pos + 1)

    xml_input_file.close()

    return data
### END read_from_xml_format ###


### BEGIN read_from_odyssey_format ###
# read_from_odyssey_format(idx_input_filename,
#   dict_input_filename, ignore_case)
# read data from the given odyssey dictionary
# and return a list of [ [word, definition] ]
# if ignore_case = True, lowercase all the index word
def read_from_odyssey_format(idx_input_filename, dict_input_filename, ignore_case):

    data = []

    # unzip dictionary
    extractedFiles = unzip(dict_input_filename)

    # open index
    sql_connection = sqlite3.connect(idx_input_filename)
    
    # get a cursor
    sql_cursor = sql_connection.cursor()
    # get the index data
    sql_cursor.execute('select * from T_DictIndex ')
    index_data = sql_cursor.fetchall()

    # dictionary from file to words
    words = collections.defaultdict(list)

    # process index
    for tuple in index_data:
        key = tuple[1]
        if ignore_case:
            key = key.lower()
        offset = tuple[2]
        length = tuple[3]
        cNumber = tuple[4]
        words[cNumber].append([key, offset, length])

    cNumberMax = len(words.keys())
    for i in range(1, cNumberMax+1):
        f = open("c_" + str(i), "rb")
        for tuple in words[i]:
            definition = ""
            key = tuple[0]
            offset = tuple[1]
            length = tuple[2]
            f.seek(offset)
            definition = f.read(length)
            #Python2#            data += [ [key, definition] ]
            #Python3#
            data += [ [key, definition.decode("utf-8")] ]
        f.close()

    sql_cursor.close()
    sql_connection.close()

    for e in extractedFiles:
        os.remove(e)

    return data
### END read_from_odyssey_format ###


### BEGIN unzip ###
# unzip(zip_filename)
# unzip the give zip_filename
# returning the list of extracted files
def unzip(zip_filename):
    extractedFiles = []
    zfile = zipfile.ZipFile(zip_filename)
    for name in zfile.namelist():
        (dirname, filename) = os.path.split(name)
        if (len(dirname) > 0 and not os.path.exists(dirname)):
            os.mkdir(dirname)
        fd = open(name,"wb")
        fd.write(zfile.read(name))
        fd.close()
        extractedFiles += [ name ]
    return extractedFiles
### END unzip ###


### BEGIN read_from_kobo_format ###
# read_from_kobo_format(kobo_input_filename, ignore_case)
# read data from the given Kobo dictionary
# and return a list of [ [word, definition] ]
# if ignore_case = True, lowercase all the index word
def read_from_kobo_format(kobo_input_filename, ignore_case):

    data = []
    
    # extract words file
    words_filename = "words"
    zfile = zipfile.ZipFile(kobo_input_filename)
    fd = open(words_filename,"wb")
    fd.write(zfile.read(words_filename))
    fd.close()
    
    # FIXME is there a better way to extract all the words from a MARISA trie?
    ids = ""
    for i in range(1000000):
        ids += str(i) + "\n"
    #Python3#
    ids = bytearray(ids, "utf-8")

    p = subprocess.Popen([MARISA_REVERSE_LOOKUP_PATH, words_filename], stdout=subprocess.PIPE, stdin=subprocess.PIPE, stderr=subprocess.PIPE)
    #Python2#    stdout = p.communicate(input=ids)[0]
    #Python3#
    stdout = p.communicate(input=ids)[0].decode("utf-8")    

    for s in stdout.splitlines():
        x = s.split("\t")
        if len(x) > 1:
            key = x[1]
            if ignore_case:
                key = key.lower()
            # just return the index, since content might be encrypted
            if (len(key) > 0):
                data += [ [key, ""] ]

    # unzip dictionary
    os.remove(words_filename)

    return data
### END read_from_kobo_format ###


### BEGIN read_from_csv_format ###
# read_from_csv_format(csv_input_filename, fs, ls, ignore_case)
# read data from the given CSV dictionary
# and return a list of [ [word, definition] ]
# if ignore_case = True, lowercase all the index word
def read_from_csv_format(csv_input_filename, fs, ls, ignore_case):

    data = []

    # open file
    #Python2#    csv_input_file = open(csv_input_filename, "rb")
    #Python3#
    csv_input_file = open(csv_input_filename, "r") 
    csv_input = csv_input_file.read()
    csv_input_file.close()

    # read the whole dictionary in memory
    for line in csv_input.split(ls):
        lvals = line.split(fs)

        # grab the first two fields, ignore subsequent ones (if any)
        if len(lvals) >= 2:
            key = lvals[0]
            definition = lvals[1]

            if ignore_case:
                key = key.lower()

            data += [ [ key, definition ] ]

    return data
### END read_from_csv_format ###


### BEGIN write_to_odyssey_format ###
# write_to_odyssey_format(config, data, collation_function, debug)
# write data to the Odyssey format, using the config settings
#
# config = [ dictionary_filename, index_filename, language_from, language_to,
#            license_string, copyright_string, title, description, year, info_filename ]
#
# data = [ word, include, synonyms, substitutions, definition ]
#
# where:
#        word is the sorting key
#        include is a boolean saying whether the word should be included
#        synonyms is a list of alternative strings for word
#        substitutions is a list of pairs [ word_to_replace, replacement ]
#        definition is the definition of word
def write_to_odyssey_format(config, data, collation, debug):

    # Note: chunks on Odyssey seems have size between
    # 262144 = 2^18 and 524288 = 2^19 bytes
    SPLIT_CHUNK_SIZE = 262144
    CHUNK_STRING = "c_"

    # read config parameters
    [ dictionary_filename,
      index_filename,
      language_from,
      language_to,
      license_string,
      copyright_string,
      title,
      description,
      year,
      info_filename ] = config

    # copy empty.idx into index_filename
    input_file = open('empty.idx', "rb")
    output_file = open(index_filename, "wb")
    output_file.write(input_file.read())
    input_file.close()
    output_file.close()

    # open index
    sql_connection = sqlite3.connect(index_filename)

    # install collation in the index
    if collation == None:
        print_info("Using built-in collation function...")
        sql_connection.create_collation("IcuNoCase", collate_function_default)
    else:
        print_info("Using custom collation function...")
        sql_connection.create_collation("IcuNoCase", collation.collate_function)
    sql_connection.text_factory = str

    # get a cursor
    sql_cursor = sql_connection.cursor()
    # delete any data from the index (just for safety...)
    sql_cursor.execute('delete from T_DictIndex ')

    # open debug file
    if debug:
        #Python2#        debug_file = open("debug." + dictionary_filename, "wb")
        #Python3#
        debug_file = open("debug." + dictionary_filename, "w", encoding="utf-8")
    
    # split data in chunks of size between MAX_CHUNK_SIZE and 2*MAX_CHUNK_SIZE bytes
    byte_count = 0
    current_chunk = 1
    current_chunk_filename = CHUNK_STRING + str(current_chunk)
    current_chunk_file = open(current_chunk_filename, "wb")
    chunk_filenames = [ current_chunk_filename ]

    # keep a dictionary of words, with their sql_tuples
    global_dictionary = collections.defaultdict(list)

    # keep a global list of substitutions
    global_substitutions = []

    # sort input data
    data.sort()

    for d in data:

        # get data
        word = d[0]
        include = d[1]
        synonyms = d[2]
        substitutions = d[3]
        if debug:
            # augment readability of c_* files
            definition = d[4] + "\n"
        else:
            # save 1 byte
            definition = d[4]
        #Python2#        definition_length = len(definition)
        #Python3#
        definition_length = len(bytearray(definition, "utf-8"))

        if (include):
            # write definition to debug file
            if debug:
                debug_file.write(definition)

            # write definition to current chunk file
            #Python2#            current_chunk_file.write(definition)
            #Python3#
            current_chunk_file.write(bytearray(definition, "utf-8")) 

            # insert word into index file
            sql_tuple = (0, word, byte_count, definition_length, current_chunk)
            sql_cursor.execute('insert into T_DictIndex values (?,?,?,?,?)', sql_tuple)

            # insert word into global dictionary
            global_dictionary[word].append(sql_tuple)

            # insert synonyms into index file, pointing at current definition
            for s in synonyms:
                sql_tuple = (0, s, byte_count, definition_length, current_chunk)
                sql_cursor.execute('insert into T_DictIndex values (?,?,?,?,?)', sql_tuple)

            # update byte count
            byte_count += definition_length

            # if the current chunk is complete, start new chunk Note: 262144 = 2^18
            if (byte_count > SPLIT_CHUNK_SIZE):
                current_chunk_file.close()
                current_chunk += 1
                current_chunk_filename = CHUNK_STRING + str(current_chunk)
                current_chunk_file = open(current_chunk_filename, "wb")
                chunk_filenames += [ current_chunk_filename ]
                byte_count = 0
        else:
            if len(substitutions) > 0 :
                global_substitutions += substitutions

    # close output files
    if debug:
        debug_file.close()
    current_chunk_file.close()

    # zip chunk files into dictionary_filename
    dictionary_zip_file = zipfile.ZipFile(dictionary_filename, "w", zipfile.ZIP_DEFLATED)
    for current_chunk_filename in chunk_filenames:
        dictionary_zip_file.write(current_chunk_filename)
    dictionary_zip_file.close()

    # delete chunk files unless debug mode is on
    if not debug:
        for current_chunk_filename in chunk_filenames:
            os.remove(current_chunk_filename)

    # process substitutions
    for substitution in global_substitutions:
        sub_from = substitution[0]
        sub_to = substitution[1]

        if sub_to in global_dictionary:
            # TODO Possible issue if global_dictionary[sub_to] is a list!
            # TODO If you define your own parser and you use substitutions, be aware of this!
            sql_tuple = global_dictionary[sub_to]
            sql_tuple = ( sql_tuple[0], sub_from, sql_tuple[2], sql_tuple[3], sql_tuple[4] )
            sql_cursor.execute('insert into T_DictIndex values (?,?,?,?,?)', sql_tuple)

    # update index metadata
    header = "<!DOCTYPE html PUBLIC \"-//W3C//DTD XHTML 1.0 Strict//EN\"  \"http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd\" [<!ENTITY ns \"&#8226;\">]><html xml:lang=\"%s\" xmlns=\"http://www.w3.org/1999/xhtml\"><head><title></title></head><body>" % (language_from)

    sql_cursor.execute('update T_DictInfo set F_xhtmlHeader=?', (header,))
    sql_cursor.execute('update T_DictInfo set F_LangFrom=?', (language_from,))
    sql_cursor.execute('update T_DictInfo set F_LangTo=?', (language_to,))
    sql_cursor.execute('update T_DictInfo set F_Licence=?', (license_string,))
    sql_cursor.execute('update T_DictInfo set F_Copyright=?', (copyright_string,))
    sql_cursor.execute('update T_DictInfo set F_Title=?', (title,))
    sql_cursor.execute('update T_DictInfo set F_Description=?', (description,))
    sql_cursor.execute('update T_DictInfo set F_Year=?', (year,))
    sql_cursor.execute('update T_DictInfo set F_Alphabet=?', ('Z',))
    sql_cursor.execute('update T_DictInfo set F_CollationLevel=?', ('1',))

    # these two fields might be unused
    sql_cursor.execute('update T_DictVersion set F_DictType=?', ('stardict',))
    sql_cursor.execute('update T_DictVersion set F_Version=?', ('11',))

    # compact and close index
    sql_cursor.execute('VACUUM')
    sql_cursor.close()
    sql_connection.close()
### END write_to_odyssey_format ###


### BEGIN write_to_stardict_format ###
# write_to_stardict_format(config, data, debug)
# write data to the StarDict format, using the config settings
#
# config = [ dictionary_filename, index_filename, language_from, language_to,
#            license_string, copyright_string, title, description, year, info_filename ]
#
# data = [ word, include, synonyms, substitutions, definition ]
#
# where:
#        word is the sorting key
#        include is a boolean saying whether the word should be included
#        synonyms is a list of alternative strings for word
#        substitutions is a list of pairs [ word_to_replace, replacement ]
#        definition is the definition of word
def write_to_stardict_format(config, data, debug):

    # read config parameters
    [ dictionary_filename,
      index_filename,
      language_from,
      language_to,
      license_string,
      copyright_string,
      title,
      description,
      year,
      info_filename ] = config


    # open debug file
    if debug:
        #Python2#        debug_file = open("debug." + dictionary_filename, "wb")
        #Python3#
        debug_file = open("debug." + dictionary_filename, "w", encoding="utf-8")

    # keep a dictionary of words, with their sql_tuples
    global_dictionary = collections.defaultdict(list)

    # keep a global list of substitutions
    global_substitutions = []

    # sort input data
    # data.sort()

    # open dictionary file
    dictionary_file = open(dictionary_filename, "wb")
    byte_count = 0

    for d in data:

        # get data
        word = d[0]
        include = d[1]
        synonyms = d[2]
        substitutions = d[3]
        if debug:
            # augment readability of c_* files
            definition = d[4] + "\n"
        else:
            # save 1 byte
            definition = d[4]
        #Python2#        definition_length = len(definition)
        #Python3#
        definition_bytes = bytearray(definition, "utf-8")
        #Python3#
        definition_length = len(definition_bytes)

        if (include):
            # write definition to debug file
            if debug:
                debug_file.write(definition)

            # write definition to current chunk file
            #Python2#            dictionary_file.write(definition)
            #Python3#
            dictionary_file.write(definition_bytes)

            # insert word into global dictionary
            sql_tuple = (word, byte_count, definition_length, 0)
            global_dictionary[word].append(sql_tuple)

            # insert synonyms into index file, pointing at current definition
            for s in synonyms:
                sql_tuple = (s, byte_count, definition_length, 0)
                global_dictionary[s].append(sql_tuple)
        else:
            if len(substitutions) > 0 :
                global_substitutions += substitutions

        byte_count += definition_length

    # close output files
    if debug:
        debug_file.close()
    dictionary_file.close()

    # process substitutions
    for substitution in global_substitutions:
        sub_from = substitution[0]
        sub_to = substitution[1]

        if sub_to in global_dictionary:
            # TODO Possible issue if global_dictionary[sub_to] is a list!
            # TODO If you define your own parser and you use substitutions, be aware of this!
            sql_tuple = global_dictionary[sub_to]
            sql_tuple = ( sub_from, sql_tuple[1], sql_tuple[2], sql_tuple[3] )
            global_dictionary[sub_from].append(sql_tuple)


    # sort keys (needed by StarDict format)
    #Python2#    keys = global_dictionary.keys()
    #Python3#
    keys = list(global_dictionary.keys())
    keys.sort()

    # write index file
    index_file = open(index_filename, "wb")
    for k in keys:
        if type(global_dictionary[k]) is tuple:
            # single keyword
            sql_tuple = global_dictionary[k]
            #Python2#            index_file.write(sql_tuple[0])
            #Python2#            index_file.write('\0')
            #Python3#
            index_file.write(bytearray(sql_tuple[0], "utf-8"))
            #Python3#
            index_file.write(b'\0')
            index_file.write(struct.pack('>i', sql_tuple[1]))
            index_file.write(struct.pack('>i', sql_tuple[2]))
        else:
            # multiple keyword
            for sql_tuple in global_dictionary[k]:
                #Python2#                index_file.write(sql_tuple[0])
                #Python2#                index_file.write('\0')
                #Python3#
                index_file.write(bytearray(sql_tuple[0], "utf-8"))
                #Python3#
                index_file.write(b'\0')
                index_file.write(struct.pack('>i', sql_tuple[1]))
                index_file.write(struct.pack('>i', sql_tuple[2]))
    index_file.close()


    # write info file
    #Python2#    info_file = open(info_filename, "wb")
    #Python3#
    info_file = open(info_filename, "w", encoding="utf-8")
    info_file.write("StarDict's dict ifo file\n")
    info_file.write("version=2.4.2\n")
    info_file.write("wordcount=" + str(len(keys)) + "\n")
    info_file.write("idxfilesize=" + str(os.path.getsize(index_filename)) + "\n")
    info_file.write("bookname=" + title + "\n")
    info_file.write("date=" + year + "\n")
    info_file.write("sametypesequence=m\n")
    info_file.write("description=" + description + "<br/>" + license_string + "<br/>" + copyright_string + "\n")
    # These fields are available and optional in .ifo StarDict files:
    # info_file.write("author=" + XXX + "\n")
    # info_file.write("email=" + XXX + "\n")
    # info_file.write("website=" + XXX + "\n")
    info_file.close()
### END write_to_stardict_format ###


### BEGIN write_to_xml_format ###
# write_to_xml_format(config, data, debug)
# write data to the XML format, using the config settings
#
# config = [ dictionary_filename, index_filename, language_from, language_to,
#            license_string, copyright_string, title, description, year, info_filename ]
#
# data = [ word, include, synonyms, substitutions, definition ]
#
# where:
#        word is the sorting key
#        include is a boolean saying whether the word should be included
#        synonyms is a list of alternative strings for word
#        substitutions is a list of pairs [ word_to_replace, replacement ]
#        definition is the definition of word
def write_to_xml_format(config, data, debug):
 
    # read config parameters
    [ dictionary_filename,
      index_filename,
      language_from,
      language_to,
      license_string,
      copyright_string,
      title,
      description,
      year,
      info_filename ] = config


    # open debug file
    if debug:
        debug_file = open("debug." + dictionary_filename, "wb")

    # keep a dictionary of words, with their sql_tuples
    global_dictionary = collections.defaultdict(list)

    # keep a global list of substitutions
    global_substitutions = []

    # sort input data
    # data.sort()

    # load dictionary
    byte_count = 0

    for d in data:

        # get data
        word = d[0]
        include = d[1]
        synonyms = d[2]
        substitutions = d[3]
        if debug:
            # augment readability of c_* files
            definition = d[4] + "\n"
        else:
            # save 1 byte
            definition = d[4]
        definition_length = len(definition)

        if (include):
            # append word into log file
            if debug:
                debug_file.write(word + "\n")

            # insert word into global dictionary
            sql_tuple = (word, byte_count, definition_length, 0, definition)
            global_dictionary[word].append(sql_tuple)

            # insert synonyms into index file, pointing at current definition
            for s in synonyms:
                sql_tuple = (s, byte_count, definition_length, 0, definition)
                global_dictionary[s].append(sql_tuple)
        else:
            if len(substitutions) > 0 :
                global_substitutions += substitutions

        byte_count += definition_length

    # close output files
    if debug:
        debug_file.close()

    # process substitutions
    for substitution in global_substitutions:
        sub_from = substitution[0]
        sub_to = substitution[1]

        if sub_to in global_dictionary:
            # TODO Possible issue if global_dictionary[sub_to] is a list!
            # TODO If you define your own parser and you use substitutions, be aware of this!
            sql_tuple = global_dictionary[sub_to]
            sql_tuple = ( sub_from, sql_tuple[1], sql_tuple[2], sql_tuple[3], sql_tuple[4] )
            global_dictionary[sub_from].append(sql_tuple)


    # sort keys (needed by StarDict format)
    #Python2#    keys = global_dictionary.keys()
    #Python3#
    keys = list(global_dictionary.keys())
    keys.sort()

    # output to XML format
    #Python2#    f = open(dictionary_filename, "wb")
    #Python3#
    f = open(dictionary_filename, "w", encoding="utf-8")
    f.write("<?xml version=\"1.0\" encoding=\"utf-8\"?>")
    f.write("<!DOCTYPE document SYSTEM \"dictionary.dtd\">")
    f.write("<dictionary>")
    for k in keys:
        word = xml.sax.saxutils.escape(k)
        if type(global_dictionary[k]) is tuple:
            # single keyword
            definition = xml.sax.saxutils.escape(global_dictionary[k][4])
            f.write("<entry><key>%s</key><def>%s</def></entry>" % (word, definition))
        else:
            # multiple keyword
            for sql_tuple in global_dictionary[k]:
                definition = xml.sax.saxutils.escape(sql_tuple[4])
                f.write("<entry><key>%s</key><def>%s</def></entry>" % (word, definition))
    f.write("</dictionary>")
    f.close()
### END write_to_xml_format ###


### BEGIN write_to_csv_format ###
# write_to_csv_format(config, data, fs, ls, debug)
# write data to the csv format, using the config settings
#
# config = [ dictionary_filename, index_filename, language_from, language_to,
#            license_string, copyright_string, title, description, year, info_filename ]
#
# data = [ word, include, synonyms, substitutions, definition ]
#
# where:
#        word is the sorting key
#        include is a boolean saying whether the word should be included
#        synonyms is a list of alternative strings for word
#        substitutions is a list of pairs [ word_to_replace, replacement ]
#        definition is the definition of word
def write_to_csv_format(config, data, fs, ls, debug):
 
    # read config parameters
    [ dictionary_filename,
      index_filename,
      language_from,
      language_to,
      license_string,
      copyright_string,
      title,
      description,
      year,
      info_filename ] = config


    # open debug file
    if debug:
        debug_file = open("debug." + dictionary_filename, "wb")

    # keep a dictionary of words, with their sql_tuples
    global_dictionary = collections.defaultdict(list)

    # keep a global list of substitutions
    global_substitutions = []

    # sort input data
    # data.sort()

    # load dictionary
    byte_count = 0

    for d in data:

        # get data
        word = d[0]
        include = d[1]
        synonyms = d[2]
        substitutions = d[3]
        if debug:
            # augment readability of c_* files
            definition = d[4] + "\n"
        else:
            # save 1 byte
            definition = d[4]
        definition_length = len(definition)

        if (include):
            # append word into log file
            if debug:
                debug_file.write(word + "\n")

            # insert word into global dictionary
            sql_tuple = (word, byte_count, definition_length, 0, definition)
            global_dictionary[word].append(sql_tuple)

            # insert synonyms into index file, pointing at current definition
            for s in synonyms:
                sql_tuple = (s, byte_count, definition_length, 0, definition)
                global_dictionary[s].append(sql_tuple)
        else:
            if len(substitutions) > 0 :
                global_substitutions += substitutions

        byte_count += definition_length

    # close output files
    if debug:
        debug_file.close()

    # process substitutions
    for substitution in global_substitutions:
        sub_from = substitution[0]
        sub_to = substitution[1]

        if sub_to in global_dictionary:
            # TODO Possible issue if global_dictionary[sub_to] is a list!
            # TODO If you define your own parser and you use substitutions, be aware of this!
            sql_tuple = global_dictionary[sub_to]
            sql_tuple = ( sub_from, sql_tuple[1], sql_tuple[2], sql_tuple[3], sql_tuple[4] )
            global_dictionary[sub_from].append(sql_tuple)

    # sort keys (needed by StarDict format)
    #Python2#    keys = global_dictionary.keys()
    #Python3#
    keys = list(global_dictionary.keys())
    keys.sort()

    # output to CSV format
    #Python2#    f = open(dictionary_filename, "wb")
    #Python3#
    f = open(dictionary_filename, "w", encoding="utf-8")
    for k in keys:
        word = k
        if type(global_dictionary[k]) is tuple:
            # single keyword
            definition = global_dictionary[k][4].replace(ls, " ")
            f.write("%s%s%s%s" % (word, fs, definition, ls))
        else:
            # multiple keyword
            for sql_tuple in global_dictionary[k]:
                definition = sql_tuple[4].replace(ls, " ")
                f.write("%s%s%s%s" % (word, fs, definition, ls))
    f.close()
### END write_to_csv_format ###


### BEGIN write_to_epub_format ###
# write_to_epub_format(config, data, debug)
# write data to the EPUB format, using the config settings
#
# config = [ dictionary_filename, index_filename, language_from, language_to,
#            license_string, copyright_string, title, description, year, info_filename ]
#
# data = [ word, include, synonyms, substitutions, definition ]
#
# where:
#        word is the sorting key
#        include is a boolean saying whether the word should be included
#        synonyms is a list of alternative strings for word
#        substitutions is a list of pairs [ word_to_replace, replacement ]
#        definition is the definition of word
def write_to_epub_format(config, data, debug):
 
    # read config parameters
    [ dictionary_filename,
      index_filename,
      language_from,
      language_to,
      license_string,
      copyright_string,
      title,
      description,
      year,
      info_filename ] = config


    # open debug file
    if debug:
        debug_file = open("debug." + dictionary_filename, "wb")

    # keep a dictionary of words, with their sql_tuples
    global_dictionary = collections.defaultdict(list)

    # keep a global list of substitutions
    global_substitutions = []

    # sort input data
    # data.sort()

    # load dictionary
    byte_count = 0

    for d in data:

        # get data
        word = d[0]
        include = d[1]
        synonyms = d[2]
        substitutions = d[3]
        if debug:
            # augment readability of c_* files
            definition = d[4] + "\n"
        else:
            # save 1 byte
            definition = d[4]
        definition_length = len(definition)

        if (include):
            # append word into log file
            if debug:
                debug_file.write(word + "\n")

            # insert word into global dictionary
            sql_tuple = (word, byte_count, definition_length, 0, definition)
            global_dictionary[word].append(sql_tuple)

            # insert synonyms into index file, pointing at current definition
            for s in synonyms:
                sql_tuple = (s, byte_count, definition_length, 0, definition)
                global_dictionary[s].append(sql_tuple)
        else:
            if len(substitutions) > 0 :
                global_substitutions += substitutions

        byte_count += definition_length

    # close output files
    if debug:
        debug_file.close()

    # process substitutions
    for substitution in global_substitutions:
        sub_from = substitution[0]
        sub_to = substitution[1]

        if sub_to in global_dictionary:
            # TODO Possible issue if global_dictionary[sub_to] is a list!
            # TODO If you define your own parser and you use substitutions, be aware of this!
            sql_tuple = global_dictionary[sub_to]
            sql_tuple = ( sub_from, sql_tuple[1], sql_tuple[2], sql_tuple[3], sql_tuple[4] )
            global_dictionary[sub_from].append(sql_tuple)


    # sort keys (needed by StarDict format)
    #Python2#    keys = global_dictionary.keys()
    #Python3#
    keys = list(global_dictionary.keys())
    keys.sort()

    clean_keys = []
    for k in keys:
        #Python2#        clean_keys += [ unicode(k) ]
        #Python3#
        clean_keys += [ k ]

    # output to EPUB
    #Python2#    d = dictEPUB()
    #Python3#
    d = dictEPUB3()
    d.createEPUBDictionary(clean_keys, language_from, dictionary_filename)
### END write_to_epub_format ###


### BEGIN write_to_kobo_format ###
# write_to_kobo_format(config, data, debug)
# write data to the Kobo format, using the config settings
#
# config = [ dictionary_filename, index_filename, language_from, language_to,
#            license_string, copyright_string, title, description, year, info_filename ]
#
# data = [ word, include, synonyms, substitutions, definition ]
#
# where:
#        word is the sorting key
#        include is a boolean saying whether the word should be included
#        synonyms is a list of alternative strings for word
#        substitutions is a list of pairs [ word_to_replace, replacement ]
#        definition is the definition of word
def write_to_kobo_format(config, data, debug):

    # read config parameters
    [ dictionary_filename,
      index_filename,
      language_from,
      language_to,
      license_string,
      copyright_string,
      title,
      description,
      year,
      info_filename ] = config


    # open debug file
    if debug:
        #Python2#        debug_file = open("debug." + dictionary_filename, "wb")
        #Python3#
        debug_file = open("debug." + dictionary_filename, "w", encoding="utf-8")

    # keep a dictionary of words, with their sql_tuples
    global_dictionary = collections.defaultdict(list)

    # keep a global list of substitutions
    global_substitutions = []

    # sort input data
    # data.sort()

    # load dictionary
    byte_count = 0

    for d in data:

        # get data
        word = d[0]
        include = d[1]
        synonyms = d[2]
        substitutions = d[3]
        if debug:
            # augment readability of c_* files
            definition = d[4] + "\n"
        else:
            # save 1 byte
            definition = d[4]
        definition_length = len(definition)

        if (include):
            # append word into log file
            if debug:
                debug_file.write(word + "\n")

            # insert word into global dictionary
            sql_tuple = (word, byte_count, definition_length, 0, definition)
            global_dictionary[word].append(sql_tuple)

            # insert synonyms into index file, pointing at current definition
            for s in synonyms:
                sql_tuple = (s, byte_count, definition_length, 0, definition)
                global_dictionary[s].append(sql_tuple)
        else:
            if len(substitutions) > 0 :
                global_substitutions += substitutions

        byte_count += definition_length

    # close output files
    if debug:
        debug_file.close()

    # process substitutions
    for substitution in global_substitutions:
        sub_from = substitution[0]
        sub_to = substitution[1]

        if sub_to in global_dictionary:
            # TODO Possible issue if global_dictionary[sub_to] is a list!
            # TODO If you define your own parser and you use substitutions, be aware of this!
            sql_tuple = global_dictionary[sub_to]
            sql_tuple = ( sub_from, sql_tuple[1], sql_tuple[2], sql_tuple[3], sql_tuple[4] )
            global_dictionary[sub_from].append(sql_tuple)


    # sort keys (needed by StarDict format)
    #Python2#    keys = global_dictionary.keys()
    #Python3#
    keys = list(global_dictionary.keys())
    keys.sort()

    # store file names of the HTML files
    # to be included in the ZIP file
    fileNames = []
    fileIDs = []

    # compute dictionary with (XX, key) entries
    fileToKey = dict()
    for k in keys:
        pref = compute_prefix(k)
        if pref in fileToKey:
            fileToKey[pref] += [ k ]
        else:
            fileToKey[pref] = [ k ] 
        if pref not in fileIDs:
            fileIDs += [ pref ]
            fileNames += [ pref + ".html" ]
    
    # output definitions
    for p in fileIDs:
        #Python2#        f = open(p + ".html", "wb")
        #Python3#
        f = open(p + ".html", "w", encoding="utf-8")
        f.write("<?xml version=\"1.0\" encoding=\"utf-8\"?><html>")
        for k in fileToKey[p]:
            word = k
            if type(global_dictionary[k]) is tuple:
                # single keyword
                definition = global_dictionary[k][4]
                f.write("<w><a name=\"%s\"/><div><b>%s</b><br/>%s</div></w>" % (word, word, definition))
            else:
                # multiple keyword
                for sql_tuple in global_dictionary[k]:
                    definition = sql_tuple[4]
                    f.write("<w><a name=\"%s\"/><div><b>%s</b><br/>%s</div></w>" % (word, word, definition))
        f.write("</html>")
        f.close()

        # compress with gzip
        f = open(p + ".html", "rb")
        f_out = gzip.open(p + ".html.gz", "wb")
        f_out.writelines(f)
        f_out.close()
        f.close()

        # remove .gz
        os.unlink(p + ".html")
        os.rename(p + ".html.gz", p + ".html")
    
    # accumulate index file
    #Python2#    index_file = ""
    #Python3#
    index_file = b''
    for k in keys:
        #Python2#        index_file += (k + "\n")
        #Python3#
        index_file += bytearray(k + "\n", "utf-8")

    # compress index with MARISA
    print_info("Creating compressed index file " + index_filename + "...") 
    p = subprocess.Popen([MARISA_BUILD_PATH, "-l", "-o", index_filename], stdout=subprocess.PIPE, stdin=subprocess.PIPE, stderr=subprocess.PIPE)
    p.communicate(input=index_file)
    fileNames += [ index_filename ]

    # create ZIP file
    zip_filename = dictionary_filename + ".zip"
    print_info("Creating zip file " + zip_filename + "...")
    zip_file = zipfile.ZipFile(zip_filename, "w", zipfile.ZIP_DEFLATED)
    for fileName in fileNames:
        zip_file.write(fileName)
    zip_file.close()
    print_info("File " + zip_filename + " created successfully!")

    # clean up
    if not debug:
        for fileName in fileNames:
            os.remove(fileName)
### END write_to_kobo_format ###


### BEGIN compute_prefix ###
# compute_prefix(keyword)
# compute the correct Kobo file name where keyword should be stored
#
def compute_prefix(keyword):
    pref = "11"
    #Python2#    keyword = keyword.decode('utf-8').lower()
    #Python3#
    keyword = keyword.lower()

    if len(keyword) == 0:
        return str(pref)

    if len(keyword) == 1:
        keyword += "a"
    
    # here keyword has length at least 2
    if is_char_allowed(keyword[0]) and is_char_allowed(keyword[1]):
        pref = keyword[0:2]

    return str(pref)
### END compute_prefix ###


### BEGIN is_char_allowed ###
# is_char_allowed(ch)
# returns true if ch is allowed in Kobo format, false otherwise
def is_char_allowed(ch):
    # all non-ascii are ok
    if ord(ch) > 127:
        return True

    # all ASCII letters are ok
    if ord(ch) >= 97 and ord(ch) <= 122:
        return True
    
    # everything else is not ok 
    return False
### END is_char_allowed ###


### BEGIN compress_install_file ###
# compress_install_file(dictionary_filename, index_filename, zip_filename)
# compress dictionary_filename and index_filename into zip_filename
#
def compress_install_file(dictionary_filename, index_filename, zip_filename):

    print_info("Creating zip file " + zip_filename + "...")
    zip_file = zipfile.ZipFile(zip_filename, "w", zipfile.ZIP_DEFLATED)
    zip_file.write(dictionary_filename)
    zip_file.write(index_filename)
    zip_file.close()
    print_info("File " + zip_filename + " created successfully!")
### END compress_StarDict_dictionary ###


### BEGIN compress_StarDict_dictionary ###
# compress_StarDict_dictionary(dictionary_filename, compressed_dictionary_filename, delete_uncompressed)
# compress dictionary_filename into compressed_dictionary_filename
# if delete_uncompressed is True, delete dictionary_filename
#
# Note: if dictzip is not found, simply keep the dictionary uncompressed
#
def compress_StarDict_dictionary(dictionary_filename, compressed_dictionary_filename, delete_uncompressed):

    # FIXME compressing with gzip library seems not working, I need to call dictzip

    # compress the dictionary file with dictzip
    print_info("Creating compressed dictionary file " + compressed_dictionary_filename + "...") 
    return_code = subprocess.call(["dictzip", "-k", dictionary_filename])

    # check whether the compression was successful
    if return_code == 0:
        print_info("File " + compressed_dictionary_filename + " created successfully!")

        # delete the uncompressed dictionary
        if delete_uncompressed:
            os.remove(dictionary_filename)
    else:
        print_info("File " + compressed_dictionary_filename + " cannot be created. Check that dictzip is installed in your system.")

    return return_code
### END compress_StarDict_dictionary ###


### BEGIN read_command_line_parameters ###
# read_command_line_parameters()
# read the command line parameters, and return the following list:
# config = [ prefix_list, language_from, language_to,
#            license, copyright, title, description, year
#            debug, ignore_case, parser_filename, create_zip, input_format ]
# -p : prefix list
# -f : language from
# -t : language to
# -d : debug mode
# -h : print usage and exit
# -i : ignore word case
# -z : create *.install zip file
# --license : license
# --copyright : copyright
# --title : title
# --description : description
# --year : year
# --parser : parser to be used while parsing input dictionary
# --sd : input format is StarDict (default)
# --xml : input format is XML
# --csv : input format is CSV
# --odyssey : input format is Bookeen Cybook Odyssey
# --kobo : input format is Kobo
# --output-odyssey : output format is Bookeen Cybook Odyssey (default)
# --output-sd : output format is StarDict
# --output-xml : output format is XML
# --output-kobo : output format is Kobo
# --output-csv : output format is CSV
# --output-epub : output format is epub
# --collation : collation function to be used while outputting to Bookeen Cybook Odyssey format
def read_command_line_parameters(argv):

    try:
        optlist, free = getopt.getopt(argv[1:], 'dhizf:p:t:',
            ['license=', 'copyright=', 'title=',
                'description=', 'year=', 'parser=',
                'fs=', 'ls=',
                'sd', 'odyssey', 'xml', 'kobo', 'csv',
                'output-odyssey', 'output-sd', 'output-xml', 'output-kobo', 'output-csv',
                'output-epub',
                'collation='])
    #Python2#    except getopt.GetoptError, err:
    #Python3#
    except getopt.GetoptError as err:
        print_error(str(err))
        usage()
        sys.exit(1)

    optdict = dict(optlist)

    if '-h' in optdict:
        usage()
        sys.exit(0)

    prefix_list = []
    if '-p' in optdict:
        for s in optdict['-p'].split(","):
            prefix_list.append(s.strip())
    else:
        print_error('No prefix parameter was supplied.')

    input_format = 'sd'
    if '--sd' in optdict:
        input_format = 'sd'
    if '--odyssey' in optdict:
        input_format = 'odyssey'
    if '--xml' in optdict:
        input_format = 'xml'
    if '--kobo' in optdict:
        input_format = 'kobo'
    if '--csv' in optdict:
        input_format = 'csv'

    output_format = 'odyssey'
    if '--output-odyssey' in optdict:
        output_format = 'odyssey'
    if '--output-sd' in optdict:
        output_format = 'sd'
    if '--output-xml' in optdict:
        output_format = 'xml'
    if '--output-kobo' in optdict:
        output_format = 'kobo'
    if '--output-csv' in optdict:
        output_format = 'csv'
    if '--output-epub' in optdict:
        output_format = 'epub'

    language_from = ''
    if '-f' in optdict:
        language_from = optdict['-f']
    else:
        if output_format == 'odyssey' or output_format == 'kobo' or output_format == 'epub':
            print_error('No language_from parameter was supplied.')

    language_to = ''
    if '-t' in optdict:
        language_to = optdict['-t']
    else:
        if output_format == 'odyssey' or output_format == 'kobo':
            print_error('No language_to parameter was supplied.')

    if '--license' in optdict:
        license_string = optdict['--license']
    else:
        license_string = 'GNU GPL 3'

    if '--copyright' in optdict:
        copyright_string = optdict['--copyright']
    else:
        copyright_string = 'GNU GPL 3'

    if '--title' in optdict:
        title = optdict['--title']
    else:
        title = 'Dictionary ' + language_from + ' -> ' + language_to 

    if '--description' in optdict:
        description = optdict['--description']
    else:
        description = title

    if '--year' in optdict:
        year = optdict['--year']
    else:
        year = '2012'

    if '--parser' in optdict:
        parser_filename = optdict['--parser']
    else:
        parser_filename = None

    if '--fs' in optdict:
        fs = escape_ascii(optdict['--fs'])
    else:
        fs = "\t"

    if '--ls' in optdict:
        ls = escape_ascii(optdict['--ls'])
    else:
        ls = "\n"
    
    debug = False
    if '-d' in optdict:
        debug = True

    ignore_case = False
    if '-i' in optdict:
        ignore_case = True

    create_zip = False
    if '-z' in optdict:
        create_zip = True

    if '--collation' in optdict:
        collation_filename = optdict['--collation']
    else:
        collation_filename = None

    return [ prefix_list, language_from, language_to,
             license_string, copyright_string, title, description, year,
             debug, ignore_case, parser_filename, create_zip,
             input_format, output_format, fs, ls, collation_filename ]
### END read_command_line_parameters ###


### BEGIN escape_ascii ###
# escape_ascii(s)
# escape ASCII sequences
def escape_ascii(s):
    s = s.replace("\\0", "\0")
    s = s.replace("\\a", "\a")
    s = s.replace("\\b", "\b")
    s = s.replace("\\t", "\t")
    s = s.replace("\\n", "\n")
    s = s.replace("\\v", "\v")
    s = s.replace("\\f", "\f")
    s = s.replace("\\r", "\r")
    return s
### END escape_ascii ###


### BEGIN print_config ###
# print_config(config)
# print the configuration that will be used in the dictionary conversion
#
# config = [ dictionary_filename, index_filename, language_from, language_to,
#            license, copyright, title, description, year ]
def print_config(config):
    print_info("Dictionary file: " + config[0])
    print_info("Index file:      " + config[1])
    print_info("Language from:   " + config[2])
    print_info("Language to:     " + config[3])
    print_info("License:         " + config[4])
    print_info("Copyright:       " + config[5])
    print_info("Title:           " + config[6])
    print_info("Description:     " + config[7])
    print_info("Year:            " + config[8])
### END print_config ###


### BEGIN check_ifo_file ###
# check_ifo_file(ifo_filename)
# checks that ifo_filename exists and has the right format
def check_ifo_file(ifo_filename):
    if not os.path.isfile(ifo_filename):
        return False, None

    type_sequence = ''
    #Python2#    ifo_file = open(ifo_filename, "rb")
    #Python3#
    ifo_file = open(ifo_filename, "r")
    for line in ifo_file:
        if line.strip().find('sametypesequence') > -1:
            type_sequence = line.strip().split('=')[1]
    ifo_file.close()

    if type_sequence in ['m', 'l', 'g', 'x', 'y', 'k', 'w', 'h']:
        return True, type_sequence
    else:
        return False, type_sequence
### END check_ifo_file ###


### BEGIN check_idx_file ###
# check_idx_file(idx_filename)
# checks that idx_filename exists, uncompressing it if it was compressed
def check_idx_file(idx_filename):
    uncompressed = idx_filename
    compressed = idx_filename + ".gz"

    if os.path.isfile(uncompressed):
        return True

    if os.path.isfile(compressed):
        #Python2#        uncompressed_idx_file = open(uncompressed, "wb")
        #Python2#        compressed_idx_file = gzip.open(compressed, "rb")
        #Python3#
        uncompressed_idx_file = open(uncompressed, "w", encoding="utf-8")
        #Python3#
        compressed_idx_file = gzip.open(compressed, "r")
        uncompressed_idx_file.write(compressed_idx_file.read())
        compressed_idx_file.close()
        uncompressed_idx_file.close()
        return True

    return False
### END check_idx_file ###


### BEGIN check_dict_file ###
# check_dict_file(dict_filename)
# checks that dict_filename exists, uncompressing it if it was compressed
def check_dict_file(dict_filename):
    uncompressed = dict_filename
    compressed = dict_filename + ".dz"

    if os.path.isfile(uncompressed):
        return True

    if os.path.isfile(compressed):
        uncompressed_idx_file = open(uncompressed, "wb")
        compressed_idx_file = gzip.open(compressed, "rb")
        uncompressed_idx_file.write(compressed_idx_file.read())
        compressed_idx_file.close()
        uncompressed_idx_file.close()
        return True

    return False
### END check_dict_file ###


### BEGIN check_xml_file ###
# check_xml_file(xml_filename)
# checks that xml_filename exists
def check_xml_file(xml_filename):
    return os.path.isfile(xml_filename)
### END check_xml_file ###


### BEGIN check_kobo_file ###
# check_kobo_file(kobo_filename)
# checks that kobo_filename exists
def check_kobo_file(kobo_filename):
    return os.path.isfile(kobo_filename)
### END check_kobo_file ###


### BEGIN check_csv_file ###
# check_csv_file(csv_filename)
# checks that csv_filename exists
def check_csv_file(csv_filename):
    return os.path.isfile(csv_filename)
### END check_csv_file ###


### BEGIN check_parser ###
# check_parser(parser_filename)
# checks that parser_filename exists and can be loaded
def check_parser(parser_filename):
    if parser_filename == None:
        return None

    if not os.path.isfile(parser_filename):
        return None
    try:
        parser = imp.load_source('', parser_filename)
        parser.parse([], 'x', False)
    except Exception:
        return None

    return parser
### END check_parser ###


### BEGIN check_collation ###
# check_collation(collation_filename)
# checks that collation_filename exists and can be loaded
def check_collation(collation_filename):
    if collation_filename == None:
        return None

    if not os.path.isfile(collation_filename):
        return None
    try:
        collation = imp.load_source('', collation_filename)
        collation.collate_function('', '')
    except Exception:
        return None

    return collation
### END check_collation ###


### BEGIN check_existence ###
# check_existence(filename)
# checks whether filename exists
def check_existence(filename):
    if filename == None:
        return False

    return os.path.isfile(filename)
### END check_existence ###


### BEGIN print_error ###
# print_error(error, displayusage=True)
# print the given error, call usage, and exit
# optional displayusage to skip usage
def print_error(error, displayusage = True):
    sys.stderr.write("[ERROR] " + error + " Aborting.\n")
    if displayusage :
        usage()
    sys.exit(1)
### END print_error ###


### BEGIN print_info ###
# print_info(info)
# print the given info string
def print_info(info):
    print("[INFO] " + info)
### END print_info ###


### BEGIN print_ ###
# print_(info)
# print the given string
def print_(info):
    print(info)
### END print_ ###


### BEGIN usage ###
# usage()
# print script usage
def usage():
    #Python2#    e = "python"
    #Python2#    s = "penelope.py"
    #Python3#
    e = "python3"
    #Python3#
    s = "penelope3.py"
    print_("")
    print_("$ %s %s -p <prefix list> -f <language_from> -t <language_to> [OPTIONS]" % (e, s))
    print_("")
    print_("Required arguments:")
    print_(" -p <prefix list>       : list of the dictionaries to be merged/converted (without extension, comma separated)")
    print_(" -f <language_from>     : ISO 631-2 code language_from of the dictionary to be converted")
    print_(" -t <language_to>       : ISO 631-2 code language_to of the dictionary to be converted")
    print_("")
    print_("Optional arguments:")
    print_(" -d                     : enable debug mode and do not delete temporary files")
    print_(" -h                     : print this usage message and exit")
    print_(" -i                     : ignore word case while building the dictionary index")
    print_(" -z                     : create the .install zip file containing the dictionary and the index")
    print_(" --sd                   : input dictionary in StarDict format (default)")
    print_(" --odyssey              : input dictionary in Bookeen Cybook Odyssey format")
    print_(" --xml                  : input dictionary in XML format")
    print_(" --kobo                 : input dictionary in Kobo format (reads the index only!)")
    print_(" --csv                  : input dictionary in CSV format")
    print_(" --output-odyssey       : output dictionary in Bookeen Cybook Odyssey format (default)")
    print_(" --output-sd            : output dictionary in StarDict format")
    print_(" --output-xml           : output dictionary in XML format")
    print_(" --output-kobo          : output dictionary in Kobo format")
    print_(" --output-csv           : output dictionary in CSV format")
    print_(" --output-epub          : output EPUB file containing the index of the input dictionary")
    print_(" --title <string>       : set the title string shown on the Odyssey screen to <string>")
    print_(" --license <string>     : set the license string to <string>")
    print_(" --copyright <string>   : set the copyright string to <string>")
    print_(" --description <string> : set the description string to <string>")
    print_(" --year <string>        : set the year string to <string>")
    print_(" --parser <parser.py>   : use <parser.py> to parse the input dictionary")
    print_(" --collation <coll.py>  : use <coll.py> as collation function when outputting in Bookeen Cybook Odyssey format")
    print_(" --fs <string>          : use <string> as CSV field separator, escaping ASCII sequences (default: \\t)")
    print_(" --ls <string>          : use <string> as CSV line separator, escaping ASCII sequences (default: \\n)")
    print_("")
    print_("Examples:")
    print_("$ %s %s -h" % (e, s))
    print_("$ %s %s           -p foo -f en -t en" % (e, s))
    print_("$ %s %s           -p bar -f en -t it" % (e, s))
    print_("$ %s %s           -p \"bar,foo,zam\" -f en -t it" % (e, s))
    print_("$ %s %s --xml     -p foo -f en -t en" % (e, s))
    print_("$ %s %s --xml     -p foo -f en -t en --output-sd" % (e, s))
    print_("$ %s %s           -p bar -f en -t it --output-kobo" % (e, s))
    print_("$ %s %s           -p bar -f en -t it --output-xml -i" % (e, s))
    print_("$ %s %s --kobo    -p bar -f it -t it --output-epub" % (e, s))
    print_("$ %s %s --odyssey -p bar -f en -t en --output-epub" % (e, s))
    print_("$ %s %s           -p bar -f en -t it --title \"My EN->IT dictionary\" --year 2012 --license \"CC-BY-NC-SA 3.0\"" % (e, s))
    print_("$ %s %s           -p foo -f en -t en --parser foo_parser.py --title \"Custom EN dictionary\"" % (e, s))
    print_("$ %s %s           -p foo -f en -t en --collation custom_collation.py" % (e, s))
    print_("$ %s %s --xml     -p foo -f en -t en --output-csv --fs \"\\t\\t\" --ls \"\\n\" " % (e, s))
    print_("")
### END usage ###


### BEGIN main ###
def main():
    # read command line parameters
    [ prefix_list,
      language_from,
      language_to,
      license_string,
      copyright_string,
      title,
      description,
      year,
      debug,
      ignore_case,
      parser_filename,
      create_zip,
      input_format,
      output_format,
      fs,
      ls,
      collation_filename ] = read_command_line_parameters(sys.argv)

    type_sequence = 'unknown'

    # set input filenames
    if input_format == 'sd':
        ifo_input_filename_list = []
        idx_input_filename_list = []
        dict_input_filename_list = []
        for prefix in prefix_list:
            # check ifo input file
            ifo_input_filename = prefix + ".ifo"
            readable, type_sequence = check_ifo_file(ifo_input_filename)
            if not readable:
                print_error("File " + ifo_input_filename + " not found or with wrong format.")
            print_info("Input dictionary has sequence type '" + type_sequence + "'.")
            ifo_input_filename_list.append(ifo_input_filename)

            # check idx input file, uncompressing it if it was compressed
            idx_input_filename = prefix + ".idx"
            readable = check_idx_file(idx_input_filename)
            if not readable:
                print_error("File " + idx_input_filename + " not found (even compressed).")
            idx_input_filename_list.append(idx_input_filename)

            # check dict input file, uncompressing it if it was compressed
            dict_input_filename = prefix + ".dict"
            readable = check_dict_file(dict_input_filename)
            if not readable:
                print_error("File " + dict_input_filename + " not found (even compressed).")
            dict_input_filename_list.append(dict_input_filename)

    if input_format == 'xml':
        xml_input_filename_list = []
        for prefix in prefix_list:
            # check xml input file
            xml_input_filename = prefix + ".xml"
            readable = check_xml_file(xml_input_filename)
            if not readable:
                print_error("File " + xml_input_filename + " not found.")
            xml_input_filename_list.append(xml_input_filename)

    if input_format == 'odyssey':
        idx_input_filename_list = []
        dict_input_filename_list = []
        for prefix in prefix_list:
            # check idx input file, uncompressing it if it was compressed
            idx_input_filename = prefix + ".dict.idx"
            readable = check_idx_file(idx_input_filename)
            if not readable:
                print_error("File " + idx_input_filename + " not found (even compressed).")
            idx_input_filename_list.append(idx_input_filename)

            # check dict input file, uncompressing it if it was compressed
            dict_input_filename = prefix + ".dict"
            readable = check_dict_file(dict_input_filename)
            if not readable:
                print_error("File " + dict_input_filename + " not found (even compressed).")
            dict_input_filename_list.append(dict_input_filename)

    if input_format == 'kobo':
        kobo_input_filename_list = []
        for prefix in prefix_list:
            # check kobo input file
            kobo_input_filename = prefix + ".zip"
            readable = check_kobo_file(kobo_input_filename)
            if not readable:
                print_error("File " + kobo_input_filename + " not found.")
            kobo_input_filename_list.append(kobo_input_filename)

    if input_format == 'csv':
        if len(fs) < 1:
            print_error("CSV field separator must have length at least one.")
        if len(ls) < 1:
            print_error("CSV line separator must have length at least one.")
        
        csv_input_filename_list = []
        for prefix in prefix_list:
            # check csv input file
            csv_input_filename = prefix + ".csv"
            readable = check_csv_file(csv_input_filename)
            if not readable:
                print_error("File " + csv_input_filename + " not found.")
            csv_input_filename_list.append(csv_input_filename)

    # check parser input file, if one was given
    parser = check_parser(parser_filename)
    if parser_filename != None and parser == None:
        print_error("Parser " + parser_filename + " not found or with no parse(data, type_sequence, ignore_case) function.")

    # check collation input file, if one was given
    collation = check_collation(collation_filename)
    if collation_filename != None and collation == None:
        print_error("Collation " + collation_filename + " not found or with no collate_function(string1, string2) function.")

    # set output filenames
    if output_format == 'odyssey':
        if language_from == language_to:
            dictionary_filename = language_from + "." + prefix_list[0] + ".dict"
        else:
            dictionary_filename = language_from + "-" + language_to + ".dict"
        index_filename =  dictionary_filename + ".idx"
        info_filename = ''

        existing = False
        existing = existing or check_existence(dictionary_filename)
        existing = existing or check_existence(index_filename)
        if existing:
            dictionary_filename = "new." + dictionary_filename
            index_filename = "new." + index_filename

    if output_format == 'sd':
        dictionary_filename = prefix_list[0] + ".dict"
        index_filename = prefix_list[0] + ".idx"
        info_filename = prefix_list[0] + ".ifo"
        compressed_dictionary_filename = dictionary_filename + ".dz"

        existing = False
        existing = existing or check_existence(dictionary_filename)
        existing = existing or check_existence(index_filename)
        existing = existing or check_existence(info_filename)
        existing = existing or check_existence(compressed_dictionary_filename)
        if existing:
            dictionary_filename = "new." + dictionary_filename
            index_filename = "new." + index_filename
            info_filename = "new." + info_filename
            compressed_dictionary_filename = dictionary_filename + ".dz"

    if output_format == 'xml':
        dictionary_filename = prefix_list[0] + ".xml"
        index_filename = ''
        info_filename = ''

        existing = False
        existing = existing or check_existence(dictionary_filename)
        if existing:
            dictionary_filename = "new." + dictionary_filename

    if output_format == 'kobo':
        if language_from == language_to:
            if language_from == "en":
                # en-en dictionary is simply "dicthtml.zip"
                dictionary_filename = "dicthtml"
            else:
                # it-it dictionary is "dicthtml-it.zip"
                dictionary_filename = "dicthtml-" + language_from
        else:
            # en-it dictionary is "dicthtml-en-it.zip"
            dictionary_filename = "dicthtml-" + language_from + "-" + language_to
        compressed_dictionary_filename = dictionary_filename + ".zip"
        index_filename = "words"
        info_filename = ''

        existing = False
        existing = existing or check_existence(dictionary_filename)
        existing = existing or check_existence(compressed_dictionary_filename)
        if existing:
            dictionary_filename = "new." + dictionary_filename
            compressed_dictionary_filename = "new." + compressed_dictionary_filename
    
    if output_format == 'csv':
        if len(fs) < 1:
            print_error("CSV field separator must have length at least one!")
        if len(ls) < 1:
            print_error("CSV line separator must have length at least one.")

        dictionary_filename = prefix_list[0] + ".csv"
        index_filename = ''
        info_filename = ''

        existing = False
        existing = existing or check_existence(dictionary_filename)
        if existing:
            dictionary_filename = "new." + dictionary_filename

    if output_format == 'epub':
        dictionary_filename = prefix_list[0] + ".epub"
        index_filename = ''
        info_filename = ''

        existing = False
        existing = existing or check_existence(dictionary_filename)
        if existing:
            dictionary_filename  = "new." + dictionary_filename

    # set the config list
    config = [ dictionary_filename,
               index_filename,
               language_from,
               language_to,
               license_string,
               copyright_string,
               title,
               description,
               year,
               info_filename ]


    # let the user know whether debug mode is on
    if debug:
        print_info('Debug mode is on.')


    # let the user know whether ignore_case mode is on
    if ignore_case:
        print_info('Ignoring word case while building the index.')


    # let the user know what is going on
    print_info('Starting conversion with the following parameters:')
    print_("")
    print_config(config)
    print_("")


    # read input files
    print_info('Reading input dictionaries...')
    # data = [ [word, definition] ]
    data = []
    if input_format == 'sd':
        for i in range(len(prefix_list)):
            idx_input_filename = idx_input_filename_list[i]
            dict_input_filename = dict_input_filename_list[i]
            data += read_from_stardict_format(idx_input_filename, dict_input_filename, ignore_case)

    if input_format == 'xml':
        for i in range(len(prefix_list)):
            xml_input_filename = xml_input_filename_list[i]
            data += read_from_xml_format(xml_input_filename, ignore_case)

    if input_format == 'odyssey':
        for i in range(len(prefix_list)):
            idx_input_filename = idx_input_filename_list[i]
            dict_input_filename = dict_input_filename_list[i]
            data += read_from_odyssey_format(idx_input_filename, dict_input_filename, ignore_case)

    if input_format == 'kobo':
        for i in range(len(prefix_list)):
            kobo_input_filename = kobo_input_filename_list[i]
            data += read_from_kobo_format(kobo_input_filename, ignore_case)
    
    if input_format == 'csv':
        for i in range(len(prefix_list)):
            csv_input_filename = csv_input_filename_list[i]
            data += read_from_csv_format(csv_input_filename, fs, ls, ignore_case)


    # parse input files
    print_info('Parsing the input data...')
    parsed_data = []
    if parser == None:
        print_info('Using the built-in parser...')
        for d in data:
            parsed_data += [ [ d[0], True, [], [], d[1] ] ]
    else:
        print_info("Using the custom parser defined in " + parser_filename + " ...")
        parsed_data = parser.parse(data, type_sequence, ignore_case)


    # write out to Odyssey format
    if output_format == 'odyssey':
        print_info('Outputting in Odyssey format to file...')
        write_to_odyssey_format(config, parsed_data, collation, debug)
        print_info("Files " + dictionary_filename + " and " + index_filename + " created successfully!")

        # create zip .install file, if the user asked for it
        if create_zip:
            zip_filename = dictionary_filename + ".install"
            compress_install_file(dictionary_filename, index_filename, zip_filename)

    # write out to StarDict format
    if output_format == 'sd':
        print_info('Outputting in StarDict format to file...')
        write_to_stardict_format(config, parsed_data, debug)
        delete_uncompressed = not debug
        return_code = compress_StarDict_dictionary(dictionary_filename, compressed_dictionary_filename, delete_uncompressed)

        if return_code == 0:
            print_info("Files " + compressed_dictionary_filename + ", " + index_filename + ", and " + info_filename + " created successfully!")
        else:
            print_info("Files " + dictionary_filename + ", " + index_filename + ", and " + info_filename + " created successfully!")

    # write out to XML format
    if output_format == 'xml':
        print_info('Outputting in XML format to file...')
        write_to_xml_format(config, parsed_data, debug)
        print_info("File " + dictionary_filename + " created successfully!")

    # write out to Kobo format
    if output_format == 'kobo':
        print_info('Outputting in Kobo format to file...')
        write_to_kobo_format(config, parsed_data, debug)
        print_info("File " + compressed_dictionary_filename + " created successfully!")
    
    # write out to CSV format
    if output_format == 'csv':
        print_info('Outputting in CSV format to file...')
        write_to_csv_format(config, parsed_data, fs, ls, debug)
        print_info("File " + dictionary_filename + " created successfully!")
    
    # write out to EPUB format
    if output_format == 'epub':
        print_info('Outputting in EPUB format to file...')
        write_to_epub_format(config, parsed_data, debug)
        print_info("File " + dictionary_filename + " created successfully!")
### END main ###




if __name__ == '__main__':
    # TODO let the user specify the encoding of the input, when relevant
    
    #Python2#    reload(sys)
    #Python2#    sys.setdefaultencoding("utf-8")
    main()


