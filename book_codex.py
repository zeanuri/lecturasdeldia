"""Book-name canonicalization, slugs, display names, and cita extraction.

Single source of truth for biblical book identification across the site:
- Canonical short code per book (CEE convention: "Col", "1 Cor", "Gen", ...)
- Variant → canonical map (handles data inconsistencies like "Hb"/"Heb",
  "Tobit"/"Tob", "Pedro"/"1 Pe", "(salas"/"Is", etc.)
- Full display names (ES, EU)
- URL slugs for /libros/<slug>/
- Walker that yields every cita in a lectionary tagged with liturgical
  context (dominical / ferial / solemnidad / santo / ritual / difunto / necesidad)
"""

from __future__ import annotations

import re
from typing import Iterator


# ── Canonical book codes (CEE Misal Romano abbreviations) ────────────────────
# Order = canonical biblical order. Used to render /libros/ index in canonical order.

CANONICAL_BOOKS_ES = [
    # Pentateuch
    "Gen", "Ex", "Lev", "Num", "Dt",
    # Historical
    "Jos", "Jue", "Rut", "1 Sam", "2 Sam", "1 Re", "2 Re",
    "1 Cron", "2 Cron", "Esd", "Neh", "Tob", "Jdt", "Est",
    "1 Mac", "2 Mac",
    # Wisdom
    "Job", "Sal", "Prov", "Ecl", "Cant", "Sab", "Eclo",
    # Major prophets
    "Is", "Jer", "Lam", "Bar", "Ez", "Dan",
    # Minor prophets
    "Os", "Jl", "Am", "Abd", "Jon", "Miq", "Nah", "Hab",
    "Sof", "Ag", "Zac", "Mal",
    # Gospels + Acts
    "Mt", "Mc", "Lc", "Jn", "Hch",
    # Pauline
    "Rom", "1 Cor", "2 Cor", "Gal", "Ef", "Flp", "Col",
    "1 Tes", "2 Tes", "1 Tim", "2 Tim", "Tit", "Flm",
    # Hebrews + Catholic
    "Heb", "Sant", "1 Pe", "2 Pe", "1 Jn", "2 Jn", "3 Jn", "Jds",
    # Apocalypse
    "Ap",
]


# ── Variant → canonical short code ───────────────────────────────────────────
# Handles every variant actually observed in the lectionary JSON:
#  - alternative abbreviations ("Hb"/"Heb", "Tm"/"Tim", "Co"/"Cor", "Ts"/"Tes")
#  - full Spanish names ("Corintios" → "1 Cor" disambiguated by leading digit)
#  - parsing artifacts ("(salas" → "Is", "libro de Isaías" → "Is", "Lucas" → "Lc",
#    "Hechos de los Apóstoles" → "Hch", "Colosenses" → "Col")
# Keys are matched as leading tokens (whitespace-trimmed, case-sensitive).

