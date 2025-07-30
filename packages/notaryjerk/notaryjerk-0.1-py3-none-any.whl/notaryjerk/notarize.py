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


## webhook
# {
#     "signature": "", # 1 dekachars of base64-encoded signature
#     "cert_chain": "", # 4 kilochars of base64-encoded certificate chain
#     "payload": "", # JSON-encoded(!) payload with the following content
#       {
#            "completed_time": "2023-10-25T09:23:44.624Z",
#            "event": "processing-complete",
#            "start_time": "2023-10-25T09:23:04.379Z",
#            "submission_id": "...", # the submission ID (UUID4), as return by notarize()
#            "team_id": "..." # 10char string of the teamID used for submitting
#          }
# }


import hashlib
import json
import os
import time
import logging

import requests
import boto3
from botocore.config import Config


_log = logging.getLogger("notaryjerk.notarize")
logging.basicConfig()


class Notary:
    url = "https://appstoreconnect.apple.com/notary/v2/submissions"

    def __init__(self, token: bytes):
        """create a new Notary instance that can talk to apple's notarization service
        <token> can be:
        - bytes: a pre-generated token
        - str: a path to a pre-generated token
        - tuple(private_key, key-id, issuer-id[, timeout]) to generate a new token
        throws an error if no token can be obtained
        """
        if type(token) == bytes:
            self._token = token
        elif type(token) == str:
            with open(token, "rb") as f:
                self._token = f.read()
        else:
            self._token = generate_token(*token)

        if type(self._token) == bytes:
            self._token = self._token.decode()

        self._sids = {}

    def getToken(self):
        """returns the JWT-token"""
        return self._token.encode()

    def submit(self, filename, webhook=None):
        """create a new submission request for <filename>
        the optional <webhook> is an URL that will be called asynchronously
        at the submission service's descretion when the submission was processed.

        returns submission_data to be used with upload() (or None if the submission failed)
        """
        submissionname = os.path.basename(filename)
        body = {
            "submissionName": submissionname,
            "sha256": getHash(filename),
        }
        if webhook:
            body["notifications"] = [{"channel": "webhook", "target": webhook}]

        resp = requests.post(
            self.url,
            json=body,
            headers={"Authorization": "Bearer " + self._token},
        )
        resp.raise_for_status()

        try:
            output = resp.json()
        except:
            return None

        try:
            self._sids[output["data"]["id"]] = filename
        except KeyError:
            pass

        return output

    @staticmethod
    def upload(filename, submission_data):
        """upload a file to AWS, using submission_data returned by 'Notary.submit'"""
        aws_info = submission_data["data"]["attributes"]
        bucket = aws_info["bucket"]
        key = aws_info["object"]
        sub_id = submission_data["data"]["id"]

        s3 = boto3.client(
            "s3",
            aws_access_key_id=aws_info["awsAccessKeyId"],
            aws_secret_access_key=aws_info["awsSecretAccessKey"],
            aws_session_token=aws_info["awsSessionToken"],
            config=Config(s3={"use_accelerate_endpoint": True}),
        )

        resp = s3.upload_file(filename, bucket, key)

        return resp

    def notarize(self, filename, webhook=None):
        """notarize a file
        - create a new notarization submission
        - upload the file
        returns the submission ID (or 'None' in case of failure)
        """
        _log.info("Submitting '%s' for notarization" % (filename))
        x = self.submit(filename, webhook=webhook)
        _log.debug("submission data: %r" % (x,))
        _log.info("Uploading '%s'" % (filename,))
        if webhook:
            _log.info("Webhook: %s" % (webhook,))
        y = self.upload(filename, x)
        try:
            sid = x["data"]["id"]
            self._sids[sid] = filename
            return sid
        except:
            _log.exception("submission returned: %r" % (x,))

    def check(self, sid):
        """check the current state of a submission id
        returns a tuple (<state>, <log>) or None if the submission is still pending
        """
        url = "%s/%s" % (self.url, sid)
        headers = {"Authorization": "Bearer " + self._token}
        r = requests.get(url, headers=headers)
        if r.status_code >= 300:
            _log.debug("retrieving status for '%s' returned %s" % (sid, r.status_code))
            # oops, no such resource
            return None

        try:
            statusjson = r.json()
            status = statusjson["data"]["attributes"]["status"].lower()
        except KeyError:
            # oops, cannot read status
            _log.debug("no status for '%s'" % (sid,))
            return None

        _log.debug("'%s' has status %r" % (sid, status))
        if "in progress" == status:
            # not ready yet
            return (None, statusjson)

        # get log file
        r1 = requests.get("%s/logs" % url, headers=headers)
        try:
            logurl = r1.json()["data"]["attributes"]["developerLogUrl"]
            r2 = requests.get(logurl)
            logjson = r2.json()
        except:
            logjson = None
        return (("accepted" == status), logjson)

    def wait(self, sids: list = None, timeout=60, polltime=1):
        """polls the status for a list of submission-ids
        if sids is None, polls all the SIDs that have been submitted by the Notary
        """
        if sids is None:
            sids = self._sids
        sids = {_ for _ in sids if _ is not None}
        results = {}

        now = time.time()
        while sids:
            _log.info("checking status for: %s" % (", ".join(sids),))
            processed = set()
            for sid in sids:
                state = self.check(sid)
                if state and state[0] is None:
                    continue
                results[sid] = state
                processed.add(sid)
            sids = sids.difference(processed)
            if (time.time() - now) > timeout:
                _log.warning("checking states takes longer than %s seconds" % (timeout,))
                break
            if sids:
                time.sleep(polltime)
        _log.info("checking states took %s seconds" % (time.time() - now,))
        return results


