# Overview


`notaryjerk` started as a replacement for Apple's `notarytool`
(which requires *XCode*>=13.x), by using the Apple's API directly.

It is now intended as a general toolset that helps with creating and
distributing signed binary packages, that is usable on any platform
supporting Python (not necessarily the target platform of the codesigned
binaries. E.g. you can notarize macOS binaries under Linux).

AFAIK, this is currently the only tool, that allows (somewhat easy)
notarization of macOS binaries on platforms other than macOS.


As of now, only macOS binaries are supported.

## Installation

```sh
pip install notaryjerk
```

## Documentation

- [notaryjerk notarize](tools/notarize)
- [notaryjerk staple](tools/staple)

Online documentation can be found at
[https://notaryjerk.readthedocs.io/](https://notaryjerk.readthedocs.io/).



## Development

Development is done in our [git repository](https://git.iem.at/zmoelnig/notaryjerk).


## Author
[IOhannes m zmölnig](https://zmoelnig.iem.sh) ([Institute of Electronic Music and Acoustics (IEM)](https://iem.at), [KUG, Graz/Austria](https://kug.ac.at))

## License
This code is released under the [GNU Affero General Public License, version 3](https://www.gnu.org/licenses/agpl-3.0.html).
