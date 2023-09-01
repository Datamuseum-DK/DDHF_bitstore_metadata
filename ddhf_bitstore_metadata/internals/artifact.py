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
   Artifact class
   --------------

   Provides validators (optional) access to the artifact.
'''

import os
import mmap
import zipfile

class Artifact():
    ''' Accessor class for artifacts '''

    def __init__(self, mdata):
        super().__init__()
        self.mdata = mdata
        if mdata.BitStore.Digest.val is not None:
            self.aa_id = mdata.BitStore.Digest.val[7:7+24]
        else:
            self.aa_id = None
        self.artifact = None
        self.zipfile = None
        self.octets = None
        self.length = None

    def open_artifact(self, file=None):
        ''' Open the artifact '''
        if self.artifact is not None:
            return
        self.artifact = file
        self.length = os.fstat(file.fileno()).st_size
        self.octets = mmap.mmap(
            file.fileno(),
            self.length,
            flags=mmap.MAP_PRIVATE,
            prot=mmap.PROT_READ
        )

    def open_bagit(self):
        ''' Open Zip/Bagit file '''
        self.open_artifact()
        if self.zipfile is None:
            self.zipfile = zipfile.ZipFile(self.artifact)

    def bagit_contents(self):
        ''' Yield payload filenames of Bagit file '''
        basename = self.mdata.BitStore.Filename.val
        assert basename[-4:].lower() == ".zip"
        basename = basename[:-4]
        prefix = basename + "/data/"
        lprefix = len(prefix)
        self.open_bagit()
        for zname in self.zipfile.namelist():
            if len(zname) > lprefix and zname[:lprefix] == prefix:
                yield zname[lprefix:]
