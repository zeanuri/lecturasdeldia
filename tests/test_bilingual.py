"""Tests for the ES/EU bilingual site infrastructure."""

import sys
from datetime import date
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import liturgia  # noqa: E402
from i18n import I18N_ES, I18N_EU, DAY_ES_TO_EU, get as get_i18n, localize_day_name  # noqa: E402
import generate_site  # noqa: E402


# ── i18n key parity ────────────────────────────────────────────────────────

# Keys that intentionally only exist in one variant.
ES_ONLY_KEYS = set()
EU_ONLY_KEYS = {"empty_reading_msg", "read_in_spanish"}


def test_i18n_eu_has_all_es_keys():
    es_keys = set(I18N_ES.keys())
    eu_keys = set(I18N_EU.keys())
    missing = (es_keys - eu_keys) - ES_ONLY_KEYS
    assert not missing, f"EU dict missing ES keys: {sorted(missing)}"


def test_i18n_no_unknown_eu_keys():
    es_keys = set(I18N_ES.keys())
    eu_keys = set(I18N_EU.keys())
    extras = (eu_keys - es_keys) - EU_ONLY_KEYS
    assert not extras, f"EU dict has unexpected keys: {sorted(extras)}"


def test_reading_labels_complete_both_langs():
    for label_key in ("primera", "salmo", "segunda", "evangelio"):
        assert I18N_ES["READING_LABELS"][label_key]
        assert I18N_EU["READING_LABELS"][label_key]


def test_calendar_arrays_have_right_length():
    for table in (I18N_ES, I18N_EU):
        assert len(table["month_names"]) == 12
        assert len(table["month_abbr"]) == 12
        assert len(table["calendar_month_names"]) == 12
        assert len(table["calendar_day_headers"]) == 7


# ── Basque day-name mapping ────────────────────────────────────────────────

def test_localize_day_name_eu_known():
    assert localize_day_name("Domingo", "eu") == "Igandea"
    assert localize_day_name("Lunes", "eu") == "Astelehena"
    assert localize_day_name("Sábado", "eu") == "Larunbata"


def test_localize_day_name_es_passthrough():
    assert localize_day_name("Domingo", "es") == "Domingo"


def test_localize_day_name_eu_unknown_falls_through():
    # Unknown day_name: pass through unchanged so we never crash.
    assert localize_day_name("Asteartea", "eu") == "Asteartea"


# ── Empty-reading detection ────────────────────────────────────────────────

def test_is_empty_reading_unmatched_flag():
    assert liturgia.is_empty_reading({"texto": "", "unmatched": True})


def test_is_empty_reading_blank_text():
    assert liturgia.is_empty_reading({"texto": "", "unmatched": False})
    assert liturgia.is_empty_reading({"texto": "   \n  "})


def test_is_empty_reading_populated():
    assert not liturgia.is_empty_reading({"texto": "Aldi haretan, Jesusek..."})


def test_is_empty_reading_non_dict():
    assert liturgia.is_empty_reading(None)
    assert liturgia.is_empty_reading("")


# ── Toggle URL roundtrip ────────────────────────────────────────────────────

@pytest.mark.parametrize("es_path,expected_eu", [
    ("/", "/eu/"),
    ("/buscar/", "/eu/bilatu/"),
    ("/2026/04/28/", "/eu/2026/04/28/"),
    ("/2026/12/25/", "/eu/2026/12/25/"),
])
def test_page_urls_es_to_eu(es_path, expected_eu):
    urls_es = generate_site.page_urls(es_path, "es")
    assert urls_es["canonical_self"] == es_path
    assert urls_es["toggle_url_eu"] == expected_eu

    urls_eu = generate_site.page_urls(es_path, "eu")
    assert urls_eu["canonical_self"] == expected_eu
    assert urls_eu["toggle_url_es"] == es_path


# ── End-to-end: EU page generation ─────────────────────────────────────────

@pytest.fixture(scope="module")
def lectionaries():
    return generate_site.load_leccionarios()


def test_eu_lectionary_loaded(lectionaries):
    assert lectionaries.get("eu"), "Lezionarioa_CL.json must be present in data/"
    meta = lectionaries["eu"].get("meta", {})
    assert meta.get("lang") == "eu"
    assert meta.get("no_translation_policy") is True


def test_get_day_data_eu_has_expected_slots(lectionaries):
    # Ordinary weekday — expects primera/salmo/evangelio.
    d = date(2026, 4, 28)  # Tuesday IV Easter (per current calendar)
    day = generate_site.get_day_data(d, "eu", lectionaries)
    keys = [r["key"] for r in day["readings"]]
    assert "primera" in keys
    assert "salmo" in keys
    assert "evangelio" in keys
    # Either every reading is non-empty or the empty ones all carry es_url.
    for r in day["readings"]:
        if r["empty"]:
            assert r["es_url"] == "/2026/04/28/"
            assert r["texto"] == ""
        else:
            assert r["texto"]


