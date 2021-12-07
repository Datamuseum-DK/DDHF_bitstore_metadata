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
   Syntax-checking and parsing of metadata files
   ---------------------------------------------
'''

from ddhf_bitstore_metadata.internals.exceptions import MetadataSyntaxError

class MetadataLine():
    ''' A line of metadata, knows it's own line number '''

    def __init__(self, lineno, text):
        self.lineno = lineno

        self.text = text

        if len(text) == 0:
            return

        if text[0] == ' ':
            self.complain("Leading SP (only TAB allowed)")

    def __repr__(self):
        return "<MetaLine %d: " % self.lineno + self.text + ">"

    def __len__(self):
        return len(self.text)

    def complain(self, why):
        ''' raise a syntax error on this line '''
        raise MetadataSyntaxError(why, line=self.text, where="line %d" % self.lineno)

class MetadataStanza():
    ''' A stanza of metadata '''

    def __init__(self, lines):
        self.stanza_line = lines[0]

        if self.stanza_line.text[-1] != ':':
            self.complain("Stanza header does not end in ':'")

        i = self.stanza_line.text.split('.')
        if len(i) == 0:
            self.complain("No '.' in stanza header")
        if len(i) > 2:
            self.complain("Too many '.' in stanza header")

        self.validate_section(i[0])

        assert i[1][-1] == ':'
        self.validate_field_and_index(i[1][:-1])

        if len(lines) < 2:
            self.complain("Empty stanza")

        self.lines = lines[1:]

    def __len__(self):
        return len(self.lines)

    def __iter__(self):
        yield from self.lines

    def __repr__(self):
        return "<MetadataStanza %s>" % self.name

    def __getitem__(self, idx):
        return self.lines[idx]

    def iterlines(self):
        ''' Iterate the lines withtout the leading TAB '''
        for i in self.lines:
            assert i.text[0] == '\t'
            yield i, i.text[1:]

    def validate_section(self, text):
        ''' Validate the section name '''

        if len(text) == 0:
            self.complain("Missing section name")

        if text[-1] == ']':
            i = text[:-1].split('[')
            if len(i) < 2:
                self.complain("Missing '[' character")
            if len(i) != 2:
                self.complain("Too many '[' characters")
            if len(i[1]) == 0:
                self.complain("Index is empty")
            if not i[1].isdigit():
                self.complain("Index is not a number")
            if i[1][0] == '0':
                self.complain("Index has leading zeros")
            try:
                self.index = int(i[1], 10)
            except ValueError:
                self.complain("Index is not a number")
            text = i[0]
        elif '[' in text:
            self.complain("Missing ']' character")
        elif ']' in text:
            self.complain("Index must come after section name")
        else:
            self.index = None

        if not text.isascii() or not text.isidentifier():
            self.complain("Illegal section name")

        self.section = text

    def validate_field_and_index(self, text):
        ''' Validate the field name and optional index'''

        self.name = self.section + '.' + text

        if '[' in text or ']' in text:
            self.complain("Index '[…]' must come after section name")

        if not text.isascii() or not text.isidentifier():
            self.complain("Illegal field name")

        self.field = text

    def complain(self, why):
        ''' raise a syntax error on this stanza '''
        self.stanza_line.complain(why)

class MetadataSyntax():
    ''' Check syntax and split metadata into stanzas '''

    def __init__(self, text):
        self.cursor = 0
        self.lines = [MetadataLine(num + 1, text) for num, text in enumerate(text.split("\n"))]
        self.stanzas = []
        for stanza in self.lexer():
            self.stanzas.append(MetadataStanza(stanza))

    def __iter__(self):
        yield from self.stanzas

    def get_line(self):
        ''' Get the next line '''
        if self.cursor >= len(self.lines):
            self.lines[-1].complain("Unexpected end of file")
        retval = self.lines[self.cursor]
        self.cursor += 1
        return retval

    def lexer(self):
        ''' Lexical analysis '''

        if len(self.lines) <= 1:
            raise MetadataSyntaxError("Empty")

        if len(self.lines[-1]) > 0:
            self.lines[-1].complain("Missing NL on last line")

        self.lines.pop(-1)

        retval = []
        while True:

            line = self.get_line()

            if len(line) == 0:
                line.complain("Blank line not allowed, section or *END* expected")

            if line.text == "*END*":
                if len(self.lines) != line.lineno:
                    self.lines[line.lineno].complain(
                        "*END* is not final line (%d)" % len(self.lines)
                    )
                break

            if line.text[0] == '\t':
                line.complain("Stanza header expected, not TAB-indented line")

            stanza_lines = [line]
            while True:
                line = self.get_line()
                if len(line) == 0:
                    break
                if line.text == "*END*":
                    line.complain("Missing blank line before *END*")
                stanza_lines.append(line)
            retval.append(stanza_lines)
        return retval
