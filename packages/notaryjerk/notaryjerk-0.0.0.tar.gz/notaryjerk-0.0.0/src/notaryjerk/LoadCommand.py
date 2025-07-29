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


def _getInt(bytes, bigEndian=True):
    """parse bytes[:4] to integer"""
    return int.from_bytes(bytes[:4], "big" if bigEndian else "little")


def _getLong(bytes, bigEndian=True):
    """parse bytes[:8] to integer"""
    return int.from_bytes(bytes[:8], "big" if bigEndian else "little")


def _getString(data: bytes):
    """read a null-terminated string"""

    def readTo0(data):
        for b in data:
            if not b:
                break
            yield b

    return bytes(readTo0(data)).decode("utf-8", errors="replace")


def _makeVersion(version: int):
    """Construct a version number from an integer."""

    vx = version >> 16
    vy = (version >> 8) & 0xFF
    vz = version & 0xFF

    return "{}.{}.{}".format(vx, vy, vz)


_commands = {
    1: "SEGMENT",
    2: "SYMTAB",
    3: "SYMSEG",
    4: "THREAD",
    5: "UNIXTHREAD",
    6: "LOADFVMLIB",
    7: "IDFVMLIB",
    8: "IDENT",
    9: "FVMFILE",
    10: "PREPAGE",
    11: "DYSYMTAB",
    12: "LOAD_DYLIB",
    13: "ID_DYLIB",
    14: "LOAD_DYLINKER",
    15: "ID_DYLINKER",
    16: "PREBOUND_DYLIB",
    17: "ROUTINES",
    18: "SUB_FRAMEWORK",
    19: "SUB_UMBRELLA",
    20: "SUB_CLIENT",
    21: "SUB_LIBRARY",
    22: "TWOLEVEL_HINTS",
    23: "PREBIND_CKSUM",
    25: "SEGMENT_64",
    26: "ROUTINES_64",
    27: "UUID",
    29: "CODE_SIGNATURE",
    30: "SEGMENT_SPLIT_INFO",
    32: "LAZY_LOAD_DYLIB",
    33: "ENCRYPTION_INFO",
    34: "DYLD_INFO",
    36: "VERSION_MIN_MACOSX",
    37: "VERSION_MIN_IPHONEOS",
    38: "FUNCTION_STARTS",
    39: "DYLD_ENVIRONMENT",
    41: "DATA_IN_CODE",
    42: "SOURCE_VERSION",
    43: "DYLIB_CODE_SIGN_DRS",
    44: "ENCRYPTION_INFO_64",
    45: "LINKER_OPTION",
    46: "LINKER_OPTIMIZATION_HINT",
    47: "VERSION_MIN_TVOS",
    48: "VERSION_MIN_WATCHOS",
    49: "NOTE",
    50: "BUILD_VERSION",
    0x80000000 + 24: "LOAD_WEAK_DYLIB",
    0x80000000 + 28: "RPATH",
    0x80000000 + 31: "REEXPORT_DYLIB",
    0x80000000 + 34: "DYLD_INFO_ONLY",
    0x80000000 + 35: "LOAD_UPWARD_DYLIB",
    0x80000000 + 40: "MAIN",
}


def get_loadcmd(loadcmd):
    """returns the name of the <loadcmd> (or the id if given a string);
    returns None if there's no such loadcmd"""
    if loadcmd in _commands:
        return _commands[loadcmd]
    try:
        return next(key for key, value in _commands.items() if value == loadcmd)
    except StopIteration:
        # raise KeyError(loadcmd)
        return None


def get_classes():
    """returns a list of all known LoadCommand classes"""

    def is_subclass(c, parent):
        try:
            return issubclass(c, parent) and not c == parent
        except TypeError:
            return False

    return [_ for _ in globals().values() if is_subclass(_, LoadCommand)]


def get_class(loadcmd):
    """returns the class for the given loadcmd, or None if there's no such loadcmd"""
    if type(loadcmd) is str:
        loadcmd = get_loadcmd(loadcmd)
    try:
        loadcmd = _commands[loadcmd]
    except KeyError:
        return None

    cls = [_ for _ in get_classes() if _._type == loadcmd]
    if cls:
        return cls[0]


