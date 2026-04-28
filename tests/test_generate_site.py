"""Tests for generate_site.py."""

import json
import os
import shutil
import tempfile
from datetime import date, timedelta
from pathlib import Path

import pytest

# Ensure imports work from repo root
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import generate_site


@pytest.fixture(scope="module")
def lectionaries():
    """Load both lectionaries once for the test module."""
    return generate_site.load_leccionarios()


@pytest.fixture
def outdir(tmp_path):
    """Provide a temporary output directory."""
    return tmp_path / "site"


class TestGenerateSingleDay:
    """Test generating a single day page."""

    def test_generate_single_day(self, outdir, lectionaries):
        """Generate April 9 2026 — Octava de Pascua Thursday."""
        d = date(2026, 4, 9)
        templates = generate_site.load_templates()

        day_data = generate_site.generate_day(
            d,
            prev_d=date(2026, 4, 8),
            next_d=date(2026, 4, 10),
            outdir=outdir,
            templates=templates,
            lang="es",
            lectionaries=lectionaries,
        )

        # Verify file exists
        html_path = outdir / "2026" / "04" / "09" / "index.html"
        assert html_path.exists(), f"HTML file not found at {html_path}"

        # Verify content
        html = html_path.read_text(encoding="utf-8")
        assert "Octava de Pascua" in html
        # Should have reading citations
        assert any(r["cita"] for r in day_data["readings"]), "No reading citations found"


class TestReadingKeys:
    """Test that readings have the correct keys."""

    def test_sunday_has_segunda_lectura(self, lectionaries):
        """Easter Sunday (2026-04-05) should have 'segunda' in reading keys."""
        d = date(2026, 4, 5)
        day_data = generate_site.get_day_data(d, "es", lectionaries)
        reading_keys = [r["key"] for r in day_data["readings"]]
        assert "segunda" in reading_keys, (
            f"Expected 'segunda' for Easter Sunday, got keys: {reading_keys}"
        )

    def test_weekday_no_segunda(self, lectionaries):
        """April 9 2026 (Thursday) should NOT have 'segunda' in reading keys."""
        d = date(2026, 4, 9)
        day_data = generate_site.get_day_data(d, "es", lectionaries)
        reading_keys = [r["key"] for r in day_data["readings"]]
        assert "segunda" not in reading_keys, (
            f"Weekday should not have 'segunda', got keys: {reading_keys}"
        )


class TestSearchIndex:
    """Test search index generation."""

    def test_search_index_generation(self, outdir, lectionaries):
        """Generate search index from sample data, verify JSON structure."""
        outdir.mkdir(parents=True, exist_ok=True)

        sample_days = [
            generate_site.get_day_data(date(2026, 4, 5), "es", lectionaries),
            generate_site.get_day_data(date(2026, 4, 9), "es", lectionaries),
        ]

        generate_site.generate_search_index(sample_days, outdir, "es")

        idx_path = outdir / "search-index.json"
        assert idx_path.exists()

        data = json.loads(idx_path.read_text(encoding="utf-8"))
        assert isinstance(data, list)
        assert len(data) == 2

        entry = data[0]
        for key in ("url", "fecha", "nombre", "color", "citas", "santos", "titulos"):
            assert key in entry
        assert entry["url"].startswith("/")
        assert not entry["url"].startswith("/eu/"), "ES search index should not carry /eu/ URLs"


class TestCalendarData:
    """Test calendar data generation."""

    def test_calendar_data_generation(self, outdir, lectionaries):
        """Generate calendar data, verify JSON structure."""
        outdir.mkdir(parents=True, exist_ok=True)

        sample_days = [
            generate_site.get_day_data(date(2026, 4, 5), "es", lectionaries),
            generate_site.get_day_data(date(2026, 4, 9), "es", lectionaries),
        ]

        generate_site.generate_calendar_data(sample_days, outdir, "es")

        cal_path = outdir / "calendario" / "data.json"
        assert cal_path.exists()

        data = json.loads(cal_path.read_text(encoding="utf-8"))
        assert isinstance(data, dict)
        assert "2026-04-05" in data
        assert "2026-04-09" in data

        entry = data["2026-04-05"]
        for key in ("nombre", "color", "rank", "url"):
            assert key in entry
        assert entry["url"] == "/2026/04/05/"


class TestFullBuild:
    def test_full_build_small_window(self):
        """Full build with a 3-day window produces all expected files for both languages."""
        with tempfile.TemporaryDirectory() as outdir:
            generate_site.build_site(
                today=date(2026, 4, 9), days_back=1, days_forward=1, outdir=outdir,
            )

            # ES day pages exist
            for d_offset in [-1, 0, 1]:
                d = date(2026, 4, 9) + timedelta(days=d_offset)
                path = os.path.join(outdir, str(d.year), f"{d.month:02d}", f"{d.day:02d}", "index.html")
                assert os.path.exists(path), f"Missing ES page for {d}"

            # EU day pages exist (Lezionarioa is committed to data/)
            for d_offset in [-1, 0, 1]:
                d = date(2026, 4, 9) + timedelta(days=d_offset)
                path = os.path.join(outdir, "eu", str(d.year), f"{d.month:02d}", f"{d.day:02d}", "index.html")
                assert os.path.exists(path), f"Missing EU page for {d}"

            # Apex supporting files
            assert os.path.exists(os.path.join(outdir, "index.html"))
            assert os.path.exists(os.path.join(outdir, "404.html"))
            assert os.path.exists(os.path.join(outdir, "search-index.json"))
            assert os.path.exists(os.path.join(outdir, "calendario", "data.json"))
            assert os.path.exists(os.path.join(outdir, "sitemap.xml"))
            assert os.path.exists(os.path.join(outdir, "robots.txt"))
            assert os.path.exists(os.path.join(outdir, "assets", "style.css"))
            assert os.path.exists(os.path.join(outdir, "assets", "app.js"))

            # EU supporting files
            assert os.path.exists(os.path.join(outdir, "eu", "index.html"))
            assert os.path.exists(os.path.join(outdir, "eu", "search-index.json"))
            assert os.path.exists(os.path.join(outdir, "eu", "calendario", "data.json"))
            assert os.path.exists(os.path.join(outdir, "eu", "bilatu", "index.html"))

            # Sitemap has hreflang clusters
            with open(os.path.join(outdir, "sitemap.xml"), encoding="utf-8") as f:
                sitemap = f.read()
            assert "2026/04/09" in sitemap
            assert 'hreflang="es"' in sitemap
            assert 'hreflang="eu"' in sitemap
            assert "/eu/2026/04/09/" in sitemap

            # ES search index covers the 3-day window with apex URLs
            with open(os.path.join(outdir, "search-index.json"), encoding="utf-8") as f:
                idx = json.load(f)
            assert len(idx) == 3
            assert all(not e["url"].startswith("/eu/") for e in idx)

            # EU search index has /eu/ URLs
            with open(os.path.join(outdir, "eu", "search-index.json"), encoding="utf-8") as f:
                eu_idx = json.load(f)
            assert len(eu_idx) == 3
            assert all(e["url"].startswith("/eu/") for e in eu_idx)
