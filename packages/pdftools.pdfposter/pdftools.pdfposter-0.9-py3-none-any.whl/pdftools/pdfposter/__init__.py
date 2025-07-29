#!/usr/bin/env python
"""
pdftools.pdfposter - scale and tile PDF images/pages to print on multiple pages.
"""
#
# Copyright 2008-2025 by Hartmut Goebel <h.goebel@crazy-compilers.com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#

__author__ = "Hartmut Goebel <h.goebel@crazy-compilers.com>"
__copyright__ = "Copyright 2008-2025 by Hartmut Goebel <h.goebel@crazy-compilers.com>"
__license__ = "SPDX-License-Identifier: GPL-3.0-or-later"
__version__ = "0.9"

import warnings
warnings.warn("Module 'pdftools.pdfposter' is obsolete. "
              "Please use the package and module 'pdfposter' instead.",
              DeprecationWarning)

from pdfposter import *  # noqa
