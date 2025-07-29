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

from setuptools import setup
from distutils.core import Command
from distutils import log
import os, sys


class build_docs(Command):
    description = "build documentation from rst-files"
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        self.docpages = DOCPAGES

    def run(self):
        substitutions = ('.. |VERSION| replace:: ' +
                         self.distribution.get_version())
        for writer, rstfilename, outfilename in self.docpages:
            distutils.dir_util.mkpath(os.path.dirname(outfilename))
            log.info("creating %s page %s", writer, outfilename)
            if not self.dry_run:
                try:
                    with open(rstfilename, encoding='utf-8') as fh:
                        rsttext = fh.read()
                except IOError as e:
                    sys.exit(e)
                rsttext = '\n'.join((substitutions, '', rsttext))
                # docutils.core does not offer easy reading from a
                # string into a file, so we need to do it ourself :-(
                doc = docutils.core.publish_string(source=rsttext,
                                                   source_path=rstfilename,
                                                   writer_name=writer)
                try:
                    with open(outfilename, 'wb') as fh:
                        fh.write(doc)  # is already encoded
                except IOError as e:
                    sys.exit(e)


cmdclass = {}

try:
    import docutils.core
    import docutils.io
    import docutils.writers.manpage
    import distutils.command.build
    distutils.command.build.build.sub_commands.append(('build_docs', None))
    cmdclass['build_docs'] = build_docs
except ImportError:
    log.warn("docutils not installed, can not build man pages. "
             "Using pre-build ones.")

DOCPAGES = (
    ('manpage', 'pdfposter.rst', 'docs/pdfposter.1'),
    ('html', 'pdfposter.rst', 'docs/pdfposter.html'),
    )

setup(cmdclass=cmdclass)
