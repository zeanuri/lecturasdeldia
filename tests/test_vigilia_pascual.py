"""Vigilia Pascual data invariants — locks the recurring failure modes.

The Easter Vigil readings have caused multiple regressions:
- Jon #14 (commit 39a89e5): all 7 OT lecturas were sharing L1's cita
- Jon #14b (commit 76585d6): DOCX→MD parser cloned L1 across L2-L7
- post-39a89e5: the (R.: X) responsorial cues were stripped from JSON

This test locks both invariants:
1. L1-L7 primera + salmo citas must be identical across cycles A/B/C
   (CEE Misal: the 7 OT readings of Vigilia are cycle-invariant)
2. Each salmo cita must include its (R.: X) responsorial cue
"""
import json
from pathlib import Path

import pytest

DATA_DIR = Path(__file__).resolve().parents[1] / "data"

# Verse-reference cues, language-neutral. Drawn from the CEE Misal Romano.
EXPECTED_CUES = {
    1: "(R.: cf. 30)",
    2: "(R.: 1)",
    3: "(R.: 1b)",
    4: "(R.: 2a)",
    5: "(R.: 3)",
    6: "(R.: Jn 6, 68c)",
    7: "(R.: Sal 41, 2)",
}


@pytest.mark.parametrize("filename", ["Leccionario_CL.json", "Lezionarioa_CL.json"])
def test_vigilia_lecturas_identical_across_cycles(filename):
    """L1..L7 primera + salmo citas must be byte-identical across A/B/C."""
    with open(DATA_DIR / filename, encoding="utf-8") as f:
        data = json.load(f)

    for i in range(1, 8):
        key = f"vigilia_pascual_lectura_{i}"
        citas = []
        for cycle in ("A", "B", "C"):
            entry = data["dominical"][cycle].get(key)
            assert entry, f"{filename} {cycle} missing {key}"
            citas.append((
                entry.get("primera", {}).get("cita", ""),
                entry.get("salmo", {}).get("cita", ""),
            ))
        unique = set(citas)
        assert len(unique) == 1, (
            f"{filename}: {key} primera/salmo citas differ across cycles A/B/C — "
            f"this would cause Easter Vigil pages to diverge per year. "
            f"Per-cycle citas: {citas}"
        )


@pytest.mark.parametrize("filename", ["Leccionario_CL.json", "Lezionarioa_CL.json"])
@pytest.mark.parametrize("cycle", ["A", "B", "C"])
@pytest.mark.parametrize("lectura", [1, 2, 3, 4, 5, 6, 7])
def test_vigilia_salmo_responsorial_cue_present(filename, cycle, lectura):
    """Every Vigilia Pascual salmo cita must include its (R.: X) cue."""
    with open(DATA_DIR / filename, encoding="utf-8") as f:
        data = json.load(f)
    cita = (
        data["dominical"][cycle]
        .get(f"vigilia_pascual_lectura_{lectura}", {})
        .get("salmo", {})
        .get("cita", "")
    )
    expected_cue = EXPECTED_CUES[lectura]
    assert expected_cue in cita, (
        f"{filename} cycle {cycle} L{lectura} salmo missing cue {expected_cue!r}. "
        f"Got cita={cita!r}. Vigilia data regression — see test_vigilia_pascual.py."
    )
