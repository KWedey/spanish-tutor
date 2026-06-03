# Security Audit — Phase 02: Windows First-Run Unblock

**Audit date:** 2026-04-14
**Phase:** 02-win-windows-first-run-unblock (Plans 02-01 through 02-06)
**ASVS Level:** 1
**Auditor:** gsd-security-auditor (claude-sonnet-4-6)
**Result:** SECURED — all 19 mitigate threats closed

---

## Threat Verification

### Mitigate Threats (all 19 CLOSED)

| Threat ID | Plan | Category | Evidence |
|-----------|------|----------|----------|
| T-02-01 | 02-01 | Tampering — setup.bat line endings/encoding | setup.bat: no BOM (first 3 bytes `40 65 63`, not `EF BB BF`), no `\x1b` bytes, 26 CRLF line endings, 0 bare LF. First line is `@echo off` with no leading bytes. |
| T-02-03 | 02-01 | Information Disclosure — setup.bat error output | Echo block contains only 3 literal lines: `echo Error: Python not found on PATH.` / `echo Install Python 3.10+ from https://python.org` / `echo During installation, check "Add Python to PATH".` — no `%VAR%` interpolation, no file paths, no stack traces. |
| T-02-05 | 02-01 | Denial of Service — infinite loop if both probes fail | setup.bat has no loops. All three `goto` jumps target forward-only labels (line 7→12, line 9→16, line 10→20). No label is reachable from a line after its definition. Final path falls through to `:no_python` then `exit /b 1`. |
| T-02-06 | 02-01 | Repudiation — silent success/failure | `exit /b %ERRORLEVEL%` present at lines 15 and 19, both outside any parenthesized block (depth-0 confirmed by test). Both success branches propagate setup.py's exit code. |
| T-02-08 | 02-02 | Tampering — copy-paste OS confusion | README.md lines 11-12: `#    macOS/Linux:        curl -fsSL https://claude.ai/install.sh | bash` and `#    Windows PowerShell: irm https://claude.ai/install.ps1 | iex`. Platform label on same line as command. |
| T-02-10 | 02-02 | Denial of Service — malformed Markdown | README.md has 4 triple-backtick fences (2 open + 2 close = 2 balanced code blocks). All headings intact. Requirements table pipe structure intact. |
| T-02-13 | 02-03 | Tampering — %USERPROFILE% vault path OneDrive risk | SETUP.md line 46: explicit `OneDrive Documents redirection` warning present. Anchor link `[STUDENT-GUIDE.md](STUDENT-GUIDE.md#your-study-companion-obsidian-vault)` present on same line. |
| T-02-15 | 02-03 | Tampering — broken anchor link to STUDENT-GUIDE.md | STUDENT-GUIDE.md line 48: `## Your Study Companion (Obsidian Vault)` heading confirmed present. Anchor `#your-study-companion-obsidian-vault` is valid. |
| T-02-17 | 02-03 | Denial of Service — malformed Markdown in SETUP.md | SETUP.md has 6 `##`-level section headings, 5 scripts reference table rows, all four required sections present. Closing Obsidian sentence preserved. |
| T-02-20 | 02-04 | Repudiation — setup.bat exit code propagation | goto-based structure confirmed: `exit /b %ERRORLEVEL%` at lines 15 and 19 are outside all parenthesized blocks (paren depth = 0 at both lines). The CR-01 parse-time expansion bug is absent. |
| T-02-21 | 02-04 | Tampering — setup.bat line endings/BOM | Confirmed CRLF-only (26 CRLF, 0 bare LF). No UTF-8 BOM. Inherited from T-02-01 mitigation, re-verified after goto rewrite. |
| T-02-22 | 02-04 | Tampering — error message preservation | All three locked error lines present verbatim in setup.bat (confirmed by byte inspection): `echo Error: Python not found on PATH.` / `echo Install Python 3.10+ from https://python.org` / `echo During installation, check "Add Python to PATH".` |
| T-02-23 | 02-04 | Denial of Service — Windows-only test dependency | `TestSetupBatExitCode` in tests/test_setup.py uses `Path.read_text()` — pure static content inspection, no subprocess invocation, no `pytest.mark.skipif`. Runs on macOS, Linux, and Windows. |
| T-02-25 | 02-04 | Spoofing — test passes with corrupted setup.bat | `TestSetupBatExitCode.test_setup_bat_exit_code_propagation_uses_goto` asserts 8 distinct conditions: 3 goto labels (`:use_py`, `:use_python`, `:no_python`), 2 branch statements, 1 fall-through `goto :no_python`, absence of parenthesized-if pattern, exactly 2 `exit /b %ERRORLEVEL%` lines at depth 0, 3 locked error lines verbatim, and `@echo off` as first line. tests/test_setup.py lines 256-362. |
| T-02-27 | 02-05 | Tampering — multi-line old_string matches wrong location | `cd spanish-for-alice` appears exactly 1 time in README.md (line 77, Handing Off block only). Quick Start block uses `cd language`. Edit anchor was unambiguous. |
| T-02-28 | 02-05 | Denial of Service — malformed Markdown from append | README.md Handing Off block confirmed intact: `bash` fence open → `git clone` → `cd spanish-for-alice` → `python3 scripts/setup.py    # Windows: setup.bat` → fence close. 4 total fences (2 balanced blocks). |
| T-02-33 | 02-06 | Spoofing — line 71 prose note deleted/modified | SETUP.md line 71: `**Windows users:** replace \`python3\` with \`py\` (if installed) or \`python\` — e.g., \`py scripts/init-student.py --force\`.` — present and unchanged. |
| T-02-34 | 02-06 | Tampering — force-reset line spacing normalized | SETUP.md line 100 uses THREE spaces between `--force` and `#` (confirmed `'   '`); line 101 uses TWO spaces between `--full` and `#` (confirmed `'  '`). Neither was normalized. |
| T-02-35 | 02-06 | Denial of Service — multi-line old_string matches unintended block | All three edit anchors are unique: Starting Over bash fence preceded by unique prose, `cd spanish-for-alice` appears exactly once in SETUP.md (line 91), force-reset trailing comments are unique to the force-reset block. |

