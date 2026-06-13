from __future__ import annotations

CLOUDINIT_TEXT = {
    # Any of these (lowercased substring match) means the array finished connecting.
    "success": (
        "your system is now connected",
        "launch data services cloud console",
    ),
    # Surfaced when GreenLake register/assign hasn't propagated (Component A incomplete).
    "fail_prov": ("fail-prov-no-device", "fail-prov-no-rule"),
}

# Locators authored from the live capture (HPE exposes stable name / data-test-id hooks).
# Centralized so a UI change is a one-file fix. Grommet wizard pages:
# EULA(1) -> Network(2) -> Proxy(3) -> Time(4) -> Review(5); step nav is the top "next" arrow.
CLOUDINIT = {
    "get_started": "Get Started",
    "eula_accept_input": 'input[name="acceptEULA"]',
    "eula_accept_label": "I have read and accept the agreement",
    # The wizard is responsive: a maximized window renders a footer "Continue" button
    # (setup-next-button), a narrow viewport renders a header next-arrow (setup-next-icon).
    # Only ONE is in the DOM at a time, so _next() clicks whichever this layout exposes.
    "next": ('[data-test-id="setup-next-button"]', '[data-test-id="setup-next-icon"]'),
    "mgmt_ip": 'input[name="mgmtIp"]',
    "netmask": 'input[name="netmask"]',
    "gateway": 'input[name="defaultGateway"]',
    "dns_inputs": ('input[name="dns0"]', 'input[name="dns1"]', 'input[name="dns2"]'),
    "proxy_http_option": "HTTP Proxy",
    "proxy_none_option": "No proxy",
    "proxy_server": 'input[name="proxyServer"]',
    "proxy_port": 'input[name="proxyPort"]',
    "ntp": 'input[name="ntpServer"]',
    "time_region_select": '[data-test-id="timeRegion"]',
    "time_zone_select": '[data-test-id="timeZone"]',
    "submit": "Submit",
}

DSCC_TEXT = {
    "initialized": ("Initialized",),
    "not_initialized": ("Not initialized",),
    "missing_subscription": ("no subscription", "attach first"),
}
