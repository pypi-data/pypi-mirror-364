notarize
========

`notaryjerk notarize` lets you submit signed binaries to Apple's notarization service.


## Prerequisites
In order to be able to use Apple's notarization service,
you *must* have signed up with Apple (about 100,-€/p.a.)
and created an API-Key to access the "App Store Connect API".

In the [webinterface](https://appstoreconnect.apple.com/access/integrations/api),
you need create a new *Developer* key and obtain the following data:

| name                   | variable          | (non-working) example values           |
|------------------------|-------------------|----------------------------------------|
| Apple Issuer ID        | `APPLE_ISSUER_ID` | `57246542-96fe-1a63-e053-0824d011072a` |
| Apple Key ID           | `APPLE_KEY_ID`    | `2X9R4HXF34`                           |
| Apple Private Key file | `APPLE_KEY_FILE`  | `private_key.pem`                      |

(I'll use the names in the *variable* column to reference these requirements in the scripts below)

## Preparation

You can only notarize [**signed**](../sign/) applications and binaries.

Also, the notarization service accepts only `.zip` archives and `.dmg` disk images.
If you want to notarize a single binary, you have to wrap it into a `zip` file first.

```sh
zip mybin.zip coolcmdlineutility
zip -r myapp.zip MyApp.app
```

## Notarization

Once you have your credentials and the archive file(s),
you can simply notarize the latter with:

```sh
notaryjerk notarize \
     --issuer-id "${APPLE_ISSUER_ID}"      \
     --key-id "${APPLE_KEY_ID}"            \
     --private-keyfile "${APPLE_KEY_FILE}" \
     myapp.zip myapp.zip
```

This will upload the archive(s) to the cloud and submit it to the notarization service.
The script will return immediately.

The notarization process takes a short while (seconds, minutes... depending on Apple's resources),
and might fail (e.g. if invalid or harmful content was detected)...
or because your key is currently unusable (mostly this is because Apple
keeps updating their Terms and Conditions and you have to accept them again and again and again).

### Status-File

If you want to catch the result of the notarization process (so you know that everything went well),
pass the `--wait` option, which will make `notaryjerk` wait until it receives a status notification
from the service (or a configurable timeout has been reached).

```sh
notaryjerk notarize \
     --issuer-id "${APPLE_ISSUER_ID}"      \
     --key-id "${APPLE_KEY_ID}"            \
     --private-keyfile "${APPLE_KEY_FILE}" \
     --wait                                \
     --status-file notarize.json           \
     mybin.zip
```

The above also uses the `--status-file` argument, which will output the result of the notarization
into a machine raedable file, that might look like this:

```json
{
  "5ea058bf-f80e-4e73-b02b-8d84fca3b24a": [
    true,
    {
      "logFormatVersion": 1,
      "jobId": "5ea058bf-f80e-4e73-b02b-8d84fca3b24a",
      "status": "Accepted",
      "statusSummary": "Ready for distribution",
      "statusCode": 0,
      "archiveFilename": "mybin.zip",
      "uploadDate": "1970-01-01T00:00:01.102Z",
      "sha256": "5dd6ddbf653e7c5ab57607220ecb41b6a1d55bd123fe8cd15c8dfc4efede8d31",
      "ticketContents": [
        {
          "path": "coolcmdlineutility",
          "digestAlgorithm": "SHA-256",
          "cdhash": "625d1bc6c2fe6b34845b26615b3ab54c5ec6acf0",
          "arch": "x86_64"
        },
        {
          "path": "coolcmdlineutility",
          "digestAlgorithm": "SHA-256",
          "cdhash": "8227e9f1fa9a8c6015eaf2f777cca324cbbfa154",
          "arch": "arm64"
        }
      ],
      "issues": null
    }
  ]
}
```

### Status-Webhook

Alternatively (e.g. if you don't want to wait until the notarization process has completed),
you can specify a webhook that will be called (by the Apple service) on finishing the process:

```sh
notaryjerk notarize \
     --issuer-id "${APPLE_ISSUER_ID}"      \
     --key-id "${APPLE_KEY_ID}"            \
     --private-keyfile "${APPLE_KEY_FILE}" \
     --webhook https://example.com/notariz \
     mybin.zip myapp.zip
```

The webhook will have a payload like so:

```json
{
    "signature": "J8uPBwO2...",
    "cert_chain": "pjZljv/o...",
    "payload": "{\"completed_time\": \"1970-01-01T00:12:20.624Z\", \"event\": \"processing-complete\", \"start_time\": \"1970-01-01T00:00:04.379Z\", \"submission_id\": \"5ea058bf-f80e-4e73-b02b-8d84fca3b24a\", \"team_id\": \"UWO5Z8GT3G\"}"
}
```
