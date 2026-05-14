"""RED tests for curriculum/l1-interference.yaml voseo + vosotros entries (Phase 8 FOLLOWUP).

08-04 adds entries for the voseo conversion (es-AR/es-UY targets) and vosotros recognition
(non-es-ES targets) so the tutor can preempt dialect friction at first encounter with the
Benedetti / Laforet reading entries added in 07-01.

Requirements covered: CURR-FOLLOWUP-03.
"""
import yaml
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
L1_FILE = REPO_ROOT / "curriculum" / "l1-interference.yaml"


class TestVoseoVosotrosInterference:
    """CURR-FOLLOWUP-03: l1-interference.yaml must include entries for the voseo
    conversion (es-AR/es-UY targets) and vosotros recognition (non-es-ES targets)."""

    def _load(self):
        return yaml.safe_load(L1_FILE.read_text(encoding="utf-8"))

    def _patterns(self):
        return (self._load() or {}).get("interference_patterns") or []

    def test_voseo_entry_present(self):
        ids = {(p or {}).get("id") for p in self._patterns()}
        assert any(i and "voseo" in i for i in ids), (
            "CURR-FOLLOWUP-03: l1-interference.yaml must include an entry whose id "
            "contains 'voseo' (preempts the tú/vos confusion for es-AR/es-UY learners "
            "encountering the Benedetti reading entry from media-bank). Found ids: "
            f"{sorted(i for i in ids if i)}"
        )

    def test_vosotros_entry_present(self):
        ids = {(p or {}).get("id") for p in self._patterns()}
        assert any(i and "vosotros" in i for i in ids), (
            "CURR-FOLLOWUP-03: l1-interference.yaml must include an entry whose id "
            "contains 'vosotros' (preempts the ustedes/vosotros confusion for non-es-ES "
            "learners encountering the Laforet reading entry from media-bank)."
        )

    def test_entries_cross_reference_media_bank(self):
        """Each new entry should reference the source title in media-bank that motivated it
        (Benedetti for voseo, Laforet for vosotros) — discoverability for the tutor agent."""
        patterns = self._patterns()
        voseo = next((p for p in patterns if "voseo" in (p or {}).get("id", "")), None)
        vosotros = next((p for p in patterns if "vosotros" in (p or {}).get("id", "")), None)
        assert voseo and ("Benedetti" in repr(voseo) or "benedetti" in repr(voseo).lower()), (
            "CURR-FOLLOWUP-03: voseo entry must reference Benedetti (the R4 reading entry "
            "where the learner first encounters voseo in authentic literature)."
        )
        assert vosotros and ("Laforet" in repr(vosotros) or "laforet" in repr(vosotros).lower()), (
            "CURR-FOLLOWUP-03: vosotros entry must reference Laforet (the R4 reading entry "
            "where the learner first encounters vosotros in authentic literature)."
        )
