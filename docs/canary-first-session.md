# Canary: First Real Tutoring Session

**Purpose:** v1.1 audit-fix shipped 2026-05-13. Phases 1-7 (38 plans, 455 tests passing,
all validate-state checks green) are infrastructure that has never run end-to-end against a real
tutoring session. The first session is a canary — its job is to exercise every code
path under realistic conditions and surface the latent failures.

This protocol exists so the implementer (also the learner) can run the canary without
re-inventing pre-flight, during-session note-taking, post-flight verification, or
rollback while in the middle of a session.

---

## Pre-session

Run these checks **before** invoking the tutor agent (15-20 min).

1. **Confirm clean tree.**
   ```bash
   git status   # expect: nothing to commit, working tree clean
   ```
   If anything is staged or modified, decide whether to commit, stash, or abort.

2. **Run validate-state.**
   ```bash
   python3 scripts/validate-state.py
   ```
   Must report all checks passing (record the exact PASS count here as your pre-session baseline).
   Any FAIL is a STOP — fix before starting the canary.

3. **Take a Step 0 snapshot manually.**
   ```bash
   python3 scripts/snapshot-state.py snapshot
   ls -la state/.snapshot/
   ```
   This is the rollback target. The first-real-session post-session.sh will run
   this automatically (per ENFORCE-01), but doing it manually before the canary
   gives you a labelled snapshot to compare against.

4. **Run the routing harness (added by 08-03) against the current state.**
   ```bash
   python3 scripts/route_session.py state/
   ```
   Confirm the printed session-type matches your expectation (probably
   `first-session` if no session logs exist; otherwise the appropriate row).
   If it doesn't, STOP — the routing layer is wrong and the canary will route
   to the wrong tutor-guide.

5. **Verify pre-commit hook is active.**
   ```bash
   git config --get core.hooksPath   # expect: .githooks
   ```
   If empty, run `python3 scripts/setup.py` to restore the hook (LEAK
   protection is inert otherwise). The pre-commit hook is what stops a leaked
   `learner-profile.yaml` from reaching the remote.

6. **Run a real pre-commit hook fire-test** (NOT a dry-run — `git commit --dry-run`
   does not invoke the hook):
   ```bash
   git add -f state/learner-profile.yaml
   git commit -m "canary hook fire-test" || echo "hook fired as expected"
   git reset HEAD state/learner-profile.yaml
   ```
   Expect: the commit FAILS because the pre-commit hook blocks the leaked-data
   pattern, and the error message names the blocked pattern (LEAK rule).
   If the commit succeeds, the hook is inert — STOP, run `python3 scripts/setup.py`,
   verify `core.hooksPath` again, and re-run this fire-test before continuing.

7. **Have rollback materials ready.**
   - Terminal pane #1: tutor session
   - Terminal pane #2: open with `state/.snapshot/` listed and the rollback
     command pre-typed (see Rollback section below)
   - Note today's date as `YYYY-MM-DD` — you'll use it for session-log
     filename and the snapshot label.
   - Create the observations sink: `mkdir -p docs/canary-observations/` if
     not present. Observations live OUTSIDE `state/` (which is gitignored)
     so the post-session branch-commit (Step 6 below) works without
     `--force` on a gitignored path.

---

## During session

Run the tutor session as normal. In parallel, capture observations in
`docs/canary-observations/YYYY-MM-DD.md` (committed to a `canary/...` branch
in Post-session Step 6 — NOT gitignored; this file is a triage artifact, not
learner state).

For each CLAUDE.md startup step (Steps 1, 1b, 2, 3, 4), note:

