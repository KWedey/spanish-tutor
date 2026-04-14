"""Content tests for STUDENT-GUIDE.md cloud-sync warning (LEAK-12).

Reads STUDENT-GUIDE.md and verifies that the cloud-sync warning paragraph:
- Names all four cloud services (iCloud, Dropbox, OneDrive, Google Drive)
- Describes the failure mode (sync races, .md corruption)
- Recommends safe vault paths for macOS and Windows
- Is positioned AFTER the "Your Study Companion" heading and BEFORE "Open Obsidian"
- Is NOT a new section heading (remains an inline paragraph)

Mirrors the TestSetupBatExitCode pattern: static content assertions,
no doc-rendering or link-following.
"""
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
GUIDE_PATH = REPO_ROOT / "STUDENT-GUIDE.md"


def _read_guide() -> str:
    assert GUIDE_PATH.exists(), (
        f"STUDENT-GUIDE.md missing at {GUIDE_PATH}"
    )
    return GUIDE_PATH.read_text(encoding="utf-8")


def _guide_lines() -> list[str]:
    return _read_guide().splitlines()


# ---------------------------------------------------------------------------
# LEAK-12: Cloud-sync warning content requirements
# ---------------------------------------------------------------------------

class TestCloudSyncWarning:
    """LEAK-12: STUDENT-GUIDE.md Obsidian section warns against cloud-synced vault placement."""

    def test_icloud_named_in_warning(self):
        """LEAK-12: Warning names iCloud as a problematic cloud-sync service."""
        content = _read_guide()
        assert "iCloud" in content, (
            "LEAK-12: 'iCloud' not found in STUDENT-GUIDE.md — "
            "cloud-sync warning must name all four services"
        )

    def test_dropbox_named_in_warning(self):
        """LEAK-12: Warning names Dropbox as a problematic cloud-sync service."""
        content = _read_guide()
        assert "Dropbox" in content, (
            "LEAK-12: 'Dropbox' not found in STUDENT-GUIDE.md — "
            "cloud-sync warning must name all four services"
        )

    def test_onedrive_named_in_warning(self):
        """LEAK-12: Warning names OneDrive as a problematic cloud-sync service."""
        content = _read_guide()
        assert "OneDrive" in content, (
            "LEAK-12: 'OneDrive' not found in STUDENT-GUIDE.md — "
            "cloud-sync warning must name all four services"
        )

    def test_google_drive_named_in_warning(self):
        """LEAK-12: Warning names Google Drive as a problematic cloud-sync service."""
        content = _read_guide()
        assert "Google Drive" in content, (
            "LEAK-12: 'Google Drive' not found in STUDENT-GUIDE.md — "
            "cloud-sync warning must name all four services"
        )

    def test_all_four_services_in_same_paragraph(self):
        """LEAK-12: All four cloud services appear together — confirms one coherent warning."""
        lines = _guide_lines()
        # Find a paragraph (blank-line-bounded block) that contains all four services
        paragraphs: list[str] = []
        current: list[str] = []
        for line in lines:
            if line.strip() == "":
                if current:
                    paragraphs.append(" ".join(current))
                    current = []
            else:
                current.append(line)
        if current:
            paragraphs.append(" ".join(current))

        services = {"iCloud", "Dropbox", "OneDrive", "Google Drive"}
        found = any(
            all(svc in para for svc in services)
            for para in paragraphs
        )
        assert found, (
            "LEAK-12: no single paragraph contains all four cloud services "
            "(iCloud, Dropbox, OneDrive, Google Drive) — they should appear "
            "together in one warning paragraph"
        )

    def test_sync_failure_mode_described(self):
        """LEAK-12: Warning describes sync as the failure mechanism."""
        content = _read_guide()
        # The plan requires citing "sync processes that race" or similar language
        assert "sync" in content.lower(), (
            "LEAK-12: 'sync' not found in STUDENT-GUIDE.md"
        )

    def test_corruption_cited_as_risk(self):
        """LEAK-12: Warning mentions file corruption as the consequence of cloud sync."""
        content = _read_guide()
        assert "corrupt" in content.lower(), (
            "LEAK-12: 'corrupt' (or variation) not found in STUDENT-GUIDE.md — "
            "the warning must explain that sync races can corrupt .md files"
        )

    def test_macos_recommended_path_present(self):
        """LEAK-12: Warning recommends ~/Documents/language-vault for macOS users."""
        content = _read_guide()
        assert "~/Documents/language-vault" in content, (
            "LEAK-12: macOS recommended path '~/Documents/language-vault' "
            "not found in STUDENT-GUIDE.md"
        )

    def test_windows_recommended_path_present(self):
        """LEAK-12: Warning recommends %USERPROFILE%\\Documents\\language-vault for Windows users."""
        content = _read_guide()
        assert "%USERPROFILE%" in content, (
            "LEAK-12: Windows environment variable '%USERPROFILE%' not found in "
            "STUDENT-GUIDE.md — Windows path recommendation missing"
        )
        assert "language-vault" in content, (
            "LEAK-12: 'language-vault' path not found in STUDENT-GUIDE.md"
        )

    def test_warning_is_after_obsidian_section_heading(self):
        """LEAK-12: Warning appears AFTER 'Your Study Companion (Obsidian Vault)' heading."""
        lines = _guide_lines()

        section_line = next(
            (i for i, l in enumerate(lines) if "Your Study Companion" in l),
            None,
        )
        assert section_line is not None, (
            "LEAK-12: 'Your Study Companion' section heading not found in STUDENT-GUIDE.md"
        )

        # iCloud is a reliable signal for the warning paragraph
        warning_line = next(
            (i for i, l in enumerate(lines) if "iCloud" in l),
            None,
        )
        assert warning_line is not None, (
            "LEAK-12: line containing 'iCloud' not found in STUDENT-GUIDE.md"
        )

        assert section_line < warning_line, (
            f"LEAK-12: cloud-sync warning (line {warning_line + 1}) must appear "
            f"AFTER 'Your Study Companion' heading (line {section_line + 1})"
        )

    def test_warning_is_before_open_obsidian_instructions(self):
        """LEAK-12: Warning appears BEFORE 'Open Obsidian and you'll see:' instruction."""
        lines = _guide_lines()

        warning_line = next(
            (i for i, l in enumerate(lines) if "iCloud" in l),
            None,
        )
        assert warning_line is not None, (
            "LEAK-12: line containing 'iCloud' not found in STUDENT-GUIDE.md"
        )

        open_obsidian_line = next(
            (i for i, l in enumerate(lines) if "Open Obsidian" in l),
            None,
        )
        assert open_obsidian_line is not None, (
            "LEAK-12: 'Open Obsidian' instruction line not found in STUDENT-GUIDE.md"
        )

        assert warning_line < open_obsidian_line, (
            f"LEAK-12: cloud-sync warning (line {warning_line + 1}) must appear "
            f"BEFORE 'Open Obsidian' instructions (line {open_obsidian_line + 1})"
        )

    def test_warning_is_not_a_new_section_heading(self):
        """LEAK-12: Warning must be an inline paragraph, NOT a new ## heading.

        The plan explicitly requires one paragraph inside the existing section,
        not a new subsection.
        """
        lines = _guide_lines()

        # Find line containing iCloud — that's the warning paragraph
        warning_line_idx = next(
            (i for i, l in enumerate(lines) if "iCloud" in l),
            None,
        )
        assert warning_line_idx is not None, (
            "LEAK-12: line containing 'iCloud' not found"
        )

        warning_line = lines[warning_line_idx]
        assert not warning_line.startswith("#"), (
            f"LEAK-12: cloud-sync warning line starts with '#' — it must be "
            f"a paragraph, not a heading. Line {warning_line_idx + 1}: {warning_line!r}"
        )
