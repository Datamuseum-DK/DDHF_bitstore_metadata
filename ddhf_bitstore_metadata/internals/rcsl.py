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
   RCSL fields
'''

from ddhf_bitstore_metadata.internals import fields

RCSLS = [
    ["21", "M", ],
    ["21", "V", ],
    ["28", "D", ],
    ["30", "M", ],
    ["31", "D", ],
    ["42", "I", ],
    ["43", "GL", ],
    ["43", "R", ],
    ["43", "RI", ],
    ["44", "D", ],
    ["44", "RT", ],
    ["51", "VB", ],
    ["52", "AA", ],
    ["53", "D", ],
    ["53", "M", ],
    ["53", "S", ],
    ["55", "D", ],
    ["82", "D", ],
    ["82", "H", ],
    ["82", "Q", ],
    ["99", "0", ],
    ["99", "1", ],
]

class GSLField(fields.Field):
    ''' GIER System Library numbers '''

    def __init__(self, **kwargs):
        super().__init__("GSL", **kwargs)

    def validate(self, **kwargs):
        yield from super().validate()
        if not self.sect.metadata.DDHF.has_keyword("GSL"):
            yield self.complaint('DDHF.Keywords lack "GSL"')

class RCSLField(fields.Field):
    ''' RegneCentralen System Library numbers '''

    def __init__(self, single=False, **kwargs):
        super().__init__("RCSL", single=False, **kwargs)

    def validate(self, **kwargs):
        yield from super().validate()
        for line in self.stanza:
            if len(line.text[1:].split()) > 1:
                yield self.complaint("White-space not allowed", line)
                return
            parts = line.text.strip().split('-')
            if len(parts) != 4 or parts[0] != "RCSL":
                yield self.complaint('RCSL must have form RCSL-#-$-#', line)
                return

            try:
                int(parts[3], 10)
            except ValueError:
                yield self.complaint('RCSL must have form RCSL-#-$-#', line)
                return

            if not parts[1:3] in RCSLS:
                yield self.complaint('Unknown RCSL dept-loc', line)
                return
            kw_want = "RCSL/" + "/".join(parts[1:3])
            if not self.sect.metadata.DDHF.has_keyword(kw_want):
                yield self.complaint('DDHF.Keywords lack "%s"' % kw_want, line)
