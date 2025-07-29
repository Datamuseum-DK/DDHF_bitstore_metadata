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

    def iterate_image_descriptions(self):
        ''' Iterate over image filenames and the image descriptions '''
        assert False # out of order
        desc = []
        for line in reversed(self.stanza):
            if line.text[-1] != ':':
                if len(line.text) > 1:
                    desc.insert(0, line.text[1:])
            else:
                while desc and desc[-1].strip() == "":
                    desc.pop(-1)
                if len(desc) > 0:
                    lstrip = min(len(x) - len(x.lstrip()) for x in desc)
                    if lstrip:
                        desc = [x[lstrip:] for x in desc]
                for filename in self.iterate_image_line(line):
                    yield filename, desc
                desc = []

    def process_image_line(self, line):
        assert line.text[-1] == ':'
        key = line.text[:-1].split()
        if len(key) == 1:
            if self.images is None:
                return
            state = self.images.get(key[0], None)
            if state is None:
                yield self.complaint("No image '%s' in bagit file" % key[0], line)
                return
            if state:
                yield self.complaint("Image '%s' described more than once" % key[0], line)
                return
            self.images[key[0]] = True
            return
        if key[1] != '-':
            yield self.complaint("No '-' in image range", line)
            return
        if len(key[0]) != len(key[2]):
            yield self.complaint("Image names have different length ", line)
            return
        if key[0] == key[2]:
            yield self.complaint("Identical image names ", line)
            return
        if key[0] > key[2]:
            yield self.complaint("Images names are in wrong order", line)
            return
        if self.images is None:
            return
        iterate = True
        if key[0] not in self.images:
            yield self.complaint("No image '%s' in bagit file" %  key[0], line)
            iterate = False
        if key[2] not in self.images:
            yield self.complaint("No image '%s' in bagit file" %  key[2], line)
            iterate = False
        if not iterate:
            return
        x = list(self.images.keys())
        while x[0] < key[0]:
            x.pop(0)
        while x[-1] > key[2]:
            x.pop(-1)
        for y in x:
            if self.images[y]:
                yield self.complaint("Image '%s' described more than once" % y, line)
            else:
                self.images[y] = True

    def validate(self, **kwargs):
        yield from super().validate(**kwargs)

        if self.sect.metadata.artifact:
            self.images = dict(
                (x, False) for x in sorted(self.sect.metadata.artifact.bagit_contents())
            )
        else:
            self.images = None

        for line in self.stanza:
            if line.text[-1] == ':':
                yield from self.process_image_line(line)
        bad = [[]]
        for nm, st in self.images.items():
            if not st:
                bad[-1].append(nm)
            elif len(bad[-1]) > 0:
                bad.append([])
        for rg in bad:
            if len(rg) == 1:
                yield self.complaint("Image '%s' not described" % rg[0])
            elif len(rg) >= 1:
                yield self.complaint("Images '%s' - '%s' not described" % (rg[0], rg[-1]))

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
        self += fields.Field("Photographer", single=False)
        self.acceptable_formats(
            'BAGIT',
        )
