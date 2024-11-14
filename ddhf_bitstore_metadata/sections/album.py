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
    Album sections
    ==============
'''

import time

from ..internals import fields
from ..internals.section import Section


class AlbumDescriptionField(fields.Field):
    ''' ... '''

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.images = {}

    def single_image(self, line, key):
        ''' Single image line '''
        if key in self.images:
            yield self.complaint("Image '%s' listed multiple times" % key, line)
        else:
            self.images[key] = line

    def image_range(self, line, key):
        ''' Range of images line '''
        if key[1] != '-':
            yield self.complaint("Syntax error in range of images", line)
            return
        if len(key[0]) != len(key[2]):
            yield self.complaint("Different length filenames in range of images", line)
            return
        if key[0] == key[2]:
            yield self.complaint("Identical filenames in range of images", line)
            return
        start = key[0].rsplit(".", 1)
        end = key[2].rsplit(".", 1)
        if start[-1] != end[-1]:
            yield self.complaint("Different filetypes in range of images", line)
            return
        pfxlen = 0
        for i, j in zip(start[0], end[0]):
            if i != j:
                break
            pfxlen += 1

        pfx = start[0][:pfxlen]
        fmt = "%0" + "%dd" % (len(start[0]) - pfxlen)
        try:
            low = int(start[0][pfxlen:], 10)
            high = int(end[0][pfxlen:], 10) + 1
        except ValueError:
            yield self.complaint("Non-decimal tail of filenames range of images", line)
            return
        for i in range(low, high):
            imgnm = pfx + fmt % i + "." + start[-1]
            yield from self.single_image(line, imgnm)

    def validate(self, **kwargs):
        yield from super().validate(**kwargs)
        if not self.images:
            for line in self.stanza:
                if line.text[-1] == ':':
                    key = line.text[:-1].split()
                    if len(key) == 1:
                        yield from self.single_image(line, key[0])
                    else:
                        yield from self.image_range(line, key)
        if self.sect.metadata.artifact:
            found = set()
            for i in self.sect.metadata.artifact.bagit_contents():
                if i in self.images:
                    found.add(i)
                else:
                    yield self.complaint("Image '%s' missing in metadata list" % i)
            for key, line in self.images.items():
                if key not in found:
                    yield self.complaint("Image missing in BAGIT file", line)

    def descriptions(self):
        ''' Iterate (image_filename, description) '''
        spec = None
        cur = None
        for line in list(self.stanza):
            line = line.text.strip()
            if not line:
                continue
            if line[-1] == ':':
                if spec:
                    yield spec, cur
                spec = line[:-1]
                cur = []
            elif spec and line:
                cur.append(line)
        if spec:
            yield spec, cur

class AlbumDate(fields.Field):
    ''' Date pictures taken '''

    def validate(self, **kwargs):
        yield from super().validate(**kwargs)
        try:
            time.strptime(self.val, "%Y%m%d")
        except ValueError:
            yield self.complaint('Album.Date should be YYYYMMDD format')

class Album(Section):
    ''' Album sections '''

    def build(self):
        self += fields.Field("Title", mandatory=True)
        self += AlbumDate("Date")
        self += AlbumDescriptionField("Description", single=False)
        self.acceptable_formats(
            'BAGIT',
        )
