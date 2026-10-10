"""Compose the lab Replication test sheet for D22U27 -> E18U31 through the running app (no xlsx by hand).

    python scripts\\rc_sheet.py sync|async [out.xlsx]

Default out: ~\\Downloads\\D22U27_replication_<mode>.xlsx. Needs the app on http://127.0.0.1:8765.
Same body as the 2026-10-09 live runs: one 1 GiB volume zz_rc_vol01 in set zz_rc_vvs, host set zz_rc_hs
(member `none`, made by hand for Custom-mode runs), one Protection row zz_rc_vvs -> SSD_r6 in the given mode.
"""
import base64
import getpass
import json
import os
import sys
import urllib.request

MODE = sys.argv[1] if len(sys.argv) > 1 else ""
if MODE not in ("sync", "async"):
    sys.exit("first argument must be sync or async")
OUT = sys.argv[2] if len(sys.argv) > 2 else os.path.join(os.path.expanduser("~"), "Downloads", "D22U27_replication_%s.xlsx" % MODE)
pw = os.environ.get("ARRAY_PW") or getpass.getpass("3paradm password (used for both arrays in the sheet): ")

body = {
    "init": {
        "gl_client_id": "not-used", "gl_client_secret": "not-used", "gl_token_url": "https://not-used",
        "serial_number": "CZ2D320BT1", "part_number": "not-used", "subscription_key": "not-used",
        "service_catalog_region_id": "ap-northeast", "dscc_region_code": "jp1",
        "mgmt_ipv4": "10.64.122.99", "mask": "255.255.248.0", "gateway": "10.64.127.254", "dns1": "10.64.122.1",
        "ntp": "not-used", "timezone": "Asia/Kolkata",
        "contact_first_name": "Sai", "contact_last_name": "Roopesh", "contact_language": "English",
        "contact_company": "HPE", "contact_phone": "0", "contact_email": "not-used@hpe.com",
        "dscc_system_name": "AlletraMP_D22U27", "dscc_country": "India",
        "secret_name": "b10000-admin", "secret_username": "3paradm", "customer_name": "Lab replication test",
    },
    "targets": {
        "prov_array_host": "10.64.122.99", "prov_array_user": "3paradm", "prov_array_password": pw,
        "prov_vcenter_host": "10.54.154.226", "prov_vcenter_user": "Administrator@vsphere.local",
        "prov_vcenter_password": "not-used",
    },
    "volumes": [{"name": "zz_rc_vol01", "size_gib": "1", "vvset": "zz_rc_vvs"}],
    "hostsets": [{"name": "zz_rc_hs", "members": "none"}],
    "replication": {
        "fields": {"peer_host": "10.64.154.190", "peer_user": "3paradm", "peer_password": pw, "rtt_ms": "1"},
        "rows": [{"vvset": "zz_rc_vvs", "peer_cpg": "SSD_r6", "mode": MODE}],
    },
}
req = urllib.request.Request("http://127.0.0.1:8765/init-sheet/compose", data=json.dumps(body).encode(),
                             headers={"Content-Type": "application/json"}, method="POST")
opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
with opener.open(req, timeout=60) as resp:
    content = json.loads(resp.read())["content_b64"]
with open(OUT, "wb") as f:
    f.write(base64.b64decode(content))
print("Written %s (%d bytes), Protection row mode = %s" % (OUT, os.path.getsize(OUT), MODE))
