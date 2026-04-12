# First-Session Dry Run

A manual checklist for verifying a fresh install end-to-end before handing the system to a real learner. Run this from a **fresh clone** — don't reuse a checkout that's already been initialized.

Budget ~60-90 minutes end-to-end. Most of that is the simulated first session itself.

---

## Part 1 — Installation (~5 min)

```bash
git clone <repo-url> language-dryrun
cd language-dryrun
python3 scripts/setup.py
```

- [ ] `setup.py` finishes without errors
- [ ] PyYAML is already installed, or auto-install succeeds
- [ ] Exit code is 0

**If setup fails:** stop here. Fix the install path before continuing. The learner's first experience is this command — it needs to work on a clean machine.

## Part 2 — Pre-flight check (~2 min)

```bash
python3 scripts/preflight.py
```

- [ ] All 6 checks pass (State validation, Key files exist, Test suite, Vault generation, Obsidian ready, Fresh init cycle)
- [ ] Verdict reads **GO**
- [ ] No warnings about missing files or empty directories

**If NO-GO:** investigate the failing check. Never ship a NO-GO state to a learner.

## Part 3 — State inspection (~3 min)

- [ ] `state/learner-profile.yaml` exists and is a blank template
- [ ] `state/skill-map.yaml` exists with unseen concepts
- [ ] `state/schedule.yaml` exists with `last_session_date: null`
- [ ] `state/sessions/` contains only `.gitkeep` (no session logs yet)
- [ ] `state/system-health.yaml` exists
- [ ] `state/resource-tracker.yaml` exists
- [ ] `parking-lot.md` exists
- [ ] `feedback/` contains only `TEMPLATE.md` and `.gitkeep`
- [ ] `vault/Home.md` exists
- [ ] `vault/Getting Started.md` exists
- [ ] `vault/` has 70+ markdown files (`find vault -name '*.md' | wc -l`)

## Part 4 — Obsidian browse (~5 min)

Open the project folder as an Obsidian vault.

- [ ] Obsidian opens without prompting for a "create vault" dialog twice
- [ ] Dataview plugin prompt appears (or is already installed)
- [ ] `Home.md` renders — sections populate (even with blank state, tables are empty but present)
- [ ] `Getting Started.md` renders
- [ ] Roadmap page renders with phase flowcharts
- [ ] Curriculum pages (grammar / vocabulary / pronunciation) are browsable
- [ ] No broken wikilinks (hover over a few — no "create" prompts)

**If broken wikilinks exist:** they'll confuse a real learner. Regenerate the vault (`python3 scripts/generate-vault.py --full`) and recheck.

## Part 5 — Simulated first session (~30-45 min)

Start a fresh Claude Code session in the project directory:

```bash
claude
```

Say hello. The tutor should:

- [ ] Silently run the startup protocol (you won't see this, but the first response shouldn't ask for state it should have read)
- [ ] Detect no session logs exist → route to first-session guide
- [ ] Greet warmly, ask for your name and background
- [ ] Walk through goals, target dialect, schedule
- [ ] Ask about Anki / Dreaming Spanish / other tool setup
- [ ] Introduce the Obsidian vault concept
- [ ] Assign initial homework (Anki deck setup + first video)

Things to watch for:

- [ ] Tutor doesn't hallucinate a previous session
- [ ] Tutor doesn't claim to have read things that don't exist
- [ ] Tutor writes a session log to `state/sessions/YYYY-MM-DD.yaml` at the end
- [ ] Tutor runs `python3 scripts/post-session.sh YYYY-MM-DD` (or runs the steps manually) — exit code 0
- [ ] Session log protocol check passes (expected fields for `first-session` type are populated — or session_type is valid per schema)

**If the tutor skips the startup protocol:** it's a critical failure. The whole system depends on that protocol running every session.

**If the tutor makes up data:** also critical. Inspect `state/` manually after the session and remove any fabricated fields.

## Part 6 — Post-session verification (~5 min)

After the simulated first session ends:

```bash
python3 scripts/validate-state.py
python3 scripts/check-session-log.py $(date +%Y-%m-%d)
```

- [ ] `validate-state.py` reports 0 warnings, 0 failures
- [ ] `check-session-log.py` passes (or only warns about empty fields that are legitimately empty for session 1)
- [ ] `state/sessions/YYYY-MM-DD.yaml` exists
- [ ] `state/learner-profile.yaml` has been populated (name, goals, etc.)
- [ ] `state/schedule.yaml` `last_session_date` is today
- [ ] A git commit was created for the session
- [ ] Vault was regenerated (daily note exists in `vault/Daily/`)

## Part 7 — Second-session smoke test (~10 min)

Start a new Claude Code session. Greet briefly.

- [ ] Tutor recognizes you from the previous session
- [ ] Tutor references something specific from session 1 (your name, a goal, a tool you picked)
- [ ] Tutor does NOT re-run the onboarding questions
- [ ] Tutor routes to the second onboarding session (or standard, depending on flow)

End the session. Verify:

- [ ] A new session log exists at `state/sessions/YYYY-MM-DD.yaml`
- [ ] `skill-map.yaml` reflects any changes from today
- [ ] No duplicate entries in `learner-profile.yaml`

---

## Cleanup

```bash
cd ..
rm -rf language-dryrun
```

Or keep the dry-run folder around as a reference — it's a working example of what a real learner's state should look like after session 2.

## When to re-run this checklist

- Before every release that touches `scripts/setup.py`, `scripts/init-student.py`, `scripts/generate-vault.py`, or the startup protocol in `CLAUDE.md`
- After any schema change
- After any change to the first-session or onboarding guides
- Before handing the system to a new learner for the first time

## Common failure modes

| Symptom | Likely cause | Fix |
|---------|--------------|-----|
| `setup.py` hangs on pip install | Missing network / pip config | Rerun with `--verbose` |
| Vault has 0 files after setup | `generate-vault.py --full` errored silently | Run it manually and read stderr |
| Tutor asks "who are you?" on session 2 | Session 1 didn't write `learner-profile.yaml` | Inspect post-session logs, re-run startup protocol |
| `check-session-log.py` fails on session 1 | First-session guide doesn't populate `decision_engine_trace` (expected — that's session 2+) | Tweak expected fields for `first-session` type, or accept the warning |
| Obsidian prompts to create files when clicking wikilinks | Generated links point to paths that don't exist | Check `generate-vault.py` wikilink output — usually a dataview path issue |
| `validate-state.py` fails on blank state | Schema and template are out of sync | Run `pytest tests/test_init_student.py` to pin down the drift |
