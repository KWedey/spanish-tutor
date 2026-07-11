# Changelog

All notable changes to this project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.2.0] - 2026-07-10

Portability and correctness overhaul: separate the deterministic engine from the
LLM tutor and the data layer so the system can be ported to a web or mobile host,
and clear out accumulated defects and dead code along the way.

### Added

- Portability layer for a future non-Claude-Code host:
  - `curriculum/manifest.yaml` — a single index of the curriculum data banks and
    content files a port bundles as a versioned content package.
  - `schemas/json/` — JSON Schema exports of the six state schemas for
    client-side validation and type generation.
  - Engine data files that lift previously prose-only logic into portable data:
    `curriculum/decision-weights.yaml` (concept-scoring numbers) and
    `curriculum/error-correction-matrix.yaml` (stage × phase correction modes).
  - A `StateStore` seam in `scripts/shared.py` decoupling engine logic from the
    filesystem backend, so a port can supply its own storage.
  - `docs/engine-api.md` — the engine boundary: the deterministic lifecycle
    contracts (validate, route, score, gates, ladders, metrics, view-model), the
    `StateStore` interface, the prompt-split boundary, and a porting checklist.
- Demo mode: `python3 scripts/init-student.py --demo` seeds a sample mid-course
  learner so the state files and Obsidian vault can be previewed populated,
  without going through onboarding.
- 100+ additional automated tests, expanding coverage of the engine contracts.

### Changed

- CI now runs `ruff` lint alongside the pytest suite and `validate-state.py`.

### Fixed

- 63 verified correctness fixes across the curriculum, scripts, session protocol,
  and state schemas — covering guardrail enforcement, state/router/schema drift,
  data-leak boundaries, onboarding progression, post-session rollback, and vault
  generation.

### Removed

- Deletion pass across the scripts and test suite: unreachable branches,
  speculative code paths, dead fields, and stale test scaffolding.

## [1.1.0] - 2026-05-14

Audit-fix milestone: close the load-management, routing, and curriculum-data gaps
found in the post-v1.0 system audits.

### Added

- Load management: a `study_time_budget` schema plus a homework-minutes budget
  guardrail in `check-session-log.py`, and a `homework_load_rating` field driving
  the D-11 tiered `daily_target` ladder, backed by validator drift detectors.
- Curriculum data: reading prescriptive episodes with topic alignment in the
  media bank; a dialect re-filter advisory wired through the session-log schema
  and validator; voseo/vosotros L1-interference entries.
- An end-to-end routing harness exercising the Step 3 session-routing table.

### Changed

- Acquisition gate split by concept category — numeric gate for CORE (grammar,
  vocabulary), tutor judgment for SECONDARY (LOAD-01 / D-02) — with explicit
  Core vs Secondary phase-transition prerequisites (LOAD-02 / D-03).
- Session-routing precedence inlined into the startup protocol, with warmer,
  non-clinical return-session framing and explicit gap-in-onboarding and
  maintenance weekly-review handling.

### Fixed

- Fluency-day routing now fires correctly in production.
- Routing uses a locale-independent weekday table.
- The `session_type` enum was extended to cover every router output string.

## [1.0.0] - 2026-04-15

Initial system.

### Added

- Prompt-driven Spanish tutor (`CLAUDE.md`) with a per-session startup protocol,
  session routing, and a silent post-session state-update protocol.
- Schema-validated learner state: six state documents (learner profile, skill
  map, schedule, per-day session logs, resource tracker, system health) with
  standalone schema files.
- Phase A–D curriculum: grammar concepts, tiered vocabulary clusters,
  pronunciation guides, activity templates, and onboarding sessions 1–10.
- A decision engine for concept selection, L1-interference preemption, and
  weekly reviews.
- Obsidian vault generation for a browsable roadmap, daily notes, and progress
  dashboards.
- Setup, init, validate, and migrate scripts, plus a comprehensive pytest suite.
- Packaging for a small test group: Windows entry points and a pre-commit hook
  that blocks accidental commits of personal data.

[1.2.0]: https://github.com/KWedey/spanish-tutor/releases/tag/v1.2.0
[1.1.0]: https://github.com/KWedey/spanish-tutor/releases/tag/v1.1.0
[1.0.0]: https://github.com/KWedey/spanish-tutor/releases/tag/v1.0.0
