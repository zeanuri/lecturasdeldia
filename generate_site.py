#!/usr/bin/env python3
"""
Static site generator for lecturasdeldia.org (ES + EU bilingual).

Spanish version is rendered into site/, Basque into site/eu/. Both
share the same domain (lecturasdeldia.org via CNAME) and live under
the same GitHub Pages deployment.

Usage: python generate_site.py [YYYY-MM-DD]
"""

import json
import shutil
import sys
from datetime import date, timedelta
from pathlib import Path

from jinja2 import Environment, FileSystemLoader

import liturgia
from i18n import COLOR_CSS, get as get_i18n, localize_day_name
from book_abbr_eu import localize_cita
from liturgical_names_eu import (
    localize_name as localize_liturgical_name,
    localize_memorial,
    localize_season,
    localize_rank,
    localize_sunday_cycle,
    localize_weekday_cycle,
)

# ── Paths ──────────────────────────────────────────────────────────────────────

ROOT = Path(__file__).resolve().parent
DATA_DIR = ROOT / "data"
TEMPLATES_DIR = ROOT / "templates"
ASSETS_DIR = ROOT / "assets"
DEFAULT_OUTDIR = ROOT / "site"

# Per-language sub-path under the site root.
LANG_ROOT = {"es": "/", "eu": "/eu/"}

# Static (non-date) routes: ES path -> EU path.
STATIC_ROUTE_MAP = {
    "/": "/eu/",
    "/buscar/": "/eu/bilatu/",
}


# ── Loading ────────────────────────────────────────────────────────────────────

def load_leccionarios():
    """Load both ES and EU lectionaries.

    The Spanish cache is also injected as the global `liturgia._leccionario_cache`
    so any code path that calls `lookup_readings(result)` without a cache argument
    keeps the previous behaviour.
    """
    es_path = DATA_DIR / "Leccionario_CL.json"
    with open(es_path, "r", encoding="utf-8") as f:
        es = json.load(f)
    liturgia._leccionario_cache = es

    eu_path = DATA_DIR / "Lezionarioa_CL.json"
    eu = None
    if eu_path.exists():
        with open(eu_path, "r", encoding="utf-8") as f:
            eu = json.load(f)

    return {"es": es, "eu": eu}


def load_templates(templates_dir=None):
    if templates_dir is None:
        templates_dir = TEMPLATES_DIR
    env = Environment(
        loader=FileSystemLoader(str(templates_dir)),
        autoescape=True,
    )
    env.globals["cache_bust"] = int(date.today().strftime("%Y%m%d"))
    return env


# ── URL helpers ────────────────────────────────────────────────────────────────

def page_urls(es_path: str, lang: str) -> dict:
    """Compute the bilingual URL bundle for a given canonical ES path."""
    eu_path = STATIC_ROUTE_MAP.get(es_path)
    if eu_path is None:
        # Date page or other passthrough: prefix with /eu.
        eu_path = "/eu" + es_path
    return {
        "canonical_es": es_path,
        "canonical_eu": eu_path,
        "canonical_self": es_path if lang == "es" else eu_path,
        "toggle_url_es": es_path,
        "toggle_url_eu": eu_path,
    }


# ── Day data ───────────────────────────────────────────────────────────────────

def _build_readings_es(readings_raw, i18n):
    reading_labels = i18n["READING_LABELS"]
    out = []
    if not readings_raw:
        return out

    if "vigilia_lecturas" in readings_raw:
        for i, lec in enumerate(readings_raw["vigilia_lecturas"], 1):
            p = lec.get("primera", {})
            if isinstance(p, dict) and p.get("texto"):
                out.append({
                    "key": f"lectura_{i}",
                    "label": i18n["vigilia_lectura_format"].format(n=i),
                    "cita": p.get("cita", ""),
                    "titulo": p.get("titulo", ""),
                    "texto": p.get("texto", ""),
                    "antifona": "",
                    "empty": False,
                })
            s = lec.get("salmo", {})
            if isinstance(s, dict) and s.get("texto"):
                is_psalm = "Sal" in s.get("cita", "")
                out.append({
                    "key": f"salmo_{i}",
                    "label": i18n["vigilia_salmo"] if is_psalm else i18n["vigilia_cantico"],
                    "cita": s.get("cita", ""),
                    "titulo": "",
                    "texto": s.get("texto", ""),
                    "antifona": s.get("antifona", ""),
                    "empty": False,
                })

    for key in ("primera", "salmo", "segunda", "evangelio"):
        r = readings_raw.get(key)
        if not r or not isinstance(r, dict):
            continue
        label = reading_labels.get(key, key)
        if key == "segunda" and "vigilia_lecturas" in readings_raw:
            label = i18n["vigilia_epistola"]
        out.append({
            "key": key,
            "label": label,
            "cita": r.get("cita", ""),
            "titulo": r.get("titulo", ""),
            "texto": r.get("texto", ""),
            "antifona": r.get("antifona", ""),
            "empty": False,
        })

    return out


