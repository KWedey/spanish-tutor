#!/usr/bin/env bash
# post-session.sh — Automate mechanical post-session steps.
#
# Runs vault generation, session archival, state validation, session log
# well-formedness + protocol-compliance checks, and (optionally) git commit.
# Reduces the tutor agent's post-session responsibility from ~15 manual steps
# to ~7.
#
# Usage:
#   scripts/post-session.sh 2026-04-11
#   scripts/post-session.sh --dry-run 2026-04-11
#   scripts/post-session.sh --no-commit 2026-04-11

set -e

# ---------------------------------------------------------------------------
# Resolve project root (parent of scripts/)
# ---------------------------------------------------------------------------

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

# ---------------------------------------------------------------------------
# Color helpers (respect non-TTY output)
# ---------------------------------------------------------------------------

if [ -t 1 ]; then
    GREEN='\033[32m'
    YELLOW='\033[33m'
    RED='\033[31m'
    DIM='\033[2m'
    RESET='\033[0m'
else
    GREEN='' YELLOW='' RED='' DIM='' RESET=''
fi

info()  { printf "%s\n" "${GREEN}[OK]${RESET}   $1"; }
warn()  { printf "%s\n" "${YELLOW}[WARN]${RESET} $1"; }
error() { printf "%s\n" "${RED}[FAIL]${RESET} $1" >&2; }
step()  { printf "%s\n" "${DIM}---${RESET} $1"; }

# ---------------------------------------------------------------------------
# Parse arguments
# ---------------------------------------------------------------------------

DRY_RUN=false
NO_COMMIT=false
DATE=""

while [[ $# -gt 0 ]]; do
    case "$1" in
        --dry-run)  DRY_RUN=true; shift ;;
        --no-commit) NO_COMMIT=true; shift ;;
        -h|--help)
            echo "Usage: $0 [--dry-run] [--no-commit] YYYY-MM-DD"
            echo ""
            echo "Automates post-session mechanical steps:"
            echo "  1. Generate/update vault content"
            echo "  2. Archive session logs older than 60 days"
            echo "  3. Validate state files"
            echo "  4. Verify session log exists and is well-formed"
            echo "  5. Check session log protocol compliance"
            echo "  5b. Aggregate recast_uptake_stats into skill-map"
            echo "  5c. Reset study_time_budget.today_stretch to 0"
            echo "  6. Git commit all changes"
            echo ""
            echo "Options:"
            echo "  --dry-run     Show what would be done without executing"
            echo "  --no-commit   Run all steps except the git commit"
            echo "  -h, --help    Show this help message"
            exit 0
            ;;
        *)
            if [[ -z "$DATE" ]]; then
                DATE="$1"
            else
                error "Unexpected argument: $1"
                exit 1
            fi
            shift
            ;;
    esac
done

# ---------------------------------------------------------------------------
# Validate date argument
# ---------------------------------------------------------------------------

if [[ -z "$DATE" ]]; then
    error "Missing required date argument (YYYY-MM-DD)"
    echo "Usage: $0 [--dry-run] [--no-commit] YYYY-MM-DD"
    exit 1
fi

if ! [[ "$DATE" =~ ^[0-9]{4}-[0-9]{2}-[0-9]{2}$ ]]; then
    error "Invalid date format: $DATE (expected YYYY-MM-DD)"
    exit 1
fi

# ---------------------------------------------------------------------------
# Dry-run wrapper — prints instead of executing when --dry-run is set
# ---------------------------------------------------------------------------

run() {
    if $DRY_RUN; then
        printf "${YELLOW}[dry-run]${RESET} Would run: %s\n" "$*"
        return 0
    fi
    "$@"
}

# ---------------------------------------------------------------------------
# Step 0: Snapshot state (must run before any writes; provides rollback point)
# ---------------------------------------------------------------------------

