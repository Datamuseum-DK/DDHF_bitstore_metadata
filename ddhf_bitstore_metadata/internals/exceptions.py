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
   Common exceptions
   -----------------
'''

class MetadataError(Exception):
    ''' ... '''

    kind = "Metadata Error"

    def __init__(self, text, line="", where=""):
        super().__init__(text)
        self.text = text
        self.line = line
        self.where = where

    def __str__(self):
        text = "Semantic Error: " + self.text
        if self.where:
            text += "\n  " + self.where
        if self.line:
            text += "\n  ⎣" + self.line + "⎤"
        return text

class MetadataSyntaxError(MetadataError):
    ''' Syntax error in metadata '''
    kind = "Metadata Syntax Error"

class MetadataSemanticError(MetadataError):
    ''' Semantic error in metadata '''
    kind = "Metadata Semantic Error"

class FileFormatError(MetadataError):
    ''' ... '''
    kind = "FileFormat Error"

class ShortFile(FileFormatError):
    ''' ... '''
    kind = "File too short"
