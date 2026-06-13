// Flat form model for the per-array work item, mirrored to/from the API's nested shape.

export interface WorkItemForm {
  serial_number: string;
  part_number: string;
  subscription_key: string;
  service_catalog_region_id: string;
  dscc_region_code: string;
  cloudinit_url: string;
  mgmt_ipv4: string;
  mask: string;
  gateway: string;
  dns: string; // semicolon separated
  ntp: string;
  timezone: string;
  proxy_host: string;
  proxy_port: string;
  dscc_system_name: string;
  dscc_country: string;
  contact_first_name: string;
  contact_last_name: string;
  contact_language: string;
  contact_company: string;
  contact_phone: string;
  contact_email: string;
  secret_name: string;
  secret_username: string;
}

export const EMPTY_FORM: WorkItemForm = {
  serial_number: '',
  part_number: 'S0B84A',
  subscription_key: '',
  service_catalog_region_id: 'ap-northeast',
  dscc_region_code: 'jp1',
  cloudinit_url: '',
  mgmt_ipv4: '',
  mask: '',
  gateway: '',
  dns: '',
  ntp: '',
  timezone: '',
  proxy_host: '',
  proxy_port: '',
  dscc_system_name: '',
  dscc_country: 'India',
  contact_first_name: '',
  contact_last_name: '',
  contact_language: 'English',
  contact_company: '',
  contact_phone: '',
  contact_email: '',
  secret_name: 'b10000-admin',
  secret_username: '3paradm',
};

export function toWorkItemPayload(form: WorkItemForm) {
  return {
    serial_number: form.serial_number.trim(),
    part_number: form.part_number.trim(),
    subscription_key: form.subscription_key.trim(),
    service_catalog_region_id: form.service_catalog_region_id.trim(),
    dscc_region_code: form.dscc_region_code.trim(),
    cloudinit_url: form.cloudinit_url.trim(),
    network: {
      mgmt_ipv4: form.mgmt_ipv4.trim(),
      mask: form.mask.trim(),
      gateway: form.gateway.trim(),
      dns: form.dns.split(';').map((value) => value.trim()).filter(Boolean),
      ntp: form.ntp.trim(),
      timezone: form.timezone.trim(),
      proxy_host: form.proxy_host.trim() || null,
      proxy_port: form.proxy_port.trim() ? Number(form.proxy_port.trim()) : null,
    },
    dscc_setup: {
      system_name: form.dscc_system_name.trim(),
      country: form.dscc_country.trim(),
      credential_name: form.secret_name.trim() || 'b10000-admin',
      username: form.secret_username.trim() || '3paradm',
      contact_first_name: form.contact_first_name.trim() || null,
      contact_last_name: form.contact_last_name.trim() || null,
      contact_language: form.contact_language.trim() || 'English',
      contact_company: form.contact_company.trim() || null,
      contact_phone: form.contact_phone.trim() || null,
      contact_email: form.contact_email.trim() || null,
    },
  };
}

/** Fill the form from one parsed work item returned by POST /work-items/parse. */
export function fromParsedWorkItem(item: any): WorkItemForm {
  const network = item.network ?? {};
  const dscc = item.dscc_setup ?? {};
  return {
    serial_number: item.serial_number ?? '',
    part_number: item.part_number ?? '',
    subscription_key: item.subscription_key ?? '',
    service_catalog_region_id: item.service_catalog_region_id ?? '',
    dscc_region_code: item.dscc_region_code ?? '',
    cloudinit_url: item.cloudinit_url ?? '',
    mgmt_ipv4: network.mgmt_ipv4 ?? '',
    mask: network.mask ?? '',
    gateway: network.gateway ?? '',
    dns: (network.dns ?? []).join(';'),
    ntp: network.ntp ?? '',
    timezone: network.timezone ?? '',
    proxy_host: network.proxy_host ?? '',
    proxy_port: network.proxy_port == null ? '' : String(network.proxy_port),
    dscc_system_name: dscc.system_name ?? '',
    dscc_country: dscc.country ?? '',
    contact_first_name: dscc.contact_first_name ?? '',
    contact_last_name: dscc.contact_last_name ?? '',
    contact_language: dscc.contact_language ?? 'English',
    contact_company: dscc.contact_company ?? '',
    contact_phone: dscc.contact_phone ?? '',
    contact_email: dscc.contact_email ?? '',
    secret_name: dscc.credential_name ?? 'b10000-admin',
    secret_username: dscc.username ?? '3paradm',
  };
}
