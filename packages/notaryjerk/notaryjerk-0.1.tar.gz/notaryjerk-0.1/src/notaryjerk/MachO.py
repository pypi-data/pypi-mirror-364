#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# notaryjerk -tools for codesigning, notarization,...
#
# Copyright © 2023, IOhannes m zmölnig, forum::für::umläute
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU Affero General Public License as
#  published by the Free Software Foundation, either version 3 of the
#  License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU Affero General Public License for more details.
#
#  You should have received a copy of the GNU Affero General Public License
#  along with this program.  If not, see <http://www.gnu.org/licenses/>.


import logging
import plistlib

import struct

try:
    from . import LoadCommand
except ImportError:
    import LoadCommand


_log = logging.getLogger("notaryjerk.MachO")


class MachO:
    """describe a single-architecture ("thin") Mach-O binary"""

    _magic = {
        0xFEEDFACE: (False, True),  # 32 bit, big endian
        0xFEEDFACF: (True, True),  # 64 bit, big endian
        0xCEFAEDFE: (False, False),  # 32 bit, little endian
        0xCFFAEDFE: (True, False),  # 64 bit, little endian
    }
    _flags = {
        0: "NOUNDEFS",
        1: "INCRLINK",
        2: "DYLDLINK",
        3: "BINDATLOAD",
        4: "PREBOUND",
        5: "SPLIT_SEGS",
        6: "LAZY_INIT",
        7: "TWOLEVEL",
        8: "FORCE_FLAT",
        9: "NOMULTIDEFS",
        10: "NOFIXPREBINDING",
        11: "PREBINDABLE",
        12: "ALLMODSBOUND",
        13: "SUBSECTIONS_VIA_SYMBOLS",
        14: "CANONICAL",
        15: "WEAK_DEFINES",
        16: "BINDS_TO_WEAK",
        17: "ALLOW_STACK_EXECUTION",
        18: "ROOT_SAFE",
        19: "SETUID_SAFE",
        20: "NOREEXPORTED_DYLIBS",
        21: "PIE",
        22: "DEAD_STRIPPABLE_DYLIB",
        23: "HAS_TLV_DESCRIPTORS",
        24: "NO_HEAP_EXECUTION",
        25: "APP_EXTENSION_SAFE",
    }
    # https://opensource.apple.com/source/cctools/cctools-973.0.1/include/mach/machine.h
    _cputypes = {
        -1: {None: "ANY", -1: "MULTIPLE", 0: "LITTLE_ENDIAN", 1: "BIG_ENDIAN"},
        1: {
            None: "VAX",
            -1: "MULTIPLE",
            0: "VAX_ALL",
            1: "VAX780",
            2: "VAX785",
            3: "VAX750",
            4: "VAX730",
            5: "UVAXI",
            6: "UVAXII",
            7: "VAX8200",
            8: "VAX8500",
            9: "VAX8600",
            10: "VAX8650",
            11: "VAX8800",
            12: "UVAXIII",
        },
        6: {
            None: "MC680x0",
            -1: "MULTIPLE",
            1: "MC680x0_ALL or MC68030",
            2: "MC68040",
            3: "MC68030_ONLY",
        },
        7: {
            None: "X86 (I386)",
            -1: "MULTIPLE",
            0: "INTEL_MODEL_ALL",
            3: "X86_ALL, X86_64_ALL, I386_ALL, or 386",
            4: "X86_ARCH1 or 486",
            5: "586 or PENT",
            8: "X86_64_H or PENTIUM_3",
            9: "PENTIUM_M",
            10: "PENTIUM_4",
            11: "ITANIUM",
            12: "XEON",
            15: "INTEL_FAMILY_MAX",
            22: "PENTPRO",
            24: "PENTIUM_3_M",
            26: "PENTIUM_4_M",
            27: "ITANIUM_2",
            28: "XEON_MP",
            40: "PENTIUM_3_XEON",
            54: "PENTII_M3",
            86: "PENTII_M5",
            103: "CELERON",
            119: "CELERON_MOBILE",
            132: "486SX",
        },
        10: {None: "MC98000", -1: "MULTIPLE", 0: "MC98000_ALL", 1: "MC98601"},
        11: {
            None: "HPPA",
            -1: "MULTIPLE",
            0: "HPPA_ALL or HPPA_7100",
            1: "HPPA_7100LC",
        },
        12: {
            None: "ARM",
            -1: "MULTIPLE",
            0: "ARM_ALL",
            1: "ARM_A500_ARCH",
            2: "ARM_A500",
            3: "ARM_A440",
            4: "ARM_M4",
            5: "ARM_V4T",
            6: "ARM_V6",
            7: "ARM_V5TEJ",
            8: "ARM_XSCALE",
            9: "ARM_V7",
            10: "ARM_V7F",
            11: "ARM_V7S",
            12: "ARM_V7K",
            13: "ARM_V8",
            14: "ARM_V6M",
            15: "ARM_V7M",
            16: "ARM_V7EM",
        },
        13: {
            None: "MC88000",
            -1: "MULTIPLE",
            0: "MC88000_ALL",
            1: "MMAX_JPC or MC88100",
            2: "MC88110",
        },
        14: {
            None: "SPARC",
            -1: "MULTIPLE",
            0: "SPARC_ALL or SUN4_ALL",
            1: "SUN4_260",
            2: "SUN4_110",
        },
        15: {None: "I860 (big-endian)", -1: "MULTIPLE", 0: "I860_ALL", 1: "I860_860"},
        18: {
            None: "POWERPC",
            -1: "MULTIPLE",
            0: "POWERPC_ALL",
            1: "POWERPC_601",
            2: "POWERPC_602",
            3: "POWERPC_603",
            4: "POWERPC_603e",
            5: "POWERPC_603ev",
            6: "POWERPC_604",
            7: "POWERPC_604e",
            8: "POWERPC_620",
            9: "POWERPC_750",
            10: "POWERPC_7400",
            11: "POWERPC_7450",
            100: "POWERPC_970",
        },
        0x1000000
        + 7: {
            None: "X86_64",
            -1: "MULTIPLE",
            0: "INTEL_MODEL_ALL",
            3: "X86_ALL, X86_64_ALL, I386_ALL, or 386",
            4: "X86_ARCH1 or 486",
            5: "586 or PENT",
            8: "X86_64_H or PENTIUM_3",
            9: "PENTIUM_M",
            10: "PENTIUM_4",
            11: "ITANIUM",
            12: "XEON",
            15: "INTEL_FAMILY_MAX",
            22: "PENTPRO",
            24: "PENTIUM_3_M",
            26: "PENTIUM_4_M",
            27: "ITANIUM_2",
            28: "XEON_MP",
            40: "PENTIUM_3_XEON",
            54: "PENTII_M3",
            86: "PENTII_M5",
            103: "CELERON",
            119: "CELERON_MOBILE",
            132: "486SX",
            0x80000000 + 0: "INTEL_MODEL_ALL (LIB64)",
            0x80000000 + 3: "X86_ALL, X86_64_ALL, I386_ALL, or 386 (LIB64)",
            0x80000000 + 4: "X86_ARCH1 or 486 (LIB64)",
            0x80000000 + 5: "586 or PENT (LIB64)",
            0x80000000 + 8: "X86_64_H or PENTIUM_3 (LIB64)",
            0x80000000 + 9: "PENTIUM_M (LIB64)",
            0x80000000 + 10: "PENTIUM_4 (LIB64)",
            0x80000000 + 11: "ITANIUM (LIB64)",
            0x80000000 + 12: "XEON (LIB64)",
            0x80000000 + 15: "INTEL_FAMILY_MAX (LIB64)",
            0x80000000 + 22: "PENTPRO (LIB64)",
            0x80000000 + 24: "PENTIUM_3_M (LIB64)",
            0x80000000 + 26: "PENTIUM_4_M (LIB64)",
            0x80000000 + 27: "ITANIUM_2 (LIB64)",
            0x80000000 + 28: "XEON_MP (LIB64)",
            0x80000000 + 40: "PENTIUM_3_XEON (LIB64)",
            0x80000000 + 54: "PENTII_M3 (LIB64)",
            0x80000000 + 86: "PENTII_M5 (LIB64)",
            0x80000000 + 103: "CELERON (LIB64)",
            0x80000000 + 119: "CELERON_MOBILE (LIB64)",
            0x80000000 + 132: "486SX (LIB64)",
        },
        0x1000000
        + 12: {
            None: "ARM64",
            -1: "MULTIPLE",
            0: "ARM64_ALL",
            1: "ARM64_V8",
            0x80000000 + 0: "ARM64_ALL",
            0x80000000 + 1: "ARM64_V8",
        },
        0x1000000
        + 18: {
            None: "POWERPC64",
            -1: "MULTIPLE",
            0: "POWERPC_ALL",
            1: "POWERPC_601",
            2: "POWERPC_602",
            3: "POWERPC_603",
            4: "POWERPC_603e",
            5: "POWERPC_603ev",
            6: "POWERPC_604",
            7: "POWERPC_604e",
            8: "POWERPC_620",
            9: "POWERPC_750",
            10: "POWERPC_7400",
            11: "POWERPC_7450",
            100: "POWERPC_970",
            0x80000000 + 0: "POWERPC_ALL (LIB64)",
            0x80000000 + 1: "POWERPC_601 (LIB64)",
            0x80000000 + 2: "POWERPC_602 (LIB64)",
            0x80000000 + 3: "POWERPC_603 (LIB64)",
            0x80000000 + 4: "POWERPC_603e (LIB64)",
            0x80000000 + 5: "POWERPC_603ev (LIB64)",
            0x80000000 + 6: "POWERPC_604 (LIB64)",
            0x80000000 + 7: "POWERPC_604e (LIB64)",
            0x80000000 + 8: "POWERPC_620 (LIB64)",
            0x80000000 + 9: "POWERPC_750 (LIB64)",
            0x80000000 + 10: "POWERPC_7400 (LIB64)",
            0x80000000 + 11: "POWERPC_7450 (LIB64)",
            0x80000000 + 100: "POWERPC_970 (LIB64)",
        },
    }

    def __init__(self, data: bytes):
        self._data = data

        magic = struct.unpack(">I", data[:4])[0]
        if magic not in MachO._magic:
            raise ValueError("not a Mach-O binary: %s" % data[:4])
        self._is64, self._isBIG = MachO._magic[magic]
        self._byteorder = ">" if self._isBIG else "<"
        (
            self._cpu_type,
            self._cpu_subtype,
            self._file_type,
            nlcs,
            slcs,
            self._flags,
        ) = struct.unpack(self._byteorder + "6I", data[4:28])
        offset = 28
        if self._is64:
            offset += 4

        self._loadcommands = []
        lc_totalsize = 0
        for n in range(nlcs):
            (cmd, cmdsize) = LoadCommand.getcmd(self, offset, self._isBIG)
            if self._is64 and cmdsize % 8:
                raise ValueError(
                    "Load command size %d for 64bit Mach-O at %d is not divisible by 8."
                    % (cmdsize, offset)
                )
            elif cmdsize % 4:
                raise ValueError(
                    "Load command size %d for 32bit Mach-O at %d is not divisible by 4."
                    % (cmdsize, offset)
                )

            lc = LoadCommand.parse(self, offset)
            lc_totalsize += cmdsize
            offset += cmdsize
            self._loadcommands.append(lc)
        if slcs != lc_totalsize:
            _log.error(
                "Expected LoadCommands with a total size of %d bytes, but needed %d bytes",
                slcs,
                lc_totalsize,
            )
        print(", ".join(str(_) for _ in self._loadcommands))

    def __bytes__(self):
        """get bytes() representation of Mach-O binary"""
        return self._data

    @property
    def flags(self):
        """get a symbolic representation of the Mach-O flags"""
        flags = self._flags
        return [
            MachO._flags.get(_, _)
            for _ in range(flags.bit_length())
            if 0x1 & (flags >> _)
        ]

    @property
    def cpu_type_raw(self):
        """get a tuple of (type, subtype) describing the CPU"""
        return (self._cpu_type, self._cpu_subtype)

    @property
    def cpu_type(self):
        """get a symbolic representation of the CPU type/subtype tuple"""
        unknown = "UNKNOWN"
        try:
            cpu = MachO._cputypes[self._cpu_type]
            return (cpu[None], cpu.get(self._cpu_subtype, unknown))
        except KeyError:
            return (unknown, unknown)

    @staticmethod
    def loads(b):
        """load a Mach-O binary from a bytes() object"""
        m = MachO(b)
        return m


