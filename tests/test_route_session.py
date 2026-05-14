"""ROUTE-FOLLOWUP-01: scripts/route_session.py simulates Step 3 routing decisions.

08-00 lands an import-level RED stub. 08-03 fills in the full row-by-row coverage.
08-06 adds the pairwise priority property test.
"""

import pytest


class TestRouteSessionHarnessExists:
    def test_module_importable(self):
        """The routing harness module must exist and expose route_session(state_dir).
        Today this fails with ImportError; 08-03 turns it green."""
        from scripts import route_session as rs  # noqa: F401
        assert hasattr(rs, "route_session"), (
            "ROUTE-FOLLOWUP-01: scripts/route_session.py must define route_session(state_dir). "
            "See .planning/phases/08-followup-v1.1-improvements/08-03-PLAN.md."
        )