BOOK_VARIANTS_ES: dict[str, str] = {
    # ── Same-as-canonical (identity entries are added programmatically below)

    # ── Common short-form variants
    "1 Co": "1 Cor", "2 Co": "2 Cor",
    "1 Cro": "1 Cron", "2 Cro": "2 Cron",
    "1 Ts": "1 Tes", "2 Ts": "2 Tes",
    "1 Tm": "1 Tim", "2 Tm": "2 Tim",
    "Hb": "Heb",
    "Rm": "Rom",
    "Ga": "Gal",
    "Dn": "Dan",
    "Ct": "Cant",
    "St": "Sant",
    "Tobit": "Tob",
    "Tito": "Tit",

    # ── Full Spanish names (with and without accents)
    "Génesis": "Gen", "Genesis": "Gen",
    "Éxodo": "Ex", "Exodo": "Ex",
    "Levítico": "Lev", "Levitico": "Lev",
    "Números": "Num", "Numeros": "Num",
    "Deuteronomio": "Dt",
    "Josué": "Jos", "Josue": "Jos",
    "Jueces": "Jue",
    "Rut": "Rut",
    "Samuel": "1 Sam",  # disambiguated by leading "1 "/"2 " stripped before lookup
    "Reyes": "1 Re",
    "Crónicas": "1 Cron", "Cronicas": "1 Cron",
    "Esdras": "Esd",
    "Nehemías": "Neh", "Nehemias": "Neh",
    "Tobías": "Tob", "Tobias": "Tob",
    "Judit": "Jdt",
    "Ester": "Est",
    "Macabeos": "1 Mac",
    "Salmos": "Sal", "Salmo": "Sal",
    "Proverbios": "Prov",
    "Eclesiastés": "Ecl", "Eclesiastes": "Ecl",
    "Cantar": "Cant", "Cantares": "Cant",
    "Sabiduría": "Sab", "Sabiduria": "Sab",
    "Eclesiástico": "Eclo", "Eclesiastico": "Eclo",
    "Sirácida": "Eclo", "Siracida": "Eclo",
    "Isaías": "Is", "Isaias": "Is",
    "Jeremías": "Jer", "Jeremias": "Jer",
    "Lamentaciones": "Lam",
    "Baruc": "Bar",
    "Ezequiel": "Ez",
    "Daniel": "Dan",
    "Oseas": "Os",
    "Joel": "Jl",
    "Amós": "Am", "Amos": "Am",
    "Abdías": "Abd", "Abdias": "Abd",
    "Jonás": "Jon", "Jonas": "Jon",
    "Miqueas": "Miq",
    "Nahúm": "Nah", "Nahum": "Nah",
    "Habacuc": "Hab",
    "Sofonías": "Sof", "Sofonias": "Sof",
    "Ageo": "Ag",
    "Zacarías": "Zac", "Zacarias": "Zac",
    "Malaquías": "Mal", "Malaquias": "Mal",
    "Mateo": "Mt",
    "Marcos": "Mc",
    "Lucas": "Lc",
    "Juan": "Jn",
    "Hechos": "Hch",
    "Romanos": "Rom",
    "Corintios": "1 Cor",
    "Gálatas": "Gal", "Galatas": "Gal",
    "Efesios": "Ef",
    "Filipenses": "Flp",
    "Colosenses": "Col",
    "Tesalonicenses": "1 Tes",
    "Timoteo": "1 Tim",
    "Filemón": "Flm", "Filemon": "Flm",
    "Hebreos": "Heb",
    "Santiago": "Sant",
    "Pedro": "1 Pe",
    "Judas": "Jds",
    "Apocalipsis": "Ap",
}

# Add identity entries
for _c in CANONICAL_BOOKS_ES:
    BOOK_VARIANTS_ES.setdefault(_c, _c)


# ── Display names (full Spanish form for headings) ───────────────────────────
DISPLAY_NAMES_ES: dict[str, str] = {
    "Gen": "Génesis", "Ex": "Éxodo", "Lev": "Levítico",
    "Num": "Números", "Dt": "Deuteronomio",
    "Jos": "Josué", "Jue": "Jueces", "Rut": "Rut",
    "1 Sam": "1 Samuel", "2 Sam": "2 Samuel",
    "1 Re": "1 Reyes", "2 Re": "2 Reyes",
    "1 Cron": "1 Crónicas", "2 Cron": "2 Crónicas",
    "Esd": "Esdras", "Neh": "Nehemías",
    "Tob": "Tobías", "Jdt": "Judit", "Est": "Ester",
    "1 Mac": "1 Macabeos", "2 Mac": "2 Macabeos",
    "Job": "Job", "Sal": "Salmos", "Prov": "Proverbios",
    "Ecl": "Eclesiastés", "Cant": "Cantar de los Cantares",
    "Sab": "Sabiduría", "Eclo": "Eclesiástico",
    "Is": "Isaías", "Jer": "Jeremías", "Lam": "Lamentaciones",
    "Bar": "Baruc", "Ez": "Ezequiel", "Dan": "Daniel",
    "Os": "Oseas", "Jl": "Joel", "Am": "Amós", "Abd": "Abdías",
    "Jon": "Jonás", "Miq": "Miqueas", "Nah": "Nahúm",
    "Hab": "Habacuc", "Sof": "Sofonías", "Ag": "Ageo",
    "Zac": "Zacarías", "Mal": "Malaquías",
    "Mt": "Mateo", "Mc": "Marcos", "Lc": "Lucas", "Jn": "Juan",
    "Hch": "Hechos de los Apóstoles",
    "Rom": "Romanos", "1 Cor": "1 Corintios", "2 Cor": "2 Corintios",
    "Gal": "Gálatas", "Ef": "Efesios", "Flp": "Filipenses",
    "Col": "Colosenses",
    "1 Tes": "1 Tesalonicenses", "2 Tes": "2 Tesalonicenses",
    "1 Tim": "1 Timoteo", "2 Tim": "2 Timoteo",
    "Tit": "Tito", "Flm": "Filemón",
    "Heb": "Hebreos", "Sant": "Santiago",
    "1 Pe": "1 Pedro", "2 Pe": "2 Pedro",
    "1 Jn": "1 Juan", "2 Jn": "2 Juan", "3 Jn": "3 Juan",
    "Jds": "Judas", "Ap": "Apocalipsis",
}

