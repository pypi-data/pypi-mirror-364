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
import os
import plistlib

_log = logging.getLogger()


def _readonly(self, *args, **kwargs):
    raise RuntimeError("Cannot modify ReadOnlyDict")


class ReadOnlyDict(dict):
    __setitem__ = _readonly
    __delitem__ = _readonly
    pop = _readonly
    popitem = _readonly
    clear = _readonly
    update = _readonly
    setdefault = _readonly


class Bundle:
    """extract various information from a bundle"""

    types = {
        "APPL": "Application",
        "FMWK": "Framework",
        "AAPL": "??",
        "BNDL": "Bundle",
        "BRPL": "plug-in",  ## which one?
        "CCLB": "??",  # sonoma shows these as ordinary 'Folder'
        "KEXT": "Kernel Extension",
        "WBPL": "Web Plugin",
        "XPC!": "XPC Service",
        "thng": "?? QuickTime component",
    }
    extensions = {
        "APPL": ".app",
        "BNDL": None,  # often '.bundle', but others are valid as well
        "CCLB": ".cclb",
        "FMWK": ".framework",
        "KEXT": ".kext",
        "XPC!": ".xpc",
    }

    def __init__(self, path):
        self._type = None
        self._executable = None
        self._info_plist = None

        # the Info.plist file location depends on the bundle type
        # - Application: Contents/Info.plist
        # - Framework  : Versions/Current/Resources/Info.plist
        # - others     : ?
        # - "AAPL" (??): "Contents/Info.plist"
        # - "APPL" (Application): "Contents/Info.plist"
        # - "BNDL" (Bundle): "Contents/Info.plist"
        # - "BRPL" (??): "Contents/Info.plist"
        # - "CCLB" (??): "Contents/Info.plist"
        # - "FMWK" (Framework): "Versions/Current/Resources/Info.plist"
        # - "KEXT" (Kernel Extension): "Contents/Info.plist"
        # - "WBPL" (Web Plugin): "Contents/Info.plist"
        # - "XPC!" (XPC Service?): "Contents/Info.plist"
        # - "thng" (?? QuickTime component): "Contents/Info.plist"

        # however, we just try them all
        info_plist = os.path.join(
            path, "Versions", "Current", "Resources", "Info.plist"
        )
        if not os.path.exists(info_plist):
            info_plist = os.path.join(path, "Contents", "Info.plist")
        try:
            with open(info_plist, "rb") as f:
                info = plistlib.load(f)
        except:
            raise ValueError("%r is not a NeXTSTEP/macOS Bundle" % path)

        self._info_plist = info_plist
        self._info = info

        self._type = info.get("CFBundlePackageType")
        self._exe = info.get("CFBundleExecutable")

        if self._type not in self.types:
            log.info("Unknown bundle type '%s'...proceeding anyhow" % (self._type,))

        # CFBundlePackageType can be:
        # - "" (??): ?
        # - "AAPL" (??): ?
        # - "APPL" (Application): "MacOS"/info["CFBundleExecutable"]
        # - "BNDL" (Bundle):
        # - "BRPL" (??): ?
        # - "CCLB" (??): ?
        # - "FMWK" (Framework): info["CFBundleExecutable"] -> "Versions"/"Current"/info["CFBundleExecutable"]
        # - "KEXT" (Kernel Extension)
        # - "WBPL" (??): ?
        # - "XPC!" (??): ?
        # - "thng" (??): ?

        if self._type == "APPL":
            self._executable = os.path.join(path, "Contents", "MacOS", self._exe)
        elif self._type == "FMWK":
            self._executable = os.path.join(path, "Versions, Current", self._exe)
        else:
            # ???
            pass

        if self._executable is not None and not os.path.exists(self._executable):
            self._executable = None

    @property
    def type(self):
        return self._type

    @property
    def executable(self):
        """get the full path to the bundle's main executable (if any)"""
        return self._executable

    @property
    def info_plist(self):
        """get the full path to the bundle's info.plist file"""
        return self._info_plist

    @property
    def info(self):
        """get the contents of the bundle's info.plist file as a read-only dictionary"""
        return ReadOnlyDict(self._info)


def _main():
    import sys

    for f in sys.argv[1:]:
        try:
            b = Bundle(f)
            print("%r - '%s' (%s)" % (f, b.type, (b.types.get(b.type, "unknown"))))
            print("\tinfo_plist=%r" % (b.info_plist))
            print("\texecutable=%r" % (b.executable))
            print("\tinfo=%r" % (b.info))
        except ValueError as e:
            _log.error(e)


if __name__ == "__main__":
    _main()
