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
    Fileformats - fall-back if ddhf_bitstore_fileformats not installed
    ==================================================================
'''

from ..internals.fileformatclass import FileFormat

from ..formats.imagedisk import ImageDisk
from ..formats.bagit import BagIt
from ..formats.wav import Wav

class Ascii(FileFormat):
    ''' ... '''
    EXTENSION = "txt"

class AsciiEven(FileFormat):
    ''' ... '''
    EXTENSION = "bin"

class AsciiOdd(FileFormat):
    ''' ... '''
    EXTENSION = "bin"

class GierText(FileFormat):
    ''' ... '''
    EXTENSION = "flx"

class Binary(FileFormat):
    ''' ... '''
    EXTENSION = "bin"

class Iso(FileFormat):
    ''' ... '''
    EXTENSION = "iso"

class JPG(FileFormat):
    ''' ... '''
    EXTENSION = "jpg"

class KryoFlux(FileFormat):
    ''' ... '''
    EXTENSION = "zip"

class MP4(FileFormat):
    ''' ... '''
    EXTENSION = "mp4"

class PDF(FileFormat):
    ''' ... '''
    EXTENSION = "pdf"

class PNG(FileFormat):
    ''' ... '''
    EXTENSION = "png"

class SimhTap(FileFormat):
    ''' ... '''
    EXTENSION = "tap"

class Tar(FileFormat):
    ''' ... '''
    EXTENSION = "tar"

class Fileformats():
    ''' Fallback file format check, if ddhf_bitstore_fileformats not installed '''

    OK_LIST = {
        'ASCII': Ascii,
        'ASCII_EVEN': AsciiEven,
        'ASCII_ODD': AsciiOdd,
        'BAGIT': BagIt,
        'BINARY': Binary,
        'GIERTEXT': GierText,
        'IMAGEDISK': ImageDisk,
        'ISO9660': Iso,
        'JPG': JPG,
        'KRYOFLUX': KryoFlux,
        'MP4': MP4,
        'PDF': PDF,
        'PNG': PNG,
        'SIMH-TAP': SimhTap,
        'TAR': Tar,
        'WAV': Wav,
    }

    def __contains__(self, what):
        return what in self.OK_LIST

    def get_extension(self, what):
        ''' Appropriate extension for this format '''
        return self.OK_LIST[what].EXTENSION

    def litany(self, mdi, **kwargs):
        ''' Yield a litany of complaints '''
        assert mdi.artifact
        fmt = mdi.BitStore.Format.val
        # fmt = "BAGIT"
        yield from self.OK_LIST[fmt](mdi).litany(**kwargs)

FileFormats = Fileformats()