---

## Accepted Risks (13 threats — pre-classified, no code evidence required)

| Threat ID | Plan | Category | Rationale |
|-----------|------|----------|-----------|
| T-02-02 | 02-01 | Elevation of Privilege — `where py`/`where python` PATH lookup | `where` resolves via standard Windows PATH. Malicious `py.exe` on PATH implies pre-existing code execution equivalent. Not defensible at wrapper layer. |
| T-02-04 | 02-01 | Tampering — `%*` argument forwarding | Same surface as typing `py scripts\setup.py <args>` directly. No new injection vector. |
| T-02-07 | 02-02 | Spoofing — `irm https://claude.ai/install.ps1 \| iex` | Official Anthropic install URL. Compromise is a supply-chain issue beyond this plan's scope — same model as any `curl \| bash` pattern. |
| T-02-09 | 02-02 | Information Disclosure — README.md changes | Pure documentation change. No secrets, environment variables, or file contents exposed. |
| T-02-11 | 02-02 | Repudiation — README.md static artifact | No applicable repudiation surface. |
| T-02-12 | 02-02 | Path injection via cwd reminder | Reminder is comment text only. No user input interpolated into any shell command. |
| T-02-14 | 02-03 | Information Disclosure — `%USERPROFILE%` interpolation | Expands to current user's home directory only. Literal variable name in docs does not leak other users' paths. |
| T-02-16 | 02-03 | Path Injection — Obsidian guidance cwd | Names a specific path; no user input interpolated; no shell invocation. |
| T-02-18 | 02-03 | Spoofing — cloud-sync warning anchor | Points to in-tree STUDENT-GUIDE.md under same git history. No external URL. |
| T-02-24 | 02-04 | Elevation of Privilege — goto labels unreachable | All three labels (`:use_py`, `:use_python`, `:no_python`) are reachable. No label jumps backward. No infinite loop possible. |
| T-02-26 | 02-05 | Tampering — trailing-comment confusion | `    # Windows: setup.bat` is a shell comment. macOS/Linux users pasting the full line execute `python3 scripts/setup.py` correctly; `#` comment is ignored. |
| T-02-31 | 02-06 | Tampering — pipe character inside fenced code block | GitHub Markdown does not parse pipes inside fenced code blocks as table separators. Literal pipe in bash comment block. |
| T-02-32 | 02-06 | Shell comment semantics — pipe-continuation lines | `|` inside a `#` comment is not a pipeline operator in bash/zsh. The comment line does not execute the Windows command on macOS/Linux. |

---

## N/A Threats (6 threats)

| Threat ID | Plan | Category | Reason |
|-----------|------|----------|--------|
| T-02-09 | 02-02 | Information Disclosure | Pure doc change — listed twice in register; see accepted risks |
| T-02-11 | 02-02 | Repudiation | N/A — static artifact |
| T-02-19 | 02-03 | Information Disclosure in vault path | Pure doc change; no secrets written at edit time |
| T-02-29 | 02-05 | Information Disclosure | Pure doc change; names literal filename only |
| T-02-30 | 02-05 | Spoofing | No external links added; existing anchor link untouched |
| T-02-36 | 02-06 | Information Disclosure | Pure doc change; no secrets exposed |

---

## Unregistered Threat Flags from SUMMARY.md

No unregistered threat flags. All six SUMMARY.md files either contain no `## Threat Flags` section (02-01, 02-02, 02-04, 02-05) or explicitly state no new security surface was introduced (02-03, 02-04, 02-05, 02-06). Plan 02-03 flags T-02-13 and T-02-14 which are both registered in the threat register.

---

## Threat Count Summary

| Disposition | Total | Closed | Open |
|-------------|-------|--------|------|
| mitigate | 19 | 19 | 0 |
| accept | 13 | 13 | 0 |
| N/A | 6 | 6 | 0 |
| **Total** | **38** | **38** | **0** |