DISPLAY_NAMES_EU: dict[str, str] = {
    "Gen": "Hasiera", "Ex": "Irteera", "Lev": "Lebitarrak",
    "Num": "Zenbakiak", "Dt": "Deuteronomioa",
    "Jos": "Josue", "Jue": "Epaileak", "Rut": "Rut",
    "1 Sam": "1 Samuel", "2 Sam": "2 Samuel",
    "1 Re": "1 Erregeak", "2 Re": "2 Erregeak",
    "1 Cron": "1 Kronikak", "2 Cron": "2 Kronikak",
    "Esd": "Esdras", "Neh": "Nehemias",
    "Tob": "Tobit", "Jdt": "Judit", "Est": "Ester",
    "1 Mac": "1 Makabearrak", "2 Mac": "2 Makabearrak",
    "Job": "Job", "Sal": "Salmoak", "Prov": "Esaera Zaharrak",
    "Ecl": "Kohelet", "Cant": "Kantarik Ederrena",
    "Sab": "Jakinduria", "Eclo": "Sirakida",
    "Is": "Isaias", "Jer": "Jeremias", "Lam": "Auhenak",
    "Bar": "Baruk", "Ez": "Ezekiel", "Dan": "Daniel",
    "Os": "Oseas", "Jl": "Joel", "Am": "Amos", "Abd": "Abdias",
    "Jon": "Jonas", "Miq": "Mikeas", "Nah": "Nahum",
    "Hab": "Habakuk", "Sof": "Sofonias", "Ag": "Ageo",
    "Zac": "Zakarias", "Mal": "Malakias",
    "Mt": "Mateo", "Mc": "Markos", "Lc": "Lukas", "Jn": "Joan",
    "Hch": "Eginak",
    "Rom": "Erromatarrei", "1 Cor": "1 Korintoarrei",
    "2 Cor": "2 Korintoarrei", "Gal": "Galatarrei",
    "Ef": "Efesoarrei", "Flp": "Filipoarrei",
    "Col": "Kolosarrei",
    "1 Tes": "1 Tesalonikarrei", "2 Tes": "2 Tesalonikarrei",
    "1 Tim": "1 Timoteo", "2 Tim": "2 Timoteo",
    "Tit": "Tito", "Flm": "Filemoni",
    "Heb": "Hebrearrei", "Sant": "Santiago",
    "1 Pe": "1 Pedro", "2 Pe": "2 Pedro",
    "1 Jn": "1 Joan", "2 Jn": "2 Joan", "3 Jn": "3 Joan",
    "Jds": "Judas", "Ap": "Apokalipsia",
}


# ── URL slugs for /libros/<slug>/ ────────────────────────────────────────────
# Lowercased Spanish full name, accent-stripped, "1 ", "2 ", "3 " → "1-", "2-", "3-".
def _slug_for(canonical: str) -> str:
    name = DISPLAY_NAMES_ES.get(canonical, canonical).lower()
    import unicodedata
    name = ''.join(c for c in unicodedata.normalize('NFD', name)
                   if unicodedata.category(c) != 'Mn')
    name = name.replace(' de los cantares', '').replace(' ', '-')
    return name


SLUGS: dict[str, str] = {c: _slug_for(c) for c in CANONICAL_BOOKS_ES}
SLUG_TO_CANONICAL: dict[str, str] = {v: k for k, v in SLUGS.items()}


