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
    Data Media sections
    ===================
'''

from ..internals.fields import Field, EnumField
from ..internals.section import Section
from ..internals import rcsl

LEGAL_MEDIA_TYPES = {
    '3½" Floppy Disk',
    '4mm DAT magtape',
    '5-hole paper tape',
    '5¼" Floppy Disk',
    '8" Floppy Disk',
    '8-hole paper tape',
    '8mm "Exabyte" magtape',
    'ATA Disk',
    'CDC Disc Pack',
    'Cassette Tape',
    'IBM 2315 Disk Cartridge',
    'Integrated Circuit',
    'LTO cartridge magtape',
    'Mini-Cassette',
    'ESDI Disk',
    'SCSI Disk',
    'ST506 Disk',
    '¼" cartridge magtape',
    '½" Magnetic Tape',
    '⅛" cartridge magtape',
}

LEGAL_MEDIA_FORMATS = (
    'ASCII',
    'ASCII_EVEN',
    'ASCII_ODD',
    'BAGIT',
    'BINARY',
    'GIERTEXT',
    'IMAGEDISK',
    'KRYOFLUX',
    'SIMH-TAP',
    'TAR',
    'WAV',
)

class GeometryException(Exception):
    ''' ... '''

class GeometryEntry():
    ''' Parse a Geometry field '''

    def __init__(self, arg, next_cyl):
        self.input = arg.split()
        self.dims = {'c': (next_cyl,next_cyl), 'h': (0,0), 's': (1,1), 'b': (0,0)}
        for i in self.input:
            d = self.dims.get(i[-1])
            if d is None:
                raise GeometryException("Dimension '%s' unknown (in '%s')" % (i[-1], arg))
            j = i[:-1].split('…')
            if len(j) == 1:
                try:
                    x = int(j[0])
                except Exception as err:
                    raise GeometryException(
                        "Cannot grok number '%s' (in '%s')" % (j[0], arg)
                    ) from err
                self.dims[i[-1]] = (d[0], d[0] + x - 1)
            else:
                try:
                    x = int(j[0])
                except Exception as err:
                    raise GeometryException(
                        "Cannot grok number '%s' (in '%s')" % (j[0], arg)
                    ) from err
                try:
                    y = int(j[1])
                except Exception as err:
                    raise GeometryException(
                        "Cannot grok number '%s' (in '%s')" % (j[1], arg)
                    ) from err
                self.dims[i[-1]] = (x, y)

    def __repr__(self):
        return " ".join(self.input)

    def __iter__(self):
        for c in range(self.dims["c"][0], self.dims["c"][1] + 1):
            for h in range(self.dims["h"][0], self.dims["h"][1] + 1):
                for s in range(self.dims["s"][0], self.dims["s"][1] + 1):
                    yield ((c, h, s), self.dims["b"][1] + 1)

    def __len__(self):
        retval = 1
        for j in self.dims.values():
            retval *= (1 + j[1] - j[0])
        return retval

class ParseGeometry():
    ''' Parse a Geometry line '''

    def __init__(self, arg, tolerant=False):
        self.parts = []
        if isinstance(arg, str):
            arg = [arg]
        for line in arg:
            next_cyl = 0
            j = [i.strip() for i in line.split(',')]
            if tolerant and j[0] == "1c 1h 16s 128b" and j[1] == "1c 1h 16s 256b":
                j[0] = "0…0c 0…0h 16s 128b"
                j[1] = "0…0c 1…1h 16s 256b"
            for i in j:
                self.parts.append(GeometryEntry(i, next_cyl))
                next_cyl = self.parts[-1].dims['c'][1] + 1

    def __repr__(self):
        return ", ".join(str(x) for x in self.parts)

    def __len__(self):
        return sum(len(x) for x in self.parts)

    def __iter__(self):
        for i in self.parts:
            yield from i

class Geometry(Field):
    '''
    Layout of random-access media
    =============================

    Random-access media can be zoned, for instance 8" and CBM floppies,
    so a geometry description is list of comma-separated zones, each
    described by a number of cylinders, heads, sectors and bytes.

    For instance the CBM 1541 diskformat is described by:

        17c 21s 256b, 7c 19s 256b, 6c 18s 256b, 5c 17s 256b

    (Since it is single-headed, the '1h' can be left out.)

    8" floppies with an IBM pedigree will often have the first
    cylinder formated as 26s 128b and the rest of the disk in a
    higher density format, for instance:

        2h 26s 128b, 76c 2h 15s 256b

    By default the first index is zero, except for 's' where it is one
    for compatibility with traditional floppy disk conventions.

        2h means heads are numbered 0 & 1
        5s means sectors are numbered 1,2,3,4&5

    Instead of an integer, a range of integers can be specified:

        0…4s means sectors are numbered 0,1,2,3&4

    '''

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.geom = []

    def validate(self, **kwargs):
        yield from super().validate(**kwargs)

        self.geom = []
        for line in self.val:
            try:
                self.geom.append(ParseGeometry(line))
            except GeometryException as err:
                yield self.complaint("Geometry: " + err.args[0])
                return
            hds = set(x.dims['h'] for x in self.geom[-1].parts)
            if len(hds) > 1:
                yield self.complaint(
                    "Geometry had multiple head-counts (use ranges instead)"
                )
        bitstore_size = self.sect.metadata.BitStore.Size.val
        if bitstore_size is not None:
            bsz = int(bitstore_size)
            gsz = sum(len(x) for x in self.geom)
            if gsz != bsz:
                yield self.complaint(
                    "Geometry (%d) disagrees with Bitstore.Size (%d)" % (gsz, bsz)
                )

class Media(Section):
    '''
        Data Media sections
    '''

    def build(self):
        self += Field("Summary", mandatory=True)
        self += Geometry("Geometry", single=False)
        self += rcsl.RCSLField()
        self += EnumField(
            "Type",
            mandatory=True,
            legal_values=LEGAL_MEDIA_TYPES,
        )
        self += Field("Date")
        self += Field("Model")
        self += Field("Serial")
        self += Field("Description", single=False)
        self.acceptable_formats(*LEGAL_MEDIA_FORMATS)

    def litany(self, **kwargs):
        fmt = self.metadata.BitStore.Format.val
        if fmt in (
            "IMAGEDISK",
        ):
            if self.Geometry.val:
                yield self.Geometry.complaint(
                    "Media.Geometry not allowed for %s format" % fmt
                )
        yield from super().litany(**kwargs)