def _build_readings_eu(readings_raw, es_readings_raw, result, i18n, d):
    """For Basque, always emit the expected reading slots; mark empties so the
    template renders the 'no official Basque translation' notice with a link
    to the ES page.

    Biblical citations (cita) are language-neutral — when missing in the EU
    lectionary we fall back to the ES one. We DO NOT fall back on `titulo`,
    `texto` or `antifona`: those are translated content and copying Spanish
    would violate no_translation_policy.

    Vigilia Pascual gets the same 7 OT readings + 7 psalms + epistle + gospel
    sequence as the ES rendering, with each slot independently marked empty.
    """
    reading_labels = i18n["READING_LABELS"]
    rank = result.get("rank", "")
    is_sunday = result.get("day_name") == "Domingo"
    has_segunda = is_sunday or rank in ("Solemnidad", "Fiesta")

    raw = readings_raw or {}
    es_raw = es_readings_raw or {}
    es_url = f"/{d.year:04d}/{d.month:02d}/{d.day:02d}/"

    def _es_cita_from(es_dict, key):
        ref = es_dict.get(key) if isinstance(es_dict, dict) else None
        return ref.get("cita", "") if isinstance(ref, dict) else ""

    def _emit(key, label, eu_dict, es_dict_for_cita):
        es_cita = _es_cita_from(es_dict_for_cita, key)
        r = eu_dict.get(key) if isinstance(eu_dict, dict) else None
        if isinstance(r, dict) and not liturgia.is_empty_reading(r):
            cita = r.get("cita") or es_cita
            return {
                "key": key,
                "label": label,
                "cita": localize_cita(cita, "eu"),
                "titulo": r.get("titulo", ""),
                "texto": r.get("texto", ""),
                "antifona": r.get("antifona", ""),
                "empty": False,
            }
        return {
            "key": key,
            "label": label,
            "cita": localize_cita(es_cita, "eu"),
            "titulo": "",
            "texto": "",
            "antifona": "",
            "empty": True,
            "es_url": es_url,
        }

    out = []

    # Vigilia Pascual: 7 OT readings + 7 psalms + epistle + gospel
    if "vigilia_lecturas" in raw or "vigilia_lecturas" in es_raw:
        eu_lecturas = raw.get("vigilia_lecturas") or [{}] * 7
        es_lecturas = es_raw.get("vigilia_lecturas") or [{}] * 7
        for i in range(7):
            eu_lec = eu_lecturas[i] if i < len(eu_lecturas) else {}
            es_lec = es_lecturas[i] if i < len(es_lecturas) else {}
            out.append(_emit(
                "primera",
                i18n["vigilia_lectura_format"].format(n=i + 1),
                eu_lec, es_lec,
            ) | {"key": f"lectura_{i + 1}"})
            # Psalm: ES sometimes uses "Cantico" instead of psalm — detect from ES cita.
            es_psalm_cita = _es_cita_from(es_lec, "salmo")
            label_psalm = (i18n["vigilia_salmo"] if "Sal" in es_psalm_cita
                           else i18n["vigilia_cantico"])
            out.append(_emit("salmo", label_psalm, eu_lec, es_lec)
                       | {"key": f"salmo_{i + 1}"})

        # Post-epistle psalm (Sal 117) + Epistle (Romans) + Gospel from the
        # top-level vigilia_pascual entry. Order matches ES rendering.
        out.append(_emit("salmo", reading_labels.get("salmo", "salmo"), raw, es_raw))
        out.append(_emit("segunda", i18n["vigilia_epistola"], raw, es_raw))
        out.append(_emit("evangelio", reading_labels.get("evangelio", "evangelio"),
                         raw, es_raw))
        return out

    # Ordinary day: primera/salmo/(segunda)/evangelio
    expected = ["primera", "salmo"]
    if has_segunda:
        expected.append("segunda")
    expected.append("evangelio")

    for key in expected:
        out.append(_emit(key, reading_labels.get(key, key), raw, es_raw))
    return out


