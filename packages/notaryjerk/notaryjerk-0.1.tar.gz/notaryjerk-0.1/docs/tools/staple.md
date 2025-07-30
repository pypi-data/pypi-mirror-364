staple
======

Once an application has been *notarized*, you can embed ("*staple*")
a notarization ticket into the bundle
with `notaryjerk staple`.

Since the ticket is signed by a party trusted by macOS (namely: Apple itself),
this allows users to use the application without needing internet access
(for online verification of the ticket) when they first run it.


## Preparation

You can only staple notarization tickets into *bundles* (e.g. `MyApp.app`).
Single binaries cannot be stapled.
These bundles obviously have to be signed and notarized first.


## Stapling

Once you have notarized your signed application,
you can embed the notarization ticket with:

```sh
notaryjerk staple MyApp.app
```

This will retrieve the notarization ticket, and put it into a file `Contents/_CodeSignature/CodeResources`
within the bundle.
