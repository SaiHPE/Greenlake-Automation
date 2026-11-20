"""WSAPI v1 mutating client for the Alletra MP B10000 (STANDARD S2).

Extends `WsapiReader` with the 14 mutating calls for provisioning, snapshots, Remote Copy groups
and disaster-recovery failover tests. Only `application/runs/writer_clients.py` may import this
module (import-linter `S2-wsapi-writer`).
"""

from __future__ import annotations

from collections.abc import Callable

from alletra_onboard.adapters.array.wsapi_client import (
    _WSAPI_PERSONA,
    HPE3ParClient,
    WsapiReader,
    _iscsi_names,
    _members,
)
from alletra_onboard.domain.errors import WsapiError
from alletra_onboard.domain.replication import (
    DR_ACTION_FAILOVER,
    DR_ACTION_RECOVER,
    DR_ACTION_RESTORE,
)
from alletra_onboard.domain.shared import normalize_wwpn

_DR_ACTION = {DR_ACTION_FAILOVER: "failover", DR_ACTION_RECOVER: "recover", DR_ACTION_RESTORE: "restore"}


class WsapiWriter(WsapiReader):
    """Mutating WSAPI v1 client: session and reads from `WsapiReader`, plus the 14 array writes."""

    def __enter__(self) -> WsapiWriter:
        self.connect()
        return self

    # ------------------------------------------------------------------ idempotent provisioning writes

    def ensure_host(self, name: str, fc_wwns: list[str], persona: str = "VMware") -> str:
        """Create ONE host carrying all FC WWNs at the given persona NAME (default 'VMware'), resolved to
        the WSAPI persona id via `_WSAPI_PERSONA`. Returns 'created', 'updated' (the host existed but was
        missing some of these WWNs — they were added), or 'exists' (already carries every WWN). The
        persona of an existing host is never modified.

        Raises WsapiError if any WWN already belongs to a *different* host (EXISTENT_PATH) — that is a
        real conflict the operator must resolve, not something to silently adopt.
        """
        # ONE getHosts read answers both questions: who owns each WWN, and does the host exist.
        owners_map = self.wwn_owners()
        host_exists = name in set(self.host_names())
        by_norm = {w: normalize_wwpn(w) for w in fc_wwns}
        other = {owners_map[n] for n in by_norm.values() if n in owners_map and owners_map[n] != name}
        if other:
            raise WsapiError(
                f"WWN(s) for host '{name}' already belong to another host definition: {sorted(other)}. "
                "Resolve this on the array before provisioning."
            )
        missing = [w for w, n in by_norm.items() if owners_map.get(n) != name]
        if host_exists and not missing:
            return "exists"
        if not host_exists:
            # Checked here only: an existing host keeps whatever persona the array gave it (e.g. Generic).
            persona_id = _WSAPI_PERSONA.get(persona)
            if persona_id is None:
                raise WsapiError(f"unknown host persona '{persona}' (expected one of {sorted(_WSAPI_PERSONA)})")
            try:
                self._require().createHost(name, FCWwns=fc_wwns, optional={"persona": persona_id})
                return "created"
            except Exception as exc:
                if not self._is_conflict(exc):
                    raise self._translate(exc, where=f"create host {name}") from exc
                # EXISTENT_HOST race: someone created the name since our read — fall through and add.
        # The host object exists but lacks some of these WWNs. Reporting "exists" here would be the
        # silent single-path trap: the object looks green while the unregistered HBAs' paths never
        # light up. Reconcile by ADDing exactly the missing WWNs — never re-adding present ones
        # (the array answers EXISTENT_PATH even for a WWN already on the SAME host — proven live),
        # and never removing or adopting anyone else's.
        try:
            self._require().modifyHost(
                name,
                {"pathOperation": getattr(HPE3ParClient, "HOST_EDIT_ADD", 1), "FCWWNs": missing},
            )
            return "updated"
        except Exception as exc:
            # No conflict-swallow here: `missing` excludes WWNs already on this host, so a 409 now
            # means a real race or another owner — masking it as 'exists' is how the live bug hid.
            raise self._translate(exc, where=f"add {len(missing)} WWN(s) to host {name}") from exc

    def ensure_iscsi_host(self, name: str, iqns: list[str], persona: str = "VMware") -> str:
        """The iSCSI twin of ensure_host: ONE host carrying these iSCSI names (`createhost -iscsi`).
        Returns 'created', 'updated' (the IQNs it lacked were added) or 'exists'. The array takes an
        IQN it has never seen a session from, so this does not wait for a login.

        Raises WsapiError when an IQN belongs to a different host, or when the host of that name
        carries FC WWNs: WSAPI refuses FC and iSCSI names in one request, and this tool does not put
        both on one host (not proven on the array)."""
        if not iqns:
            raise WsapiError(f"no iSCSI name given for host '{name}'")
        members = {m.get("name", ""): m for m in _members(self._require().getHosts()) if m.get("name")}
        owners = {i.lower(): n for n, m in members.items() for i in _iscsi_names(m)}
        other = sorted({owners[i.lower()] for i in iqns if owners.get(i.lower(), name) != name})
        if other:
            raise WsapiError(
                f"iSCSI name(s) for host '{name}' already belong to another host definition: {other}. "
                "Resolve this on the array before provisioning."
            )
        existing = members.get(name)
        if existing is not None and any(p.get("wwn") for p in existing.get("FCPaths") or []):
            raise WsapiError(
                f"host '{name}' exists with FC WWNs; this tool does not add iSCSI names to an FC host. "
                "Use another host name, or add the IQN on the array."
            )
        missing = [i for i in iqns if owners.get(i.lower()) != name]
        if existing is not None and not missing:
            return "exists"
        if existing is None:
            persona_id = _WSAPI_PERSONA.get(persona)
            if persona_id is None:
                raise WsapiError(f"unknown host persona '{persona}' (expected one of {sorted(_WSAPI_PERSONA)})")
            try:
                self._require().createHost(name, iscsiNames=list(iqns), optional={"persona": persona_id})
                return "created"
            except Exception as exc:
                if not self._is_conflict(exc):
                    raise self._translate(exc, where=f"create iSCSI host {name}") from exc
                # EXISTENT_HOST race, as in ensure_host: add the names to the host someone just made.
        try:
            self._require().modifyHost(
                name,
                {"pathOperation": getattr(HPE3ParClient, "HOST_EDIT_ADD", 1), "iSCSINames": missing},
            )
            return "updated"
        except Exception as exc:
            raise self._translate(exc, where=f"add {len(missing)} iSCSI name(s) to host {name}") from exc

    def _existing_set_members(self, getter: Callable[[str], object], name: str) -> list[str] | None:
        """The set's current members, or None if the set does not exist. Sets share ensure_host's
        reconciliation problem: exists-with-missing-members must gain them, never report 'exists'."""
        try:
            data = getter(name)
        except Exception:  # not-found raises in the SDK
            return None
        if isinstance(data, dict):
            return list(data.get("setmembers") or [])
        return list(getattr(data, "setmembers", None) or [])

    def ensure_host_set(self, name: str, members: list[str]) -> str:
        """Create the host set, or ADD any missing members to an existing one (additive only — a
        member someone else added is never removed). 'exists' means every requested member verified."""
        existing = self._existing_set_members(self._require().getHostSet, name)
        if existing is None:
            try:
                self._require().createHostSet(name, setmembers=list(members))
                return "created"
            except Exception as exc:
                if not self._is_conflict(exc):
                    raise self._translate(exc, where=f"create host set {name}") from exc
                existing = self._existing_set_members(self._require().getHostSet, name) or []
        missing = [m for m in members if m not in existing]
        if not missing:
            return "exists"
        try:
            self._require().modifyHostSet(
                name, action=getattr(HPE3ParClient, "SET_MEM_ADD", 1), setmembers=missing,
            )
            return "updated"
        except Exception as exc:
            if self._is_conflict(exc):
                return "exists"
            raise self._translate(exc, where=f"add {len(missing)} host(s) to host set {name}") from exc

    def ensure_volume(self, name: str, cpg: str, size_mib: int, provisioning_type: str) -> str:
        # Data reduction is ONE flag on the Alletra MP WSAPI: `reduce`. The legacy 3PAR pair
        # {"tdvv": True, "compression": True} is rejected outright -- proven live on a B10000
        # (WSAPI 1.15.60 / OS 10.5.60.36): `tdvv` returns code 78 "one of the parameters is
        # required: tpvv,reduce", and `compression` returns code 42 "unrecognized name" in ANY
        # body. `{"reduce": True}` alone is accepted and reads back provisioningType=6 with
        # deduplication on -- so do not "restore" the compression flag; the array has no such field.
        optional = {"reduce": True} if provisioning_type == "reduce" else {"tpvv": True}
        try:
            self._require().createVolume(name, cpg, size_mib, optional=optional)
            return "created"
        except Exception as exc:
            if self._is_conflict(exc):
                return "exists"
            # Live on rack13-ARCUS, 2026-11-16: a 1 PiB volume was refused with HTTP 400 code 28,
            # "client request contains value that is too large". The size is the one number in the body.
            if self._array_code(exc) == "28":
                size = f"{size_mib // 1024} GiB" if size_mib % 1024 == 0 else f"{size_mib} MiB"
                raise WsapiError(
                    f"the array says {size} is more than it can create in one volume. Make it smaller on the "
                    f"sheet's Volumes tab, then build the plan again. Array said: "
                    f"{self._array_reason(exc) or self._safe_str(exc)}"
                ) from exc
            raise self._translate(exc, where=f"create volume {name}") from exc

    def ensure_volume_set(self, name: str, members: list[str]) -> str:
        """Create the VV set, or ADD any missing members to an existing one (additive only)."""
        existing = self._existing_set_members(self._require().getVolumeSet, name)
        if existing is None:
            try:
                self._require().createVolumeSet(name, setmembers=list(members))
                return "created"
            except Exception as exc:
                if not self._is_conflict(exc):
                    raise self._translate(exc, where=f"create volume set {name}") from exc
                existing = self._existing_set_members(self._require().getVolumeSet, name) or []
        missing = [m for m in members if m not in existing]
        if not missing:
            return "exists"
        try:
            self._require().modifyVolumeSet(
                name, action=getattr(HPE3ParClient, "SET_MEM_ADD", 1), setmembers=missing,
            )
            return "updated"
        except Exception as exc:
            if self._is_conflict(exc):
                return "exists"
            raise self._translate(exc, where=f"add {len(missing)} volume(s) to volume set {name}") from exc

    def ensure_vlun(self, volume_name: str, host_name: str, lun: int | None = None) -> str:
        """Export a source to a target as a VLUN. ``volume_name`` is a bare volume or ``set:<vvset>``;
        ``host_name`` is a bare host or ``set:<hostset>``. ``lun=None`` lets the array auto-assign;
        an explicit ``lun`` presents at that number. Returns 'created' or 'exists' (idempotent)."""
        try:
            if lun is None:
                self._require().createVLUN(volume_name, hostname=host_name, auto=True)
            else:
                self._require().createVLUN(volume_name, lun=lun, hostname=host_name, auto=False)
            return "created"
        except Exception as exc:
            if self._is_conflict(exc):
                return "exists"
            raise self._translate(exc, where=f"export {volume_name} to {host_name}") from exc

    # ------------------------------------------------------------------ snapshots (SPEC-023 R5)
    # hpe3parclient 4.5 `createSnapshot` and `createSnapshotOfVolumeSet` (read 2026-11-17, LESSONS 29):
    # plain WSAPI, no SSH. POST /volumes/<vol> and /volumesets/<set> with {action: createSnapshot,
    # parameters: {name, readOnly, expirationHours}}; a set's `name` may be a VV name pattern. Never
    # `retentionHours`: no lock in the first slice (ADR 0016 decision 2). A duplicate name is the array's
    # refusal, never "exists": the plan judged that from its read (LESSONS 29, 37). `@vvname@.initial`
    # over WSAPI is confirmed on the lab before the live run (work packet, live check 2).

    def create_snapshot(self, volume: str, name: str, *, read_only: bool, expire_hours: int) -> None:
        try:
            self._require().createSnapshot(name, volume, optional={"readOnly": read_only, "expirationHours": expire_hours})
        except Exception as exc:
            raise self._translate(exc, where=f"create snapshot {name} of volume {volume}") from exc

    def create_set_snapshot(self, vvset: str, pattern: str, *, read_only: bool, expire_hours: int) -> None:
        try:
            self._require().createSnapshotOfVolumeSet(
                pattern, vvset, optional={"readOnly": read_only, "expirationHours": expire_hours})
        except Exception as exc:
            raise self._translate(exc, where=f"create snapshots {pattern} of volume set {vvset}") from exc

    # ------------------------------------------------------------------ Remote Copy groups & DR (SPEC-016, SPEC-017)
    # The `/remotecopygroups` resource, confirmed on WSAPI 1.15 (B10000, OS 10.5.0, both lab
    # arrays): group records carry `role` 1/2, `targets[].mode` 1 sync / 2 periodic,
    # `targets[].policies.{autoRecover,autoSynchronize,…}`, `targets[].syncPeriod`,
    # `remoteGroupName`, `volumes[].remoteVolumes[].syncStatus` (tests/fixtures/rc_pair/README.md).

    def create_remote_copy_group(self, name: str, *, target: str, mode: str, peer_cpg: str, local_cpg: str = "") -> str:
        """`creatercopygroup -usr_cpg <local> <target>:<peer_cpg> <name> <target>:<sync|periodic>`."""
        targets = [{"targetName": target, "mode": 1 if mode == "sync" else 2, "userCPG": peer_cpg}]
        optional = {"localUserCPG": local_cpg} if local_cpg else None
        try:
            self._require().createRemoteCopyGroup(name, targets, optional=optional)
            return "created"
        except Exception as exc:
            if self._is_conflict(exc):
                return "exists"
            raise self._translate(exc, where=f"create Remote Copy group {name}") from exc

    def set_remote_copy_group(
        self, name: str, *, target: str, period_seconds: int | None, auto_recover: bool, auto_synchronize: bool,
    ) -> str:
        """`setrcopygroup period …` then `setrcopygroup pol …` — as TWO PUTs. Proven live on
        AlletraMP_D22U27 (WSAPI 1.15, 2026-10-09): one body carrying both draws HTTP 400 code 44
        "parameters cannot be present at the same time - policies, syncPeriod". Returns a note when
        the array refused `autoSynchronize` as a WSAPI field (then only `autoRecover` was set)."""
        if period_seconds:
            try:
                self._require().modifyRemoteCopyGroup(name, optional={"targets": [{"targetName": target, "syncPeriod": period_seconds}]})
            except Exception as exc:
                raise self._translate(exc, where=f"set the sync period of Remote Copy group {name}") from exc
        policies = {"autoRecover": auto_recover, "autoSynchronize": auto_synchronize}
        try:
            self._require().modifyRemoteCopyGroup(name, optional={"targets": [{"targetName": target, "policies": policies}]})
            return ""
        except Exception as exc:
            detail = self._safe_str(exc).lower()
            if "autosynchronize" not in detail and "unrecognized" not in detail:
                raise self._translate(exc, where=f"set the policies of Remote Copy group {name}") from exc
        try:
            self._require().modifyRemoteCopyGroup(name, optional={"targets": [{"targetName": target, "policies": {"autoRecover": auto_recover}}]})
        except Exception as exc:
            raise self._translate(exc, where=f"set the policies of Remote Copy group {name}") from exc
        return (f"The array did not accept 'autoSynchronize' for {name}; auto_recover and the "
                f"period were set. Set it on the array: setrcopygroup pol {'auto_synchronize' if auto_synchronize else 'no_auto_synchronize'} {name}")

    def admit_remote_copy_volume(self, group: str, volume: str, *, target: str, secondary: str | None = None) -> str:
        """`admitrcopyvv -createvv <volume> <group> <target>:<secondary>` — the secondary is auto-created."""
        targets = [{"targetName": target, "secVolumeName": secondary or volume}]
        try:
            self._require().addVolumeToRemoteCopyGroup(group, volume, targets, optional={"volumeAutoCreation": True})
            return "created"
        except Exception as exc:
            if self._is_conflict(exc):
                return "exists"
            raise self._translate(exc, where=f"add volume {volume} to Remote Copy group {group}") from exc

    def start_remote_copy_group(self, name: str) -> str:
        try:
            self._require().startRemoteCopy(name)
            return "started"
        except Exception as exc:
            if self._is_conflict(exc) or "already" in self._safe_str(exc).lower():
                return "exists"
            raise self._translate(exc, where=f"start Remote Copy group {name}") from exc

    def stop_remote_copy_group(self, name: str) -> str:
        try:
            self._require().stopRemoteCopy(name)
            return "stopped"
        except Exception as exc:
            if self._is_conflict(exc) or "already" in self._safe_str(exc).lower():
                return "exists"
            raise self._translate(exc, where=f"stop Remote Copy group {name}") from exc

    def remote_copy_dr_action(self, name: str, action: int) -> None:
        """`setrcopygroup failover|recover|restore -f <name>` as the WSAPI disaster-recovery action
        (7 / 9 / 10) on `/remotecopygroups/<name>`. Issued on the array that holds the group under
        that name; the array mirrors the role change to its partner. SPEC-017."""
        try:
            self._require().recoverRemoteCopyGroupFromDisaster(name, action)
        except Exception as exc:
            raise self._translate(exc, where=f"run {_DR_ACTION.get(action, f'action {action}')} on Remote Copy group {name}") from exc
