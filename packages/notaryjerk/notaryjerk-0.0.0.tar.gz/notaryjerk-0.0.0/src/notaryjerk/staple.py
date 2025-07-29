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


import base64
import logging
import os
import plistlib
import re
import struct

import requests

try:
    from . import utilities
except ImportError:
    import utilities

_log = logging.getLogger()

# Apple API URL to retrieve tickets
ticket_url = "https://api.apple-cloudkit.com/database/1/com.apple.gk.ticket-delivery/production/public/records/lookup"

# if all goes well, the Apple Cloudkit API returns a JSON object with the following content:
#    {
#      "records": [
#        {
#          "recordName": str:recordName,
#          "recordType": "DeveloperIDTicket",
#          "fields": {
#            "signedTicket": {
#              "value": b64:ticket,
#              "type": "BYTES"
#            }
#          },
#          "pluginFields": {},
#          "recordChangeTag": str:recordChangeTag,
#          "created": {
#            "timestamp": int:secSincEepoch,
#            "userRecordName": str:userRecordName
#            "deviceID": "2"
#          },
#          "modified": {
#            "timestamp": int:secSinceEpoch,
#            "userRecordName": str:userRecordName
#            "deviceID": "2"
#          },
#          "deleted": false
#        }
#      ]
#    }
#
# recordName is like "2/2/c110d0633733b5893ec3a4804d2b9daceb98177c" (and the same as we passed)
# ticket is the base64 encoded ticket data
# recordChangeTag is like "lo5d1jwm"
# secSinceEpoch is like 1698214460428
# usrRecordName is like "_b133e60953755a92966d7ca08d9c731a"
#
#
# when requesting the ticket for an invalid cdhash, we get this JSON object instead (still with HTTP 200):
#    {
#      "recordName": str:recordName,
#      "reason": "Record not found",
#      "serverErrorCode": "NOT_FOUND"
#    }


def _extractEmbeddedPlists(filename):
    """extract embedded plist data sections from binary file"""
    # this is a very crude way to do it
    # LATER properly parse the macho file for the relevant sections (see 'macholibre')
    with open(filename, "rb") as f:
        data = f.read()
    try:
        return [
            plistlib.loads(_)
            for _ in re.findall(b"<plist.*?</plist>", data, flags=re.DOTALL)
        ]
    except:
        _log.warning("no embedded plists found", exc_info=True)
    return []


