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
   Field classes
   -------------
'''

from ..internals.syntax import MetadataLine
from ..internals.exceptions import MetadataSemanticError

class Field():
    ''' A field in a metadata section '''

    def __init__(self, name, single=True, mandatory=False):
        assert name[0].isupper()
        assert single in (True, False)
        assert mandatory in (True, False, "strict")
        self.name = name
        self.full_name = None
        self.stanza = None
        self.sect = None
        self.single = single
        self.mandatory = mandatory
        self.val = None

    def complaint(self, why, where=None):
        ''' Produce MetadataSemanticError on this field '''
        if where is None and self.stanza is not None:
            where = self.stanza[0]
        if where is None:
            return MetadataSemanticError(why + " (" + str(where) + ")")
        assert isinstance(where, MetadataLine)
        return MetadataSemanticError(
            why,
            where="line % d" % where.lineno,
            line=where.text,
        )

    def litany(self, **kwargs):
        ''' Yield a litany of exceptions '''
        if self.mandatory is True and self.stanza is None:
            yield self.complaint("Missing mandatory field " + self.full_name)
        if self.mandatory == "strict" and self.stanza is None:
            yield self.complaint("Missing mandatory field " + self.full_name)
        if self.stanza:
            if self.stanza.stanza_line.text[-1].isspace():
                yield self.complaint("Trailing white space")
            for i in self.stanza.lines:
                if i.text != "\t" and i.text[-1].isspace():
                    yield self.complaint("Trailing white space", i)
            yield from self.validate(**kwargs)

    def validate(self, **_kwargs):
        ''' By default validation passes '''
        return
        yield self

    def create(self, stanza):
        ''' create this field '''
        if self.stanza:
            stanza.complain("Field already defined at line %d" % self.stanza.stanza_line.lineno)
        self.stanza = stanza
        if self.single and len(stanza) > 1:
            stanza[1].complain(self.sect.name + "." + self.name + " only allows a single line")
        self.parse()

    def parse(self):
        ''' Parse the stanza, if necessary '''
        self.val = [j for i, j in self.stanza.iterlines()]
        if self.single:
            self.val = self.val[0]

    def serialize(self):
        ''' Serialize field in canonical metadata format '''
        if self.val is None:
            return
        yield self.full_name + ":"
        if isinstance(self.val, list):
            for i in self.val:
                yield "\t" + i
        else:
            yield "\t" + str(self.val)
        yield ""

class EnumField(Field):
    '''
    Field which takes value(s) from an limited enumerated set of values
    '''

    def __init__(self, name, legal_values, **kwargs):
        super().__init__(name, **kwargs)
        self.legal_values = legal_values

    def validate(self, **kwargs):
        yield from super().validate(**kwargs)
        for line in self.stanza:
            if line.text[1:] not in self.legal_values:
                yield self.complaint("Illegal value (%s)" % line.text[1:], where=line)
