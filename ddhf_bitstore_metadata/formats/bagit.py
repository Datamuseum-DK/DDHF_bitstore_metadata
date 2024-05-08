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
    BAGIT Format
    ============
'''

import hashlib

from ddhf_bitstore_metadata.internals.fileformatclass import FileFormat, FileFormatError

def validate_bagit_txt(lines, vfilename, *_args):
    ''' ... '''
    vbi = {}
    for i in lines:
        j = i.split(":", 1)
        if len(j) != 2:
            yield FileFormatError("Syntax error in " + vfilename)
            return
        vbi[j[0]] = j[1].strip()

    i = vbi.get("BagIt-Version")
    if not i:
        yield FileFormatError("No 'BagIt-Version:' in " + vfilename)
        return
    if i not in ("0.97", "1.0"):
        yield FileFormatError("Bad 'BagIt-Version:' in " + vfilename)
        return

    i = vbi.get("Tag-File-Character-Encoding")
    if not i:
        yield FileFormatError("No 'Tag-File-Character-Encoding:' in " + vfilename)
        return
    if i not in ("UTF-8",):
        yield FileFormatError("Bad 'Tag-File-Character-Encoding:' in " + vfilename)
        return

def validate_manifest(lines, vfilename, files):
    ''' ... '''
    for line in lines:
        flds = line.split(maxsplit=1)
        if len(flds[0]) != 64:
            yield FileFormatError("Format error (bad digest) in " + vfilename)
            return
        files[flds[1]] = flds[0]

class BagIt(FileFormat):
    ''' ... '''

    EXTENSION = "zip"

    def validate(self, **kwargs):
        try:
            self.mdi.artifact.open_bagit()
        except Exception as err:
            yield FileFormatError(str(err))
            return

        zfil = self.mdi.artifact.zipfile

        dname = self.mdi.BitStore.Filename.val
        assert dname[-4:].lower() == ".zip"
        dname = dname[:-4] + '/'
        try:
            _info = zfil.getinfo(dname + "bagit.txt")
        except KeyError:
            yield FileFormatError("'" + dname + "bagit.txt' not found")
            return

        expected_files = {}
        for mfn, validator in (
            ("bagit.txt", validate_bagit_txt),
            ("bag-info.txt", None),
            ("manifest-sha256.txt", validate_manifest),
        ):
            try:
                _info = zfil.getinfo(dname + mfn)
            except KeyError:
                yield FileFormatError("Bagit lacks '" + dname + mfn + "'")
            if validator:
                with zfil.open(dname + mfn, "r") as vfil:
                    try:
                        lines = vfil.read().decode("utf8").splitlines()
                    except Exception as err:
                        print("ERR", err)
                        yield FileFormatError("Format error in " + dname + mfn)
                        return
                    yield from validator(lines, dname + mfn, expected_files)

        pfx = dname + "data/"
        lpfx = len(pfx)
        for zfi in zfil.infolist():
            if zfi.is_dir():
                continue
            zfn = zfi.filename
            if zfn[:lpfx] != pfx or len(zfn) == lpfx:
                continue
            rfn = zfn[len(dname):]
            digest = expected_files.get(rfn)
            if not digest:
                yield FileFormatError("File '" + rfn + " not in manifest")
                return
            del expected_files[rfn]
            sha256 = hashlib.sha256()
            sha256.update(zfil.read(zfn))
            if sha256.hexdigest() != digest:
                yield FileFormatError("File '" + zfn + " wrong digest: " + sha256.hexdigest())
        for rfn in expected_files:
            yield FileFormatError("File '" + rfn + " only in manifest")
