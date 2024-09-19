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

KEYWORDS = {
    "ABC80": "FACIT ABC80",
    "ALGOL": "The ALGOL Programming Language",
    "AMIGA": "Commodore Amiga computer",
    "ANALOG_COMPUTING": "Analog/Mixed Computing",
    "ARTIFACTS": "Relating to physical artifacts",
    "B&O": "Bang&Olufsen",
    "B&O/DOCS": "",
    "B&O/SW": "",
    "BESK/PHOTOS": "",
    "C64": "Commodore C=64 computer",
    "CALCULATORS": "",
    "CBM900": "Commodore C900 (Unix) Prototype",
    "COMAL": "The COMAL Programming Language",
    "COMAL/RC3600": "",
    "COMAL/RC700": "",
    "COMAL/Z80": "",
    "COMPANY/AMSTRAD/CPC": "",
    "COMPANY/ANJA_DATA": "",
    "COMPANY/APPLE/II": "",
    "COMPANY/ATARI/ST": "",
    "COMPANY/ATP": "",
    "COMPANY/AT_T": "",
    "COMPANY/BOGIKA": "",
    "COMPANY/BOGIKA/BUTLER": "",
    "COMPANY/BONDWELL": "",
    "COMPANY/BORLAND": "",
    "COMPANY/BULL": "",
    "COMPANY/BURROUGHS": "",
    "COMPANY/BØRGE_PEDERSEN": "",
    "COMPANY/CIRCUIT_DESIGN": "",
    "COMPANY/COMMODORE": "",
    "COMPANY/CONTEX": "",
    "COMPANY/CORTEX_SYSTEMS": "",
    "COMPANY/CYBERCITY": "",
    "COMPANY/DAMGAARD": "",
    "COMPANY/DANLINE": "",
    "COMPANY/DANSK_SELSKAB_FOR_DATALOGI": "",
    "COMPANY/DATACENTRALEN": "",
    "COMPANY/DATACO": "",
    "COMPANY/DATAPOINT": "",
    "COMPANY/DATA_GENERAL": "",
    "COMPANY/DATA_GENERAL/NOVA": "",
    "COMPANY/DATA_INFORM": "",
    "COMPANY/DC": "",
    "COMPANY/DDC": "",
    "COMPANY/DEC/MARKETING": "",
    "COMPANY/DEC/VAX": "",
    "COMPANY/DSB": "",
    "COMPANY/DSI": "",
    "COMPANY/ELLIOTT_AUTOMATION": "",
    "COMPANY/ERICSSON/STEP-ONE": "",
    "COMPANY/FACIT": "",
    "COMPANY/FACIT/ABC80": "",
    "COMPANY/FACIT/TWIST": "",
    "COMPANY/FAG": "",
    "COMPANY/FLÅDEN": "",
    "COMPANY/FOUR_PHASE": "",
    "COMPANY/GNT": "",
    "COMPANY/GRUNDY/NEWBRAIN": "",
    "COMPANY/GYLDENDAL/SCANDIS": "",
    "COMPANY/HALDOR_TOPSØE": "",
    "COMPANY/HCØ": "H.C.Ørsteds Institutted på KU.",
    "COMPANY/HERA-DATA": "",
    "COMPANY/HP/120": "",
    "COMPANY/HP/150": "",
    "COMPANY/HS_MØLLER": "",
    "COMPANY/HT": "",
    "COMPANY/IBM": "",
    "COMPANY/IBM/3270": "",
    "COMPANY/IBM/3340": "",
    "COMPANY/IBM/3410": "",
    "COMPANY/IBM/3740": "",
    "COMPANY/IBM/OS2": "",
    "COMPANY/IBM/SYSTEM3": "",
    "COMPANY/ICL/COMET": "",
    "COMPANY/ICL/COMET/TAPE": "",
    "COMPANY/INTEL/ISIS": "Intel ISIS udviklingssystem",
    "COMPANY/JDC": "",
    "COMPANY/JDC/Q1": "",
    "COMPANY/JTAS": "",
    "COMPANY/JYSKE_BANK": "",
    "COMPANY/KTAS": "",
    "COMPANY/KVIK_DATA": "",
    "COMPANY/LAMBDA/8300": "",
    "COMPANY/LEC": "",
    "COMPANY/LFU": "",
    "COMPANY/LINK_DATA": "",
    "COMPANY/MABUSE_DATA": "",
    "COMPANY/METANIC": "",
    "COMPANY/MIAC": "",
    "COMPANY/MICROPRO": "",
    "COMPANY/MICROSOFT": "",
    "COMPANY/MIDAS": "",
    "COMPANY/MIKRO_VÆRKSTEDET": "",
    "COMPANY/NAVISION": "",
    "COMPANY/NCR/DMV": "",
    "COMPANY/NCR/DMV/CPM-80": "",
    "COMPANY/NCR/DMV/CPM-86": "",
    "COMPANY/NCR/DMV/MS-DOS": "",
    "COMPANY/NEUCC": "",
    "COMPANY/NIXDORF": "",
    "COMPANY/NORDJYSK_EDB_CENTER": "",
    "COMPANY/NORDU": "",
    "COMPANY/NORSK_DATA": "",
    "COMPANY/NORSK_DATA/DISK": "",
    "COMPANY/NORSK_DATA/DOCS": "",
    "COMPANY/ODENSE_UNI": "",
    "COMPANY/OLICOM": "",
    "COMPANY/OLIVETTI/M20": "",
    "COMPANY/OSBORNE": "",
    "COMPANY/OSM/ZEUS": "",
    "COMPANY/PBS": "",
    "COMPANY/PHILIPS": "",
    "COMPANY/POLYDATA": "",
    "COMPANY/PRESSPLAY": "",
    "COMPANY/RECAU": "",
    "COMPANY/RISØ": "",
    "COMPANY/SAMFUNDSDATA": "",
    "COMPANY/SAS": "",
    "COMPANY/SC-METRIC": "",
    "COMPANY/SC-METRIC/8": "",
    "COMPANY/SC-METRIC/MICROMUX": "",
    "COMPANY/SCAN-NOTE": "",
    "COMPANY/SCANDINAVIAN_SOFTWARE": "",
    "COMPANY/SDC": "",
    "COMPANY/SGI/DISK": "",
    "COMPANY/SILVERROCK": "",
    "COMPANY/SINCLAIR": "",
    "COMPANY/SOEKRIS": "",
    "COMPANY/SWTPC": "",
    "COMPANY/SYSTIME": "",
    "COMPANY/TATUNG/TPC2000": "",
    "COMPANY/TJÆREBORG": "",
    "COMPANY/TOSHIBA/T1100": "",
    "COMPANY/UNICOMAL": "",
    "COMPANY/UNIFORUM": "",
    "COMPANY/UNIGRAM_X": "",
    "COMPANY/UV-DATATEKET": "",
    "COMPANY/VEGA_DATA": "",
    "COMPANY/VESTKRAFT": "",
    "COMPANY/VP": "",
    "COMPANY/ZILOG": "",
    "COMPANY/ÅLBORG_UNI": "",
    "COMPANY/ØK_DATA": "",
    "CPR": "",
    "CR": "",
    "CR/CR16": "",
    "CR/CR5": "",
    "CR/CR7": "",
    "CR/CR8": "",
    "CR/CR80/DOCS": "",
    "CR/CR80/SW": "",
    "CR/FIKS": "",
    "CR/INTERNT": "",
    "CR/MARKETING": "",
    "CR/TAPE": "",
    "CRYPTOGRAPHY": "",
    "DANKORT": "",
    "DASK": "",
    "DASK/DOCS": "",
    "DASK/LIBRARY": "",
    "DASK/PHOTOS": "",
    "DASK/SW": "Software & hulstrimler",
    "DATALOGI": "",
    "DATALÆRE": "",
    "DDE": "",
    "DDE/ID-7000": "",
    "DDE/INTERNT": "",
    "DDE/IPC-1": "",
    "DDE/MARKETING": "",
    "DDE/KURSUS": "",
    "DDE/SPC-1": "",
    "DDE/SUPERMAX": "",
    "DDE/SUPERMAX/DISK": "",
    "DDE/SUPERMAX/DOCS": "",
    "DDE/SUPERMAX/SW": "",
    "DDHF/DOCUMENTS": "Documents pertaining to artifacts",
    "DDHF/FORMALIA": "Formal documents of Datamuseum.dk ",
    "DDHF/HISTORY": "Historical events about Datamuseum.dk",
    "DDHF/MEDLEMSBLAD": "Datamuseum.dk's medlemsblad 'dask'",
    "DDHF/NYHEDSBREV": "Newsletters from Datamuseum.dk",
    "DKUUG": "",
    "DKUUG/DISKS": "",
    "DKUUG/EUROBSDCON": "",
    "DKUUG/EUUG": "",
    "EDUCATION": "",
    "EDUCATION/ASTRONOMY": "",
    "EDUCATION/CHEMISTRY": "",
    "EDUCATION/GEOGRAPHY": "",
    "EDUCATION/LANGUAGE": "",
    "EDUCATION/MATH": "",
    "EDUCATION/PHYSICS": "",
    "EVENT/COVER": "Cover art for Datamuseum.dk DVDs",
    "EVENT/PHOTOS": "Photos from events",
    "EVENT/SLIDES": "Presentation material from events",
    "EVENT/VIDEO": "Video recordings of events",
    "FORMIDLING": "",
    "GAMES": "",
    "GAMES/HUGO": "",
    "GIER": "",
    "GIER/ALGOL_4": "",
    "GIER/ALGOL_II": "",
    "GIER/ALGOL_III": "",
    "GIER/DEMO": "",
    "GIER/GAMES": "",
    "GIER/HELP": "",
    "GIER/HELP3": "",
    "GIER/HW": "",
    "GIER/MATHEMATICS": "",
    "GIER/MISC": "",
    "GIER/MUSIC": "",
    "GIER/OTHER_SCIENCE": "",
    "GIER/SCIENCE": "",
    "GIER/TEST": "",
    "GIER/UTIL": "",
    "GSL": "",
    "IMAGES": "",
    "IMAGES/DDHF": "",
    "IMAGES/OLDGALLERY": "",
    "IMAGES/SDC": "",
    "JAMES": "",
    "JET80": "",
    "LANGUAGES": "",
    "LANGUAGES/APL": "",
    "LANGUAGES/BASIC": "",
    "LANGUAGES/C": "",
    "LANGUAGES/COBOL": "",
    "LANGUAGES/FORTRAN": "",
    "LANGUAGES/MODULA-2": "",
    "LANGUAGES/PASCAL": "",
    "LANGUAGES/PROLOG": "",
    "LANGUAGES/RPG-II": "",
    "MUSIC": "",
    "NASCOM": "",
    "NEMID": "",
    "NETWORKS": "",
    "NETWORKS/INTERNET": "",
    "NETWORKS/PAXNET": "",
    "NETWORKS/TELEDATA": "",
    "OS/CONCURRENT-DOS": "",
    "OS/CPM-80": "",
    "OS/CPM-86": "",
    "OS/FLEX": "",
    "OS/FREEBSD": "",
    "OS/LINUX": "",
    "OS/MIK": "",
    "OS/MIKADOS": "",
    "OS/MS-DOS": "",
    "OS/MS-DOS/DRIVERS": "",
    "OS/UNIFLEX": "",
    "OS/UNIX/TRAINING": "",
    "OS/XDOS": "",
    "PERIODICALS/CIRCUIT": "",
    "PERIODICALS/DATALÆRE": "",
    "PERIODICALS/DKUUG-NYT": "",
    "PERIODICALS/EUROPEN": "",
    "PERIODICALS/EUUG-NEWSLETTER": "",
    "PERIODICALS/MCUG": "",
    "PERIODICALS/MIKRO": "",
    "PERIODICALS/NASCOM_NYT": "",
    "PERIODICALS/OPEN_INFORMATION_SYSTEMS": "",
    "PERIODICALS/PICCOLINIEN": "",
    "PERIODICALS/POPULÆR_ELEKTRONIK": "",
    "PERIODICALS/THE_BUSINESS_UNIX_JOURNAL": "",
    "PERIODICALS/THE_YATES_PERSPECTIVE": "",
    "PERIODICALS/U-NEWS": "",
    "PERIODICALS/UNIQUE": "",
    "PERIODICALS/UNIX_IN_THE_OFFICE": "",
    "PERIODICALS/UNIX_NEWS": "",
    "PERSONS": "",
    "PERSONS/AAGE_MELBYE": "",
    "PERSONS/BENT_SCHARØE_PETERSEN": "",
    "PERSONS/BENT_SCHARØE_PETERSEN/CORE_EXPERIMENTER": "",
    "PERSONS/BENT_SCHARØE_PETERSEN/PHOTOS": "",
    "PERSONS/CHARLES_SIMONYI": "",
    "PERSONS/JØRN_JENSEN": "",
    "PERSONS/KONRAD_ZUSE": "",
    "PERSONS/MOGENS_PELLE": "",
    "PERSONS/NIELS_IVAR_BECH": "",
    "PERSONS/PER_BRINCH_HANSEN": "",
    "PERSONS/PER_JACOBI": "",
    "PERSONS/PETER_NAUR": "",
    "PERSONS/RICHARD_PETERSEN": "",
    "PRECOMPUTING": "",
    "PROJECTS/AMANDA": "",
    "PROJECTS/DORA": "",
    "PROJECTS/NATURGAS": "",
    "PÆDAT": "Educational 16 bit computer",
    "RATIONAL_1000": "Rational R1000/s400 Ada Computer",
    "RATIONAL_1000/DISK": "",
    "RATIONAL_1000/DOCS": "",
    "RATIONAL_1000/DOCS/BETA": "",
    "RATIONAL_1000/DOCS/EPSILON": "",
    "RATIONAL_1000/DOCS/GAMMA": "",
    "RATIONAL_1000/DOCS/HW": "",
    "RATIONAL_1000/HW": "",
    "RATIONAL_1000/SW": "",
    "RATIONAL_1000/TAPE": "",
    "RC": "RegneCentralen",
    "RC/CPR11": "",
    "RC/INTERNT": "",
    "RC/MARKETING": "",
    "RC/PRESSCOVERAGE": "",
    "RC/RC1000": "",
    "RC/RC1700": "",
    "RC/RC2000": "",
    "RC/RC2100": "",
    "RC/RC2500": "",
    "RC/RC3000": "",
    "RC/RC3200": "",
    "RC/RC3500": "",
    "RC/RC3500/ALARMNET": "",
    "RC/RC3500/DOCS": "",
    "RC/RC3500/HW": "",
    "RC/RC3500/TAPE": "",
    "RC/RC3600": "",
    "RC/RC3600/COMAL": "",
    "RC/RC3600/DE2": "",
    "RC/RC3600/DISK": "",
    "RC/RC3600/DOMUS": "",
    "RC/RC3600/HW": "",
    "RC/RC3600/LOADER": "",
    "RC/RC3600/MUSIL": "",
    "RC/RC3600/PAPERTAPE": "",
    "RC/RC3600/SALG": "",
    "RC/RC3600/SW": "",
    "RC/RC3600/TEST": "",
    "RC/RC3600/UTIL": "",
    "RC/RC39": "",
    "RC/RC39/DISK": "",
    "RC/RC3900": "",
    "RC/RC4000": "",
    "RC/RC4000/GAMES": "",
    "RC/RC4000/HW": "",
    "RC/RC4000/MARKETING": "",
    "RC/RC4000/MATHEMATICS": "",
    "RC/RC4000/PULAWY": "",
    "RC/RC4000/SCIENCE": "",
    "RC/RC4000/SW": "",
    "RC/RC4000/TEST": "",
    "RC/RC45": "",
    "RC/RC5000": "",
    "RC/RC6000": "",
    "RC/RC6000/DISK": "",
    "RC/RC700": "",
    "RC/RC700/COMAL": "",
    "RC/RC700/HW": "",
    "RC/RC7000": "",
    "RC/RC7100": "",
    "RC/RC750": "",
    "RC/RC750/DISK": "",
    "RC/RC750/HW": "",
    "RC/RC759": "",
    "RC/RC759/HW": "",
    "RC/RC8000": "",
    "RC/RC8000/DISK": "",
    "RC/RC8000/HW": "",
    "RC/RC8000/OU-BIBLIOTEK": "",
    "RC/RC8000/PAPERTAPE": "",
    "RC/RC8000/SALG": "",
    "RC/RC8000/TAPE": "",
    "RC/RC8000/TEST": "",
    "RC/RC850": "",
    "RC/RC850/CPM": "",
    "RC/RC850/SW": "",
    "RC/RC890": "",
    "RC/RC900": "",
    "RC/RC9000": "",
    "RC/RC9000/DISK": "",
    "RC/RC911": "",
    "RC/RCNET": "",
    "RC/RCTELEDATA": "",
    "RC/RC_DISKETTE_1100": "",
    "RC/SERVICECENTRENE": "",
    "SCIENCE/ASTRONOMY": "",
    "SCIENCE/CHEMISTRY": "",
    "SCIENCE/PHYSICS": "",
    "SDC/BALLERUP": "",
    "SDC/COMPANY": "",
    "SDC/FILIALER": "",
    "SDC/HARDWARE": "",
    "SDC/LEGAL": "",
    "SDC/PRESS": "",
    "SDC/STAFF": "",
    "SDC/TP1": "",
    "SDC/TP2": "",
    "SDC/TP2½": "",
    "SDC/VESTERPORT": "",
    "SDC/ÅRHUS": "",
    "SELVBYG": "",
    "SINCLAIR/ZX80": "",
    "SMIL/PHOTOS": "",
    "SOCIETY": "",
    "STANDARD/DANSK_STANDARD": "",
    "STANDARD/PCCARD": "",
    "STORAGE": "",
    "SUPERCOMPUTING": "",
    "UNIX": "",
    "UNIX/DISK": "",
    "UNKNOWN/CHIP": "",
    "UNKNOWN/PAPERTAPE": "",
    "UNKNOWN/TAPE": "",
    "UX": "",
}

