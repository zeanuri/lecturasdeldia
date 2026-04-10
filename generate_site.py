#!/usr/bin/env python3
"""
Static site generator for lecturasdeldia.org.

Generates HTML pages for daily Mass readings using liturgia.py
and Leccionario_CL.json data.

Usage: python generate_site.py [YYYY-MM-DD]
"""

import json
import os
import shutil
import sys
from datetime import date, timedelta
from pathlib import Path

from jinja2 import Environment, FileSystemLoader

import liturgia

# ── Paths ──────────────────────────────────────────────────────────────────────

ROOT = Path(__file__).resolve().parent
DATA_DIR = ROOT / "data"
TEMPLATES_DIR = ROOT / "templates"
ASSETS_DIR = ROOT / "assets"
DEFAULT_OUTDIR = ROOT / "site"

# ── Spanish month abbreviations ────────────────────────────────────────────────

_MONTH_ABBR = [
    "ene", "feb", "mar", "abr", "may", "jun",
    "jul", "ago", "sep", "oct", "nov", "dic",
]

# ── Color map ──────────────────────────────────────────────────────────────────

_COLOR_CSS = {
    "Blanco": "white",
    "Rojo": "red",
    "Morado": "purple",
    "Verde": "green",
    "Rosa": "pink",
}

# ── Reading labels ─────────────────────────────────────────────────────────────

_READING_LABELS = {
    "primera": "Primera Lectura",
    "salmo": "Salmo Responsorial",
    "segunda": "Segunda Lectura",
    "evangelio": "Evangelio",
}


# ── Core functions ─────────────────────────────────────────────────────────────

def load_leccionario(path=None):
    """Load Leccionario_CL.json and inject into liturgia cache."""
    if path is None:
        path = DATA_DIR / "Leccionario_CL.json"
    with open(path, "r", encoding="utf-8") as f:
        lec = json.load(f)
    liturgia._leccionario_cache = lec
    return lec


def load_templates(templates_dir=None):
    """Return a Jinja2 Environment with FileSystemLoader."""
    if templates_dir is None:
        templates_dir = TEMPLATES_DIR
    return Environment(
        loader=FileSystemLoader(str(templates_dir)),
        autoescape=True,
    )


def get_day_data(d: date) -> dict:
    """Get liturgical info + readings for a given date."""
    result = liturgia.calculate(d)
    readings_raw = liturgia.lookup_readings(result)

    # Build fecha_larga: "Jueves, 9 de abril de 2026"
    day_name = result.get("day_name", "")
    month_name = liturgia.MONTH_NAMES[d.month - 1]
    fecha_larga = f"{day_name}, {d.day} de {month_name} de {d.year}"

    # Map color to CSS class
    color = result.get("color", "")
    color_css = _COLOR_CSS.get(color, "white")

    # Build readings list
    readings = []
    if readings_raw:
        for key in ("primera", "salmo", "segunda", "evangelio"):
            r = readings_raw.get(key)
            if not r or not isinstance(r, dict):
                continue
            readings.append({
                "key": key,
                "label": _READING_LABELS.get(key, key),
                "cita": r.get("cita", ""),
                "titulo": r.get("titulo", ""),
                "texto": r.get("texto", ""),
                "antifona": r.get("antifona", ""),
            })

    fecha_corta = f"{d.day}/{d.month}/{d.year}"

    return {
        "date": result.get("date", d.isoformat()),
        "date_iso": d.isoformat(),
        "day_name": day_name,
        "fecha_corta": fecha_corta,
        "fecha_larga": fecha_larga,
        "name": result.get("name", ""),
        "rank": result.get("rank", ""),
        "season": result.get("season", ""),
        "color": color,
        "color_css": color_css,
        "sunday_cycle": result.get("sunday_cycle", ""),
        "weekday_cycle": result.get("weekday_cycle", ""),
        "memorial": result.get("memorial", ""),
        "memorial_rank": result.get("memorial_rank", ""),
        "memorial_note": result.get("memorial_note", ""),
        "readings_source": result.get("readings_source", ""),
        "readings": readings,
    }


def format_prev_next(d: date) -> str:
    """Short label for nav arrows, e.g. '8 abr'."""
    return f"{d.day} {_MONTH_ABBR[d.month - 1]}"


def generate_day(d, prev_d, next_d, outdir, templates) -> dict:
    """Render day page and write to outdir/YYYY/MM/DD/index.html."""
    day_data = get_day_data(d)

    prev_url = f"{prev_d.year}/{prev_d.month:02d}/{prev_d.day:02d}"
    next_url = f"{next_d.year}/{next_d.month:02d}/{next_d.day:02d}"
    prev_label = format_prev_next(prev_d)
    next_label = format_prev_next(next_d)

    template = templates.get_template("dia.html")
    html = template.render(
        day=day_data,
        prev_url=prev_url,
        next_url=next_url,
        prev_label=prev_label,
        next_label=next_label,
    )

    day_dir = Path(outdir) / f"{d.year}" / f"{d.month:02d}" / f"{d.day:02d}"
    day_dir.mkdir(parents=True, exist_ok=True)
    (day_dir / "index.html").write_text(html, encoding="utf-8")

    return day_data