class LoadCommand:
    """describe a single LoadCommand in a Mach-O binary, possibly consisting of multiple sections"""

    _type = None

    def __init__(self, macho, offset):
        """Create a LoadCommand"""
        (cmd, cmdsize) = getcmd(macho, offset, macho._isBIG)
        scmd = _commands.get(cmd)
        if scmd != type(self)._type:
            raise ValueError("%s cannot create %s" % (scmd, type(self).__name__))

        self._cmd = cmd
        self._cmdsize = cmdsize
        self._cmddata = macho._data[offset : offset + cmdsize]
        self._isBIG = macho._isBIG
        try:
            bar = type(self).__init__
        except AttributeError:
            bar = None
        if bar is None or bar is LoadCommand.__init__:
            print("!LoadCommand: %s [%d]" % (type(self).__name__, self._cmdsize))
        else:
            print("LoadCommand: %s" % (type(self).__name__,))


class Segment(LoadCommand):
    """LoadCommand 'SEGMENT'"""

    _type = "SEGMENT"


class Symtab(LoadCommand):
    """LoadCommand 'SYMTAB'"""

    _type = "SYMTAB"


class Symseg(LoadCommand):
    """LoadCommand 'SYMSEG'"""

    _type = "SYMSEG"


class Thread(LoadCommand):
    """LoadCommand 'THREAD'"""

    _type = "THREAD"


class Unixthread(Thread):
    """LoadCommand 'UNIXTHREAD'"""

    _type = "UNIXTHREAD"


class Loadfvmlib(LoadCommand):
    """LoadCommand 'LOADFVMLIB'"""

    _type = "LOADFVMLIB"


class Idfvmlib(Loadfvmlib):
    """LoadCommand 'IDFVMLIB'"""

    _type = "IDFVMLIB"


class Ident(LoadCommand):
    """LoadCommand 'IDENT'"""

    _type = "IDENT"


class Fvmfile(LoadCommand):
    """LoadCommand 'FVMFILE'"""

    _type = "FVMFILE"


class Prepage(LoadCommand):
    """LoadCommand 'PREPAGE'"""

    _type = "PREPAGE"


class Dysymtab(LoadCommand):
    """LoadCommand 'DYSYMTAB'"""

    _type = "DYSYMTAB"


class LoadDylib(LoadCommand):
    """LoadCommand 'LOAD_DYLIB'"""

    _type = "LOAD_DYLIB"

    def __init__(self, macho, offset):
        """create a LOAD_DYLIB from the MachO-object at offset"""
        super().__init__(macho, offset)
        name_offset = _getInt(self._cmddata[8:], self._isBIG)
        self._timestamp = _getInt(self._cmddata[12:], self._isBIG)
        self._current_version = _getInt(self._cmddata[16:], self._isBIG)
        self._compat_version = _getInt(self._cmddata[20:], self._isBIG)
        self._name = _getString(self._cmddata[name_offset:])

    @property
    def timestamp(self):
        from datetime import datetime

        return datetime.fromtimestamp(self._timestamp)

    @property
    def compatibility_version(self):
        return _makeVersion(self._compat_version)

    @property
    def current_version(self):
        return _makeVersion(self._current_version)

    @property
    def name(self):
        return self._name

    def __str__(self):
        return "<%s name=%s timestamp=%s current_version=%s compat_version=%s>" % (
            type(self).__name__,
            self.name,
            self.timestamp,
            self.current_version,
            self.compatibility_version,
        )


class IdDylib(LoadDylib):
    """LoadCommand 'ID_DYLIB'"""

    _type = "ID_DYLIB"


class LoadDylinker(LoadCommand):
    """LoadCommand 'LOAD_DYLINKER'"""

    _type = "LOAD_DYLINKER"

    def __init__(self, macho, offset):
        """create a LOAD_DYLINKER from the MachO-object at offset"""
        super().__init__(macho, offset)

        name_offset = _getInt(self._cmddata[8:], self._isBIG)
        self._name = _getString(self._cmddata[name_offset:])

    @property
    def name(self):
        return self._name

    def __str__(self):
        return "<%s name=%s>" % (type(self).__name__, self.name)


