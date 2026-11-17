# ADR 0026 — Certificates and host keys: check the cloud, trust on-site devices on first contact

**Status:** accepted 2026-11-17 (owner's decision); built in the steps below, each pending a live run ·
**Issue:** BL-53 · **Relates to:** [ADR 0013](0013-one-array-credential-per-run.md) (where the pin is
kept), [ADR 0008](0008-proxy-auto-detect-with-override.md) (on-site devices bypass the proxy),
[ADR 0015](0015-tool-configures-remote-copy-write-scoped-ssh.md) (the Remote Copy write client connects
like the read client) · **Lesson:** [LESSONS](../LESSONS.md) 43

## Context

The tool talks to two kinds of endpoint. Cloud endpoints (GreenLake, DSCC) carry public certificates.
On-site devices (the array and its Remote Copy peer, vCenter, the Brocade switches, Linux and Windows
hosts) ship with self-signed certificates and SSH keys that nobody has recorded, and the jump box has
no `known_hosts` for them.

Today the tool checks every cloud certificate and no on-site one. Most on-site links carry an admin
password. A machine that answers in a device's place on the management network gets that password
(for WSAPI, the session key too) and can feed the tool false reads. A review asked for one decision
per endpoint instead of a single "self-signed, accepted" comment.

What the code does today (checked against `main` at b7006373, 2026-11-17):

| Endpoint | Code (`src/alletra_onboard/`) | Today |
|---|---|---|
| GreenLake API, token, clock check | `adapters/greenlake/http_client.py`, `adapters/greenlake/auth.py`, `adapters/system/clock.py` | `verify=ssl_context()` from `application/platform/tls.py`: the Windows store, certifi and an optional PEM (`ALLETRA_CA_BUNDLE`, `SSL_CERT_FILE`, `REQUESTS_CA_BUNDLE`). No setting turns it off. |
| DSCC | `adapters/browser/dscc_setup.py` | Attaches over CDP to the operator's own Chrome on `localhost:9222`, started with no certificate flags. Chrome checks the certificate. |
| Setup wizard (`https://169.254.x.x` or `fe80::`) | `adapters/browser/cloudinit_wizard.py` | `ignore_https_errors=True` in the browser the tool launches; attached over CDP, the operator's Chrome shows its own warning. `domain/cloudinit_url.py` refuses any address that is not link-local. The wizard is given network values only; no password is typed. |
| Array WSAPI (the array and the peer) | `adapters/array/wsapi_client.py` | `HPE3ParClient(..., secure=False, suppress_ssl_warnings=True)`. The SDK passes `secure` to `requests` as `verify`; `suppress_ssl_warnings` turns off urllib3's warnings for the whole process. The admin password, then the session key, go to whoever answers. |
| Array SSH: reads, the link check, the Console, the Remote Copy write client | `adapters/array/cli_client.py` (`ArrayRcCliClient` inherits its `connect`) | `paramiko.AutoAddPolicy()`. |
| Brocade switch | `adapters/fabric/brocade_client.py` | `AutoAddPolicy()`. Old FOS offers only `ssh-rsa` host keys, which is why paramiko is held below 4 (LESSONS 43). |
| Linux hosts | `adapters/hosts/linux_ssh.py` | `AutoAddPolicy()`. |
| vCenter | `adapters/vcenter/vcenter_client.py` | `ssl.CERT_NONE` with `check_hostname = False`. The account is often the vSphere administrator. |
| Windows hosts (WinRM) | `adapters/hosts/windows_winrm.py` | `transport="ntlm"`. Port 5985 first, where pywinrm encrypts every message with the NTLM session; then 5986 with `server_cert_validation="ignore"`. A fixed set of PowerShell reads. |

## Decision

### Per endpoint

| Endpoint | Decision | Why |
|---|---|---|
| GreenLake API, token, clock check | **Keep checking.** No setting to turn it off. Do not pin. | Public certificates rotate, and an inspecting proxy re-signs them; a pin would break on both. The OWASP Pinning Cheat Sheet advises against pinning public certificates. |
| DSCC | **Keep.** The operator's Chrome checks the certificate. | The tool never handles DSCC credentials. |
| Setup wizard | **Keep unchecked, with this reason written at the site.** The link-local address check stays. | A link-local address is not routed, so the wizard is reached only from the array's own segment, in practice the same cable. No password is typed, only network values. A fresh array has no certificate anyone could have recorded before this moment. |
| Array WSAPI | **Pin on first contact.** Before `login()`, open a TLS connection, hash the leaf certificate (SHA-256) and compare it with the run's pin; record it if there is none. With a device CA bundle set, pass its path as `secure` instead (requests accepts a path as `verify`). | The password and the session key are the most valuable secrets the tool sends to a device. |
| Array SSH, read and Remote Copy write | **Pin on first contact.** | The same admin password as WSAPI; the write client changes the array. |
| Brocade switch | **Pin on first contact.** | The switch admin password. The pin is the key itself, so an `ssh-rsa` key pins like any other. |
| Linux hosts | **Pin on first contact.** | The host login, used with `sudo -n` for two reads. |
| vCenter | **Pin on first contact**, through pyVmomi's `serverPemCert`, which pyVmomi checks on every connection it opens. With a device CA bundle set, verify against the bundle instead. | Often the vSphere administrator account. |
| Windows hosts (WinRM) | **Keep unchecked, with this reason written at the site.** The existing test that `transport` stays `"ntlm"` (`tests/unit/test_host_reads.py`) is the guard. With a device CA bundle set, 5986 validates against it (`server_cert_validation="validate"`, `ca_trust_path=<bundle>`). | NTLM never sends the password. On 5985 every message is encrypted with the NTLM session, and the client only reads. An impostor could get an NTLM response to attack offline and could return false reads; accepted for a read-only path. 5985 has no certificate to pin. |

### How pinning works

1. **Where the pin lives.** In the run's record in `state.db`, with the same lifetime as the run's
   credentials (ADR 0013): it goes when the run goes. The key is the device address, port and kind
   (TLS or SSH). A new run starts with no pins and trusts on its own first contact.
   - SSH: the key type, the public key (base64, as in `known_hosts`) and its `SHA256:` fingerprint.
     paramiko needs the key itself, not only the fingerprint, to compare.
   - TLS: the leaf certificate (PEM) and its SHA-256. pyVmomi needs the PEM.
2. **SSH.** A custom paramiko `MissingHostKeyPolicy` records the key and `key.fingerprint`
   (`SHA256:…`) on first contact. Later connections preload the pinned key into
   `client.get_host_keys()` (under `[host]:port` when the port is not 22), so paramiko compares it
   and raises `BadHostKeyException` on a mismatch. paramiko checks the host key before it
   authenticates, so a mismatch stops before the password is sent.
3. **TLS.** Probe and compare first, then log in. A mismatch stops before the credentials are sent.
4. **The operator sees it.** The fingerprint shows in the run, marked as trusted on first contact,
   and in the as-built, so the customer can compare it with the device's own console.
5. **A mismatch blocks the step.** The message names the device, the fingerprint the run trusted and
   the one it got now, and says the password was not sent.
6. **Re-trusting is a separate, logged action** on the run, recorded as a run event with both
   fingerprints. It is never a button on the error: OWASP advises not letting the user bypass the
   pin, and a button beside the error teaches people to press it.
7. **A device CA bundle, where the customer has one, replaces first-contact trust** for the TLS
   endpoints (WSAPI, vCenter, WinRM 5986). It is one optional setting, separate from the cloud
   bundle and read by all three. With it set, the check is the full one (chain and name), and a
   failure does not fall back to first-contact trust. SSH has no CA here, so SSH devices are always
   pinned.

Why pin rather than tell people to put the device's self-signed certificate in a CA bundle: since
Python 3.13, `ssl.create_default_context()` turns on `VERIFY_X509_STRICT` (urllib3 2 does the same on
3.13 and later), which refuses many device-made self-signed certificates, and the name check needs the
device's IP address inside the certificate. A pin compares the certificate's bytes and needs neither.

### Change set, in order

Each step is its own pull request with fake-based tests. None calls a device in the test suite.

1. The pin store (in `state.db`, removed with the run) and one helper that records, compares and
   refuses, with fake-based tests for all three.
2. Array SSH `connect` in `cli_client.py`. This covers the Remote Copy write client, the link check
   and the Console, which share it. `application/documents/verification.py` builds `ArrayCliClient`
   itself instead of through `application/provisioning/clients.py`; it gets the run's pins too.
3. Brocade and Linux SSH.
4. The WSAPI TLS probe before `login()`; then the follow-up below.
5. vCenter through `serverPemCert`.
6. One optional device CA bundle setting, read by WSAPI, vCenter and WinRM.
7. The LESSONS 43 rule: the reason written at each site that still turns a check off, and a test that
   lists those sites, so a new one fails until it carries a reason.
8. Docs: SCOPE, the HLD security section, the README (where the fingerprint shows, how to re-trust).
9. A live run to see whether the array's WSAPI certificate or SSH key changes after initial setup
   (the setup wizard, DSCC setup, a restart). If it does, a pin taken too early would block a good
   array, and first contact has to move past that point. Until this run, every step above is
   *built, pending live run*.

**Known gap, closed after step 4.** The probe and the login are separate connections, and the SDK opens
a new connection for every call (it calls the module-level `requests.request`). The fix is to route the
SDK's requests through urllib3's `assert_fingerprint`, which urllib3 2.8.0 still checks when
certificate verification is off (`CERT_NONE`). Then every WSAPI connection is checked, not only the
probe.

## Consequences

- Cloud trust does not change: still checked, still no switch to turn it off.
- A replaced or reset device stops the run until the operator re-trusts it. That is the intent; the
  message must make the next step plain.
- Two links stay unchecked, each with its reason at the code site and here: the setup wizard and
  WinRM.
- `secure=False` on the WSAPI SDK and `CERT_NONE` on vCenter stay in the code, because a self-signed
  certificate cannot pass a chain check. Each sits behind a pin; WSAPI fully so only once the known gap
  is closed.
- Pins last one run. A second run against the same array trusts again on its first contact, and the
  as-built of the earlier run is what to compare against. Keeping pins across runs (a jump-box
  `known_hosts`) is not decided here.
- The as-built gains a short table of device fingerprints.
- On-site devices are already in the proxy bypass (ADR 0008), so an inspecting proxy never re-signs
  them and cannot break a pin.

## Sources

Read 2026-11-17:

- paramiko `SSHClient`: docs.paramiko.org/en/stable/api/client.html
- OWASP Pinning Cheat Sheet: cheatsheetseries.owasp.org/cheatsheets/Pinning_Cheat_Sheet.html
- pywinrm: github.com/diyan/pywinrm
- Python `ssl`: docs.python.org/3/library/ssl.html

Checked in the installed packages the same day: python-3parclient (`http.py` passes `secure` as
`verify` and calls `disable_warnings`), paramiko 3.5.1 (`client.py` checks the host key before
authenticating and prefers a preloaded key's type), urllib3 2.8.0 (`connection.py` runs
`assert_fingerprint` with `CERT_NONE`), pyVmomi 9.1.1.0 (`SoapAdapter.py` checks `serverPemCert` on
connect), pywinrm 0.5.0 (`transport.py` uses `ca_trust_path` only when validating).