def generate_token(private_key, key_id, issuer_id, timeout=600):
    """generate a signed JWT token given a private key (file) <private_key>,
    a <key_id> and an <issuer_id>

    <private_key>: the private key (PEM), as obtained from App Store Connect
    - if <private_key> is a file-like object the private key is read() from it
    - if it is a str() which cannot be used directly as a private_key,
      the string is interpreted as a filename which is then read to be used
      as the actual key.
      this potentially leaks the private key via a filesystem access
    - if you want to make sure that the private key you pass directly to this
      function, pass it as bytes()
    <key_id>: Your private key ID from App Store Connect;
              for example 2X9R4HXF34.
    <issuer_id>: Your issuer ID from the API Keys page in App Store Connect;
                 for example, 57246542-96fe-1a63-e053-0824d011072a.
    <timeout>: life time (in seconds) of the token
    """
    from authlib.jose import jwt

    now = int(time.time())
    header = {
        "alg": "ES256",
        "kid": key_id,
        "typ": "JWT",
    }
    payload = {
        "iss": issuer_id,
        "iat": now,
        "exp": now + timeout,
        "aud": "appstoreconnect-v1",
        # "scope": ["GET /v1/apps?filter[platform]=IOS"]
    }

    try:
        s = jwt.encode(header, payload, private_key)
        return s
    except Exception as e:
        if type(private_key) != str:
            raise
        try:
            with open(private_key) as f:
                private_key = f.read()
        except:
            raise e
        s = jwt.encode(header, payload, private_key)

    return s


def _test_generate_token(privkey="tmp/privatekey.pem", pubkey="tmp/publickey.pem"):
    from authlib.jose import jwt

    with open(pubkey) as f:
        public_key = f.read()
    s = generate_token(privkey, "2X9R4HXF34", "57246542-96fe-1a63-e053-0824d011072a")
    claims = jwt.decode(s, public_key)
    print(claims)
    print(claims.header)
    try:
        claims.validate()
        print("Validation successful!")
    except Exception as e:
        _log.exception("Validation failed")


def getHash(filename):
    """get the sha256 hash of a file"""
    sha256 = None
    with open(filename, "rb") as file:
        hash = hashlib.sha256()
        hash.update(file.read())
        sha256 = hash.hexdigest()
    return sha256


def _test_getHash(filename=None):
    if not filename:
        filename = __file__
    print("%s\t%s" % (getHash(filename), filename))


