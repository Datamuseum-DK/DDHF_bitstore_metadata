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
   Main-program, validates the metadata fields given as arguments
'''

import sys

from ddhf_bitstore_metadata import internals

def main():
    ''' Validate all metadata files given as arguments '''
    exit_status = 0
    for filename in sys.argv[1:]:
        mentioned = False
        try:
            mdi = internals.Metadata(filename=filename)
        except internals.MetadataSyntaxError as err:
            if not mentioned:
                print(filename, "=> Syntax error")
                mentioned = True
            print("    Syntax Error: ", err)
            if err.where:
                print("\t" + err.where)
            print("\t⎣" + err.line + "⎤")
            exit_status = 1
            continue

        if filename[-5:] == ".meta":
            try:
                file = open(filename[:-5], "rb")
                i = internals.Artifact(mdi)
                i.tmpfile = file
                mdi.add_accessor(i)
            except FileNotFoundError:
                pass

        # We do not insist on certain fields
        bitstore = getattr(mdi, "BitStore", None)
        if bitstore:
            for fldname in ("Size", "Ident", "Digest",):
                fld = getattr(bitstore, fldname, None)
                if fld:
                    fld.mandatory = False

        for err in mdi.litany():
            if not mentioned:
                print(filename, "=> Semantic error")
                mentioned = True
            print('    ' + str(err.text))
            if err.where:
                print('\t' + str(err.where))
            if err.line:
                print("\t⎣" + err.line + "⎤")
            exit_status = 1

        if not mentioned:
            print(filename, "=> OK")

    sys.exit(exit_status)

if __name__ == "__main__":
    main()