class IdDylinker(LoadDylinker):
    """LoadCommand 'ID_DYLINKER'"""

    _type = "ID_DYLINKER"


class PreboundDylib(LoadCommand):
    """LoadCommand 'PREBOUND_DYLIB'"""

    _type = "PREBOUND_DYLIB"


class Routines(LoadCommand):
    """LoadCommand 'ROUTINES'"""

    _type = "ROUTINES"


class SubFramework(LoadCommand):
    """LoadCommand 'SUB_FRAMEWORK'"""

    _type = "SUB_FRAMEWORK"


class SubUmbrella(SubFramework):
    """LoadCommand 'SUB_UMBRELLA'"""

    _type = "SUB_UMBRELLA"


class SubClient(SubFramework):
    """LoadCommand 'SUB_CLIENT'"""

    _type = "SUB_CLIENT"


class SubLibrary(SubFramework):
    """LoadCommand 'SUB_LIBRARY'"""

    _type = "SUB_LIBRARY"


class TwolevelHints(LoadCommand):
    """LoadCommand 'TWOLEVEL_HINTS'"""

    _type = "TWOLEVEL_HINTS"


class PrebindCksum(LoadCommand):
    """LoadCommand 'PREBIND_CKSUM'"""

    _type = "PREBIND_CKSUM"


class Segment64(Segment):
    """LoadCommand 'SEGMENT_64'"""

    _type = "SEGMENT_64"


class Routines64(Routines):
    """LoadCommand 'ROUTINES_64'"""

    _type = "ROUTINES_64"


class Uuid(LoadCommand):
    """LoadCommand 'UUID'"""

    _type = "UUID"

    def __init__(self, macho, offset):
        """create a UUID from the MachO-object at offset"""
        super().__init__(macho, offset)
        self._uuid = self._cmddata[8:24]

    @property
    def uuid(self):
        from uuid import UUID

        if self._isBIG:
            fmt = ">16s"
        else:
            fmt = "<16s"
        return UUID(bytes=self._uuid)

    def __str__(self):
        return "<%s UUID=%s>" % (type(self).__name__, self.uuid)


class CodeSignature(LoadCommand):
    """LoadCommand 'CODE_SIGNATURE'"""

    _type = "CODE_SIGNATURE"


class SegmentSplitInfo(CodeSignature):
    """LoadCommand 'SEGMENT_SPLIT_INFO'"""

    _type = "SEGMENT_SPLIT_INFO"


class LazyLoadDylib(LoadDylib):
    """LoadCommand 'LAZY_LOAD_DYLIB'"""

    _type = "LAZY_LOAD_DYLIB"


class EncryptionInfo(LoadCommand):
    """LoadCommand 'ENCRYPTION_INFO'"""

    _type = "ENCRYPTION_INFO"


class DyldInfo(LoadCommand):
    """LoadCommand 'DYLD_INFO'"""

    _type = "DYLD_INFO"


class VersionMinMacosx(LoadCommand):
    """LoadCommand 'VERSION_MIN_MACOSX'"""

    _type = "VERSION_MIN_MACOSX"

    def __init__(self, macho, offset):
        """create a VERSION_MIN_MACOSX from the MachO-object at offset"""
        super().__init__(macho, offset)
        self._version = _getInt(self._cmddata[8:])
        self._sdk = _getInt(self._cmddata[12:])

    @property
    def version(self):
        return _makeVersion(self._version)

    @property
    def sdk(self):
        return _makeVersion(self._sdk)

    def __str__(self):
        return "<%s version=%s, sdk=%s>" % (type(self).__name__, self.version, self.sdk)


class VersionMinIphoneos(VersionMinMacosx):
    """LoadCommand 'VERSION_MIN_IPHONEOS'"""

    _type = "VERSION_MIN_IPHONEOS"


class FunctionStarts(CodeSignature):
    """LoadCommand 'FUNCTION_STARTS'"""

    _type = "FUNCTION_STARTS"


class DyldEnvironment(LoadDylinker):
    """LoadCommand 'DYLD_ENVIRONMENT'"""

    _type = "DYLD_ENVIRONMENT"


class DataInCode(CodeSignature):
    """LoadCommand 'DATA_IN_CODE'"""

    _type = "DATA_IN_CODE"


