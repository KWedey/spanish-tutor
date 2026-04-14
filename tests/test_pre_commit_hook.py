"""Structural tests for .githooks/pre-commit.

These tests read the hook file and assert that all required patterns are
present, that ordering invariants hold (template before block arm), and that
the output format includes category labels.  They do NOT execute git commands
or run the hook at runtime — this mirrors the TestSetupBatExitCode pattern.

Requirements covered: LEAK-01, LEAK-02, LEAK-03, LEAK-04, LEAK-05, LEAK-06,
LEAK-07, LEAK-08, LEAK-09, LEAK-13.
"""
import subprocess
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
HOOK_PATH = REPO_ROOT / ".githooks" / "pre-commit"


def _read_hook() -> str:
    assert HOOK_PATH.exists(), (
        f"pre-commit hook missing at {HOOK_PATH} — "
        "it must exist per the phase-01 data-leak-hardening implementation."
    )
    return HOOK_PATH.read_text(encoding="utf-8")


def _hook_lines() -> list[str]:
    return _read_hook().splitlines()


# ---------------------------------------------------------------------------
# LEAK-01: Hook blocks state/learner-profile.yaml
# ---------------------------------------------------------------------------

class TestLeak01LearnerProfile:
    def test_case_arm_present(self):
        """LEAK-01: pre-commit hook has a case arm for state/learner-profile.yaml."""
        content = _read_hook()
        assert "state/learner-profile.yaml)" in content, (
            "LEAK-01: case arm 'state/learner-profile.yaml)' missing from hook"
        )

    def test_personal_state_category_assigned(self):
        """LEAK-01: learner-profile arm assigns 'personal-state' category."""
        content = _read_hook()
        lines = content.splitlines()
        arm_lines = [l for l in lines if "state/learner-profile.yaml)" in l]
        assert arm_lines, "LEAK-01: arm line not found"
        assert any("personal-state" in l for l in arm_lines), (
            "LEAK-01: 'personal-state' category not assigned in learner-profile arm"
        )


# ---------------------------------------------------------------------------
# LEAK-02: Hook blocks state/schedule.yaml
# ---------------------------------------------------------------------------

class TestLeak02Schedule:
    def test_case_arm_present(self):
        """LEAK-02: pre-commit hook has a case arm for state/schedule.yaml."""
        content = _read_hook()
        assert "state/schedule.yaml)" in content, (
            "LEAK-02: case arm 'state/schedule.yaml)' missing from hook"
        )

    def test_personal_state_category_assigned(self):
        """LEAK-02: schedule arm assigns 'personal-state' category."""
        lines = _hook_lines()
        arm_lines = [l for l in lines if "state/schedule.yaml)" in l]
        assert arm_lines, "LEAK-02: arm line not found"
        assert any("personal-state" in l for l in arm_lines), (
            "LEAK-02: 'personal-state' category not assigned in schedule arm"
        )


# ---------------------------------------------------------------------------
# LEAK-03: Hook blocks state/skill-map.yaml but allows template
# ---------------------------------------------------------------------------

class TestLeak03SkillMap:
    def test_template_allow_arm_present(self):
        """LEAK-03: explicit allow arm for skill-map.template.yaml (no-op) is present."""
        content = _read_hook()
        assert "state/skill-map.template.yaml)" in content, (
            "LEAK-03: allow arm 'state/skill-map.template.yaml)' missing from hook"
        )

    def test_block_arm_present(self):
        """LEAK-03: blocking arm for state/skill-map.yaml is present."""
        lines = _hook_lines()
        # Block arm lines must reference skill-map.yaml but NOT template
        block_arms = [
            l for l in lines
            if "state/skill-map.yaml)" in l and "template" not in l
        ]
        assert block_arms, (
            "LEAK-03: blocking arm for 'state/skill-map.yaml)' (non-template) missing"
        )

    def test_template_arm_before_block_arm(self):
        """LEAK-03: template allow arm must appear BEFORE the blocking arm.

        Bash case uses first-match semantics; if the block arm came first,
        state/skill-map.template.yaml would be blocked instead of allowed.
        """
        lines = _hook_lines()
        template_lines = [
            i for i, l in enumerate(lines)
            if "state/skill-map.template.yaml)" in l
        ]
        block_lines = [
            i for i, l in enumerate(lines)
            if "state/skill-map.yaml)" in l and "template" not in l
        ]
        assert template_lines, "LEAK-03: template allow arm not found (cannot check ordering)"
        assert block_lines, "LEAK-03: block arm not found (cannot check ordering)"
        assert template_lines[0] < block_lines[0], (
            f"LEAK-03: template arm (line {template_lines[0] + 1}) must appear before "
            f"block arm (line {block_lines[0] + 1}) — bash case is first-match"
        )

    def test_template_arm_is_noop(self):
        """LEAK-03: template allow arm does NOT append to MATCHED_FILES."""
        lines = _hook_lines()
        template_arm_lines = [
            l for l in lines if "state/skill-map.template.yaml)" in l
        ]
        assert template_arm_lines, "LEAK-03: template arm line not found"
        # The no-op arm should contain only ';;' and not append to MATCHED_FILES
        for line in template_arm_lines:
            assert "MATCHED_FILES+=" not in line, (
                "LEAK-03: template allow arm must NOT append to MATCHED_FILES — "
                f"it must be a pass-through (no-op). Offending line: {line!r}"
            )


