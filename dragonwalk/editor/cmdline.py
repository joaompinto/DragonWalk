#!/usr/bin/python
# -*- coding: utf-8 -*-
#

from optparse import OptionParser

def command_line_parser():
    """
    Returns an option parser object with the available
    command line parameters
    """
    parser = OptionParser()
    parser.add_option("-n", "--new"
        , action="store_true", dest="new_file", default=False
        , help="indicate that a new file should be create")
    return parser