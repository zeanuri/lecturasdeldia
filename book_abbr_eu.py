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
    """Localize a cita to Basque. Alias of `localize_cita_full`.

    It used to translate ONLY the leading book token, so the site rendered
    "Cf. Lc 1, 28. 42" and "(R.: Lc 23, 46)" half in Spanish while
    `localize_cita_full` — same module, same file — got them right. Two
    localizers with different reach in one module is a bug generator, so this
    is now a thin alias and there is a single behaviour to reason about.

    Examples:
        localize_cita("Hch 11, 19-26", "eu")  -> "Eg 11, 19-26"
        localize_cita("Mt 5, 1-12", "eu")     -> "Mt 5, 1-12"  (same)
        localize_cita("1 Cor 12, 4-11", "eu") -> "1 Kor 12, 4-11"
        localize_cita("Cf. Lc 1, 28. 42", "eu") -> "Ik. Lk 1, 28. 42"
    """
    return localize_cita_full(cita, lang)


# ── Full-string localizer ─────────────────────────────────────────────────────
# Translates EVERY book token in a cita (not just the leading one), plus
# the Spanish " y " connector that survives in chapter:verse listings like
# "Sal 68, 31 y 33-34 (R.: Lc 23, 46)" → "Sal 68, 31 eta 33-34 (R.: Lk 23, 46)".
#
# The pattern is: match a known ES abbrev or "[1-3] <abbrev>" surrounded by
# word boundaries, followed (eventually) by a digit. This catches both
# leading and inline references.

import re as _re

# Pre-build a regex of all ES abbreviations (longest-first so "1 Cor" wins
# before "1 Co"). Use look-ahead for the trailing digit to avoid eating
# already-localized tokens that happen to share letters with ES abbrevs.
_ES_BOOK_RE = _re.compile(
    r'\b(' +
    '|'.join(_re.escape(k) for k in _KEYS_LONGEST_FIRST) +
    r')(?=[\s\.,;:]|$|\d)'
)


def localize_cita_full(cita: str, lang: str = "eu") -> str:
    """Translate ALL Spanish biblical-citation fragments to Basque.

    - Replaces every recognized ES book abbrev with its EU equivalent
      (handles inline cross-references like "(R.: Lc 23, 46)").
    - Replaces the Spanish " y " connector with " eta ".

    Examples:
        localize_cita_full("Sal 68, 8-10 y 11. 31 y 33-34 (R.: Lc 23, 46)", "eu")
            -> "Sal 68, 8-10 eta 11. 31 eta 33-34 (R.: Lk 23, 46)"
    """
    if not cita or lang != "eu":
        return cita or ""
    out = _ES_BOOK_RE.sub(lambda m: ES_TO_EU_BOOK_ABBR[m.group(1)], cita)
    # " y " (with surrounding spaces) → " eta ". Word-boundary protects names
    # that legitimately contain "y" inside (none do in our citas, but be safe).
    out = _re.sub(r'(?<=\s)y(?=\s)', 'eta', out)
    # "cf." → "ik.", keeping the case. The two real Basque lectionary sources
    # write "ik."/"Ik." 427 times and "cf." zero; nothing was translating it,
    # so the EU pages printed the Spanish marker. Same fix landed in ZClaude's
    # tools/pipeline/leccionario/lib/cita_eu.py on 2026-08-23.
    out = _re.sub(r'\bcf\.', lambda m: 'Ik.' if m.group(0)[0].isupper() else 'ik.',
                  out, flags=_re.IGNORECASE)
    return out


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