def get_day_data(d: date, lang: str, lectionaries: dict) -> dict:
    """Get liturgical info + readings for a date in the requested language."""
    i18n = get_i18n(lang)

    result = liturgia.calculate(d)
    cache = lectionaries.get(lang)
    readings_raw = liturgia.lookup_readings(result, cache=cache)

    day_name_es = result.get("day_name", "")
    day_name = localize_day_name(day_name_es, lang)
    month_name = i18n["month_names"][d.month - 1]
    fecha_larga = i18n["fecha_larga_format"].format(
        day_name=day_name, day=d.day, month=month_name, year=d.year,
    )

    color = result.get("color", "")
    color_css = COLOR_CSS.get(color, "white")

    if lang == "es":
        readings = _build_readings_es(readings_raw, i18n)
    else:
        # Citations are language-neutral; fall back to ES cache for cita-only fields.
        es_readings_raw = liturgia.lookup_readings(result, cache=lectionaries.get("es"))
        readings = _build_readings_eu(readings_raw, es_readings_raw, result, i18n, d)

    aclamacion = {}
    if readings_raw:
        acl = readings_raw.get("aclamacion")
        if isinstance(acl, dict) and acl.get("texto"):
            cita = acl.get("cita", "")
            if not cita and lang == "eu":
                # Pull cita from ES cache (citas are language-neutral references).
                es_acl = (liturgia.lookup_readings(result, cache=lectionaries.get("es")) or {}).get("aclamacion") or {}
                cita = es_acl.get("cita", "")
            aclamacion = {
                "tipo": acl.get("tipo", "aleluya"),
                "texto": acl.get("texto", ""),
                "cita": localize_cita(cita, lang),
            }

    # Saint's proper readings (alternative for memorias)
    saint_readings = []
    memorial = result.get("memorial", "")
    if memorial and result.get("readings_source") == "feriales":
        santos_key = f"{d.month:02d}-{d.day:02d}"
        lec = cache or {}
        santo = (lec.get("santos") or {}).get(santos_key, {})
        has_full_readings = santo and all(
            isinstance(santo.get(k), dict) and santo.get(k, {}).get("texto")
            for k in ("primera", "salmo", "evangelio")
        )
        if has_full_readings:
            for key in ("primera", "salmo", "segunda", "evangelio"):
                r = santo.get(key)
                if not r or not isinstance(r, dict) or not r.get("texto"):
                    continue
                saint_readings.append({
                    "key": key,
                    "label": i18n["READING_LABELS"].get(key, key),
                    "cita": r.get("cita", ""),
                    "titulo": r.get("titulo", ""),
                    "texto": r.get("texto", ""),
                    "antifona": r.get("antifona", ""),
                    "empty": False,
                })

    fecha_corta = f"{d.day}/{d.month}/{d.year}"

    name_es = result.get("name", "")
    rank_es = result.get("rank", "")
    season_es = result.get("season", "")
    sunday_cycle_es = result.get("sunday_cycle", "")
    weekday_cycle_es = result.get("weekday_cycle", "")
    memorial_rank_es = result.get("memorial_rank", "")

    memorial_es = result.get("memorial", "")

    if lang == "eu":
        name_out = localize_liturgical_name(name_es, "eu")
        rank_out = localize_rank(rank_es, "eu")
        season_out = localize_season(season_es, "eu")
        sunday_cycle_out = localize_sunday_cycle(sunday_cycle_es, "eu")
        weekday_cycle_out = localize_weekday_cycle(weekday_cycle_es, "eu")
        memorial_rank_out = localize_rank(memorial_rank_es, "eu")
        memorial_out = localize_memorial(memorial_es, "eu")
    else:
        name_out = name_es
        rank_out = rank_es
        season_out = season_es
        sunday_cycle_out = sunday_cycle_es
        weekday_cycle_out = weekday_cycle_es
        memorial_rank_out = memorial_rank_es
        memorial_out = memorial_es

    return {
        "date": result.get("date", d.isoformat()),
        "date_iso": d.isoformat(),
        "day_name": day_name,
        "fecha_corta": fecha_corta,
        "fecha_larga": fecha_larga,
        "name": name_out,
        "rank": rank_out,
        "season": season_out,
        "color": color,
        "color_css": color_css,
        "sunday_cycle": sunday_cycle_out,
        "weekday_cycle": weekday_cycle_out,
        "memorial": memorial_out,
        "memorial_rank": memorial_rank_out,
        "memorial_note": result.get("memorial_note", ""),
        "readings_source": result.get("readings_source", ""),
        "readings": readings,
        "aclamacion": aclamacion,
        "saint_readings": saint_readings,
    }


def format_prev_next(d: date, i18n: dict) -> str:
    return i18n["prev_next_format"].format(
        day=d.day, month_abbr=i18n["month_abbr"][d.month - 1],
    )