# ── EU short forms (Basque liturgical abbreviations) ─────────────────────────
# Mirrors ES_TO_EU_BOOK_ABBR in book_abbr_eu.py — the short Basque form of
# each book. Used to build the EU-only alias map.
ES_TO_EU_SHORT: dict[str, str] = {
    "Gen": "Has", "Ex": "Ir", "Lev": "Lb", "Num": "Zen", "Dt": "Dt",
    "Jos": "Jos", "Jue": "Ep", "Rut": "Rt",
    "1 Sam": "1 Sm", "2 Sam": "2 Sm",
    "1 Re": "1 Erg", "2 Re": "2 Erg",
    "1 Cron": "1 Kro", "2 Cron": "2 Kro",
    "Esd": "Esd", "Neh": "Ne", "Tob": "Tb", "Jdt": "Jdt", "Est": "Est",
    "1 Mac": "1 Mak", "2 Mac": "2 Mak",
    "Job": "Job", "Sal": "Sal", "Prov": "Es", "Ecl": "Koh",
    "Cant": "Ka", "Sab": "Jkd", "Eclo": "Si",
    "Is": "Is", "Jer": "Jr", "Lam": "Aud", "Bar": "Ba",
    "Ez": "Ez", "Dan": "Dn",
    "Os": "Os", "Jl": "Jl", "Am": "Am", "Abd": "Ab",
    "Jon": "Jon", "Miq": "Mi", "Nah": "Nah", "Hab": "Hab",
    "Sof": "Sof", "Ag": "Ag", "Zac": "Za", "Mal": "Ml",
    "Mt": "Mt", "Mc": "Mk", "Lc": "Lk", "Jn": "Jn", "Hch": "Eg",
    "Rom": "Erm",
    "1 Cor": "1 Kor", "2 Cor": "2 Kor",
    "Gal": "Gal", "Ef": "Ef", "Flp": "Flp", "Col": "Kol",
    "1 Tes": "1 Tes", "2 Tes": "2 Tes",
    "1 Tim": "1 Tim", "2 Tim": "2 Tim",
    "Tit": "Tit", "Flm": "Flm",
    "Heb": "Heb", "Sant": "Sant",
    "1 Pe": "1 P", "2 Pe": "2 P",
    "1 Jn": "1 Jn", "2 Jn": "2 Jn", "3 Jn": "3 Jn",
    "Jds": "Jud", "Ap": "Ap",
}


# ── Cita parsing & cleaning ──────────────────────────────────────────────────

# Typo / parsing-artifact replacements (run BEFORE the noise-strip patterns).
_TYPO_FIXES = [
    (re.compile(r'^\s*\(?salas?\s+', re.IGNORECASE), 'Is '),  # "(salas " → "Is "
]

# Noise prefixes/phrases to strip from cita strings before extracting the book.
_NOISE_PATTERNS = [
    re.compile(r'^\s*libro\s+de\s+(?:los\s+|las\s+|la\s+|el\s+)?', re.IGNORECASE),
    re.compile(r'^\s*(?:según\s+)?san\s+', re.IGNORECASE),
    re.compile(r'^\s*(?:según|de)\s+los\s+', re.IGNORECASE),
    re.compile(r'\s+de\s+los\s+Apóstoles\b', re.IGNORECASE),
    re.compile(r'\s+de\s+los\s+Apostoles\b', re.IGNORECASE),
]

# "1 Corintios" / "2 Tesalonicenses" pattern: leading digit + full Spanish name.
_DIGIT_PREFIX_RE = re.compile(r'^([1-3])\s+(\S+?)\b(.*)$')

# Sort variants longest-first to avoid prefix collisions ("1 Cor" before "1 Co").
_VARIANT_KEYS_LONG_FIRST = sorted(BOOK_VARIANTS_ES.keys(), key=lambda k: (-len(k), k))


def clean_cita(cita: str) -> str:
    """Strip noise and canonicalize the leading book token.

    Returns a cita whose leading token is one of CANONICAL_BOOKS_ES (when
    recognizable), preserving the chapter:verse tail intact.

    Examples:
        clean_cita("(salas 65, 17-21")              → "Is 65, 17-21"
        clean_cita("libro de Isaías 49, 3. 5-6")    → "Is 49, 3. 5-6"
        clean_cita("Hechos de los Apóstoles 10, 1") → "Hch 10, 1"
        clean_cita("Lucas 2, 41-51")                → "Lc 2, 41-51"
        clean_cita("Colosenses 3, 12-21")           → "Col 3, 12-21"
        clean_cita("F 727, 3")                      → "F 727, 3"  (unchanged — not a book)
    """
    if not cita:
        return ""
    s = cita
    for pat, repl in _TYPO_FIXES:
        s = pat.sub(repl, s)
    for pat in _NOISE_PATTERNS:
        s = pat.sub('', s)
    s = s.strip()
    if not s:
        return cita.strip()

    # Handle "1 Corintios"/"2 Tesalonicenses"/etc.: leading digit + full name.
    m = _DIGIT_PREFIX_RE.match(s)
    if m:
        digit, word, rest = m.groups()
        bare = BOOK_VARIANTS_ES.get(word)
        if bare and ' ' in bare:
            _, abbr = bare.split(' ', 1)
            return f'{digit} {abbr}{rest}'

    # Try to match a known variant at the start.
    for key in _VARIANT_KEYS_LONG_FIRST:
        if s.startswith(key):
            tail_idx = len(key)
            if tail_idx >= len(s):
                continue
            ch = s[tail_idx]
            if ch.isspace() or ch.isdigit() or ch in ',.;:':
                canonical = BOOK_VARIANTS_ES[key]
                return canonical + s[tail_idx:]
    return s