class SourceVersion(LoadCommand):
    """LoadCommand 'SOURCE_VERSION'"""

    _type = "SOURCE_VERSION"

    def __init__(self, macho, offset):
        """create a BUILD_VERSION from the MachO-object at offset"""
        super().__init__(macho, offset)
        self._version = _getLong(self._cmddata[8:])

    @property
    def version(self):
        version = self._version
        mask = 0b1111111111  # 10 bit mask for B, C, D, and E

        a = version >> 40
        b = (version >> 30) & mask
        c = (version >> 20) & mask
        d = (version >> 10) & mask
        e = version & mask
        return "{}.{}.{}.{}.{}".format(a, b, c, d, e)

    def __str__(self):
        return "<%s version=%s>" % (type(self).__name__, self.version)


class DylibCodeSignDrs(CodeSignature):
    """LoadCommand 'DYLIB_CODE_SIGN_DRS'"""

    _type = "DYLIB_CODE_SIGN_DRS"


class EncryptionInfo64(EncryptionInfo):
    """LoadCommand 'ENCRYPTION_INFO_64'"""

    _type = "ENCRYPTION_INFO_64"


class LinkerOption(LoadCommand):
    """LoadCommand 'LINKER_OPTION'"""

    _type = "LINKER_OPTION"


class LinkerOptimizationHint(CodeSignature):
    """LoadCommand 'LINKER_OPTIMIZATION_HINT'"""

    _type = "LINKER_OPTIMIZATION_HINT"


class VersionMinTvos(VersionMinMacosx):
    """LoadCommand 'VERSION_MIN_TVOS'"""

    _type = "VERSION_MIN_TVOS"


class VersionMinWatchos(VersionMinMacosx):
    """LoadCommand 'VERSION_MIN_WATCHOS'"""

    _type = "VERSION_MIN_WATCHOS"


class Note(LoadCommand):
    """LoadCommand 'NOTE'"""

    _type = "NOTE"


class BuildVersion(LoadCommand):
    """LoadCommand 'BUILD_VERSION'"""

    _type = "BUILD_VERSION"

    _platforms = {
        1: "macos",
        2: "ios",
        3: "tvos",
        4: "watchos",
    }

    _tools = {1: "clang", 2: "swift", 3: "ld"}

    def __init__(self, macho, offset):
        """create a BUILD_VERSION from the MachO-object at offset"""
        super().__init__(macho, offset)
        self._platform = _getInt(self._cmddata[8:], self._isBIG)
        self._minos = _getInt(self._cmddata[12:], self._isBIG)
        self._sdk = _getInt(self._cmddata[16:], self._isBIG)
        ntools = _getInt(self._cmddata[20:], self._isBIG)

        # throw an error if this is an unknown platform
        plat = BuildVersion._platforms[self._platform]

        tools = []
        for t in range(ntools):
            off = 24 + t * 8
            tool = _getInt(self._cmddata[off:], self._isBIG)
            version = _getInt(self._cmddata[off + 4 :], self._isBIG)
            # throw an error if this is an unknown tool
            toolname = BuildVersion._tools[tool]
            tools.append((tool, version))
        self._tools = tools

    @property
    def platform(self):
        return BuildVersion._platforms[self._platform]

    @property
    def minOS(self):
        return _makeVersion(self._minos)

    @property
    def sdk(self):
        return _makeVersion(self._sdk)

    @property
    def tools(self):
        return [(BuildVersion._tools[t], _makeVersion(v)) for t, v in self._tools]

    def __str__(self):
        return "<%s platform=%s, minOS=%s SDK=%s tools=%s>" % (
            type(self).__name__,
            self.platform,
            self.minOS,
            self.sdk,
            self.tools,
        )


class LoadWeakDylib(LoadDylib):
    """LoadCommand 'LOAD_WEAK_DYLIB'"""

    _type = "LOAD_WEAK_DYLIB"


class Rpath(LoadCommand):
    """LoadCommand 'RPATH'"""

    _type = "RPATH"


class ReexportDylib(LoadDylib):
    """LoadCommand 'REEXPORT_DYLIB'"""

    _type = "REEXPORT_DYLIB"


