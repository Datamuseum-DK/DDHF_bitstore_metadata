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
    Imagedisk Format
    ================
'''

from ddhf_bitstore_metadata.internals.fileformatclass import FileFormat, FileFormatError

class ImageDisk(FileFormat):
    ''' ... '''

    EXTENSION = "imd"

    def validate(self):
        self.need(4)
        if self.octets[:4] != b'IMD ':
            yield FileFormatError("No 'IMD ' magic marker")
            return
        ptr = self.octets.find(b'\x1a')
        if ptr < 4:
            yield FileFormatError("0x1A byte found")
            return
        try:
            header = self.octets[:ptr].decode('ascii')
        except UnicodeDecodeError:
            yield FileFormatError("Illegal chars in header text")
            return

        ptr += 1
        ntracks = 0

        while ptr < len(self.octets):
            ntracks += 1

            self.need(ptr + 1)
            track_mode = self.octets[ptr]
            ptr += 1
            if track_mode > 0x5:
                yield FileFormatError("Illegal track mode (0x%x)" % track_mode)
                return

            self.need(ptr + 1)
            cyl = self.octets[ptr]
            ptr += 1
            if cyl > 90:
                yield FileFormatError("Illegal cylinder (0x%x)" % cyl)
                return

            self.need(ptr + 1)
            head = self.octets[ptr]
            ptr += 1
            cylmap = head & 0x80
            headmap = head & 0x40
            head &= 0x3f
            if head > 1:
                yield FileFormatError("Illegal head (0x%x)" % head)
                return

            self.need(ptr + 1)
            nsect = self.octets[ptr]
            ptr += 1
            if nsect > 50:
                yield FileFormatError("Illegal sector count (0x%x)" % nsect)
                return

            self.need(ptr + 1)
            sectsize = self.octets[ptr]
            ptr += 1
            if sectsize > 0x6:
                yield FileFormatError("Illegal sector size (0x%x)" % sectsize)
                return

            self.need(ptr + nsect)
            sec_num_map = self.octets[ptr:ptr + nsect]
            ptr += nsect
            # can we check sec_num_map ?

            if cylmap:
                self.need(ptr + nsect)
                cylmap = self.octets[ptr:ptr + nsect]
                ptr += nsect
                # can we check cylmap ?

            if headmap:
                self.need(ptr + nsect)
                headmap = self.octets[ptr:ptr + nsect]
                ptr += nsect
                # can we check headmap ?

            seclen = 128 << sectsize
            for secno in range(1, nsect + 1):
                self.need(ptr + 1)
                state = self.octets[ptr]
                ptr += 1
                if state in (1, 3, 5, 7):
                    self.need(ptr + seclen)
                    ptr += seclen
                elif state in (2, 4, 6, 8):
                    self.need(ptr + 1)
                    ptr += 1
                elif state:
                    yield FileFormatError("Illegal sector state (0x%x)" % state)
                    return
