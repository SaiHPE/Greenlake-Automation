import { describe, expect, it } from 'vitest';
import { InitSheetUploadResult, snapshotsTabNotPicked } from './api';

const WORK_ITEM: InitSheetUploadResult['work_item'] = {
  serial_number: 'SGH1',
  part_number: 'S0B84A',
  subscription_key: 'KEY',
  service_catalog_region_id: 'ap-northeast',
  dscc_region_code: 'jp1',
  cloudinit_url: 'https://169.254.0.1/cloudinit',
  network: {
    mgmt_ipv4: '10.0.0.1',
    mask: '255.255.255.0',
    gateway: '10.0.0.254',
    dns: [],
    ntp: 'ntp.example.com',
    timezone: 'UTC',
    proxy_host: null,
    proxy_port: null,
    proxy_username: null,
    proxy_password_ref: null,
  },
  dscc_setup: {
    system_name: 'arr',
    country: 'India',
    credential_name: 'b10000-admin',
    username: '3paradm',
    contact_first_name: null,
    contact_last_name: null,
    contact_language: 'English',
    contact_company: null,
    contact_phone: null,
    contact_email: null,
    blueprint_name: null,
    apply_blueprint: false,
  },
  tags: {},
  support_contact: {},
  customer_name: '',
  site: '',
  application_workload: '',
  storage_purpose: '',
};

const sheet = (snapshotRows: string[]): InitSheetUploadResult => ({
  token: 't',
  work_item: WORK_ITEM,
  credentials_saved: true,
  targets: {},
  replication_ports: [],
  snapshot_rows: snapshotRows,
  problems: [],
});

describe('snapshotsTabNotPicked', () => {
  it('reminds the operator when the Snapshots tab is filled and the run lacks the step', () => {
    expect(snapshotsTabNotPicked(sheet(['zz_sn_vvs: Snapshot now']), ['greenlake', 'cloudinit', 'dscc']))
      .toBe('The Snapshots tab is filled in; pick the Snapshots step to apply it.');
  });

  it('says nothing when the run has the Snapshots step', () => {
    expect(snapshotsTabNotPicked(sheet(['zz_sn_vvs: Snapshot now']), ['provision', 'snapshots'])).toBeNull();
  });

  it('says nothing for a sheet without the tab, or before a sheet is uploaded', () => {
    expect(snapshotsTabNotPicked(sheet([]), ['greenlake'])).toBeNull();
    expect(snapshotsTabNotPicked(undefined, ['greenlake'])).toBeNull();
    expect(snapshotsTabNotPicked(null, ['greenlake'])).toBeNull();
  });
});