class DyldInfoOnly(DyldInfo):
    """LoadCommand 'DYLD_INFO_ONLY'"""

    _type = "DYLD_INFO_ONLY"


class LoadUpwardDylib(LoadDylib):
    """LoadCommand 'LOAD_UPWARD_DYLIB'"""

    _type = "LOAD_UPWARD_DYLIB"


class Main(LoadCommand):
    """LoadCommand 'MAIN'"""

    _type = "MAIN"

    def __init__(self, macho, offset):
        """create a BUILD_VERSION from the MachO-object at offset"""
        super().__init__(macho, offset)
        self._entryoff = _getInt(self._cmddata[8:], self._isBIG)
        self._stacksize = _getInt(self._cmddata[12:], self._isBIG)

    @property
    def entry_offset(self):
        return self._entryoff

    @property
    def stacksize(self):
        return self._stacksize

    def __str__(self):
        return "<%s entry_offset=%s, stacksize=%s>" % (
            type(self).__name__,
            self.entry_offset,
            self.stacksize,
        )


def parse(macho, offset, bigEndian=None):
    """parses macho[offset:] to create a LoadCommand"""
    if bigEndian is None:
        bigEndian = macho._isBIG
    data = macho._data

    def is_subclass(c, parent):
        try:
            return issubclass(c, parent) and not c == parent
        except TypeError:
            return False

    (cmd, size) = getcmd(macho, offset, bigEndian)

    lc_classes = [_ for _ in globals().values() if is_subclass(_, LoadCommand)]
    lc_class = [_ for _ in lc_classes if _._type == _commands.get(cmd)]
    if not lc_class:
        print("unimplemented LoadCommand[%d] %s" % (cmd, _commands.get(cmd)))
        return None
    return lc_class[0](macho, offset)


def getcmd(macho, offset, bigEndian):
    """get (cmd,size) tuple for the LoadCommand at macho[offset:]"""
    data = macho._data
    return (
        _getInt(data[offset : offset + 4], bigEndian),
        _getInt(data[offset + 4 : offset + 8], bigEndian),
    )


def _test():
    from collections import Counter

    def _print_cmd(cmd):
        print("\tloadcmd[%s] %s" % (cmd, get_loadcmd(cmd)))

    classes = get_classes()

    # print all classes
    print("LoadCommand classes:")
    for c in classes:
        print("\t%s\t%s" % (c._type, c))

    # check if the mapping works
    print("get_loadcmd")
    _print_cmd("UUID")
    _print_cmd(27)
    _print_cmd("illegal")

    # check if we don't have any duplicate loadcmd names
    dupes = [k for k, v in Counter(_commands.values()).items() if v > 1]
    if dupes:
        print("duplicate LoadCommand names")
        for d in dupes:
            print("\t%s" % (d,))

    # check if there are no two classes with the same loadcmd
    dupecount = {}
    for c in classes:
        x = dupecount.get(c._type, [])
        x.append(c)
        dupecount[c._type] = x
    dupes = {k: v for k, v in dupecount.items() if len(v) > 1}
    if dupes:
        print("duplicate LoadCommand classes")
        for d in dupes:
            print("\t%s\t%s" % (d, ", ".join(_.__name__ for _ in dupes[d])))

    # check how many loadcommands are missing
    implemented = {c._type for c in classes}
    known = {_ for _ in _commands.values()}
    unimplemented = known.difference(implemented)
    if unimplemented:
        print("missing LoadCommand classes")
        for c in unimplemented:
            print("\t%s" % (c,))

    # check order of classes
    known = [_ for _ in _commands.values()]
    implemented = [c._type for c in classes]
    for k, i in zip(known, implemented):
        if k != i:
            print("out-of-order: %s" % (i,))

    # check how many loadcommands are missing
    existing = {c._type for c in classes}
    implemented = {c._type for c in classes if c.__init__ != LoadCommand.__init__}
    unimplemented = existing.difference(implemented)
    if unimplemented:
        print(
            "partly implemented LoadCommand classes (%d vs %d)"
            % (len(implemented), len(unimplemented))
        )
        for c in unimplemented:
            print("\t%s" % (c,))


if __name__ == "__main__":
    _test()
