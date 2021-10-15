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
    DDHF sections
    =============
'''

from ddhf_bitstore_metadata.internals.fields import Field, EnumField
from ddhf_bitstore_metadata.internals.section import Section
from ddhf_bitstore_metadata.internals import rcsl

KEYWORDS = set([
    "ALGOL",
    "ANALOG_COMPUTING",
    "APL",
    "ARTIFACTS",
    "ASTRONOMY",
    "B&O/DOCS",
    "B&O/SW",
    "CALCULATORS",
    "C64",
    "CBM900",
    "COMAL",
    "COMAL/RC3600",
    "COMAL/RC700",
    "COMAL/Z80",
    "COMPANY/ATP",
    "COMPANY/BULL",
    "COMPANY/BURROUGHS",
    "COMPANY/CONTEX",
    "COMPANY/COMMODORE",
    "COMPANY/DATACENTRALEN",
    "COMPANY/DATACO",
    "COMPANY/DATA_GENERAL",
    "COMPANY/DATA_GENERAL/NOVA",
    "COMPANY/BOGIKA",
    "COMPANY/DC",
    "COMPANY/DDC",
    "COMPANY/DSB",
    "COMPANY/DSI",
    "COMPANY/FACIT",
    "COMPANY/FACIT/ABC80",
    "COMPANY/FACIT/TWIST",
    "COMPANY/FLÅDEN",
    "COMPANY/GNT",
    "COMPANY/HALDOR_TOPSØE",
    "COMPANY/IBM",
    "COMPANY/ICL/COMET",
    "COMPANY/ICL/COMET/TAPE",
    "COMPANY/JTAS",
    "COMPANY/KTAS",
    "COMPANY/LEC",
    "COMPANY/METANIC",
    "COMPANY/MICROSOFT",
    "COMPANY/NAVISION",
    "COMPANY/NEUCC",
    "COMPANY/NORDJYSK_EDB_CENTER",
    "COMPANY/NORSK_DATA",
    "COMPANY/NORSK_DATA/DISK",
    "COMPANY/NORSK_DATA/DOCS",
    "COMPANY/OLICOM",
    "COMPANY/ODENSE_UNI",
    "COMPANY/PBS",
    "COMPANY/PRESSPLAY",
    "COMPANY/RISØ",
    "COMPANY/SAS",
    "COMPANY/SCMETRIC/MICROMUX",
    "COMPANY/SDC",
    "COMPANY/SWTPC",
    "COMPANY/SILVERROCK",
    "COMPANY/SINCLAIR",
    "COMPANY/TJÆREBORG",
    "COMPANY/VEGA_DATA",
    "COMPANY/VESTKRAFT",
    "COMPANY/VP",
    "COMPANY/ÅLBORG_UNI",
    "COMPANY/ZILOG",
    "COMPUTER-KITS",
    "COMPILERS",
    "CPR",
    "CR",
    "CR/FIKS",
    "CR/INTERNT",
    "CR/MARKETING",
    "CR/CR80/SW",
    "CR/TAPE",
    "CRYPTOGRAPHY",
    "DANKORT",
    "DASK",
    "DASK/LIBRARY",
    "DATALOGI",
    "DATALÆRE",
    "DDE",
    "DDE/SUPERMAX",
    "DDE/SUPERMAX/DISK",
    "DDE/MARKETING",
    "DDHF/FORMALIA",
    "DDHF/HISTORY",
    "DKUUG",
    "DKUUG/DISKS",
    "DKUUG/EUUG",
    "EDUCATION",
    "EVENT/1958",
    "EVENT/1960",
    "EVENT/1965",
    "EVENT/2002",
    "EVENT/2003",
    "EVENT/2004",
    "EVENT/2005",
    "EVENT/2006",
    "EVENT/2007",
    "EVENT/2008",
    "EVENT/2009",
    "EVENT/2010",
    "EVENT/2011",
    "EVENT/2012",
    "EVENT/2013",
    "EVENT/2014",
    "EVENT/2015",
    "EVENT/2016",
    "EVENT/2017",
    "EVENT/2018",
    "EVENT/2019",
    "EVENT/2020",
    "EVENT/COVER",
    "EVENT/SLIDES",
    "EVENT/VIDEO",
    "FORMIDLING",
    "GAMES",
    "GAMES/HUGO",
    "GIER",
    "GIER/ALGOL_4",
    "GIER/ALGOL_II",
    "GIER/ALGOL_III",
    "GIER/ASTRONOMY",
    "GIER/CHEMISTRY",
    "GIER/DEMO",
    "GIER/GAMES",
    "GIER/HELP",
    "GIER/HELP3",
    "GIER/HW",
    "GIER/MATHEMATICS",
    "GIER/MISC",
    "GIER/MUSIC",
    "GIER/OTHER_SCIENCE",
    "GIER/TEST",
    "GIER/UTIL",
    "GSL",
    "IMAGES",
    "IMAGES/OLDGALLERY",
    "IMAGES/SDC",
    "JET80",
    "LANGUAGES",
    "LANGUAGES/BASIC",
    "LANGUAGES/C",
    "LANGUAGES/COBOL",
    "LANGUAGES/PASCAL",
    "NEMID",
    "NETWORKS",
    "NETWORKS/INTERNET",
    "NETWORKS/PAXNET",
    "OS/FLEX",
    "OS/MS-DOS",
    "OS/UNIFLEX",
    "OS/XDOS",
    "PERIODICALS/DKUUG-NYT",
    "PERIODICALS/PICCOLINIEN",
    "PERSONS",
    "PERSONS/AAGE_MELBYE",
    "PERSONS/BENT_SCHARØE_PETERSEN",
    "PERSONS/CHARLES_SIMONYI",
    "PERSONS/JØRN_JENSEN",
    "PERSONS/KONRAD_ZUSE",
    "PERSONS/NIELS_IVAR_BECH",
    "PERSONS/PETER_NAUR",
    "PERSONS/PER_BRINCH_HANSEN",
    "PERSONS/RICHARD_PETERSEN",
    "PRECOMPUTING",
    "PÆDAT",
    "RATIONAL_1000/DISK",
    "RATIONAL_1000/DOCS",
    "RATIONAL_1000/HW",
    "RATIONAL_1000/SW",
    "RATIONAL_1000/TAPE",
    "RC",
    "RC/RCNET",
    "RC1000",
    "RC2000",
    "RC2100",
    "RC2500",
    "RC3000",
    "RC3500",
    "RC3500/ALARMNET",
    "RC3500/DOCS",
    "RC3500/HW",
    "RC3600",
    "RC3600/COMAL",
    "RC3600/DE2",
    "RC3600/DISK",
    "RC3600/DOMUS",
    "RC3600/HW",
    "RC3600/LOADER",
    "RC3600/MUSIL",
    "RC3600/PAPERTAPE",
    "RC3600/SALG",
    "RC3600/SW",
    "RC3600/TEST",
    "RC3600/UTIL",
    "RC39/DISK",
    "RC3900",
    "RC4000",
    "RC4000/CHEMISTRY",
    "RC4000/GAMES",
    "RC4000/HW",
    "RC4000/MARKETING",
    "RC4000/MATHEMATICS",
    "RC4000/PULAWY",
    "RC4000/SW",
    "RC4000/TEST",
    "RC6000",
    "RC6000/DISK",
    "RC700",
    "RC700/COMAL",
    "RC700/HW",
    "RC7100",
    "RC750",
    "RC750/HW",
    "RC750/DISK",
    "RC759/HW",
    "RC759",
    "RC8000/DISK",
    "RC8000/HW",
    "RC8000/OU-BIBLIOTEK",
    "RC8000/PAPERTAPE",
    "RC8000/SALG",
    "RC8000/TEST",
    "RC8000/TAPE",
    "RC9000",
    "RC850",
    "RC850/CPM",
    "RC900",
    "RC911",
    "SDC/COMPANY",
    "SDC/BALLERUP",
    "SDC/FILIALER",
    "SDC/HARDWARE",
    "SDC/LEGAL",
    "SDC/PRESS",
    "SDC/STAFF",
    "SDC/TP1",
    "SDC/TP2",
    "SDC/TP2½",
    "SDC/VESTERPORT",
    "SDC/ÅRHUS",
    "SINCLAIR/ZX80",
    "SOCIETY",
    "STORAGE",
    "SUPERCOMPUTING",
    "UNIX",
    "UNIX/DISK",
    "UNKNOWN/PAPERTAPE",
    "UNKNOWN/TAPE",
    "UNKNOWN/CHIP",
    "UX",
    "XXX",
])

for i in rcsl.RCSLS:
    KEYWORDS.add("/".join(["RCSL"] + i))

class KeywordField(EnumField):
    ''' We render keywords as links to the wiki index pages '''

    def validate(self):
        super().validate()
        for line in self.stanza:
            if line.text[1:] == "ARTIFACTS":
                if self.sect.Genstand.stanza is None:
                    line.complain('Has DDHF.Keywords "ARTIFACTS" but no DDHF.Genstand')

class GenstandField(Field):
    ''' Reference to REGBASE '''

    def validate(self):
        if not self.val.isascii() or not self.val.isdigit() or len(self.val) != 8:
            self.complain('Not a valid identifier')
        if self.val[0] != '1':
            self.complain('Not a valid artifact identifier')
        if not self.sect.has_keyword("ARTIFACTS"):
            self.stanza.stanza_line.complain('DDHF.Keywords lack "ARTIFACTS"')

class DDHF(Section):
    ''' DDHF section '''

    def build(self):
        self += KeywordField("Keyword", KEYWORDS, single=False, mandatory=True)
        self += GenstandField("Genstand")
        self += Field("Provenance", single=False)

    def has_keyword(self, key):
        ''' Check if we have a particular keyword '''
        return key in self.Keyword.val
