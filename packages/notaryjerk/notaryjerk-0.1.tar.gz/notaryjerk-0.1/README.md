notaryjerk - cross platform notarization for macOS binaries
===========================================================

This started as a replacement for Apple's `notarytool` (which requires
XCode>=13.x), by using the Apple's API directly.

It is now intended as a general toolset that helps with creating and
distributing signed binary packages, that is usable on any platform
supporting Python (not necessarily the target platform of the codesigned
binaries. E.g. you can notarize macOS binaries under Linux).

AFAIK, this is currently the only tool, that allows (somewhat easy)
notarization of macOS binaries on platforms other than macOS.


While we are primarily targeting macOS binaries, the idea is to extend
this to Windows as well.


# Tools

## Code Signing

TODO

## Notarization

```python
import notaryjerk.notarize
```

## Stapling

```python
import notaryjerk.staple
```

## Creating a DMG

TODO


# How To
## Installation

The easiest way is probably using `pip`:

```sh
pip install notaryjerk
```

## Usage

### As a script


#### Notarize a disk image:

You *must* have signed up with Apple and created an API-Key to access the "App Store Connect API".
You will get a **private** key file (keep it private; in the example below I assume the key is stored in `priv.pem`),
a key-id (let's assume `2X9R4HXF34`) and an issuer-id (e.g. `57246542-96fe-1a63-e053-0824d011072a`).

Once you have all these, you can notarize your *signed* application stored in `MyApp.dmg` like so:

```sh
notaryjerk notarize \
    --private-keyfile priv.pem --key-id 2X9R4HXF34 --issuer-id 57246542-96fe-1a63-e053-0824d011072a \
    --token-file mytoken.txt \
    MyApp.dmg
```

This will create a temporary token (valid for 5 minutes, but that can be changed with the `--token-timeout` option)
and use it to submit the notarization request.
If you want to create many (different) notarization requests, you can also pass `--token-file` to store the generated
token to disk. In subsequent calls, you *only* need to pass the `--token-file` option
(and leave the `--private-keyfile`/`--key-id`/`--issuer-id`) to reuse the same token until it has expired.


#### Notarize a ZIP-file and wait until the request has been accepted
Apple accepts both disk image files and ZIP-archives.

With the `--wait` parameter, `notaryjerk` keeps running until the notarization request has been processed.
A JSON-formatted report can be saved to disk with the `--status-file` option (otherwise it will be printed to stdout)

```sh
notaryjerk notarize --token-file mytoken.txt --wait --status-file notarization.json MyApp.zip
```

#### Notarize multiple files and notify a webhook

```sh
notaryjerk notarize --token-file mytoken.txt --webhook https://example.com/notary_callback MyApp.dmg AnotherApp.zip
```


#### Staple a notarization ticket into a bundle

Once the notarization was successful, you can staple the ticket into an Application bundle.

```sh
notaryjerk staple AnotherApp.app/
```

You can only staple *bundles* (esp: you cannot staple single binaries)


# Useful links
- https://developer.apple.com/documentation/notaryapi
- https://developer.apple.com/documentation/notaryapi/submitting_software_for_notarization_over_the_web


# Author
IOhannes m zmölnig (Institute of Electronic Music and Acoustics (IEM), KUG, Graz/Austria)

# License
This code is released under the GNU Affero General Public License, version 3