def main():
    for i, j in zip(KEYWORDS, sorted(KEYWORDS)):
        if i != j:
            print("Unsorted Keywords", i, j)
    return 2

if __name__ == "__main__":
    main()

for year in range(1958, 2025):
    KEYWORDS["EVENT/%4d" % year] = "Events in %d" % year

for i in rcsl.RCSLS:
    KEYWORDS["/".join(["RCSL"] + i)] = "Artifacts in this RCSL series"

class KeywordField(EnumField):
    ''' We render keywords as links to the wiki index pages '''

    def validate(self, **kwargs):
        for line in self.stanza:
            kw = line.text[1:]
            if kw not in self.legal_values:
                if not self.sect.metadata.keyword_proposals_allowed or kw[0] != '*':
                    yield self.complaint("Unknown DDHF.Keywords (%s)" % kw, where=line)
            if kw == "ARTIFACTS":
                if self.sect.Genstand.stanza is None:
                    yield self.complaint('Has DDHF.Keywords "ARTIFACTS" but no DDHF.Genstand', line)

class GenstandField(Field):
    ''' Reference to REGBASE '''

    def validate(self, **kwargs):
        yield from super().validate()
        if not self.val.isascii() or not self.val.isdigit() or len(self.val) != 8:
            yield self.complaint('Not a valid identifier')
        elif self.val[0] != '1':
            yield self.complaint('Not a valid artifact identifier')
        if not self.sect.has_keyword("ARTIFACTS"):
            yield self.complaint('DDHF.Keywords lack "ARTIFACTS"')

class PresentationField(Field):
    ''' Instructions for presentation facilities '''

    def validate(self, **kwargs):
        yield from super().validate()
        for line in self.stanza:
            fields = line.text.split(maxsplit=1)
            if fields[0] not in (
                "AA",
                "Gallery",
            ):
                yield self.complaint('DDHF.Presentation: Unknown presentor', line)

class DDHF(Section):
    ''' DDHF section '''

    def build(self):
        self += KeywordField("Keyword", KEYWORDS, single=False, mandatory=True)
        self += GenstandField("Genstand")
        self += Field("Provenance", single=False)
        self += PresentationField("Presentation", single=False)

    def has_keyword(self, key):
        ''' Check if we have a particular keyword '''
        return key in self.Keyword.val