def test_get_day_data_eu_sunday_includes_segunda(lectionaries):
    # 2026-04-26 is a Sunday in current liturgical calendar.
    d = date(2026, 4, 26)
    day = generate_site.get_day_data(d, "eu", lectionaries)
    keys = [r["key"] for r in day["readings"]]
    assert "segunda" in keys


def test_get_day_data_eu_uses_bizkaiera_chrome(lectionaries):
    d = date(2026, 4, 27)  # any weekday
    day = generate_site.get_day_data(d, "eu", lectionaries)
    # day_name should be one of the bizkaiera weekday forms.
    assert day["day_name"] in DAY_ES_TO_EU.values()


def test_get_day_data_es_unaffected_by_eu_changes(lectionaries):
    # ES path must keep Spanish names — no contamination from Basque cache.
    d = date(2026, 4, 27)
    day = generate_site.get_day_data(d, "es", lectionaries)
    assert day["day_name"] in ("Lunes", "Martes", "Miercoles", "Miércoles",
                               "Jueves", "Viernes", "Sabado", "Sábado", "Domingo")


# ── EU page must never contain raw ES reading text ─────────────────────────

FORBIDDEN_ES_PHRASES = [
    "Palabra de Dios",
    "En aquel tiempo",
    "Salmo Responsorial",  # this is an ES label that should never appear in EU pages
    "Lectura del santo evangelio",
]


def test_localize_cita_known_substitutions():
    from book_abbr_eu import localize_cita
    assert localize_cita("Hch 11, 19-26", "eu") == "Eg 11, 19-26"
    assert localize_cita("Mc 8, 1-9", "eu") == "Mk 8, 1-9"
    assert localize_cita("Lc 3, 4. 6", "eu") == "Lk 3, 4. 6"
    assert localize_cita("1 Cor 12, 4-11", "eu") == "1 Kor 12, 4-11"
    assert localize_cita("Rom 13, 11-14a", "eu") == "Erm 13, 11-14a"
    assert localize_cita("1 Pe 2, 4-9", "eu") == "1 P 2, 4-9"
    assert localize_cita("Num 21, 4-9", "eu") == "Zen 21, 4-9"


def test_localize_cita_passthrough_unmapped_or_es():
    from book_abbr_eu import localize_cita
    # Already same in EU
    assert localize_cita("Mt 5, 1-12", "eu") == "Mt 5, 1-12"
    assert localize_cita("Sal 23 (R.: 1)", "eu") == "Sal 23 (R.: 1)"
    # ES lang -> no change
    assert localize_cita("Hch 11, 19-26", "es") == "Hch 11, 19-26"
    # Empty / None -> empty
    assert localize_cita("", "eu") == ""
    assert localize_cita(None, "eu") == ""


def test_eu_page_has_localized_citas(lectionaries):
    """A populated EU day must show the Basque book abbreviation."""
    d = date(2026, 4, 28)  # Tuesday IV Easter — first reading is Hch
    day = generate_site.get_day_data(d, "eu", lectionaries)
    citas = [r.get("cita", "") for r in day["readings"] if r.get("cita")]
    # If 'Hch' is in any cita on the EU page, the localizer didn't run.
    assert not any(c.startswith("Hch") for c in citas), citas
    # And we expect 'Eg' to appear because Acts is the first reading that day.
    assert any(c.startswith("Eg ") for c in citas), citas


def test_eu_vigilia_has_full_structure(lectionaries):
    """Easter Vigil EU must mirror ES: 7 OT pairs + post-epistle psalm + epistle + gospel."""
    d = date(2026, 4, 4)
    day = generate_site.get_day_data(d, "eu", lectionaries)
    keys = [r["key"] for r in day["readings"]]
    expected = [
        "lectura_1", "salmo_1",
        "lectura_2", "salmo_2",
        "lectura_3", "salmo_3",
        "lectura_4", "salmo_4",
        "lectura_5", "salmo_5",
        "lectura_6", "salmo_6",
        "lectura_7", "salmo_7",
        "salmo",     # post-epistle psalm
        "segunda",   # epistle
        "evangelio",
    ]
    assert keys == expected, f"got {keys}"


def test_localize_liturgical_name_sundays():
    from liturgical_names_eu import localize_name
    assert localize_name("I Domingo de Adviento", "eu") == "Abenduko I Igandea"
    assert localize_name("IV Domingo de Pascua", "eu") == "Pazko-aldiko IV Igandea"
    assert localize_name("XIV Domingo del Tiempo Ordinario", "eu") == "Urtean Zehar XIV Igandea"
    assert localize_name("II Domingo de Cuaresma", "eu") == "Garizumako II Igandea"