def generate_index(outdir, today):
    """Generate index.html with JS redirect to today's date."""
    y = today.year
    m = f"{today.month:02d}"
    d = f"{today.day:02d}"

    html = f"""<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="utf-8">
  <meta http-equiv="refresh" content="0;url=/{y}/{m}/{d}/">
  <title>Lecturas del Día</title>
</head>
<body>
  <script>
    var now = new Date();
    var y = now.getFullYear();
    var m = String(now.getMonth() + 1).padStart(2, '0');
    var d = String(now.getDate()).padStart(2, '0');
    window.location.replace('/' + y + '/' + m + '/' + d + '/');
  </script>
  <p>Redirigiendo a las <a href="/{y}/{m}/{d}/">lecturas de hoy</a>...</p>
</body>
</html>"""

    Path(outdir).mkdir(parents=True, exist_ok=True)
    (Path(outdir) / "index.html").write_text(html, encoding="utf-8")


def generate_search_index(all_days, outdir):
    """Write search-index.json for client-side search."""
    entries = []
    for day_data in all_days:
        d = day_data["date_iso"]
        citas = "|".join(r.get("cita", "") for r in day_data.get("readings", []))
        titulos = "|".join(r.get("titulo", "") for r in day_data.get("readings", []) if r.get("titulo"))
        entries.append({
            "url": f"/{d[:4]}/{d[5:7]}/{d[8:10]}/",
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


def generate_calendar_data(all_days, outdir):
    """Write calendario/data.json mapping dates to summary info."""
    cal = {}
    for day_data in all_days:
        d = day_data["date_iso"]
        cal[d] = {
            "nombre": day_data.get("name", ""),
            "color": day_data.get("color_css", ""),
            "rank": day_data.get("rank", ""),
            "url": f"/{d[:4]}/{d[5:7]}/{d[8:10]}/",
        }

    cal_dir = Path(outdir) / "calendario"
    cal_dir.mkdir(parents=True, exist_ok=True)
    (cal_dir / "data.json").write_text(
        json.dumps(cal, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def generate_sitemap(all_days, outdir):
    """Write sitemap.xml with all date URLs."""
    base = "https://lecturasdeldia.org"
    lines = ['<?xml version="1.0" encoding="UTF-8"?>']
    lines.append('<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">')

    # Home page
    lines.append("  <url>")
    lines.append(f"    <loc>{base}/</loc>")
    lines.append("  </url>")

    for day_data in all_days:
        d = day_data["date_iso"]
        url = f"{base}/{d[:4]}/{d[5:7]}/{d[8:10]}/"
        lines.append("  <url>")
        lines.append(f"    <loc>{url}</loc>")
        lines.append("  </url>")

    lines.append("</urlset>")

    (Path(outdir) / "sitemap.xml").write_text(
        "\n".join(lines), encoding="utf-8"
    )


def generate_404(outdir, templates):
    """Render 404.html template."""
    template = templates.get_template("404.html")
    html = template.render(day=None)
    (Path(outdir) / "404.html").write_text(html, encoding="utf-8")


def copy_assets(outdir):
    """Copy assets/ folder to output."""
    src = ASSETS_DIR
    dst = Path(outdir) / "assets"
    if src.exists():
        if dst.exists():
            shutil.rmtree(dst)
        shutil.copytree(str(src), str(dst))


def generate_robots(outdir):
    """Write robots.txt allowing all crawlers."""
    content = """User-agent: *
Allow: /

Sitemap: https://lecturasdeldia.org/sitemap.xml
"""
    (Path(outdir) / "robots.txt").write_text(content, encoding="utf-8")


def build_site(today=None, days_back=30, days_forward=365, outdir=None):
    """Orchestrate full site build."""
    if today is None:
        today = date.today()
    if outdir is None:
        outdir = DEFAULT_OUTDIR

    outdir = Path(outdir)

    # Clean output directory
    if outdir.exists():
        shutil.rmtree(outdir)
    outdir.mkdir(parents=True, exist_ok=True)

    # Load data
    lec = load_leccionario()
    templates = load_templates()

    # Generate all day pages
    start = today - timedelta(days=days_back)
    end = today + timedelta(days=days_forward)

    all_days = []
    total = (end - start).days + 1
    for i in range(total):
        d = start + timedelta(days=i)
        prev_d = d - timedelta(days=1)
        next_d = d + timedelta(days=1)
        day_data = generate_day(d, prev_d, next_d, outdir, templates)
        all_days.append(day_data)

    # Generate supporting files
    generate_index(outdir, today)
    generate_search_index(all_days, outdir)
    generate_calendar_data(all_days, outdir)
    generate_sitemap(all_days, outdir)
    generate_404(outdir, templates)
    copy_assets(outdir)
    generate_robots(outdir)

    print(f"Site built: {len(all_days)} days in {outdir}")
    return all_days


if __name__ == "__main__":
    if len(sys.argv) > 1:
        target = date.fromisoformat(sys.argv[1])
    else:
        target = date.today()
    build_site(today=target)
