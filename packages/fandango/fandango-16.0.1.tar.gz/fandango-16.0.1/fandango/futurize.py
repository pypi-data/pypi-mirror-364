#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
#############################################################################
##
## project :     Functional tools for Tango Control System
##
## $Author:      Sergi Rubio Manrique, srubio@cells.es $
##
## $Revision:    2008 $
##
## copyleft :    ALBA Synchrotron Controls Section, CELLS
##               Bellaterra
##               Spain
##
#############################################################################
##
## This file is part of Tango Control System
##
## Tango Control System is free software; you can redistribute it and/or
## modify it under the terms of the GNU General Public License as published
## by the Free Software Foundation; either version 3 of the License, or
## (at your option) any later version.
##
## Tango Control System is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU General Public License for more details.
##
## You should have received a copy of the GNU General Public License
## along with this program; if not, see <http://www.gnu.org/licenses/>.
####################################################################@########
"""

from __future__ import division
from __future__ import print_function

try:
    # python 2-3 compatibility
    from future import standard_library
    standard_library.install_aliases()
    from builtins import hex
    from builtins import chr
    from builtins import filter
    from builtins import next
    from builtins import zip
    #from builtins import str #NOPE! breaks joins
    from builtins import map
    from builtins import range
    from past.builtins import basestring, unicode
    from past.utils import old_div
except:
    # future past not available
    basestring = str
    chr = chr
    filter = filter
    hex = hex
    map = map
    next = next
    range = range
    unicode = str
    zip = zip
    def old_div(x, y):
        r = x/y
        if isinstance(x, int) and isinstance(y, int):
            r = int(r)
        return r
