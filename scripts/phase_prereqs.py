"""Single source of truth (for code) of the CORE phase-transition prerequisites
(LOAD-02 / D-03).

Values are concept-ID PREFIXES (e.g. "A-01" matches the skill-map grammar key
"A-01-present-regular"). The prose specs — curriculum/tutor-guides/
phase-transition-guide.md and docs/system-design.md — are kept in lockstep with
these sets by tests/test_phase_transition_parity.py, so the validator and the
docs can't silently drift apart.

Consumed by scripts/validate-state.py (check_phase_prereqs_acquired) to enforce
that a learner's current_phase was not advanced before its Core prereqs reached
acquisition.
"""

# CORE prerequisites that gate each phase transition.
CORE_A_TO_B = frozenset({"A-01", "A-02", "A-04"})
CORE_B_TO_C = frozenset({"B-01", "B-04"})
CORE_C_TO_D = frozenset({"C-01", "C-04", "C-06"})

# CORE prereqs that gate ENTRY into a phase, keyed by the leading letter of
# schedule.current_phase (e.g. "B-conversational" -> "B"). Phase "A" has no prior
# transition, so it is intentionally absent.
CORE_PREREQS_FOR_ENTRY = {
    "B": CORE_A_TO_B,
    "C": CORE_B_TO_C,
    "D": CORE_C_TO_D,
}