def test_localize_liturgical_name_weekdays():
    from liturgical_names_eu import localize_name
    assert localize_name("Lunes de la III Semana de Cuaresma", "eu") == "Garizumako III. Asteko Astelehena"
    assert localize_name("Jueves de la Octava de Pascua", "eu") == "Pazko Zortziurreneko Osteguna"
    assert localize_name("Martes de la X Semana del Tiempo Ordinario", "eu") == "Urtean Zeharreko X. Asteko Asteartea"


def test_localize_liturgical_name_solemnities():
    from liturgical_names_eu import localize_name
    assert localize_name("Domingo de Resurreccion", "eu") == "Jaunaren Biztuerako Pazko Igandea"
    assert localize_name("Santisima Trinidad", "eu") == "Hirutasun Igandea"
    assert localize_name("Santisimo Cuerpo y Sangre de Cristo (Corpus Christi)", "eu") == "Kristoren Gorputz-Odol Santuak"
    assert localize_name("Nuestro Senor Jesucristo, Rey del Universo", "eu") == "Kristo Errege"
    assert localize_name("La Ascension del Senor", "eu") == "Igokunde Igandea"


def test_localize_liturgical_name_passthrough_unknown():
    from liturgical_names_eu import localize_name
    assert localize_name("Fiesta inventada por Claude", "eu") == "Fiesta inventada por Claude"
    assert localize_name("", "eu") == ""
    assert localize_name(None, "eu") == ""


def test_localize_season_rank_cycle():
    from liturgical_names_eu import (
        localize_season, localize_rank, localize_sunday_cycle, localize_weekday_cycle,
    )
    assert localize_season("Adviento", "eu") == "Abendualdia"
    assert localize_season("Tiempo Ordinario", "eu") == "Urtean Zehar"
    assert localize_season("Cuaresma", "eu") == "Garizuma"
    assert localize_rank("Solemnidad", "eu") == "Solemnitatea"
    assert localize_rank("Memoria Obligatoria", "eu") == "Nahitaezko Oroitzapena"
    assert localize_sunday_cycle("Ciclo B", "eu") == "B zikloa"
    assert localize_weekday_cycle("Ano II", "eu") == "II urtea"


def test_eu_page_renders_batua_h1(lectionaries):
    """The H1 day name on EU pages must be translated to batua, not Spanish."""
    d = date(2026, 4, 26)  # IV Domingo de Pascua (Year A in 2026 calendar)
    day = generate_site.get_day_data(d, "eu", lectionaries)
    assert day["name"].startswith("Pazko-aldiko"), day["name"]


def test_no_spanish_reading_text_in_eu_page(tmp_path, lectionaries):
    from jinja2 import Environment, FileSystemLoader

    env = Environment(
        loader=FileSystemLoader(str(ROOT / "templates")),
        autoescape=True,
    )
    env.globals["cache_bust"] = 1

    d = date(2026, 4, 27)
    day_data = generate_site.get_day_data(d, "eu", lectionaries)
    urls = generate_site.page_urls(f"/{d:%Y/%m/%d}/", "eu")

    template = env.get_template("dia.html")
    html = template.render(
        day=day_data,
        prev_url="2026/04/26",
        next_url="2026/04/28",
        prev_label="api 26",
        next_label="api 28",
        i18n=get_i18n("eu"),
        lang="eu",
        **urls,
    )

    for phrase in FORBIDDEN_ES_PHRASES:
        assert phrase not in html, (
            f"EU page contains forbidden ES phrase {phrase!r}: "
            "the no_translation_policy is being violated."
        )


def test_eu_day_nav_arrows_stay_in_eu(tmp_path, lectionaries):
    """Day-page prev/next arrows on EU pages must keep the user in /eu/."""
    from jinja2 import Environment, FileSystemLoader

    env = Environment(
        loader=FileSystemLoader(str(ROOT / "templates")),
        autoescape=True,
    )
    env.globals["cache_bust"] = 1

    d = date(2026, 4, 27)
    prev_d = date(2026, 4, 26)
    next_d = date(2026, 4, 28)
    outdir = tmp_path / "eu"
    generate_site.generate_day(d, prev_d, next_d, outdir, env, "eu", lectionaries)
    html = (outdir / "2026" / "04" / "27" / "index.html").read_text(encoding="utf-8")

    assert 'href="/eu/2026/04/26/"' in html, "prev arrow on EU page must point to /eu/"
    assert 'href="/eu/2026/04/28/"' in html, "next arrow on EU page must point to /eu/"
    assert 'href="/2026/04/26/"' not in html, "prev arrow leaks to ES URL"
    assert 'href="/2026/04/28/"' not in html, "next arrow leaks to ES URL"
