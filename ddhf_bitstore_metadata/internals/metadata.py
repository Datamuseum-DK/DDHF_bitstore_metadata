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

from ddhf_bitstore_metadata.internals import artifact
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
        self.sections = {}
        self.valid_formats = set()
        self.valid_formats_sections = set()
        self.complaints = []
        self.artifact = None

        mds = syntax.MetadataSyntax(text)
        for stanza in mds:
            full_sect = stanza.section
            if stanza.index is not None:
                full_sect += "[%d]" % stanza.index
            sect = self.sections.get(full_sect)
            if sect is None:
                try:
                    sect = section.get_section(self, stanza.section, stanza.index)
                except section.SectionNotIndexed:
                    stanza.stanza_line.complain("Section cannot be indexed")
                except section.SectionNotFound:
                    stanza.stanza_line.complain("Unknown section")
                assert sect is not None
                self.sections[full_sect] = sect
            sect.add_field(stanza)

    def __getattr__(self, key):
        retval = self.sections.get(key)
        if retval is None:
            raise AttributeError
        return retval

    def acceptable_formats(self, sect, fmts):
        ''' Restrict acceptable formats '''
        self.valid_formats_sections.add(sect)
        if not fmts:
            return
        for i in fmts:
            assert i in FileFormats
        if not self.valid_formats:
            self.valid_formats = set(fmts)
        else:
            self.valid_formats &= set(fmts)

    def add_accessor(self, accessor):
        ''' Add accessor for the artifact '''
        assert isinstance(accessor, artifact.Artifact)
        self.artifact = accessor

    def validate(self):
        ''' Validate metadata '''
        for i in self.litany():
            raise i

    def litany(self):
        ''' Yield a litany of exceptions '''
        for mandatory in (
            "BitStore",
            "DDHF",
        ):
            if mandatory not in self.sections:
                yield exceptions.MetadataSemanticError("No %s section" % mandatory)
        if not self.valid_formats and self.valid_formats_sections:
            yield exceptions.MetadataSemanticError(
                "Incompatible content sections (%s)" % str(self.valid_formats_sections)
            )
        for sect in self.sections.values():
            yield from sect.litany()

        if self.artifact:
            yield from FileFormats.litany(self)

class Metadata(MetadataBase):
    '''
    Mostly a convenience wrapper
    '''

    def __init__(self, *args, filename=None, artifact_file=None, **kwargs):
        if filename is not None:
            with open(filename, encoding="utf8") as file:
                super().__init__(file.read(), *args, **kwargs)
        else:
            super().__init__(*args, **kwargs)
        if artifact_file is not None:
            with open(artifact_file, "rb") as file:
                i = artifact.Artifact(self)
                i.open_artifact(file)
                self.add_accessor(i)
