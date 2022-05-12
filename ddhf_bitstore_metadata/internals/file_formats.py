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

class FallbackFileformats():
    ''' Fallback file format check, if ddhf_bitstore_fileformats not installed '''

    OK_LIST = {
        'ASCII': 'txt',
        'ASCII_EVEN': 'bin',
        'ASCII_ODD': 'bin',
        'BAGIT': 'zip',
        'BINARY': 'bin',
        'GIERTEXT': 'flx',
        'IMD': 'imd',
        'JPG': 'jpg',
        'KRYOFLUX': 'zip',
        'MP4': 'mp4',
        'PDF': 'pdf',
        'PNG': 'png',
        'SIMH-TAP': 'tap',
        'TAR': 'tar',
    }

    def __contains__(self, what):
        return what in self.OK_LIST

    def get_extension(self, what):
        ''' Appropriate extension for this format '''
        return self.OK_LIST[what]

try:
    import ddhf_bitstore_fileformats
    FileFormats = ddhf_bitstore_fileformats.FileFormats()
except ModuleNotFoundError:
    FileFormats = FallbackFileformats()
