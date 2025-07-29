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


_log = logging.getLogger()
logging.basicConfig()


def positive(val):
    v = float(val)
    if v > 0:
        return v
    raise ValueError("must be positive")


def generate_token(pkey_file, key_id, issuer_id, timeout=600):
    """generate a signed JWT token given a public key file <pkey_file>,
    a <key_id> and an <issuer_id>

    <pkey>: the private key (PEM), as obtained from App Store Connect
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

    with open(pkey_file) as f:
        private_key = f.read()
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


def make_submission(filename, token, webhook=None):
    """create a new submission request"""
    submissionname = os.path.basename(filename)
    body = {
        "submissionName": submissionname,
        "sha256": getHash(filename),
    }
    if webhook:
        body["notifications"] = [{"channel": "webhook", "target": webhook}]

    resp = requests.post(
        "https://appstoreconnect.apple.com/notary/v2/submissions",
        json=body,
        headers={"Authorization": "Bearer " + token},
    )
    resp.raise_for_status()
    output = resp.json()
    return output


def upload_submission(filename, submission_data):
    """upload a file to AWS, using submission_data returned by 'make_submission'"""
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


def notarize(filename, jwttoken, webhook=None):
    """notarize a file
    - create a new notarization submission
    - upload the file to AWS
    the <jwtoken> is a (valid) token obtained with `generate_token()`
    returns the submission ID (or 'None' in case of failure)
    """
    _log.info("Submitting '%s' for notarization" % (filename))
    x = make_submission(filename, jwttoken, webhook=webhook)
    _log.debug("submission data: %r" % (x,))
    _log.info("Uploading '%s'" % (filename,))
    if webhook:
        _log.info("Webhook: %s" % (webhook,))
    y = upload_submission(filename, x)
    try:
        return x["data"]["id"]
    except:
        _log.exception("submission returned: %r" % (x,))


def check_state(sid, jwtoken):
    url = "https://appstoreconnect.apple.com/notary/v2/submissions/%s" % sid
    r = requests.get(url, headers={"Authorization": "Bearer " + jwtoken})
    if r.status_code >= 300:
        _log.debug("retrieving status for '%s' returned %s" % (sid, r.status_code))
        # oops, no such resource
        return (False, None)
    try:
        status = r.json()["data"]["attributes"]["status"].lower()
    except KeyError:
        # oops, cannot read status
        _log.debug("no status for '%s'" % (sid,))
        return (False, None)

    _log.debug("'%s' has status %r" % (sid, status))
    if "in progress" == status:
        # not ready yet
        return None

    # get log file
    r1 = requests.get("%s/logs" % url, headers={"Authorization": "Bearer " + jwtoken})
    try:
        logurl = r1.json()["data"]["attributes"]["developerLogUrl"]
        r2 = requests.get(logurl)
        logjson = r2.json()
    except:
        logjson = None
    return (("accepted" == status), logjson)


def check_states(sids, jwtoken, timeout=60, polltime=1):
    sids = {_ for _ in sids if _ is not None}
    results = {}

    now = time.time()
    while sids:
        _log.info("checking status for: %s" % (", ".join(sids),))
        processed = set()
        for sid in sids:
            state = check_state(sid, jwtoken)
            if not state:
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


def _subArgparser(parser):
    # what we actually want is to allow the user to
    # EITHER
    # - pass a token
    # - create a token

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
        token = generate_token(
            args.private_keyfile,
            args.key_id,
            args.issuer_id,
            timeout=args.token_timeout,
        )
        if args.token_file:
            with open(args.token_file, "wb") as f:
                f.write(token)
    else:
        with open(args.token_file, "rb") as f:
            token = f.read()

    if type(token) == bytes:
        token = token.decode()

    sids = set()
    for filename in args.filename:
        if not filename:
            continue
        sid = notarize(filename, token, webhook=args.webhook)
        print(sid)
        sids.add(sid)

    if args.wait and sids:
        result = check_states(
            sids, token, args.wait_timeout, polltime=args.wait_polltime
        )
        if args.status_file:
            with open(args.status_file, "w") as f:
                json.dump(result, f, indent=2, sort_keys=False)
        else:
            print(json.dumps(result, indent=2))


if __name__ == "__main__":
    _log = logging.getLogger("notaryjerk.notarize")
    logging.basicConfig()
    args = _parseArgs()
    _main(args)
