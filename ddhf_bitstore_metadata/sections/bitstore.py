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
    Bitstore Sections
    =================
'''

import os
import re
import time

from ddhf_bitstore_metadata.internals.fields import Field, EnumField
from ddhf_bitstore_metadata.internals.section import Section
from ddhf_bitstore_metadata.internals.file_formats import FileFormats

class Access(Field):
    ''' (public|private|restricted|gone)[/(public|private|restricted|gone)] '''

    def validate(self):
        yield from super().validate()
        if len(self.val.split()) > 1:
            yield self.complaint('White-space not allowed')
            return
        j = self.val.split("/")
        if not 1 <= len(j) <= 2:
            yield self.complaint('Format error (must be ACCESS or ACCESS/ACCESS)')
            return
        ok_levels = {
            'gone': -1,
            'public': 0,
            'private': 1,
            'restricted': 2,
        }
        levels = [ok_levels.get(i) for i in j]
        if None in levels:
            yield self.complaint('Valid access levels are: ' + ', '.join(ok_levels.keys()))
            return

        if -1 in levels and len(levels) > 1:
            yield self.complaint('Access "gone" invalid with split access ("/")')
            return

        if len(levels) != len(set(levels)):
            yield self.complaint('Identical split access')
            return

        if levels != list(sorted(levels)):
            yield self.complaint('Access to metadata stricter than to artifact')
            return

class Size(Field):
    ''' Must be a decimal number '''

    def validate(self):
        yield from super().validate()
        if not self.val.isascii() or not self.val.isdigit():
            yield self.complaint('Not a number')
            return
        if self.val == "0":
            yield self.complaint('Size cannot be zero')
            return
        if self.val[0] == "0":
            yield self.complaint('Leading zeros')

class Filename(Field):
    ''' Must be sensible '''

    def validate(self):
        yield from super().validate()
        if not re.match('^[a-zæøåA-ZÆØÅ0-9_][a-zæøåA-ZÆØÅ0-9_.-]*$', self.val):
            yield self.complaint('Bad filename (illegal characters)')

class Ident(Field):
    ''' Must be 8 digits with optional generation number '''

    def validate(self):
        yield from super().validate()
        if not self.val.isascii() or len(self.val.split()) != 1:
            yield self.complaint('Not a valid identifier')
            return
        flds = self.val.split(':')
        if len(flds) > 2:
            yield self.complaint('Not a valid identifier')
        try:
            i = int(flds[0], 10)
        except ValueError:
            yield self.complaint('Not a valid identifier')
            return
        if not 30000000 <= i <= 39999999:
            yield self.complaint('Not a valid identifier')
        if len(flds) == 2:
            try:
                i = int(flds[1], 10)
            except ValueError:
                yield self.complaint('Not a valid generation')
                return
            if i < 1:
                yield self.complaint('Not a valid generation')

class Digest(Field):
    ''' sha256:[0-9a-f]{64} '''

    def validate(self):
        yield from super().validate()
        if not re.match('^sha256:[0-9a-f]{64}$', self.val):
            yield self.complaint('Bad digest')

class LastEdit(Field):
    ''' Must be YYYYMMDD name '''

    def validate(self):
        yield from super().validate()
        if not re.match('^20[012][0-9][012][0-9][0-3][0-9]', self.val):
            yield self.complaint('Invalid date')
            return
        if not re.match('^[0-9]{8} ', self.val):
            yield self.complaint('Date not followed by SP')
            return
        if not re.match('^[0-9]{8} [^ ]', self.val):
            yield self.complaint('More than one SP after date')
        flds = self.val.split(" ", 1)
        assert len(flds) == 2
        try:
            time.strptime(flds[0], "%Y%m%d")
        except ValueError:
            yield self.complaint('Not a valid date')

class Format(EnumField):
    ''' Must match extension '''

    def validate(self):
        yield from super().validate()
        want_ext = FileFormats.get_extension(self.val)
        fname = self.sect.Filename
        has_ext = os.path.splitext(fname.val)
        if has_ext[1].lower() != "." + want_ext:
            yield fname.complaint('BitStore.filename suffix must be ".%s"' % want_ext)

class BitStore(Section):
    '''
        BitStore sections
    '''

    def build(self):

        self += EnumField("Metadata_version", legal_values={"1.0",}, mandatory=True)
        self += Access("Access", mandatory=True)
        self += Filename("Filename", mandatory=True)
        self += Size("Size", mandatory="strict")
        self += Format("Format", FileFormats, mandatory=True)
        self += Ident("Ident", mandatory="strict")
        self += Digest("Digest", mandatory="strict")
        self += LastEdit("Last_edit", mandatory=True)