def _subArgparser(parser):
    """adds cmdline arguments to a given argparse.ArgumentParser
    so we can reuse the arguments for both a standalone script and a meta script
    """
    # what we actually want is to allow the user to
    # EITHER
    # - pass a token
    # - create a token

    def positive(val):
        """check if a number if positive"""
        v = float(val)
        if v > 0:
            return v
        raise ValueError("must be positive")

    parser.set_defaults(func=_main, parser=parser)

    group = parser.add_argument_group("authentication")
    group.add_argument(
        "--private-keyfile",
        help="path to private key for signing the token",
    )
    group.add_argument(
        "--key-id",
        "--kid",
        help="Your private key ID from App Store Connect; for example '2X9R4HXF34'",
    )
    group.add_argument(
        "--issuer-id",
        "--iid",
        help="Your issuer ID from the API Keys page in App Store Connect; for example, '57246542-96fe-1a63-e053-0824d011072a'",
    )
    group.add_argument(
        "--token-timeout",
        default=600,
        type=int,
        help="Timeout (in seconds) for newly generated tokens (DEFAULT: %(default)s)",
    )
    group.add_argument(
        "--token-file",
        required=False,
        help="file to store the generated token. if no private-keyfile/key-id/issuer-id is passed, the token is read from this file",
    )

    group = parser.add_argument_group("verification")
    group.add_argument(
        "--wait",
        action="store_true",
        help="wait until the submission has been accepted or declined",
    )
    group.add_argument(
        "--wait-timeout",
        default=300,
        type=int,
        help="timeout when waiting for definitive submission state (DEFAULT: %(default)s)",
    )
    group.add_argument(
        "--wait-polltime",
        default=10,
        type=positive,
        help="period (in seconds) between waiting for submission state (DEFAULT: %(default)s)",
    )

    group.add_argument(
        "--status-file",
        required=False,
        help="JSON file to store the submission status after the wait",
    )

    group.add_argument(
        "--webhook",
        type=str,
        help="webhook for notification about notarization status",
    )

    parser.add_argument(
        "filename",
        nargs="+",
        help="file to submit for notarization",
    )


def _parseArgs():
    import argparse

    parser = argparse.ArgumentParser(
        description="Notarize software with Apple.",
    )

    _subArgparser(parser)

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

    args = parser.parse_args()

    # verbosity handling
    verbosity = 0 + args.verbose - args.quiet
    del args.verbose
    del args.quiet
    loglevel = max(1, logging.WARNING - (10 * verbosity))
    _log.setLevel(loglevel)

    return args


def _main(args):
    parser = args.parser
    # token handling
    if not os.path.exists(args.token_file or "") and (
        not all([args.private_keyfile, args.key_id, args.issuer_id])
    ):
        parser.print_usage()
        parser.exit(
            1,
            "\nWhen not specifying a token-file, you must give *all* of private-keyfile/key-id/issuer-id\n",
        )

    if args.private_keyfile and (not os.path.exists(args.private_keyfile)):
        parser.print_usage()
        parser.exit(
            1, "\nprivate keyfile '%s' does not exist\n" % (args.private_keyfile)
        )
    if args.private_keyfile:
        token = (args.private_keyfile, args.key_id, args.issuer_id, args.token_timeout)
    else:
        token = args.token_file

    notar = Notary(token)

    if args.private_keyfile and args.token_file:
        try:
            with open(args.token_file, "wb") as f:
                f.write(notar.getToken())
        except:
            _log.error("failed to store token in %r" % args.token_file, exc_info=True)

    sids = {}
    for filename in args.filename:
        if not filename:
            continue
        sid = notar.notarize(filename, webhook=args.webhook)
        print(sid)
        if sid:
            sids[sid] = True

    if args.wait and sids:
        result = notar.wait(timeout=args.wait_timeout, polltime=args.wait_polltime)
        if args.status_file:
            with open(args.status_file, "w") as f:
                json.dump(result, f, indent=2, sort_keys=False)
        else:
            print(json.dumps(result, indent=2))


if __name__ == "__main__":
    _log = logging.getLogger()
    logging.basicConfig()
    args = _parseArgs()
    _main(args)
