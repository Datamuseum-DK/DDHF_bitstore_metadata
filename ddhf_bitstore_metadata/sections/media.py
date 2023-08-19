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

from ddhf_bitstore_metadata.internals.fields import Field, EnumField
from ddhf_bitstore_metadata.internals.section import Section
from ddhf_bitstore_metadata.internals import rcsl

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

    '''

    def validate(self):
        yield from super().validate()
        siz = 0

        for part in self.val.split(','):
            zsiz = 1
            i = part.split()
            suf = 'chsb'
            while i:
                elem = i.pop(0)
                count = int(elem[:-1])
                if count <= 0:
                    yield self.complaint("count '%s' <= 0" % elem)
                    return
                zsiz *= count
                where = suf.find(elem[-1])
                if where < 0:
                    yield self.complaint("suffix letter '%s' unknown or out of order" % elem[-1])
                suf = suf[where + 1:]
            siz += zsiz
        bitstore_size = self.sect.metadata.BitStore.Size.val
        if bitstore_size is not None:
            bsz = int(bitstore_size)
            if siz != bsz:
                yield self.complaint("Geometry (%d) disagrees with Bitstore.Size (%d)" % (siz, bsz))

class Media(Section):
    '''
        Data Media sections
    '''

    def build(self):
        self += Field("Summary", mandatory=True)
        self += Geometry("Geometry")
        self += rcsl.RCSLField()
        self += EnumField(
            "Type",
            mandatory=True,
            legal_values={
                '8mm "Exabyte" magtape',
                '8-hole paper tape',
                'IBM 2315 Disk Cartridge',
                '8" Floppy Disk',
                '5¼" Floppy Disk',
                '3½" Floppy Disk',
		'½" Magnetic Tape',
                'Integrated Circuit',
                'ST506 Disk',
                'SCSI Disk',
                'ATA Disk',
                'Mini-Cassette',
                '¼" cartridge magtape',
                '⅛" cartridge magtape',
                'LTO cartridge magtape',
                '4mm DAT magtape',
            },
        )
        self += Field("Date")
        self += Field("Model")
        self += Field("Serial")
        self += Field("Description", single=False)
        self.acceptable_formats(
            'ASCII',
            'ASCII_EVEN',
            'ASCII_ODD',
            'BINARY',
            'GIERTEXT',
            'IMAGEDISK',
            'KRYOFLUX',
            'SIMH-TAP',
            'TAR',
        )

    def litany(self):
        fmt = self.metadata.BitStore.Format.val
        if fmt in (
            "IMAGEDISK",
        ):
            if self.Geometry.val:
                yield self.Geometry.complaint(
                    "Media.Geometry not allowed for %s format" % fmt
                )
        yield from super().litany()
