#!/usr/bin/env python3
#
# Copyright (c) 2012-2021 Poul-Henning Kamp <phk@phk.freebsd.dk>
# All rights reserved.
#
# SPDX-License-Identifier: BSD-2-Clause
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
# 1. Redistributions of source code must retain the above copyright
#    notice, this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright
#    notice, this list of conditions and the following disclaimer in the
#    documentation and/or other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE AUTHOR AND CONTRIBUTORS ``AS IS'' AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED.  IN NO EVENT SHALL AUTHOR OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS
# OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION)
# HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
# LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY
# OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF
# SUCH DAMAGE.

'''
   Metadata Base Class
   -------------------
'''

from ddhf_bitstore_metadata.internals import section
from ddhf_bitstore_metadata.internals import exceptions
from ddhf_bitstore_metadata.internals import syntax
from ddhf_bitstore_metadata.internals.file_formats import FileFormats

class MetadataBase():
    '''
    Bitstore Metadata base class
    ----------------------------
    '''

    def __init__(self, text=None):
        self.sections = dict()
        self.valid_formats = set()
        self.valid_formats_sections = set()

        mds = syntax.MetadataSyntax(text)
        for stanza in mds:
            sect = self.sections.get(stanza.section)
            if sect is None:
                try:
                    sect = section.get_section(self, stanza.section, stanza.index)
                except section.SectionNotIndexed:
                    stanza.stanza_line.complain("Section cannot be indexed")
                except section.SectionNotFound:
                    stanza.stanza_line.complain("Unknown section")
                assert sect is not None
                self.sections[stanza.section] = sect
            sect.add_field(stanza)

    def __getattr__(self, key):
        retval = self.sections.get(key)
        if retval is None:
            raise AttributeError
        return retval

    def acceptable_formats(self, sect, fmts):
        ''' Restrict acceptable formats '''
        for i in fmts:
            assert i in FileFormats
        if not self.valid_formats:
            self.valid_formats = set(fmts)
        else:
            self.valid_formats &= set(fmts)
        self.valid_formats_sections.add(sect)

    def validate(self, strict=False):
        ''' Validate metadata '''
        for mandatory in (
            "BitStore",
            "DDHF",
        ):
            if mandatory not in self.sections:
                raise exceptions.MetadataSemanticError("No %s section" % mandatory)
        if not self.valid_formats_sections:
            raise exceptions.MetadataSemanticError("No content section(s)")
        if not self.valid_formats:
            raise exceptions.MetadataSemanticError(
                "Incompatible content sections (%s)" % str(self.valid_formats_sections)
            )
        for sect in self.sections.values():
            sect.validate(strict)

class Metadata(MetadataBase):
    '''
    Mostly a convenience wrapper
    '''

    def __init__(self, filename=None):
        super().__init__(open(filename).read())
