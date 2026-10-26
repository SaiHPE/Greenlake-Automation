"""SPEC-004 R5 — path verification says the numbers the customer asks for. Pinned to the run-2
`showvlun -a` capture (tests/fixtures/rack13_array/showvlun_a.txt: 12 active paths, 3 LUNs,
2 HBAs, 4 array ports on two cross-cabled switches)."""

from __future__ import annotations

from pathlib import Path

from alletra_onboard.application.provisioning.path_verify import parse_showvlun_active, verify_paths

FIX = Path(__file__).resolve().parents[1] / "fixtures" / "rack13_array"
PATHS = parse_showvlun_active((FIX / "showvlun_a.txt").read_text(encoding="utf-8"))
EXPECTED = {"10.132.30.136": {"zz_t2_vol01", "zz_t2_vol02", "zz_t2_vol03"}}
# rack13arcus is cross-cabled: F1 (SAN6700R13U38) = 0:3:4 + 1:3:3, F2 (SAN6700R13U40) = 0:3:3 + 1:3:4.
FABRIC_BY_PORT = {"0:3:4": "odd", "1:3:3": "odd", "0:3:3": "even", "1:3:4": "even"}
SWITCH_BY_FABRIC = {"odd": "SAN6700R13U38", "even": "SAN6700R13U40"}


def test_detail_counts_luns_hbas_and_paths_per_lun():
    h = verify_paths(EXPECTED, PATHS, FABRIC_BY_PORT).hosts[0]
    assert h.verdict == "live"
    assert h.lun_count == 3 and h.hbas_with_paths == 2 and h.paths_per_lun == 4
    assert h.detail.startswith("3 LUN(s) · 2 HBA(s) · 4 path(s) per LUN · both fabrics")


def test_detail_uses_switch_names_when_discovery_has_them():
    h = verify_paths(EXPECTED, PATHS, FABRIC_BY_PORT, switch_by_fabric=SWITCH_BY_FABRIC).hosts[0]
    assert h.fabric_names == ["SAN6700R13U40", "SAN6700R13U38"]          # fabric order: even, odd
    assert "both fabrics (SAN6700R13U40, SAN6700R13U38)" in h.detail
    assert "even" not in h.detail and "odd" not in h.detail                # slot labels never shown when names exist


def test_detail_falls_back_to_slot_labels():
    h = verify_paths(EXPECTED, PATHS, FABRIC_BY_PORT).hosts[0]
    assert h.fabric_names == []
    assert "both fabrics (even, odd)" in h.detail


def test_partial_names_the_missing_fabric_by_switch():
    one_switch = [p for p in PATHS if p.port in ("0:3:4", "1:3:3")]          # F1 only
    h = verify_paths(EXPECTED, one_switch, FABRIC_BY_PORT, switch_by_fabric=SWITCH_BY_FABRIC).hosts[0]
    assert h.verdict == "partial"
    assert "SAN6700R13U38 only" in h.detail and "missing SAN6700R13U40" in h.detail
    assert h.paths_per_lun == 2 and h.lun_count == 3


def test_uneven_paths_per_lun_report_the_minimum():
    fewer = [p for p in PATHS if not (p.lun == 2 and p.port == "0:3:4")]      # LUN 2 loses one path
    h = verify_paths(EXPECTED, fewer, FABRIC_BY_PORT).hosts[0]
    assert h.paths_per_lun == 3
    assert "3–4 path(s) per LUN" in h.detail
