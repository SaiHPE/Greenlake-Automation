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
    "back": "Back",
    "submit": "Submit",
}

DSCC_TEXT = {
    "initialized": ("Initialized",),
    "not_initialized": ("Not initialized",),
    "missing_subscription": ("no subscription", "attach first"),
}

# DSCC "Set Up System" wizard. It renders inside an IFRAME (data-test-id="setup-iframe"),
# so the adapter scopes every locator to that frame. Steps:
#   Welcome -> Network Domain -> Time -> Attributes(Proxy, Support Contact) -> System -> Review.
# Footer advance button is the SAME element on every step; its label changes Get Started ->
# Continue -> Submit (on Review). The adapter NEVER clicks it on Review (operator submits).
DSCC = {
    "iframe": '[data-test-id="setup-iframe"]',
    # footer nav (inside the iframe)
    "continue": '[data-test-id="footer-continue-btn"]',  # Get Started / Continue / Submit
    "back": '[data-test-id="footer-back-btn"]',
    "cancel": '[data-test-id="footer-cancel-btn"]',
    # generic searchable-select internals (Grommet v2: open trigger -> search box -> role=option)
    "select_search": 'input[type="search"]',
    # Network Domain — DNS server IP inputs (names carry random UUIDs, so key off data-test-id)
    "dns_inputs": (
        '[data-test-id="attributes-domain-0-input"]',
        '[data-test-id="attributes-domain-1-input"]',
        '[data-test-id="attributes-domain-2-input"]',
    ),
    "dns_add": '[data-test-id="attributes-domain-add-dns-servers-ip-addresses-add"]',
    # Time — NTP inputs + timezone region/city searchable selects
    "ntp_inputs": (
        '[data-test-id="attributes-time-0-input"]',
        '[data-test-id="attributes-time-1-input"]',
    ),
    "ntp_add": '[data-test-id="attributes-time-add-remove-ntp-servers-add"]',
    "time_region_select": '[data-test-id="attributes-time-region-select"]',
    "time_city_select": '[data-test-id="attributes-time-country-state-city-select"]',
    # Attributes -> Proxy (server/port are read-only value-text, inherited from cloudinit;
    # only the type radio is editable)
    "proxy_http_radio": "#proxy-http-only-radio",
    "proxy_none_radio": "#proxy-none-radio",
    # Attributes -> Support Contact
    "sc_first": '[data-test-id="support-contact-firstName-TextInput"]',
    "sc_last": '[data-test-id="support-contact-lastName-TextInput"]',
    "sc_country_select": '[data-test-id="support-contact-country-TextInput"]',
    "sc_language_select": '[data-test-id="support-contact-language-Select"]',
    "sc_company": '[data-test-id="support-contact-company-TextInput"]',
    "sc_phone": '[data-test-id="support-contact-phone-TextInput"]',
    "sc_email": '[data-test-id="support-contact-email-TextInput"]',
    # System
    "system_name": '[data-test-id="system-setup-initial-system-name-textinput"]',
    "system_country_select": '[data-test-id="system-setup-initial-country-TextInput"]',
    "credentials_select": '[data-test-id="system-setup-initial-credentials-select"]',
    "credentials_create": '[data-test-id="system-setup-initial-credentials-create"]',
    # Create Secret modal — NOT captured open; label-based, verify on first live run.
    "secret_name": 'input[name="name"]',
    "secret_username": 'input[name="username"]',
    "secret_password": 'input[name="password"]',
    "secret_verify": 'input[name="verifyPassword"]',
    "secret_save": "Save",
    # Review — the step is reached when this left-nav button is present; STOP here.
    "review_nav_button": '[data-test-id="navigation-subpanel-button-7"]',
    "save_blueprint_checkbox": '[data-test-id="save-blueprint-checkbox"]',
}