# ---------------------------------------------------------------------------
# LEAK-04: Hook blocks state/system-health.yaml
# ---------------------------------------------------------------------------

class TestLeak04SystemHealth:
    def test_case_arm_present(self):
        """LEAK-04: pre-commit hook has a case arm for state/system-health.yaml."""
        content = _read_hook()
        assert "state/system-health.yaml)" in content, (
            "LEAK-04: case arm 'state/system-health.yaml)' missing from hook"
        )

    def test_personal_state_category_assigned(self):
        """LEAK-04: system-health arm assigns 'personal-state' category."""
        lines = _hook_lines()
        arm_lines = [l for l in lines if "state/system-health.yaml)" in l]
        assert arm_lines, "LEAK-04: arm line not found"
        assert any("personal-state" in l for l in arm_lines), (
            "LEAK-04: 'personal-state' category not assigned in system-health arm"
        )


# ---------------------------------------------------------------------------
# LEAK-05: Hook blocks state/resource-tracker.yaml
# ---------------------------------------------------------------------------

class TestLeak05ResourceTracker:
    def test_case_arm_present(self):
        """LEAK-05: pre-commit hook has a case arm for state/resource-tracker.yaml."""
        content = _read_hook()
        assert "state/resource-tracker.yaml)" in content, (
            "LEAK-05: case arm 'state/resource-tracker.yaml)' missing from hook"
        )

    def test_personal_state_category_assigned(self):
        """LEAK-05: resource-tracker arm assigns 'personal-state' category."""
        lines = _hook_lines()
        arm_lines = [l for l in lines if "state/resource-tracker.yaml)" in l]
        assert arm_lines, "LEAK-05: arm line not found"
        assert any("personal-state" in l for l in arm_lines), (
            "LEAK-05: 'personal-state' category not assigned in resource-tracker arm"
        )


# ---------------------------------------------------------------------------
# LEAK-06: Hook blocks state/.snapshot/*
# ---------------------------------------------------------------------------

class TestLeak06Snapshot:
    def test_case_arm_present(self):
        """LEAK-06: pre-commit hook has a glob arm for state/.snapshot/*."""
        content = _read_hook()
        assert "state/.snapshot/*)" in content, (
            "LEAK-06: glob arm 'state/.snapshot/*)' missing from hook"
        )

    def test_snapshot_category_assigned(self):
        """LEAK-06: snapshot arm assigns 'snapshot' category."""
        lines = _hook_lines()
        arm_lines = [l for l in lines if "state/.snapshot/*)" in l]
        assert arm_lines, "LEAK-06: arm line not found"
        assert any("snapshot" in l for l in arm_lines), (
            "LEAK-06: 'snapshot' category not assigned in state/.snapshot arm"
        )


# ---------------------------------------------------------------------------
# LEAK-07: Hook blocks state/offline-guides/* except .gitkeep
# ---------------------------------------------------------------------------

