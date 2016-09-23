#!/usr/bin/env python
# coding=utf-8

"""
This file contains a collection of miscellaneous utility functions.
"""

from __future__ import absolute_import
from __future__ import print_function
import imp
import os
import shutil
import stat
import sys
import tempfile
import uuid

__author__ = "Alberto Pettarin"
__copyright__ = "Copyright 2012-2016, Alberto Pettarin (www.albertopettarin.it)"
__license__ = "MIT"
__version__ = "3.1.3"
__email__ = "alberto@albertopettarin.it"
__status__ = "Production"


PY2 = (sys.version_info[0] == 2)


def print_debug(msg, do_print=True):
    if do_print:
        print(u"[DEBU] %s" % msg)


def print_error(msg):
    print(u"[ERRO] %s" % msg)


def print_info(msg):
    print(u"[INFO] %s" % msg)


def print_warning(msg):
    print(u"[WARN] %s" % msg)


def get_uuid():
    return str(uuid.uuid4()).replace("-", "")


def load_input_parser(parser_file_path):
    parser = None
    if os.path.exists(parser_file_path):
        try:
            # load source file
            parser = imp.load_source("", parser_file_path)
            try:
                # try calling parse function
                parser.parse(None, None)
            except:
                print_error("Error trying to call the parse() function. Does file '%s' contain a parse() function?" % parser_file_path)
        except:
            print_error("Error trying to load parser from file '%s'" % parser_file_path)
    else:
        print_error("File '%s' does not exist" % parser_file_path)
    return parser


def create_temp_file():
    tmp_handler, tmp_path = tempfile.mkstemp()
    return (tmp_handler, tmp_path)


def create_temp_directory():
    return tempfile.mkdtemp()


def copy_file(origin, destination):
    try:
        shutil.copy(origin, destination)
    except:
        pass


def rename_file(origin, destination):
    try:
        os.rename(origin, destination)
    except:
        pass


def delete_file(handler, path):
    """
    Safely delete file.

    :param handler: the file handler (as returned by tempfile)
    :type  handler: obj
    :param path: the file path
    :type  path: string (path)
    """
    if handler is not None:
        try:
            os.close(handler)
        except:
            pass
    if path is not None:
        try:
            os.remove(path)
        except:
            pass


def delete_directory(path):
    """
    Safely delete a directory.

    :param path: the file path
    :type  path: string (path)
    """
    def remove_readonly(func, path, _):
        """
        Clear the readonly bit and reattempt the removal

        Adapted from https://docs.python.org/3.5/library/shutil.html#rmtree-example

        See also http://stackoverflow.com/questions/2656322/python-shutil-rmtree-fails-on-windows-with-access-is-denied
        """
        try:
            os.chmod(path, stat.S_IWRITE)
            func(path)
        except:
            pass
    if path is not None:
        shutil.rmtree(path, onerror=remove_readonly)


def utf_lower(string, encoding="utf-8", lower=True):
    """
    Convert the given Unicode string
    (unicode on Python 2, str on Python 3)
    to a byte string in the given encoding,
    and lowercase it.

    :param string: the string to convert
    :type  string: Unicode string
    :param encoding: the encoding to use
    :type  encoding: string
    :param lower: lowercase the string
    :type  lower: bool
    :rtype: byte string
    """
    native_str = isinstance(string, str)
    ret = None
    if (PY2 and native_str) or ((not PY2) and (not native_str)):
        ret = string
    else:
        try:
            ret = string.encode(encoding)
        except UnicodeEncodeError:
            print_warning(u"UnicodeEncodeError in collate function, ignoring it")
            ret = string.encode(encoding, errors="ignore")
    if lower:
        return ret.lower()
    return ret