# Auto-rollback trap: if any step fails AFTER the snapshot is taken, restore
# state from that snapshot. This wires the rollback the script header has always
# promised but never performed (audit H5) — the explicit `exit 1` failure paths
# below all route through this EXIT trap.
SNAPSHOT_TAKEN=false
ROLLED_BACK=false
on_exit() {
    local code=$?
    if $DRY_RUN || ! $SNAPSHOT_TAKEN || $ROLLED_BACK || [[ $code -eq 0 ]]; then
        exit "$code"
    fi
    ROLLED_BACK=true
    error "post-session.sh failed (exit $code) after the Step 0 snapshot."
    error "Rolling back state to the snapshot taken at the start of this run..."
    if python3 "$ROOT/scripts/snapshot-state.py" rollback; then
        error "Rollback complete. Fix the issue and re-run post-session.sh."
    else
        error "AUTOMATIC ROLLBACK FAILED — restore manually: python3 scripts/snapshot-state.py rollback"
    fi
    exit "$code"
}
trap on_exit EXIT

step "Step 0/8: Snapshotting state before writes"
if $DRY_RUN; then
    printf "${YELLOW}[dry-run]${RESET} Skipping snapshot (dry-run writes nothing)\n"
else
    if ! python3 "$ROOT/scripts/snapshot-state.py" snapshot; then
        error "Snapshot failed — post-session aborted. State was not modified."
        error "Fix the snapshot error before running post-session.sh again."
        exit 1
    fi
    SNAPSHOT_TAKEN=true
    info "State snapshot created"
fi

# ---------------------------------------------------------------------------
# Step 1: Generate/update vault content
# ---------------------------------------------------------------------------

step "Step 1/8: Generating vault content for $DATE"
run python3 "$ROOT/scripts/generate-vault.py" --session --date "$DATE"
if ! $DRY_RUN; then info "Vault generation complete"; fi

# ---------------------------------------------------------------------------
# Step 2: Archive old session logs
# ---------------------------------------------------------------------------

step "Step 2/8: Archiving session logs older than 60 days"
run python3 "$ROOT/scripts/archive-sessions.py"
if ! $DRY_RUN; then info "Session archival complete"; fi

# ---------------------------------------------------------------------------
# Step 3: Validate state files
# ---------------------------------------------------------------------------

step "Step 3/8: Validating state files"
run python3 "$ROOT/scripts/validate-state.py"
if ! $DRY_RUN; then info "State validation passed"; fi

# ---------------------------------------------------------------------------
# Step 4: Verify session log exists and is well-formed
# ---------------------------------------------------------------------------

SESSION_LOG="$ROOT/state/sessions/$DATE.yaml"

step "Step 4/8: Verifying session log at state/sessions/$DATE.yaml"
if $DRY_RUN; then
    printf "${YELLOW}[dry-run]${RESET} Would verify: %s\n" "$SESSION_LOG"
else
    if [[ ! -f "$SESSION_LOG" ]]; then
        error "Session log not found: state/sessions/$DATE.yaml"
        exit 1
    fi

    # Basic YAML well-formedness check via Python
    if ! python3 - "$SESSION_LOG" <<'PYEOF'
import sys, yaml
try:
    with open(sys.argv[1]) as f:
        data = yaml.safe_load(f)
    if not isinstance(data, dict):
        print('Session log is not a YAML mapping', file=sys.stderr)
        sys.exit(1)
except yaml.YAMLError as e:
    print(f'Session log has invalid YAML: {e}', file=sys.stderr)
    sys.exit(1)
PYEOF
    then
        error "Session log is not valid YAML: state/sessions/$DATE.yaml"
        exit 1
    fi

    info "Session log verified: state/sessions/$DATE.yaml"
fi

# ---------------------------------------------------------------------------
# Step 4.5: Transcript presence check (FAIL for session_number > 1)
# ---------------------------------------------------------------------------

step "Step 4.5/8: Checking transcript file for $DATE"
if $DRY_RUN; then
    printf "${YELLOW}[dry-run]${RESET} Would check: transcripts/%s.md\n" "$DATE"