class TestLeak07OfflineGuides:
    def test_case_arm_present(self):
        """LEAK-07: pre-commit hook has a glob arm for state/offline-guides/*."""
        content = _read_hook()
        assert "state/offline-guides/*)" in content, (
            "LEAK-07: glob arm 'state/offline-guides/*)' missing from hook"
        )

    def test_gitkeep_exception_present(self):
        """LEAK-07: offline-guides arm guards against .gitkeep files."""
        content = _read_hook()
        lines = content.splitlines()
        # Find lines in the vicinity of the offline-guides arm
        for i, line in enumerate(lines):
            if "state/offline-guides/*)" in line:
                # The guard should appear within a few lines of the arm opener
                context = "\n".join(lines[i : i + 5])
                assert ".gitkeep" in context, (
                    "LEAK-07: .gitkeep exclusion check not found near "
                    "state/offline-guides/* arm"
                )
                break
        else:
            pytest.fail("LEAK-07: state/offline-guides/*) arm not found")

    def test_offline_guide_category_assigned(self):
        """LEAK-07: offline-guides arm assigns 'offline-guide' category."""
        content = _read_hook()
        # The category assignment should appear near the arm
        lines = content.splitlines()
        found_arm = False
        for i, line in enumerate(lines):
            if "state/offline-guides/*)" in line:
                found_arm = True
                context = "\n".join(lines[i : i + 5])
                assert "offline-guide" in context, (
                    "LEAK-07: 'offline-guide' category not found near "
                    "state/offline-guides arm"
                )
                break
        assert found_arm, "LEAK-07: state/offline-guides/*) arm not found"


# ---------------------------------------------------------------------------
# LEAK-08: Hook blocks vault/**/*.md (both depth levels)
# ---------------------------------------------------------------------------

class TestLeak08VaultMarkdown:
    def test_shallow_vault_arm_present(self):
        """LEAK-08: hook has arm for vault/*.md (top-level vault files)."""
        content = _read_hook()
        assert "vault/*.md)" in content, (
            "LEAK-08: shallow arm 'vault/*.md)' missing — "
            "bash 3.2 requires this to catch vault/Home.md"
        )

    def test_deep_vault_arm_present(self):
        """LEAK-08: hook has arm for vault/**/*.md (nested vault files)."""
        content = _read_hook()
        assert "vault/**/*.md)" in content, (
            "LEAK-08: deep arm 'vault/**/*.md)' missing — "
            "required to catch files in vault subdirectories"
        )

    def test_vault_generated_category_on_shallow_arm(self):
        """LEAK-08: shallow vault arm assigns 'vault-generated' category."""
        lines = _hook_lines()
        arm_lines = [l for l in lines if "vault/*.md)" in l]
        assert arm_lines, "LEAK-08: shallow vault arm not found"
        assert any("vault-generated" in l for l in arm_lines), (
            "LEAK-08: 'vault-generated' category not assigned in vault/*.md arm"
        )

    def test_vault_generated_category_on_deep_arm(self):
        """LEAK-08: deep vault arm assigns 'vault-generated' category."""
        lines = _hook_lines()
        arm_lines = [l for l in lines if "vault/**/*.md)" in l]
        assert arm_lines, "LEAK-08: deep vault arm not found"
        assert any("vault-generated" in l for l in arm_lines), (
            "LEAK-08: 'vault-generated' category not assigned in vault/**/*.md arm"
        )


# ---------------------------------------------------------------------------
# LEAK-09: Output format uses [category] labels and mentions --no-verify
# ---------------------------------------------------------------------------

class TestLeak09OutputFormat:
    def test_matched_cats_array_declared(self):
        """LEAK-09: MATCHED_CATS=() parallel array is declared in hook."""
        content = _read_hook()
        assert "MATCHED_CATS=()" in content, (
            "LEAK-09: MATCHED_CATS=() declaration missing — "
            "required for category-labeled output"
        )

    def test_output_loop_uses_category_index(self):
        """LEAK-09: output loop accesses ${MATCHED_CATS[$i]} alongside file name."""
        content = _read_hook()
        assert "${MATCHED_CATS[$i]}" in content, (
            "LEAK-09: output loop does not reference ${MATCHED_CATS[$i]} — "
            "category labels will not appear in error output"
        )

    def test_output_loop_uses_file_index(self):
        """LEAK-09: output loop accesses ${MATCHED_FILES[$i]} (indexed, not iterated)."""
        content = _read_hook()
        assert "${MATCHED_FILES[$i]}" in content, (
            "LEAK-09: output loop should use ${MATCHED_FILES[$i]} indexed access "
            "to stay aligned with MATCHED_CATS indices"
        )

    def test_no_verify_escape_mentioned(self):
        """LEAK-09: error output instructs user about --no-verify override."""
        content = _read_hook()
        assert "--no-verify" in content, (
            "LEAK-09: '--no-verify' override instruction missing from hook error output"
        )

    def test_category_bracket_format_in_output(self):
        """LEAK-09: output loop formats categories with surrounding brackets [cat]."""
        content = _read_hook()
        # The format string should place ${MATCHED_CATS[$i]} inside [...]
        assert "[${MATCHED_CATS[$i]}]" in content, (
            "LEAK-09: category in output loop is not bracketed as [${MATCHED_CATS[$i]}] — "
            "the --no-verify line says '[category]' labels; the loop must match that format"
        )


