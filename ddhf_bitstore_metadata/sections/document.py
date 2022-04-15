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
    Document sections
    =================
'''

import re

from ddhf_bitstore_metadata.internals.fields import Field
from ddhf_bitstore_metadata.internals.section import Section
from ddhf_bitstore_metadata.internals import rcsl

class ISSN(Field):
    ''' ISSN - International Standard Serial Number '''

    def validate(self):
        yield from super().validate()
        if not re.match('^[0-9]{4}-[0-9]{4}$', self.val):
            yield self.complaint("ISSN format is not ####-#### (%s)" % self.val)

class ISBN(Field):
    ''' International Standard Book Number '''

    def validate(self):
        yield from super().validate()
        if not re.match('^[0-9]{10}$', self.val):
            yield self.complaint("ISBN format is not ########## (%s)" % self.val)

class Document(Section):
    ''' Document sections '''

    def build(self):
        self += Field("Title", mandatory=True)
        self += Field("Subtitle", single=False)
        self += rcsl.RCSLField()
        self += rcsl.GSLField()
        self += Field("Author", single=False)
        self += Field("Date")
        self += Field("Description", single=False)
        self += ISSN("ISSN")
        self += ISBN("ISBN")
        self.acceptable_formats('PDF', 'ASCII')
