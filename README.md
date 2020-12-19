# Mailkill, a Matrix Email Killer
<!-- Place badges here someday -->

* :electric_plug: **Modular:** Switch-enabled modules allow for only the functionality you want to be enabled
* :envelope: **Receiving:** Email reception is supported
* :airplane: **Sending:** You can reply to messages sent to you
* :person: **Single-user:** Set it up on your own homeserver

## Error Codes
Mailkill may give the following error codes to the homeserver:
* **`IO.GITHUB.BLEONARD252.MAILKILL_UNAUTHORIZED` (401):** The service token is missing
* **`IO.GITHUB.BLEONARD252.MAILKILL_FORBIDDEN` (403):** The service token is wrong
* **`IO.GITHUB.BLEONARD252.MAILKILL_NOT_FOUND` (404):** The entity could not be found
* **`IO.GITHUB.BLEONARD252.MAILKILL_MALFORMED` (404):** The user does not exist because the localpart is invalid.