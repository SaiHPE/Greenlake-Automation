"""SPEC-013 (G-3): the ESXi host's own view of the exported LUNs, read through vCenter.

R1 parse vCenter's storageDevice (duck-typed fakes, no pyVmomi); R2 join on the volume WWN, never the
name; R3 per-host states ok / degraded / absent / not_in_vcenter; R4 the rescan sentence; R6 a failed
read degrades to a note and leaves the array-side verdict alone.
"""

from __future__ import annotations

from types import SimpleNamespace as NS

from alletra_onboard.adapters.vcenter.vcenter_client import parse_storage_device
from alletra_onboard.application.provisioning.path_verify import attach_esxi_view, verify_paths
from alletra_onboard.domain.provisioning import EsxiLun, VolumePath

WWN1 = "60002AC0000000000000007900002D495"[:32]   # 32 hex, as WSAPI reports it (upper-case)
WWN2 = "60002AC0000000000000007A00002D495"[:32]
NAA1 = f"naa.{WWN1.lower()}"


def _path(state: str, adapter: str) -> NS:
    return NS(pathState=state, adapter=f"key-vim.host.FibreChannelHba-{adapter}", state=state)


def _storage_device(*, luns: dict[str, list[NS]], names: dict[str, str] | None = None) -> NS:
    """A HostStorageDeviceInfo look-alike: scsiLun[] + multipathInfo.lun[] + hostBusAdapter[]."""
    names = names or {}
    keys = {naa: f"key-vim.host.ScsiDisk-{i}" for i, naa in enumerate(luns)}
    return NS(
        hostBusAdapter=[NS(key="key-vim.host.FibreChannelHba-vmhba1", device="vmhba1"),
                        NS(key="key-vim.host.FibreChannelHba-vmhba2", device="vmhba2")],
        scsiLun=[NS(key=keys[naa], canonicalName=names.get(naa, naa), operationalState=["ok"]) for naa in luns]
        + [NS(key="key-local", canonicalName="mpx.vmhba0:C0:T0:L0", operationalState=["ok"])],  # local disk, ignored
        multipathInfo=NS(lun=[NS(lun=keys[naa], path=paths) for naa, paths in luns.items()]),
    )


def test_parse_storage_device_counts_paths_per_naa_and_names_adapters():
    sd = _storage_device(luns={NAA1: [_path("active", "vmhba1"), _path("active", "vmhba2"),
                                     _path("standby", "vmhba1"), _path("dead", "vmhba2")]},
                         names={NAA1: NAA1.upper()})          # vCenter may report the canonical name upper-case
    out = parse_storage_device("esx1", sd)
    assert [l.naa for l in out] == [NAA1]                      # mpx local disk dropped; lower-cased
    lun = out[0]
    assert (lun.paths_total, lun.paths_active, lun.paths_dead) == (4, 2, 1)
    assert lun.adapters == ["vmhba1", "vmhba2"] and lun.operational_state == "ok"


def test_parse_storage_device_without_storage_is_empty():
    assert parse_storage_device("esx1", None) == []


def _array_live_report(host: str = "esx1", volumes=("vol01", "vol02")):
    paths = [VolumePath(lun=i, volume=v, host=host, host_wwpn="10000000C9000001", port="0:3:1", status="active")
             for i, v in enumerate(volumes)]
    paths += [VolumePath(lun=i, volume=v, host=host, host_wwpn="10000000C9000002", port="0:3:2", status="active")
              for i, v in enumerate(volumes)]
    return verify_paths({host: set(volumes)}, paths)


def test_esxi_view_ok_when_every_volume_has_two_active_paths():
    rep = _array_live_report()
    luns = [EsxiLun(host_name="esx1", naa=NAA1, paths_total=4, paths_active=4, adapters=["vmhba1", "vmhba2"]),
            EsxiLun(host_name="esx1", naa=f"naa.{WWN2.lower()}", paths_total=4, paths_active=4, adapters=["vmhba1", "vmhba2"])]
    attach_esxi_view(rep, {"esx1": {"vol01", "vol02"}}, luns, {"vol01": WWN1, "vol02": WWN2}, {"esx1"})
    row = rep.hosts[0]
    assert row.verdict == "live"                               # array side untouched
    assert row.esxi_state == "ok"
    assert row.esxi_note == "ESXi sees 2 volume(s) · 4 active of 4 path(s) per LUN · vmhba1, vmhba2"
    assert [lp.present for lp in row.esxi_luns] == [True, True]
    assert row.esxi_luns[0].naa == NAA1                        # joined on the WWN, lower-cased


def test_esxi_view_absent_says_rescan_and_keeps_the_array_verdict():
    rep = _array_live_report()
    luns = [EsxiLun(host_name="esx1", naa=NAA1, paths_total=4, paths_active=4)]   # vol02 not rescanned yet
    attach_esxi_view(rep, {"esx1": {"vol01", "vol02"}}, luns, {"vol01": WWN1, "vol02": WWN2}, {"esx1"})
    row = rep.hosts[0]
    assert row.verdict == "live"
    assert row.esxi_state == "absent"
    assert row.esxi_note.startswith("ESXi sees 1 of 2 exported volume(s); no device yet for vol02 — rescan the host's storage adapters")


def test_esxi_view_degraded_on_one_active_path_or_a_dead_path():
    rep = _array_live_report(volumes=("vol01",))
    attach_esxi_view(rep, {"esx1": {"vol01"}},
                     [EsxiLun(host_name="esx1", naa=NAA1, paths_total=2, paths_active=1, adapters=["vmhba1"])],
                     {"vol01": WWN1}, {"esx1"})
    assert rep.hosts[0].esxi_state == "degraded" and rep.hosts[0].esxi_note.endswith("— one active path")
    rep = _array_live_report(volumes=("vol01",))
    attach_esxi_view(rep, {"esx1": {"vol01"}},
                     [EsxiLun(host_name="esx1", naa=NAA1, paths_total=4, paths_active=3, paths_dead=1)],
                     {"vol01": WWN1}, {"esx1"})
    assert rep.hosts[0].esxi_state == "degraded" and rep.hosts[0].esxi_note.endswith("— 1 dead path(s)")


def test_esxi_view_not_in_vcenter_and_not_read():
    rep = _array_live_report(host="arcus-win137", volumes=("vol01",))
    attach_esxi_view(rep, {"arcus-win137": {"vol01"}}, [], {"vol01": WWN1}, {"esx1"})
    assert rep.hosts[0].esxi_state == "not_in_vcenter" and "not an ESXi host" in rep.hosts[0].esxi_note

    rep = _array_live_report()
    attach_esxi_view(rep, {"esx1": {"vol01", "vol02"}}, [], {}, {"esx1"}, read_error="Login failed for x@vc")
    assert rep.hosts[0].esxi_state == "not_read"
    assert rep.hosts[0].esxi_note == "ESXi view: not read (Login failed for x@vc)"
    assert rep.hosts[0].verdict == "live"


def test_esxi_view_names_a_volume_without_a_wwn_instead_of_guessing():
    rep = _array_live_report(volumes=("vol01",))
    attach_esxi_view(rep, {"esx1": {"vol01"}}, [EsxiLun(host_name="esx1", naa=NAA1, paths_active=4, paths_total=4)],
                     {}, {"esx1"})
    row = rep.hosts[0]
    assert row.esxi_state == "absent" and "(no WWN read for vol01)" in row.esxi_note