- **What loaded.** (Did the tutor cite the files it was supposed to read?
  If it skipped a load, that's a bug.)
- **What failed.** (Any error message visible to the tutor or to you. Capture
  verbatim — partial transcriptions are useless for triage.)
- **What was slow.** (>2 seconds for a single file read is suspicious.
  >5 seconds is a finding.)
- **What required manual fix.** (Did you have to intervene? What did you do?
  This is a candidate for a v1.2 plan.)

Specific surfaces to watch for (the latent paths from each phase):

| Phase | Latent path | Watch for |
|-------|-------------|-----------|
| 1 LEAK | pre-commit hook on every staged file | False-positives on legit edits, false-negatives on personal-data leaks |
| 2 WIN | only relevant on Windows | Skip on macOS canary |
| 2.1 HOOK | hook activation chain | Already validated above; should be no-op |
| 3 ENFORCE | post-session.sh Step 0 snapshot, transcript presence check | Snapshot taken? Transcript written? |
| 4 ENGINE | recast_uptake / learner_interest / metalinguistic protocol | Tutor uses INTEREST in decision-engine? Records recasts? |
| 5 LOAD | study_time_budget / homework_load_rating / D-11 ladder | Does the tutor warn or fail on over-budget homework? |
| 6 ROUTE | Step 3 routing + return-session warmth | (Won't apply on canary — no prior gap. Verify Step 3 chose `first-session`.) |
| 7 CURR | reading prescriptive_episodes / dialect advisory | (Won't apply unless reading homework is assigned. Skip on canary.) |

When the session ends, write the observations file in full before
running `post-session.sh`.

---

## Post-session

Run these checks **after** the session ends (10-15 min).

1. **Run post-session.sh.**
   ```bash
   bash scripts/post-session.sh $(date -u +%Y-%m-%d)
   ```
   Expect: Step 0 snapshot taken, validate-state PASS, session-log written,
   transcript saved, commit prepared (or warnings about gitignored state).
   Any FAIL is a finding.

2. **Run check-session-log.py manually.**
   ```bash
   python3 scripts/check-session-log.py $(date -u +%Y-%m-%d)
   ```
   The script takes a **date**, not a path — it builds `state/sessions/<date>.yaml`
   itself. Must pass. If `dialect_advisory` (added in 08-02) fires falsely or
   misses, that's a v1.2 fix candidate.

3. **Verify vault generation.**
   ```bash
   python3 scripts/generate-vault.py --session --date $(date -u +%Y-%m-%d)
   ls -la vault/Daily/
   ```
   Expect: Home + Roadmap refreshed and existing notes re-stamped (exit 0).
   Note: `--session` does **not** create today's daily note — per CLAUDE.md
   State Updates step 12a the tutor writes `vault/Daily/<date>.md` manually
   (with `generated: true` frontmatter). Confirm that file exists *after* the
   tutor's manual write, not as output of this script.

4. **Confirm transcript captured.**
   ```bash
   ls -la transcripts/$(date -u +%Y-%m-%d).md
   ```
   If missing, that's an ENFORCE-09 regression — post-session.sh should
   have FAILed earlier.

5. **Re-run validate-state.**
   ```bash
   python3 scripts/validate-state.py
   ```
   Must report the same PASS count as the pre-session baseline. If any check that passed pre-session now FAILs,
   that's a state-corruption finding — see Rollback below.

6. **Commit observations.**
   Add `docs/canary-observations/YYYY-MM-DD.md` to a NEW branch
   `canary/YYYY-MM-DD-observations` (not main; observations live in
   project memory, not in the state surface). Push, file an issue or
   start a v1.2 plan.

---

## Rollback

Run if any state file is corrupted or contradicts itself, OR if the tutor
session ends in an unrecoverable error.

1. **Stop.** Do not run more scripts. Do not commit anything.

2. **Identify the available snapshots.**
   ```bash
   python3 scripts/snapshot-state.py list
   ```
   `rollback` restores the **most recent** snapshot (the post-session.sh one if
   it ran, otherwise the pre-session manual snapshot from Pre-session step 3).
   There is no per-label restore — the tool always targets the latest snapshot.

3. **Roll back.**
   ```bash
   python3 scripts/snapshot-state.py rollback
   ```
   This restores skill-map / schedule / profile to the snapshot; any session
   log written after the snapshot is preserved (for transparency). Confirm by
   running `validate-state.py` immediately after — it must report the same
   PASS count it reported pre-session.

4. **Diff and document.**
   ```bash
   git diff HEAD -- state/    # see what the canary changed
   ```
   Write what corrupted into `docs/canary-observations/YYYY-MM-DD.md`
   under a `## Rollback Cause` heading. This is the next-most-important
   piece of evidence for the v1.2 plan.

5. **Re-attempt or stop.**
   - If the cause is understood and unlikely to recur, you may re-run.
   - Otherwise, stop the canary, file the issue, and address it in v1.2
     before retrying.

---

## Success Definition

Split into **infrastructure success** (commands return 0 — testable, named in this protocol) and **session success** (judgment, owned by Kyle the learner).

### Infrastructure success (the only thing this protocol asserts)

All of the following return exit code 0 and produce the expected artifact:

1. Pre-session steps 2-6 all return 0 (validate-state, snapshot, routing-harness, hook-config check, hook fire-test).
2. `bash scripts/post-session.sh $(date -u +%Y-%m-%d)` returns 0.
3. `python3 scripts/check-session-log.py state/sessions/$(date -u +%Y-%m-%d).yaml` returns 0.
4. `python3 scripts/generate-vault.py --session --date $(date -u +%Y-%m-%d)` returns 0.
5. `python3 scripts/validate-state.py` returns 0 (same PASS count as the pre-session baseline) AFTER the session.
6. `transcripts/$(date -u +%Y-%m-%d).md` exists and is non-empty.
7. `docs/canary-observations/$(date -u +%Y-%m-%d).md` exists (the protocol REQUIRES Kyle to capture observations, even if "all clean — nothing surfaced").

If any of these 7 fail, the infrastructure surfaced a real bug. File it in a v1.2 plan or scratch issue and either fix-and-rerun or stop.

### Session success (judgment — not asserted here)

Kyle decides whether the tutoring session itself was useful — was the lesson at the right level, did the corrections land, did the tutor's startup-protocol output match what the docs say should happen? This is signal for `feedback/` notes, not a checkbox in this protocol.

### Severity rubric for canary findings

Use this when triaging items captured in `canary-observations-YYYY-MM-DD.md`:

| Severity | Definition | Action |
|----------|-----------|--------|
| **BLOCKER** | Infrastructure check failed; data corrupted; rollback executed | v1.2 plan must fix before next canary attempt |
| **HIGH** | Infrastructure passed but a CLAUDE.md/decision-engine rule fired incorrectly (e.g., routed to wrong session type, broke a load guardrail) | v1.2 plan within 1 session |
| **MEDIUM** | UX friction (tutor was slow, awkward prompt, doc cross-reference broke mid-session) | Triage in next weekly review |
| **LOW** | Cosmetic (a word in a guide that lands awkwardly; a minor formatting issue) | Parking lot |

The rubric exists so an "every observation becomes a v1.2 plan" failure mode doesn't happen. MEDIUM and LOW findings go to weekly review / parking lot, not to a planning phase.
