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
    Fileformat base class
    =====================
'''

from ..internals.exceptions import FileFormatError, ShortFile


class FileFormat():
    ''' ... '''

    EXTENSION = None

    def __init__(self, mdi):
        self.mdi = mdi
        self.octets = mdi.artifact.octets

    def need(self, length):
        ''' Complain if artifict not at least this long '''
        if self.octets is None:
            self.mdi.artifact.open_artifact()
            self.octets = self.mdi.artifact.octets
        if length > len(self.octets):
            raise ShortFile("Artifact (at least) %d bytes too short" % (length - len(self.octets)))

    def validate(self, **_kwargs):
        ''' Validate file format '''
        return
        yield FileFormatError("(FileFormat Not Checked)")

    def litany(self, **kwargs):
        ''' Yield the litany of faults found '''
        try:
            yield from self.validate(**kwargs)
        except ShortFile as err:
            yield err
