"""Spanish (CEE) → Basque biblical citation abbreviations.

Translates the leading book token of a Spanish lectionary cita into its
Basque liturgical equivalent. The mapping was built by inventorying every
unique book prefix actually present in `Leccionario_CL.json`, then matching
each to the Basque convention used by Bizkeliza / EAB.

Presentation-layer only — the source MD/JSON keep the Spanish abbreviation.
Run `python book_abbr_eu.py` to dump the table for human review.

Mapping authority and uncertainty:
- Where the Spanish and Basque abbreviations are the SAME glyph (Mt, Jn, Sal,
  Is, Jr, Ez, Dn, Ap, Os, Am, Jon, Job, ...), the entry is high-confidence.
- Where they differ, entries marked with REVIEW need an authoritative source
  check (EAB, Idatzia missal, Bizkeliza editor) before publishing.
"""

from __future__ import annotations

import re

# CEE Spanish abbreviation -> Basque liturgical abbreviation.
# Keys are CASE-SENSITIVE matches to the leading token in the cita string.
# Inventory built from `Leccionario_CL.json` (every distinct prefix).
ES_TO_EU_BOOK_ABBR: dict[str, str] = {
    # ── Pentateuch ─────────────────────────────────────────────────
    "Gen": "Has",                         # Génesis -> Hasiera
    "Ex": "Ir",                           # Éxodo -> Irteera
    "Lev": "Lb",                          # Levítico -> Lebitarrak       # REVIEW
    "Num": "Zen",                         # Números -> Zenbakiak          # REVIEW
    "Dt": "Dt",                           # Deuteronomio
    # ── Historical ─────────────────────────────────────────────────
    "Jos": "Jos",                         # Josué
    "Jue": "Ep",                          # Jueces -> Epaileak            # REVIEW
    "Rut": "Rt",                          # Rut
    "1 Sam": "1 Sm",                      # 1 Samuel                       # REVIEW
    "2 Sam": "2 Sm",                                                       # REVIEW
    "1 Re": "1 Erg",                      # 1 Reyes -> Erregeak            # REVIEW
    "2 Re": "2 Erg",                                                        # REVIEW
    "1 Cron": "1 Kro",                    # Crónicas -> Kronikak           # REVIEW
    "2 Cron": "2 Kro",                                                       # REVIEW
    "Esd": "Esd",                         # Esdras
    "Neh": "Ne",                          # Nehemías
    "Tob": "Tb",                          # Tobías
    "Est": "Est",                         # Ester
    "1 Mac": "1 Mak",                     # Macabeos -> Makabearrak         # REVIEW
    "2 Mac": "2 Mak",                                                        # REVIEW
    # ── Wisdom ────────────────────────────────────────────────────
    "Job": "Job",                         # Job (same)
    "Sal": "Sal",                         # Salmos -> Salmoak (same abbrev)
    "Prov": "Es",                         # Proverbios -> Esaera Zaharrak   # REVIEW
    "Ecl": "Koh",                         # Eclesiastés -> Kohelet          # REVIEW
    "Cant": "Ka", "Ct": "Ka",             # Cantar -> Kantarik Ederrena     # REVIEW
    "Sab": "Jkd",                         # Sabiduría -> Jakinduria         # REVIEW
    "Eclo": "Si",                         # Eclesiástico -> Sirakida        # REVIEW
    # ── Major prophets ────────────────────────────────────────────
    "Is": "Is",                           # Isaías
    "Jer": "Jr",                          # Jeremías -> Jeremias (Jr abbrev)
    "Lam": "Aud",                         # Lamentaciones -> Auhenak        # REVIEW
    "Bar": "Ba",                          # Baruc
    "Ez": "Ez",                           # Ezequiel
    "Dan": "Dn", "Dn": "Dn",              # Daniel
    # ── Minor prophets ────────────────────────────────────────────
    "Os": "Os",                           # Oseas
    "Jl": "Jl",                           # Joel
    "Am": "Am",                           # Amós
    "Abd": "Ab",                          # Abdías                          # REVIEW
    "Jon": "Jon",                         # Jonás
    "Miq": "Mi",                          # Miqueas
    "Nah": "Nah",                         # Nahum
    "Hab": "Hab",                         # Habacuc
    "Sof": "Sof",                         # Sofonías
    "Ag": "Ag",                           # Ageo
    "Zac": "Za",                          # Zacarías                        # REVIEW
    "Mal": "Ml",                          # Malaquías                       # REVIEW
    # ── Gospels ────────────────────────────────────────────────────
    "Mt": "Mt",                           # Mateo
    "Mc": "Mk",                           # Marcos -> Markos
    "Lc": "Lk", "Lucas": "Lk",            # Lucas -> Lukas
    "Jn": "Jn",                           # Juan -> Joan
    # ── Acts ───────────────────────────────────────────────────────
    "Hch": "Eg",                          # Hechos -> Eginak                # REVIEW
    # ── Pauline ────────────────────────────────────────────────────
    "Rom": "Erm",                         # Romanos -> Erromatarrei         # REVIEW
    "1 Cor": "1 Kor",                     # 1 Corintios -> Korintoarrei
    "2 Cor": "2 Kor",
    "Gal": "Gal",                         # Gálatas
    "Ef": "Ef",                           # Efesios
    "Flp": "Flp",                         # Filipenses (same letters)
    "Col": "Kol",                         # Colosenses
    "1 Tes": "1 Tes",                     # Tesalonicenses
    "2 Tes": "2 Tes",
    "1 Tim": "1 Tim",
    "2 Tim": "2 Tim",
    "Tit": "Tit", "Tito": "Tit",
    "Flm": "Flm",
    # ── Hebrews + Catholic epistles ───────────────────────────────
    "Heb": "Heb",                         # Hebreos -> Hebrearrei
    "Sant": "Sant",                       # Santiago                        # REVIEW
    "1 Pe": "1 P",                        # Pedro
    "2 Pe": "2 P",
    "1 Jn": "1 Jn",
    "2 Jn": "2 Jn",
    "3 Jn": "3 Jn",
    "Jds": "Jud",
    # ── Apocalypse ────────────────────────────────────────────────
    "Ap": "Ap",                           # Apocalipsis -> Apokalipsia
}