_LEADING_TOKEN_RE = re.compile(
    r'^\s*((?:[1-3]\s+)?[A-Za-zÁÉÍÓÚáéíóúÑñ]+\.?(?:\s+[a-záéíóúñ]+){0,2})'
)


def parse_book(cita: str) -> str | None:
    """Return the canonical book code for a cita, or None if unrecognized."""
    if not cita:
        return None
    cleaned = clean_cita(cita)
    for key in _VARIANT_KEYS_LONG_FIRST:
        if cleaned.startswith(key):
            tail_idx = len(key)
            if tail_idx >= len(cleaned):
                continue
            ch = cleaned[tail_idx]
            if ch.isspace() or ch.isdigit() or ch in ',.;:':
                return BOOK_VARIANTS_ES[key]
    return None


# ── Lectionary walker ────────────────────────────────────────────────────────

# Slot keys we treat as "containing a cita":
_CITA_SLOTS = ("primera", "primera_alt", "segunda", "segunda_alt",
               "salmo", "salmo_alt", "evangelio", "evangelio_alt",
               "aclamacion", "epistola")


def _classify_path(path: tuple[str, ...]) -> dict:
    """Map a JSON path to liturgical context fields. Returns {}-shaped dict."""
    if not path:
        return {"section": "otros"}

    top = path[0]
    if top == "dominical" and len(path) >= 2:
        return {
            "section": "dominical",
            "cycle": path[1],          # A / B / C
            "slug": path[2] if len(path) > 2 else "",
            "slot": path[-1],
        }
    if top == "ferial_to" and len(path) >= 2:
        cycle = path[1]                # I / II / evangelio
        return {
            "section": "ferial_to",
            "cycle": cycle if cycle in ("I", "II") else None,
            "slug": path[2] if len(path) > 2 else "",
            "slot": path[-1],
        }
    if top == "ferial_fuerte":
        return {
            "section": "ferial_fuerte",
            "slug": path[1] if len(path) > 1 else "",
            "slot": path[-1],
        }
    if top == "santos":
        return {
            "section": "santos",
            "slug": path[1] if len(path) > 1 else "",
            "slot": path[-1],
        }
    if top in ("rituales", "diversas_necesidades", "votivas", "lecturas",
               "moniciones_entrada", "oraciones_fieles"):
        return {
            "section": top,
            "slug": "/".join(path[1:-1]),
            "slot": path[-1],
        }
    return {"section": top, "slug": "/".join(path[1:-1]), "slot": path[-1]}


def walk_citas(data, path: tuple = ()) -> Iterator[tuple[str, str, dict]]:
    """Yield (canonical_book, raw_cita, context_dict) for every cita in `data`.

    Skips cita slots in vigilia_lecturas / vigilia_pascual etc. for now —
    they're complex and the search index has them as a separate stream.
    Also skips the "comun_ref" slot (a saint-day reference, not a cita).
    """
    if isinstance(data, dict):
        # Direct cita field
        cita = data.get("cita")
        if isinstance(cita, str) and cita.strip():
            book = parse_book(cita)
            if book is not None:
                ctx = _classify_path(path)
                yield (book, cita.strip(), ctx)
        # Recurse into children (skip 'texto' / 'titulo' / 'antifona' leaves)
        for k, v in data.items():
            if k in ("texto", "titulo", "antifona", "cita", "comun_ref",
                     "day_name", "saint_name", "date", "rank", "tipo"):
                continue
            yield from walk_citas(v, path + (k,))
    elif isinstance(data, list):
        for i, v in enumerate(data):
            yield from walk_citas(v, path + (f"[{i}]",))