# ── Page generators ────────────────────────────────────────────────────────────

def generate_day(d, prev_d, next_d, outdir, templates, lang, lectionaries) -> dict:
    """Render a day page into the language-specific outdir."""
    i18n = get_i18n(lang)
    day_data = get_day_data(d, lang, lectionaries)

    es_path = f"/{d.year:04d}/{d.month:02d}/{d.day:02d}/"
    urls = page_urls(es_path, lang)

    prev_url = f"{prev_d.year}/{prev_d.month:02d}/{prev_d.day:02d}"
    next_url = f"{next_d.year}/{next_d.month:02d}/{next_d.day:02d}"
    prev_label = format_prev_next(prev_d, i18n)
    next_label = format_prev_next(next_d, i18n)

    template = templates.get_template("dia.html")
    html = template.render(
        day=day_data,
        prev_url=prev_url,
        next_url=next_url,
        prev_label=prev_label,
        next_label=next_label,
        i18n=i18n,
        lang=lang,
        **urls,
    )

    day_dir = Path(outdir) / f"{d.year}" / f"{d.month:02d}" / f"{d.day:02d}"
    day_dir.mkdir(parents=True, exist_ok=True)
    (day_dir / "index.html").write_text(html, encoding="utf-8")

    return day_data


def generate_index(outdir, today, templates, lang):
    """Render the homepage redirect for a given language."""
    i18n = get_i18n(lang)
    y = today.year
    m = f"{today.month:02d}"
    d = f"{today.day:02d}"

    lang_path = LANG_ROOT[lang]  # '/' or '/eu/'
    today_url = f"{lang_path}{y}/{m}/{d}/"
    urls = page_urls("/", lang)

    template = templates.get_template("index_redirect.html")
    html = template.render(
        i18n=i18n,
        lang=lang,
        today_url=today_url,
        lang_path=lang_path,
        **urls,
    )

    Path(outdir).mkdir(parents=True, exist_ok=True)
    (Path(outdir) / "index.html").write_text(html, encoding="utf-8")