else
    TRANSCRIPT="$ROOT/transcripts/$DATE.md"
    SESSION_NUMBER=$(python3 - "$SESSION_LOG" <<'PYEOF'
import sys, yaml
with open(sys.argv[1]) as f:
    data = yaml.safe_load(f)
# `or 1`: a null session_number would yield "None" and the bash `-gt` compare
# would silently treat it as session 1, skipping the transcript gate (audit LOW).
print(data.get('session_number') or 1)
PYEOF
    )

    if [[ ! -f "$TRANSCRIPT" ]]; then
        if [[ "$SESSION_NUMBER" -gt 1 ]]; then
            error "Transcript file not found: transcripts/$DATE.md"
            error "Session number is $SESSION_NUMBER (>1) — transcript is required."
            error "Save the session conversation to transcripts/$DATE.md before re-running."
            exit 1
        else
            warn "Transcript file not found: transcripts/$DATE.md (session 1 — exempt)"
        fi
    else
        info "Transcript found: transcripts/$DATE.md"
    fi
fi

# ---------------------------------------------------------------------------
# Step 5: Check session log protocol compliance
# ---------------------------------------------------------------------------
#
# Deeper than Step 4 (YAML well-formedness). This catches silent protocol
# drift — the tutor agent skipping steps in the 19-step post-session
# protocol. Missing expected fields → FAIL. Empty expected fields → WARN
# (use --strict on check-session-log.py directly to treat empties as fails).

step "Step 5/8: Checking session log protocol compliance"
if $DRY_RUN; then
    printf "${YELLOW}[dry-run]${RESET} Would run: scripts/check-session-log.py %s\n" "$DATE"
else
    if python3 "$ROOT/scripts/check-session-log.py" "$DATE"; then
        info "Session log protocol check passed"
    else
        error "Session log is missing fields expected for its session type."
        error "Populate them in state/sessions/$DATE.yaml before committing."
        exit 1
    fi
fi

# ---------------------------------------------------------------------------
# Step 5b: Aggregate recast_uptake_stats into skill-map (D-07)
# ---------------------------------------------------------------------------
#
# Folds today's recasts[] entries from the session log into each grammar
# concept's recast_uptake_stats counters in skill-map.yaml. Additive write
# on top of the Step 0 snapshot — if this fails, snapshot provides rollback.

step "Step 5b/8: Aggregating recast_uptake_stats into skill-map"
if $DRY_RUN; then
    printf "${YELLOW}[dry-run]${RESET} Would aggregate recasts from %s\n" "$SESSION_LOG"
else
    if ! python3 - "$SESSION_LOG" "$ROOT/state/skill-map.yaml" "$DATE" <<'PYEOF'
import yaml, sys, os
from pathlib import Path

LOG  = Path(sys.argv[1])
SM   = Path(sys.argv[2])
DATE = sys.argv[3]

def _leading_header(text):
    """Return the top comment/blank-line block (the schema-pointer header)."""
    out = []
    for ln in text.splitlines(keepends=True):
        if ln.lstrip().startswith("#") or not ln.strip():
            out.append(ln)
        else:
            break
    return "".join(out)

def _atomic_write_yaml(path, data, header):
    body = yaml.safe_dump(data, sort_keys=False, allow_unicode=True)
    tmp = path.with_name(path.name + ".tmp")
    tmp.write_text(header + body, encoding="utf-8")
    os.replace(tmp, path)

with LOG.open() as f:
    session = yaml.safe_load(f) or {}
recasts = session.get("recasts") or []
if not recasts:
    print("No recasts to aggregate")
    sys.exit(0)

_sm_header = _leading_header(SM.read_text(encoding="utf-8"))
with SM.open() as f:
    sm = yaml.safe_load(f) or {}
grammar = sm.setdefault("grammar", {})

aggregated = 0
for r in recasts:
    cid = r.get("concept_id")
    uptake = r.get("uptake")
    if not cid or cid not in grammar:
        continue
    entry = grammar[cid]
    stats = entry.setdefault("recast_uptake_stats", {
        "recasts_given": 0, "landed": 0, "missed": 0, "partial": 0,
        "last_updated": None,
    })
    stats["recasts_given"] = (stats.get("recasts_given") or 0) + 1
    if uptake in ("landed", "missed", "partial"):
        stats[uptake] = (stats.get(uptake) or 0) + 1
    stats["last_updated"] = DATE
    aggregated += 1