def _extractCDHashes(filename):
    """extract cdhashes from Mach-O binary
    the result is a list of lists of cdhashes
    - one list per arch in the Mach-O binary
    - additional cdhashes (per arch) might be SHA1-encoded or so

    the code tries hard to parse the Mach-O binary to get to the correct
    section that contains the cdhashes.
    if the asn1crypto module is missing, the actual blob is extracted without
    cryptographical checks.

    this code is based on https://github.com/aaronst/macholibre
    with some insights from https://blog.umangis.me/posts/a-deep-dive-into-ios-code-signing/
    and https://medium.com/csit-tech-blog/demystifying-ios-code-signature-309d52c2ff1d
    (as of 2023-11-15)
    """

    def blob2cdhashes_crypto(blobdata):
        from asn1crypto.cms import ContentInfo

        cdhashes = []
        signed_data = ContentInfo.load(blobdata)
        for sd in signed_data["content"]["signer_infos"]:
            sas = sd["signed_attrs"]
            for sa in sas:
                for s in sa[1]:
                    try:
                        result = plistlib.loads(s.parsed.contents)
                    except (AttributeError, ValueError, KeyError):
                        result = {}
                    cdhashes += result.get("cdhashes", [])
        return cdhashes

    def blob2cdhashes_raw(blobdata):
        import re

        cdhashes = []
        for raw in re.findall(b"<plist.*?</plist>", blobdata, flags=re.DOTALL):
            try:
                result = plistlib.loads(raw)
            except (AttributeError, ValueError, KeyError):
                result = {}
            cdhashes += result.get("cdhashes", [])
        return cdhashes

    def blob2cdhashes(blobdata):
        cdhashes = None
        for f in [blob2cdhashes_crypto, blob2cdhashes_raw]:
            try:
                cdhashes = f(blobdata)
                if cdhashes:
                    return cdhashes
            except:
                continue

    def parse_macho(f, offset, length):
        f.seek(offset)

        machos = {
            0xFEEDFACE: (False, False),  # 32 bit, big endian
            0xFEEDFACF: (True, False),  # 64 bit, big endian
            0xCEFAEDFE: (False, True),  # 32 bit, little endian
            0xCFFAEDFE: (True, True),  # 64 bit, little endian
        }
        cmd_codesignature = 29
        EMBEDDED_SIGNATURE = 0xFADE0CC0
        SIGNATURE_SLOT = 0x10000
        BLOBWRAPPER = 0xFADE0B01

        identity = struct.unpack(">I", f.read(4))[0]
        try:
            is64, isLittle = machos[identity]
        except KeyError:
            raise ValueError("not a Mach-O file")

        endianspec = "<" if isLittle else ">"

        def readInt():
            return struct.unpack(endianspec + "I", f.read(4))[0]

        def readIntBE():
            return struct.unpack(">I", f.read(4))[0]

        f.read(3 * 4)
        nlcs = readInt()
        f.read((2 + int(is64)) * 4)

        codesig_data = None

        for _ in range(nlcs):
            # read the load commands
            cmd = readInt()
            cmd_size = readInt()
            if is64 and cmd_size % 8 != 0:
                raise ValueError(
                    "Load command size %d for 64-bit Mach-O at "
                    "offset %d is not divisible by 8." % (cmd_size, f.tell() - 4)
                )
            elif cmd_size % 4 != 0:
                raise ValueError(
                    "Load command size %d for 32-bit Mach-O at "
                    "offset %d is not divisible by 4." % (cmd_size, f.tell() - 4)
                )
            if cmd == cmd_codesignature:
                data = f.read(cmd_size - 8)
                # offset, size:
                codesig_data = struct.unpack(endianspec + "II", data[:8])
            else:
                f.read(cmd_size - 8)

        if not codesig_data:
            return

        f.seek(offset + codesig_data[0])
        if EMBEDDED_SIGNATURE != readIntBE():
            raise ValueError("Bad magic for EMBEDDED_SIGNATURE")
        f.read(4)  # size(BIG)
        cdhashes = []
        for _ in range(readIntBE()):
            index_type = readIntBE()
            index_offset = readIntBE()
            if index_type == SIGNATURE_SLOT:
                index_current = f.tell()
                f.seek(offset + codesig_data[0] + index_offset)
                if BLOBWRAPPER != readIntBE():
                    raise ValueError("bad BLOBWRAPPER signature 0x%X" % (magic,))
                blobsize = readIntBE()
                if blobsize <= 0:
                    raise ValueError("non-positive CMS size" % (blobsize,))
                blobdata = f.read(blobsize)
                try:
                    cdhashes += blob2cdhashes(blobdata)
                except Exception as e:
                    print(e)
                f.seek(index_current)
        return cdhashes

    def parse_universal(f, length):
        machos = []
        n_machos = struct.unpack(">I", f.read(4))[0]
        for _ in range(n_machos):
            # cpu(sub)type data[4:12]
            f.read(8)
            offset = struct.unpack(">I", f.read(4))[0]
            size = struct.unpack(">I", f.read(4))[0]
            f.read(4)  # alignment

            prev = f.tell()
            try:
                machos.append(parse_macho(f, offset, size))
            except:
                pass
            f.seek(prev)
        return machos

    # check if this is a (universal) Mach-O file
    try:
        with open(filename, "rb") as f:
            magic = struct.unpack(">I", f.read(4))[0]
            if magic not in [
                0xCAFEBABE,
                0xFEEDFACE,
                0xFEEDFACF,
                0xCEFAEDFE,
                0xCFFAEDFE,
            ]:
                # not a Mach-O file (neither thin nor fat)
                return
    except Exception as e:
        return

    try:
        with open(filename, "rb") as f:
            f.seek(0, 2)
            length = f.tell()
            f.seek(0)
            magic = struct.unpack(">I", f.read(4))[0]
            if magic == 0xCAFEBABE:
                # universal
                return parse_universal(f, length)
            else:
                try:
                    return [parse_macho(f, 0, length)]
                except:
                    pass
    except Exception as e:
        _log.warning("Unable to extract cdhashes from %r" % (filename,), exc_info=True)
    return []