class Universal:
    def __init__(self, machos: MachO, alignments: list = None):
        self._machos = machos
        self._alignments = alignments

    def __bytes__(self):
        """get bytes() representation of Universal binary"""

        def get_alignment(macho, defalign):
            """get alignment of macho (using defalign as default)"""
            data = bytes(macho)
            datalength = len(data)
            if not defalign:
                return datalength.bit_length()
            return defalign

        if len(self._machos) < 1:
            return b""
        if len(self._machos) == 1:
            # thin binary
            return bytes(self._machos[0])

        alignments = self._alignments
        if not alignments:
            alignments = [None] * len(self._machos)

        alignments = [get_alignment(m, a) for (m, a) in zip(self._machos, alignments)]

        header = struct.pack(">II", 0xCAFEBABE, len(self._machos))
        offset = (2 + len(self._machos) * 5) * 4

        data = bytearray(offset)

        machopos = []
        for m, a in zip(self._machos, alignments):
            mdata = bytes(m)
            # pad the startposition
            pagesize = 2**a
            mstart = pagesize * (1 + (len(data) - 1) // pagesize)

            data += bytearray(mstart - len(data))
            data += mdata

            (cpu_type, cpu_subtype) = m.cpu_type_raw
            header += struct.pack(">5I", cpu_type, cpu_subtype, mstart, len(mdata), a)

        data[: len(header)] = header

        return bytes(data)

    def __getitem__(self, key):
        """access the named (thin) Mach-O binary"""
        try:
            return self._machos[key]
        except IndexError as e:
            ex = IndexError(str(e))
        except:
            raise
        raise (ex)

    @staticmethod
    def load(fp):
        """load a Universal binary from a file-like object"""
        return Universal.loads(fp.read())

    @staticmethod
    def loads(b):
        """load a Universal binary from a bytes() object"""
        magic = struct.unpack(">I", b[:4])[0]
        if magic == 0xCAFEBABE:
            # universal
            machos = []
            n_machos = struct.unpack(">I", b[4:8])[0]
            macho_pos = [
                struct.unpack(">5I", b[8 + i * 20 : 8 + (i + 1) * 20])
                for i in range(n_machos)
            ]
            machos = [
                MachO.loads(b[offset : offset + size])
                for (cpu_type, cpu_subtype, offset, size, alignment) in macho_pos
            ]
            alignment = [
                alignment
                for (cpu_type, cpu_subtype, offset, size, alignment) in macho_pos
            ]
        else:
            machos = [MachO.loads(b)]
            alignment = None

        return Universal(machos, alignment)


def _main():
    import sys

    for fname in sys.argv[1:]:
        with open(fname, "rb") as f:
            u = Universal.load(f)
        print(u)
        with open("out.bin", "wb") as f:
            f.write(bytes(u))


if __name__ == "__main__":
    _main()