_atomic_write_yaml(SM, sm, _sm_header)
print(f"Aggregated {aggregated} recasts into skill-map")
PYEOF
    then
        error "Recast aggregation failed"
        exit 1
    fi
    info "Recast aggregation complete"
fi

# ---------------------------------------------------------------------------
# Step 5c: Reset today_stretch to 0 (D-04 ephemeral semantic)
# ---------------------------------------------------------------------------
#
# today_stretch is a per-session extension above daily_maximum. Clearing it
# at end-of-session ensures a one-day "extra today" doesn't silently persist.
# Pattern: quoted heredoc + sys.argv per CR-01 (commits c4139b2, e273529).

step "Step 5c/8: Resetting study_time_budget.today_stretch to 0"
if $DRY_RUN; then
    printf "${YELLOW}[dry-run]${RESET} Would reset today_stretch in schedule.yaml\n"
else
    if ! python3 - "$ROOT/state/schedule.yaml" <<'PYEOF'
import yaml, sys, os
from pathlib import Path
SCHED = Path(sys.argv[1])
if not SCHED.exists():
    print("No schedule.yaml found - skipping today_stretch reset")
    sys.exit(0)

def _leading_header(text):
    out = []
    for ln in text.splitlines(keepends=True):
        if ln.lstrip().startswith("#") or not ln.strip():
            out.append(ln)
        else:
            break
    return "".join(out)

_header = _leading_header(SCHED.read_text(encoding="utf-8"))
with SCHED.open() as f:
    sched = yaml.safe_load(f) or {}
stb = sched.get("study_time_budget")
if not isinstance(stb, dict):
    print("No study_time_budget configured - skipping today_stretch reset")
    sys.exit(0)
prev = stb.get("today_stretch", 0) or 0
stb["today_stretch"] = 0
_body = yaml.safe_dump(sched, sort_keys=False, allow_unicode=True)
_tmp = SCHED.with_name(SCHED.name + ".tmp")
_tmp.write_text(_header + _body, encoding="utf-8")
os.replace(_tmp, SCHED)
print(f"today_stretch reset: {prev} -> 0")
PYEOF
    then
        error "today_stretch reset failed"
        exit 1
    fi
    info "today_stretch reset to 0"
fi

# ---------------------------------------------------------------------------
# Step 5d: Recompute derived pedagogy metrics (QR-P1/QR-P2)
# ---------------------------------------------------------------------------
#
# Updates the calibration counters that the decision engine + CLAUDE.md read
# but nothing previously wrote: per-concept regression_session_count in
# skill-map, and concepts_requiring_reteach_total / sessions_rated_too_easy_30d
# / sessions_rated_too_hard_30d in system-health. Deterministic — derived from
# state, not the LLM. Additive on top of the Step 0 snapshot.

step "Step 5d/8: Recomputing derived pedagogy metrics"
if $DRY_RUN; then
    printf "${YELLOW}[dry-run]${RESET} Would recompute regression/reteach/difficulty metrics\n"
else
    if ! python3 "$ROOT/scripts/recompute-metrics.py" "$DATE"; then
        error "Metric recomputation failed"
        exit 1
    fi
    info "Pedagogy metrics recomputed"
fi

# ---------------------------------------------------------------------------
# Step 6: Git commit
# ---------------------------------------------------------------------------

if $NO_COMMIT; then
    step "Step 6/8: Skipping git commit (--no-commit)"
else
    step "Step 6/8: Committing changes"
    if $DRY_RUN; then
        printf "${YELLOW}[dry-run]${RESET} Would run: git add + git commit\n"
    else
        cd "$ROOT"
        git add state/ vault/ transcripts/ progress-reports/ journal/
        # Only commit if there are staged changes
        if git diff --cached --quiet; then
            warn "No staged changes to commit"
        else
            git commit -m "session $DATE: [auto-committed by post-session.sh]"
            info "Changes committed"
        fi
    fi
fi

# ---------------------------------------------------------------------------
# Done
# ---------------------------------------------------------------------------

echo ""
if $DRY_RUN; then
    printf "${YELLOW}Dry run complete.${RESET} No changes were made.\n"
else
    info "Post-session steps complete for $DATE"
fi
