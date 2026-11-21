// Flat form model for the per-array work item, mirrored to/from the API's nested shape.
import type { InitSheetUploadResult } from './api';

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

type ParsedWorkItem = InitSheetUploadResult['work_item'];

/** Fill the form from one parsed work item returned by /init-sheet/upload or GET /runs/{id}. */
export function fromParsedWorkItem(item: ParsedWorkItem): WorkItemForm {
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