# ---------------------------------------------------------------------------
# LEAK-13: Hook blocks .planning/*
# ---------------------------------------------------------------------------

class TestLeak13Planning:
    def test_case_arm_present(self):
        """LEAK-13: pre-commit hook has a glob arm for .planning/*."""
        content = _read_hook()
        assert ".planning/*)" in content, (
            "LEAK-13: glob arm '.planning/*)' missing from hook"
        )

    def test_planning_category_assigned(self):
        """LEAK-13: planning arm assigns 'planning' category."""
        lines = _hook_lines()
        arm_lines = [l for l in lines if ".planning/*)" in l]
        assert arm_lines, "LEAK-13: arm line not found"
        assert any("planning" in l for l in arm_lines), (
            "LEAK-13: 'planning' category not assigned in .planning arm"
        )


# ---------------------------------------------------------------------------
# Syntax validity — hook must parse as valid bash
# ---------------------------------------------------------------------------

class TestHookSyntax:
    def test_hook_is_syntactically_valid_bash(self):
        """Hook must pass bash -n (syntax check) without errors."""
        result = subprocess.run(
            ["bash", "-n", str(HOOK_PATH)],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0, (
            f"bash -n syntax check failed for {HOOK_PATH}:\n{result.stderr}"
        )

    def test_hook_has_shebang(self):
        """Hook must start with a bash shebang line."""
        lines = _hook_lines()
        assert lines[0].startswith("#!/usr/bin/env bash") or lines[0].startswith("#!/bin/bash"), (
            f"Hook shebang missing or wrong: {lines[0]!r}"
        )

    def test_hook_has_set_e(self):
        """Hook must contain 'set -e' for fail-fast behavior."""
        content = _read_hook()
        assert "set -e" in content, (
            "Hook missing 'set -e' — errors inside the hook should abort immediately"
        )

    def test_hook_reads_from_git_diff_cached(self):
        """Hook must use 'git diff --cached --name-only' as its input source."""
        content = _read_hook()
        assert "git diff --cached --name-only" in content, (
            "Hook must read from 'git diff --cached --name-only' — "
            "this is the standard way to enumerate staged files"
        )


# ---------------------------------------------------------------------------
# Retrofit check — all 8 original arms also have MATCHED_CATS entries
# ---------------------------------------------------------------------------

class TestRetrofittedOriginalArms:
    """The 8 original arms (pre-LEAK-01 through LEAK-09) must also assign categories.

    Verifies that the retrofit from LEAK-09 applied uniformly to existing arms.
    """

    @pytest.mark.parametrize("pattern,expected_cat", [
        ("state/sessions/*.yaml)", "session-log"),
        ("state/summaries/*.yaml)", "summary"),
        ("state/milestones/*.yaml)", "milestone"),
        ("parking-lot.md)", "parking-lot"),
    ])
    def test_original_arm_has_category(self, pattern, expected_cat):
        """LEAK-09 retrofit: original arm assigns its category label."""
        lines = _hook_lines()
        arm_lines = [l for l in lines if pattern in l]
        assert arm_lines, f"Original arm '{pattern}' not found in hook"
        assert any(expected_cat in l for l in arm_lines), (
            f"LEAK-09 retrofit: category '{expected_cat}' not assigned in "
            f"arm matching '{pattern}'"
        )

    @pytest.mark.parametrize("dir_pattern,expected_cat", [
        ("journal/*.md)", "journal"),
        ("transcripts/*.md)", "transcript"),
        ("progress-reports/*.md)", "progress-report"),
        ("feedback/*.md)", "feedback"),
    ])
    def test_conditional_arm_has_category(self, dir_pattern, expected_cat):
        """LEAK-09 retrofit: conditional arm (with .gitkeep guard) assigns category."""
        lines = _hook_lines()
        # For conditional arms the arm opener and the MATCHED_CATS assignment
        # may be on separate lines — inspect a 5-line window
        for i, line in enumerate(lines):
            if dir_pattern in line:
                context = "\n".join(lines[i : i + 5])
                assert expected_cat in context, (
                    f"LEAK-09 retrofit: category '{expected_cat}' not found near "
                    f"arm '{dir_pattern}'"
                )
                break
        else:
            pytest.fail(f"Arm '{dir_pattern}' not found in hook")
