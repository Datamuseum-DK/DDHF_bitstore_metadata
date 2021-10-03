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
   Section class
   -------------
'''

import importlib

from ddhf_bitstore_metadata.internals import fields

class SectionNotFound(Exception):
    ''' ... '''

class SectionNotIndexed(Exception):
    ''' ... '''

SECTION_CLASSES = {}

def get_section(metadata, sect_name, index):
    '''
       Section classes are loaded dynamically
    '''
    sect_class = SECTION_CLASSES.get(sect_name)
    if sect_class is None:
        path = "ddhf_bitstore_metadata.sections." + sect_name.lower()
        try:
            module = importlib.import_module(path)
        except ModuleNotFoundError as err:
            if err.name == path:
                raise SectionNotFound from err
            raise
        sect_class = getattr(module, sect_name)
        SECTION_CLASSES[sect_name] = sect_class
    return sect_class(metadata, sect_name, index)

class Section():
    '''
    One section of metdata
    '''

    def __init__(self, metadata, name, index):
        assert name[0].isupper()
        self.metadata = metadata
        self.name = name
        self.indexed = False
        self.index = index
        self.full_name = self.name
        if index is not None:
            self.full_name += "[%d]" % index
        self.fields = {}
        self.build()
        if index is not None and not self.indexed:
            raise SectionNotIndexed()

    def __repr__(self):
        if self.index:
            return "Section %s[%d]" % (self.name, self.index)
        return "Section %s" % self.name

    def __iadd__(self, fld):
        assert isinstance(fld, fields.Field)
        self.fields[fld.name] = fld
        fld.sect = self
        fld.full_name = self.full_name + "." + fld.name
        return self

    def __getattr__(self, key):
        return self.fields[key]

    def build(self):
        ''' Actual sections define their fields here '''
        assert False, (self, "failed to define .build()")

    def acceptable_formats(self, *fmts):
        ''' Filter acceptable formats '''
        self.metadata.acceptable_formats(self, fmts)

    def add_field(self, stanza):
        ''' Add a field to this section '''
        field = self.fields.get(stanza.field)
        if field is None:
            stanza.complain("No such field in section " + self.name)
        field.create(stanza)

    def validate(self, strict=False):
        ''' Validate this section '''
        for fld in self.fields.values():
            fld.validate_field(strict)