def getCDHashes(bundle):
    """get code directory hashes from a bundle (or a single binary)
    if multiple architectures are found in the bundle/binary, all cdhashes are returned in a flat list (with duplicates removed).
    if <bundle> does not contain (resp: is not) a Mach-O binary, then 'None' is returned.
    note, that not all cdhashes might be valid!
    """
    if os.path.isfile(bundle):
        binary = bundle
    else:
        try:
            b = utilities.Bundle(bundle)
        except:
            _log.warning("no CFBundleExecutable for bundle")
            return []
        binary = b.executable

    if not binary:
        return []

    cdhashes = _extractCDHashes(binary)
    if cdhashes is None:
        return None
    _log.debug("got %d CDhashes: %s" % (len(cdhashes), cdhashes))
    hashes = {_: True for a in cdhashes for _ in a}
    return list(hashes)


def retrieve_ticket(cdhash):
    """retrieve a notarization ticket for a given cdhash"""
    if type(cdhash) == bytes:
        cdhash = cdhash.hex()

    recordName = "2/2/%s" % cdhash
    data = {
        "records": {"recordName": recordName},
    }
    r = requests.post(ticket_url, json=data)

    try:
        j = r.json()
    except Exception:
        _log.error("failed to retrieve ticket", exc_info=True)
        return

    _log.debug("got ticket record: %s" % (j,))

    if not j:
        _log.error("no ticket information")
        return

    try:
        record = j["records"][0]
    except Exception:
        _log.error("no records in %r" % (j,), exc_info=True)
        return

    if record.get("serverErrorCode") == "NOT_FOUND":
        return

    try:
        ticket = record["fields"]["signedTicket"]["value"]
    except Exception:
        _log.error("no ticket in %r" % (record,), exc_info=True)
        return

    try:
        return base64.b64decode(ticket)
    except Exception:
        _log.error("failed to decode ticket %r" % tickdet, exc_info=True)
        return


def _test_retrieve_ticket():
    ticket = retrieve_ticket("c110d0633733b5893ec3a4804d2b9daceb98177c")
    print(ticket)


def staple_ticket(bundle, ticket):
    """embed notarization ticket into bundle"""
    if not os.path.isdir(bundle):
        # we can only staple into bundle directories
        return False
    path = os.path.join(bundle, "Contents")
    if not os.path.isdir(path):
        _log.fatal("%s does not exist" % (path,))
        return False
    outfile = os.path.join(path, "CodeResources")
    try:
        with open(outfile, "wb") as f:
            f.write(ticket)
    except:
        _log.fatal("Unable to staple ticket into %s" % (outfile,), exc_info=True)
        return False
    return True


def _subArgparser(parser):
    parser.set_defaults(func=_main, parser=parser)
    parser.add_argument(
        "bundle",
        nargs="+",
        help="notarized bundle to staple",
    )


def _parseArgs():
    import argparse

    parser = argparse.ArgumentParser(
        description="Staple apple notarization tickets into bundles.",
    )

    group = parser.add_argument_group("verbosity")
    group.add_argument(
        "-v",
        "--verbose",
        action="count",
        default=0,
        help="raise verbosity (can be given multiple times)",
    )
    group.add_argument(
        "-q",
        "--quiet",
        action="count",
        default=0,
        help="lower verbosity (can be given multiple times)",
    )

    _subArgparser(parser)

    args = parser.parse_args()

    # verbosity handling
    verbosity = 0 + args.verbose - args.quiet
    del args.verbose
    del args.quiet
    loglevel = max(1, logging.WARNING - (10 * verbosity))
    _log.setLevel(loglevel)

    return args


def staple(bundle):
    """retrieves a notarization ticket for the main binary in <bundle>,
    and attempts to staple it into the bundle
    """
    cdhashes = getCDHashes(bundle)
    tickets = []
    if cdhashes:
        tickets = [retrieve_ticket(_) for _ in cdhashes]
    tickets = [_ for _ in tickets if _]
    for t in tickets:
        if staple_ticket(bundle, t):
            break


def _main(args):
    for b in args.bundle:
        _log.info("stapling %r" % (b,))
        staple(b)


if __name__ == "__main__":
    _log = logging.getLogger("notaryjerk.staple")
    logging.basicConfig()
    args = _parseArgs()
    _main(args)