# Sort longest first (e.g. "1 Cor" before "1 C", "Crón" before "Cr")
_KEYS_LONGEST_FIRST = sorted(
    ES_TO_EU_BOOK_ABBR.keys(), key=lambda k: (-len(k), k),
)


def localize_cita(cita: str, lang: str = "eu") -> str:
    """Return the cita with the leading book abbreviation translated.

    Falls through unchanged when:
    - lang != "eu"
    - the leading token is not in the mapping
    - the cita is empty / None

    Examples:
        localize_cita("Hch 11, 19-26", "eu")  -> "Eg 11, 19-26"
        localize_cita("Mt 5, 1-12", "eu")     -> "Mt 5, 1-12"  (same)
        localize_cita("1 Cor 12, 4-11", "eu") -> "1 Kor 12, 4-11"
        localize_cita("Sal 23 (R.: 1)", "eu") -> "Sal 23 (R.: 1)"
    """
    if not cita or lang != "eu":
        return cita or ""

    s = cita.lstrip()
    leading_ws = cita[: len(cita) - len(s)]

    for es_key in _KEYS_LONGEST_FIRST:
        if s.startswith(es_key):
            tail_idx = len(es_key)
            # Token must be followed by whitespace then a digit, OR the boundary
            # must be unambiguous (digit immediately after a 1-letter prefix).
            if tail_idx >= len(s):
                continue
            ch = s[tail_idx]
            if ch.isspace() or ch.isdigit() or ch in ",.":
                eu_abbr = ES_TO_EU_BOOK_ABBR[es_key]
                return leading_ws + eu_abbr + s[tail_idx:]

    return cita


def dump_review_table() -> str:
    """Return a human-readable table of every mapping."""
    out = ["Spanish abbrev    Basque abbrev"]
    out.append("-" * 32)
    for es_key in sorted(ES_TO_EU_BOOK_ABBR.keys()):
        eu_val = ES_TO_EU_BOOK_ABBR[es_key]
        same = " (same)" if es_key == eu_val else ""
        out.append(f"  {es_key:14}  ->  {eu_val}{same}")
    return "\n".join(out)


if __name__ == "__main__":
    import sys
    sys.stdout.reconfigure(encoding="utf-8")
    print(dump_review_table())
    print()
    print("Test cases:")
    for cita in [
        "Hch 11, 19-26",
        "Mt 5, 1-12",
        "1 Cor 12, 4-11",
        "Sal 23 (R.: 1)",
        "Rom 13, 11-14a",
        "Mc 8, 1-9",
        "1 Pe 2, 4-9",
        "Eclo 24, 1-2. 8-12",
        "Num 21, 4-9",
        "Sant 5, 13-20",
    ]:
        print(f"  {cita!r:42} -> {localize_cita(cita, 'eu')!r}")
