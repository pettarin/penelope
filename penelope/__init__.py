#!/usr/bin/env python
# coding=utf-8

"""
Penelope is a multi-tool for creating, editing and converting dictionaries, especially for eReader devices.

This is the main Penelope script, intended to be run from command line.
"""

from __future__ import absolute_import
import argparse
import sys

from penelope.__main__ import main
from penelope.command_line import COMMAND_LINE_PARAMETERS
from penelope.command_line import DESCRIPTION
from penelope.command_line import EPILOG
from penelope.command_line import INPUT_FORMATS
from penelope.command_line import OUTPUT_FORMATS
from penelope.command_line import REQUIRED_PARAMETERS
from penelope.command_line import USAGE
from penelope.command_line import check_arguments
from penelope.command_line import set_default_values
from penelope.dictionary import read_dictionary
from penelope.dictionary import write_dictionary
from penelope.utilities import get_uuid
from penelope.utilities import load_input_parser
from penelope.utilities import print_debug
from penelope.utilities import print_error
from penelope.utilities import print_info

__author__ = "Alberto Pettarin"
__copyright__ = "Copyright 2012-2015, Alberto Pettarin (www.albertopettarin.it)"
__license__ = "MIT"
__version__ = "3.0.1"
__email__ = "alberto@albertopettarin.it"
__status__ = "Production"



