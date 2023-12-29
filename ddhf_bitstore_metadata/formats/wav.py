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
   Validator for restricted WAV files
'''

import struct

from ddhf_bitstore_metadata.internals.fileformatclass import FileFormat, FileFormatError

VALID_FORMATS = (1, )
VALID_CHANNELS = (1, 2,)
VALID_SAMPLE_RATE = (8000, 44100, 48000,)
VALID_BITS_PER_SAMPLE = (8, 16,)

class RiffList():
    ''' "LIST" block '''

    def __init__(self, octets):
        self.octets = octets
        ptr = 0
        i = struct.unpack("<4s", octets[ptr:ptr + 4])
        self.type = i[0]
        ptr += 4
        self.complaints = []
        while ptr < len(octets):
            i = struct.unpack("<4sL", octets[ptr:ptr + 8])
            ptr += 8 + i[1]
            if i[1] & 1:
                ptr += 1
        if ptr != len(octets):
            self.complaints.append(
                FileFormatError("WAV: Bad INFO chunk (%d != %d)" % (ptr, len(octets)))
            )

class WavFmt():
    ''' "fmt " block '''

    def __init__(self, octets):
        self.octets = octets
        self.audio_format = None
        self.num_channels = None
        self.sample_rate = None
        self.byte_rate = None
        self.block_align = None
        self.bits_per_sample = None
        i = struct.unpack("<HHLLHH", octets[:16])
        self.complaints = []
        for pos, name, valid, in (
            (0, "audio_format", VALID_FORMATS),
            (1, "num_channels", VALID_CHANNELS),
            (2, "sample_rate", VALID_SAMPLE_RATE),
            (3, "byte_rate", None),
            (4, "block_align", None),
            (5, "bits_per_sample", VALID_BITS_PER_SAMPLE),
        ):
            setattr(self, name, i[pos])
            if valid and i[pos] not in valid:
                self.complaints.append(
                    FileFormatError("WAV: %s %d not in %s" % (name, i[pos], str(valid)))
                )

class Wav(FileFormat):
    ''' ... '''

    EXTENSION = "wav"

    def validate(self):

        self.need(16)

        i = struct.unpack("<4sL4s4s", self.octets[:16])

        if i[0] != b'RIFF':
            yield FileFormatError("Not a WAV file (%s not b'RIFF')" % str(i[0]))
            return

        if i[2] != b'WAVE':
            yield FileFormatError("Not a WAV file (%s not b'WAVE')" % str(i[2]))
            return

        if i[3] != b'fmt ':
            yield FileFormatError("WAV file starts with %s instead of b'fmt ' chunk" % str(i[3]))

        plen = i[1]
        if i[1] & 1:
            if len(self.octets) == 8 + i[1]:
                yield FileFormatError(
                   "WAV file lacks pad byte (%d < %d)" % (len(self.octets), 9 + plen)
                )
                return
            plen += 1

        if len(self.octets) < 8 + plen:
            yield FileFormatError("WAV file too short (%d < %d)" % (len(self.octets), 8 + plen))
            return

        if len(self.octets) > 8 + plen:
            yield FileFormatError("WAV file too long (%d > %d)" % (len(self.octets), 8 + plen))
            return

        ptr = 12
        fact = None
        datalen = None
        fmt = None
        last = None
        while ptr <= len(self.octets) - 8:
            i = struct.unpack("<4sL", self.octets[ptr:ptr+8])
            tptr = ptr + 8 + i[1]
            if i[1] & 1:
                tptr += 1
            last = i[0]
            if i[0] == b'data':
                datalen = i[1]
            elif i[0] == b'fmt ':
                fmt = WavFmt(self.octets[ptr + 8:ptr + 8 + i[1]])
                if fmt.complaints:
                    yield from fmt.complaints
            elif i[0] == b'fact' and i[1] == 4:
                fact = struct.unpack("<L", self.octets[ptr+8:ptr+8+i[1]])
            elif i[0] == b'LIST' and self.octets[ptr+8:ptr+12] == b'INFO':
                listinfo = RiffList(self.octets[ptr + 8:ptr + 8 + i[1]])
                if listinfo.complaints:
                    yield from listinfo.complaints
            else:
                yield FileFormatError("WAV chunk %s not allowed" % str(i[0]))
            ptr = tptr

        if ptr != len(self.octets):
            yield FileFormatError("WAV: Length inconsistency (%d != %d)" % (ptr, len(self.octets)))

        if datalen is None:
            yield FileFormatError("WAV: no b'data' chunk)")

        if fmt is None:
            # This is impossible (see check at top) but for consistency...
            yield FileFormatError("WAV: no b'fmt ' chunk)")

        if last != b'data':
            yield FileFormatError("WAV: b'data' must be last chunk (is: %s)" % str(last))

        if fact is not None:
            if fact[0] * fmt.bits_per_sample / 8 != datalen:
                yield FileFormatError(
                    "WAV: b'fact' does not match length of b'data' (%d * %d != %d * 8)" % \
                        (fact[0], fmt.bits_per_sample, datalen)
                )