def generate_search_index(all_days, outdir, lang):
    """Per-language search-index.json (URLs include /eu/ prefix when lang=eu)."""
    lang_path = LANG_ROOT[lang]
    entries = []
    for day_data in all_days:
        d = day_data["date_iso"]
        url = f"{lang_path}{d[:4]}/{d[5:7]}/{d[8:10]}/"
        citas = "|".join(r.get("cita", "") for r in day_data.get("readings", []))
        titulos = "|".join(
            r.get("titulo", "") for r in day_data.get("readings", []) if r.get("titulo")
        )
        entries.append({
            "url": url,
            "fecha": day_data.get("fecha_larga", ""),
            "nombre": day_data.get("name", ""),
            "color": day_data.get("color_css", ""),
            "citas": citas,
            "santos": day_data.get("memorial", ""),
            "titulos": titulos,
        })

    out = Path(outdir)
    out.mkdir(parents=True, exist_ok=True)
    (out / "search-index.json").write_text(
        json.dumps(entries, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def generate_calendar_data(all_days, outdir, lang):
    lang_path = LANG_ROOT[lang]
    cal = {}
    for day_data in all_days:
        d = day_data["date_iso"]
        cal[d] = {
            "nombre": day_data.get("name", ""),
            "color": day_data.get("color_css", ""),
            "rank": day_data.get("rank", ""),
            "url": f"{lang_path}{d[:4]}/{d[5:7]}/{d[8:10]}/",
        }

    cal_dir = Path(outdir) / "calendario"
    cal_dir.mkdir(parents=True, exist_ok=True)
    (cal_dir / "data.json").write_text(
        json.dumps(cal, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def generate_search_page(outdir, templates, lang, slug):
    """Render the search page at /buscar/ (ES) or /eu/bilatu/ (EU)."""
    i18n = get_i18n(lang)
    es_path = "/buscar/"
    urls = page_urls(es_path, lang)
    template = templates.get_template("buscar.html")
    html = template.render(day=None, i18n=i18n, lang=lang, **urls)
    target = Path(outdir) / slug
    target.mkdir(parents=True, exist_ok=True)
    (target / "index.html").write_text(html, encoding="utf-8")


def generate_sitemap(all_days_es, outdir):
    """Combined sitemap with hreflang clusters per URL.

    The same <url> entry carries <xhtml:link rel="alternate"> siblings for
    each language plus an x-default that points to the ES variant.
    """
    base = "https://lecturasdeldia.org"
    lines = ['<?xml version="1.0" encoding="UTF-8"?>']
    lines.append(
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" '
        'xmlns:xhtml="http://www.w3.org/1999/xhtml">'
    )

    def cluster(es_path: str):
        eu_path = STATIC_ROUTE_MAP.get(es_path) or ("/eu" + es_path)
        return [
            "  <url>",
            f"    <loc>{base}{es_path}</loc>",
            f'    <xhtml:link rel="alternate" hreflang="es" href="{base}{es_path}"/>',
            f'    <xhtml:link rel="alternate" hreflang="eu" href="{base}{eu_path}"/>',
            f'    <xhtml:link rel="alternate" hreflang="x-default" href="{base}{es_path}"/>',
            "  </url>",
            "  <url>",
            f"    <loc>{base}{eu_path}</loc>",
            f'    <xhtml:link rel="alternate" hreflang="es" href="{base}{es_path}"/>',
            f'    <xhtml:link rel="alternate" hreflang="eu" href="{base}{eu_path}"/>',
            f'    <xhtml:link rel="alternate" hreflang="x-default" href="{base}{es_path}"/>',
            "  </url>",
        ]

    lines.extend(cluster("/"))
    lines.extend(cluster("/buscar/"))

    for day_data in all_days_es:
        d = day_data["date_iso"]
        lines.extend(cluster(f"/{d[:4]}/{d[5:7]}/{d[8:10]}/"))

    lines.append("</urlset>")

    (Path(outdir) / "sitemap.xml").write_text("\n".join(lines), encoding="utf-8")


def generate_404(outdir, templates):
    """Single bilingual 404 served by GitHub Pages — language picked via JS sniff."""
    i18n_es = get_i18n("es")
    i18n_eu = get_i18n("eu")
    template = templates.get_template("404_bilingual.html")
    html = template.render(i18n_es=i18n_es, i18n_eu=i18n_eu)
    (Path(outdir) / "404.html").write_text(html, encoding="utf-8")


def copy_assets(outdir):
    src = ASSETS_DIR
    dst = Path(outdir) / "assets"
    if src.exists():
        if dst.exists():
            shutil.rmtree(dst)
        shutil.copytree(str(src), str(dst))


def generate_robots(outdir):
    content = """User-agent: *
Allow: /

Sitemap: https://lecturasdeldia.org/sitemap.xml
"""
    (Path(outdir) / "robots.txt").write_text(content, encoding="utf-8")


# ── Orchestrator ───────────────────────────────────────────────────────────────

def build_site(today=None, days_back=30, days_forward=365, outdir=None):
    if today is None:
        today = date.today()
    if outdir is None:
        outdir = DEFAULT_OUTDIR
    outdir = Path(outdir)

    if outdir.exists():
        shutil.rmtree(outdir)
    outdir.mkdir(parents=True, exist_ok=True)

    lectionaries = load_leccionarios()
    templates = load_templates()

    start = today - timedelta(days=days_back)
    end = today + timedelta(days=days_forward)
    total = (end - start).days + 1

    languages = [("es", outdir, "buscar"), ("eu", outdir / "eu", "bilatu")]
    if lectionaries.get("eu") is None:
        # No Basque lectionary present — skip EU variant gracefully
        languages = languages[:1]

    all_days_per_lang = {}
    for lang, lang_outdir, search_slug in languages:
        lang_outdir.mkdir(parents=True, exist_ok=True)

        days = []
        for i in range(total):
            d = start + timedelta(days=i)
            prev_d = d - timedelta(days=1)
            next_d = d + timedelta(days=1)
            day_data = generate_day(
                d, prev_d, next_d, lang_outdir, templates, lang, lectionaries,
            )
            days.append(day_data)
        all_days_per_lang[lang] = days

        generate_index(lang_outdir, today, templates, lang)
        generate_search_index(days, lang_outdir, lang)
        generate_calendar_data(days, lang_outdir, lang)
        generate_search_page(lang_outdir, templates, lang, search_slug)

    # Site-wide files (live at the apex regardless of language).
    generate_sitemap(all_days_per_lang["es"], outdir)
    generate_404(outdir, templates)
    copy_assets(outdir)
    generate_robots(outdir)

    summary = ", ".join(
        f"{lang}={len(days)}" for lang, days in all_days_per_lang.items()
    )
    print(f"Site built: {summary} days in {outdir}")
    return all_days_per_lang


if __name__ == "__main__":
    if len(sys.argv) > 1:
        target = date.fromisoformat(sys.argv[1])
    else:
        target = date.today()
    build_site(today=target)
