# ADR 0032 — Typed run events and generated frontend types

**Status:** accepted 2026-11-21 · **Issue:** BL-65 ·
**Relates to:** [ADR 0028](0028-one-engineering-standard-enforced-by-the-gate.md) (STANDARD T1, T2, T4),
[ADR 0030](0030-the-gate-fails-where-it-only-warned.md) (gate config checks)

## Context

STANDARD T4 asks for run events to carry typed data in the OpenAPI schema and for the frontend's
API and event types to be generated from that schema rather than maintained by hand. Today:

- The backend emits 57 event types across 83 call sites, passing plain `dict` payloads through
  `RunCoordinator.emit`. Nothing checks that the payload matches the event type.
- `frontend/src/api.ts` maintains 123 hand-written TypeScript definitions of backend models, and
  step pages cast `event.data` with `as <Type>` in 27 places. Two sides had already drifted:
  `GreenLakeStep.tsx` read a `data.region` field that `step.completed` never carried, and
  `SnapshotAction.state` allowed `update` on the backend while the page only mapped three states.
- Historical SQLite databases hold stored events from older releases whose payloads omit fields
  added later (for example `in_run` on a discovered host, where absent means "decide from sources"
  rather than `false`) or carry retired keys. Validating stored rows on read would either fill
  defaults no device ever reported (violating Q2) or fail to reopen an old run.

## Decision

1. **One event registry in `domain/events.py`.** Each of the 57 event types is registered as an
   invariant `EventType[D]` pairing its wire name with its pydantic payload model (22 models, with
   `NoData` forbidding extra fields for the 20 plain events). `RunCoordinator.emit` in
   `application/runs/coordinator.py` has overloads for `EventType[NoData]` (no data argument) and
   `EventType[D]` (requiring a `D`), so pyright rejects wrong, missing, or misspelt payloads at
   every emit site. Raw dict storage stays in private `_append`, called only by `emit` and
   `recover_interrupted_apply` (which must surface an older in-progress apply's removal set without
   validating).
2. **Stored events are not migrated and not validated on read.** `RunEvent.data` stays a dict in
   SQLite and on the bus, and `GET /runs/{run_id}/events` keeps `response_model=EventListResponse`
   so old or unknown stored rows return unchanged. Backend readers of stored events continue reading
   dicts and parsing models at the point of use where needed; this is a recorded exception to
   STANDARD T1 for the historical `run_events` table.
3. **OpenAPI documents events as a discriminated union.** `run_event_list` in `api/schemas.py`
   builds `RunEventList` from `EVENT_TYPES`, discriminated on `event_type`, and attaches it to
   `GET /runs/{run_id}/events` via `responses={200: {"model": run_event_list()}}` in `api/app.py`
   (documentation only; runtime behaviour unchanged).
4. **Generated TypeScript types committed outside `frontend/src`.** `scripts/api_types.py` exports
   FastAPI's OpenAPI JSON with sorted keys and runs `openapi-typescript` (pinned at `7.13.0` in
   `frontend/package.json`) to write `frontend/generated/api.ts`, marked `linguist-generated=true`
   in `.gitattributes`. Keeping it outside `frontend/src` keeps it out of M2 (`file-size`) and
   eslint while `tsc` still checks it through imports.
5. **Gate step and reproducible dev pins (STANDARD rule 4).**
   - `scripts/check.py` adds the `api-types` step (`scripts/api_types.py --check`) to
     `FRONTEND_STEPS` and adds `scripts/api_types.py` to `GATE_FILES`.
   - `frontend/package.json` adds `generated/**` to `knip.ignore` and `openapi-typescript` to
     `knip.ignoreDependencies` (invoked from `scripts/api_types.py`, like `pyright`).
   - `pyproject.toml` pins `fastapi==0.163.1` and `pydantic==2.14.3` exactly in the `dev` extra so
     every developer machine generates byte-identical OpenAPI schemas and `frontend/generated/api.ts`.
     The runtime dependency ranges in `[project].dependencies` are unchanged.
6. **Event evolution rule.** A field added to an event payload in `domain/events.py` gets a default.
   A payload field or event type is never renamed or given a new meaning; a new meaning gets a new
   event type.
7. **Remaining untyped routes documented without changing runtime serialisation.** `GET /app/profile`,
   `POST /init-sheet/upload` and the console routes carry Pydantic documentation models in
   `api/schemas.py` attached via `responses={200: {"model": ...}}` only — never adding or changing
   `response_model=` on `/app/profile`, `/init-sheet/upload` or `/runs/from-sheet` (the
   initialisation track), so their response bytes cannot change. Upload models (`UploadedDsccSetup`,
   `UploadedWorkItem`, `InitSheetUploadResult`) are derived with `create_model` from `domain/models.py`
   and `InitSheetUploadResponse` rather than copied by hand, and `CommandRecord` is shared with
   `adapters/command_log.py`. Strict contract tests (`model_validate_json(..., strict=True)` plus
   round-trip JSON equality) pin each documented model against real responses in both `full` and
   `init-only` profiles. In `frontend/src/api.ts`, every wire type is an alias of
   `frontend/generated/api.ts`; only `CredentialOverride` (a form value) stays hand-written.

## Consequences

- Every emit site is checked statically by pyright; every page read of an API response or event
  payload is checked by `tsc` against the backend's schema.
- Adding or changing an event payload requires regenerating `frontend/generated/api.ts` with
  `scripts/api_types.py`; forgetting fails the `api-types` gate step in about two seconds.
- Nothing new runs at build time or on the jump box: `frontend/generated/api.ts` is type-only, so
  the Vite production bundle does not include it.
- Landing the gate changes requires `ALLOW_CONFIG=1` on the branch under STANDARD rule 4.
