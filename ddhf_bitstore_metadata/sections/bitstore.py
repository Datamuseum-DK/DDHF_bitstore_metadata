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
        if len(self.val.split()) > 1:
            self.complain('White-space not allowed')
        j = self.val.split("/")
        if not 1 <= len(j) <= 2:
            self.complain('Format error (must be ACCESS or ACCESS/ACCESS)')
        ok_levels = {
            'gone': -1,
            'public': 0,
            'private': 1,
            'restricted': 2,
        }
        levels = [ok_levels.get(i) for i in j]
        if None in levels:
            self.complain('Valid access levels are: ' + ', '.join(ok_levels.keys()))

        if -1 in levels and len(levels) > 1:
            self.complain('Access "gone" invalid with split access ("/")')

        if len(levels) != len(set(levels)):
            self.complain('Identical split access')

        if levels != list(sorted(levels)):
            self.complain('Access to metadata stricter than to artifact')

class Size(Field):
    ''' Must be a decimal number '''

    def validate(self):
        if not self.val.isascii() or not self.val.isdigit():
            self.complain('Not a number')
        if self.val == "0":
            self.complain('Size cannot be zero')
        if self.val[0] == "0":
            self.complain('Leading zeros')

class Filename(Field):
    ''' Must be sensible '''

    def validate(self):
        if not re.match('^[a-zæøåA-ZÆØÅ][a-zæøåA-ZÆØÅ0-9_.-]*$', self.val):
            self.complain('Bad filename (illegal characters)')

class Ident(Field):
    ''' Must be 8 digits '''

    def validate(self):
        if not self.val.isascii() or not self.val.isdigit() or len(self.val) != 8:
            self.complain('Not a valid identifier')
        if self.val[0] != '3':
            self.complain('Not a valid bitstore identifier')

class Digest(Field):
    ''' sha256:[0-9a-f]{64} '''

    def validate(self):
        if not re.match('^sha256:[0-9a-f]{64}$', self.val):
            self.complain('Bad digest')

class LastEdit(Field):
    ''' Must be YYYYMMDD name '''

    def validate(self):
        if not re.match('^20[012][0-9][012][0-9][0-3][0-9]', self.val):
            self.complain('Invalid date')
        if not re.match('^[0-9]{8} ', self.val):
            self.complain('Date nog followed by SP')
        if not re.match('^[0-9]{8} [^ ]', self.val):
            self.complain('More than one SP after date')
        flds = self.val.split(" ", 1)
        assert len(flds) == 2
        try:
            time.strptime(flds[0], "%Y%m%d")
        except ValueError:
            self.complain('Not a valid date')

class Format(EnumField):
    ''' Must match extension '''

    def validate(self):
        want_ext = FileFormats.get_extension(self.val)
        fname = self.sect.Filename
        has_ext = os.path.splitext(fname.val)
        if has_ext[1].lower() != "." + want_ext:
            fname.complain('BitStore.filename suffix must be ".%s"' % want_ext)

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
