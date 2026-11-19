import { describe, expect, it } from 'vitest';
import { InitSheetUploadResult, snapshotsTabNotPicked } from './api';

const sheet = (snapshotRows: string[] | undefined): InitSheetUploadResult => ({
  token: 't', work_item: {}, credentials_saved: true, snapshot_rows: snapshotRows,
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
    expect(snapshotsTabNotPicked(sheet(undefined), ['greenlake'])).toBeNull();
    expect(snapshotsTabNotPicked(null, ['greenlake'])).toBeNull();
  });
});
