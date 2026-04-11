#!/usr/bin/env bash
# post-session.sh — Automate mechanical post-session steps.
#
# Runs vault generation, session archival, state validation, session log
# verification, and (optionally) git commit. Reduces the tutor agent's
# post-session responsibility from ~15 manual steps to ~7.
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
            echo "  5. Git commit all changes"
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
# Step 1: Generate/update vault content
# ---------------------------------------------------------------------------

step "Step 1/5: Generating vault content for $DATE"
run python3 "$ROOT/scripts/generate-vault.py" --session --date "$DATE"
if ! $DRY_RUN; then info "Vault generation complete"; fi

# ---------------------------------------------------------------------------
# Step 2: Archive old session logs
# ---------------------------------------------------------------------------

step "Step 2/5: Archiving session logs older than 60 days"
run python3 "$ROOT/scripts/archive-sessions.py"
if ! $DRY_RUN; then info "Session archival complete"; fi

# ---------------------------------------------------------------------------
# Step 3: Validate state files
# ---------------------------------------------------------------------------

step "Step 3/5: Validating state files"
run python3 "$ROOT/scripts/validate-state.py"
if ! $DRY_RUN; then info "State validation passed"; fi

# ---------------------------------------------------------------------------
# Step 4: Verify session log exists and is well-formed
# ---------------------------------------------------------------------------

SESSION_LOG="$ROOT/state/sessions/$DATE.yaml"

step "Step 4/5: Verifying session log at state/sessions/$DATE.yaml"
if $DRY_RUN; then
    printf "${YELLOW}[dry-run]${RESET} Would verify: %s\n" "$SESSION_LOG"
else
    if [[ ! -f "$SESSION_LOG" ]]; then
        error "Session log not found: state/sessions/$DATE.yaml"
        exit 1
    fi

    # Basic YAML well-formedness check via Python
    if ! python3 -c "
import sys, yaml
try:
    with open('$SESSION_LOG') as f:
        data = yaml.safe_load(f)
    if not isinstance(data, dict):
        print('Session log is not a YAML mapping', file=sys.stderr)
        sys.exit(1)
except yaml.YAMLError as e:
    print(f'Session log has invalid YAML: {e}', file=sys.stderr)
    sys.exit(1)
"; then
        error "Session log is not valid YAML: state/sessions/$DATE.yaml"
        exit 1
    fi

    info "Session log verified: state/sessions/$DATE.yaml"
fi

# ---------------------------------------------------------------------------
# Step 5: Git commit
# ---------------------------------------------------------------------------

if $NO_COMMIT; then
    step "Step 5/5: Skipping git commit (--no-commit)"
else
    step "Step 5/5: Committing changes"
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
