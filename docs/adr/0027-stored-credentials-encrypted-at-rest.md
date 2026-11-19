# ADR 0027 — Stored credentials are encrypted with a key kept next to the database

**Status:** proposed and built 2026-11-19 (BL-65); the owner can amend. Checked live on rack13-ARCUS
from a Mac 2026-11-19 ([validation record](../validation/2026-11-19-bl65-credentials-and-schema.md));
not yet run on Windows · **Issue:** BL-65 ·
**Relates to:** [ADR 0013](0013-one-array-credential-per-run.md) (a run holds its credentials;
it left encryption at rest undecided)

## Context

A run keeps the credentials from the initialisation sheet for its whole life (ADR 0013): GreenLake
registration reads the subscription key from the stored work item, and every device step reads the
passwords from the stored provisioning intent. Until now `adapters/persistence/sqlite.py` wrote them
into `state.db` as plain JSON, in three tables:

- `work_items`: the subscription key and the DSCC system password;
- `provisioning_intents`: the array, vCenter, both switch, declared host, Remote Copy peer and
  migration source passwords;
- `pending_sheets`: both of the above for a sheet uploaded but not yet turned into a run, and, when
  the upload listed problems, the uploaded workbook itself, which holds every password of the sheet.

The GreenLake client secret is not in the database: it lives in `.env` (unchanged here).

`state.db` is the file people copy: to a colleague's machine to look at a run, into a support case, or
into an evidence zip next to a lab report. Each copy carried every password of the customer's site.

## Decision

1. **Encrypt the secret fields, not whole rows.** Each secret value above is replaced in the stored
   JSON by `{"fernet": "<token>"}` (Fernet from `cryptography`: AES-128-CBC with an HMAC-SHA256,
   a timestamp and a random IV). The rest of the row (serial number, addresses, user names, volumes)
   stays readable, so support can still read a database without the key. The uploaded workbook in a
   pending sheet is one secret and is encrypted whole. The list of secret fields is in one place,
   `_WORK_ITEM_SECRETS` and `_INTENT_SECRETS` in `sqlite.py`.
2. **One key per installation, in a file next to the database:** `<folder of state.db>/secrets.key`
   (`adapters/persistence/secrets.py`). It is made on the first save that needs it, with permissions
   0600 on Linux and macOS. On Windows the packaged app keeps `state.db` in the user's own
   `%LOCALAPPDATA%\AlletraOnboard`, so the key is there too, under that user's profile permissions;
   a zip installation keeps both in its `.alletra_onboard` folder. The key never goes into the
   database, a log, an event, an API answer or an evidence zip, and git ignores `secrets.key` and
   `*.key`.
3. **Old rows keep working.** A secret stored before this change is a plain string and is read as it
   is; the next save of that work item or intent writes it encrypted. Nothing is rewritten at start-up.
4. **A value that cannot be decrypted stops with one sentence.** When the key file is missing or
   belongs to another installation, reading the run's work item, intent or pending sheet raises
   `StoredCredentialsUnreadableError` (`domain/ports.py`) with: *"This run's stored credentials cannot
   be read on this computer (the key file is missing or belongs to another installation). Upload the
   initialisation sheet again to start a new run."* The API answers 409 with that sentence; a step
   running in the background records it as its event. The run itself still opens (its record and
   events hold no secret), and its as-built document still downloads.

## What it protects against, and what it does not

It protects the credentials in a copy of `state.db` on its own: a database attached to a support
case, copied to another machine, or swept into an evidence zip. None of the app's export paths
include the key file (checked: `scripts/`, `lab/`, `session.ps1`, the release and exe packaging, and
the API's download routes, which serve only the as-built from the database).

It does not protect against anyone who can read both files: someone signed in with the same Windows
account, malware running as that user, or a backup of the whole folder. The key file sits next to the
database by design, so whoever copies the folder copies both.

## Why not DPAPI now

Windows DPAPI (`CryptProtectData`) would bind the key to the Windows user, so even a copy of the whole
folder would be unreadable elsewhere. It is the natural next step, but we have no Windows machine to
test it on before it ships, and a mistake there makes every stored run unreadable on the jump box. It
can be added later without changing this format: DPAPI would protect the key file, and the database
would stay as it is.

## Consequences

- Copying `state.db` alone to another computer leaves its runs' stored credentials unreadable there;
  upload the sheet again to start a new run. The README says to keep the key file with the database.
- Deleting `secrets.key` has the same effect on this computer. A new key is made on the next save.
- `cryptography` is declared in `pyproject.toml`; it was already installed as a dependency of paramiko.
- Rows saved before this change stay in plain text until their run is saved again. Pending sheets
  expire after 24 hours (BL-65), so old ones do not linger.
