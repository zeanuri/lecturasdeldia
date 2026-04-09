"""Tests for generate_site.py."""

import json
import os
import shutil
import tempfile
from datetime import date
from pathlib import Path

import pytest

# Ensure imports work from repo root
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import generate_site


@pytest.fixture(autouse=True)
def _load_lec():
    """Load leccionario once for all tests."""
    generate_site.load_leccionario()


@pytest.fixture
def outdir(tmp_path):
    """Provide a temporary output directory."""
    return tmp_path / "site"


class TestGenerateSingleDay:
    """Test generating a single day page."""

    def test_generate_single_day(self, outdir):
        """Generate April 9 2026 — Octava de Pascua Thursday."""
        d = date(2026, 4, 9)
        templates = generate_site.load_templates()
        lec = generate_site.load_leccionario()

        day_data = generate_site.generate_day(
            d,
            prev_d=date(2026, 4, 8),
            next_d=date(2026, 4, 10),
            outdir=outdir,
            templates=templates,
            lec=lec,
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

    def test_sunday_has_segunda_lectura(self):
        """Easter Sunday (2026-04-05) should have 'segunda' in reading keys."""
        d = date(2026, 4, 5)
        day_data = generate_site.get_day_data(d)
        reading_keys = [r["key"] for r in day_data["readings"]]
        assert "segunda" in reading_keys, (
            f"Expected 'segunda' for Easter Sunday, got keys: {reading_keys}"
        )

    def test_weekday_no_segunda(self):
        """April 9 2026 (Thursday) should NOT have 'segunda' in reading keys."""
        d = date(2026, 4, 9)
        day_data = generate_site.get_day_data(d)
        reading_keys = [r["key"] for r in day_data["readings"]]
        assert "segunda" not in reading_keys, (
            f"Weekday should not have 'segunda', got keys: {reading_keys}"
        )


class TestSearchIndex:
    """Test search index generation."""

    def test_search_index_generation(self, outdir):
        """Generate search index from sample data, verify JSON structure."""
        outdir.mkdir(parents=True, exist_ok=True)

        sample_days = [
            generate_site.get_day_data(date(2026, 4, 5)),
            generate_site.get_day_data(date(2026, 4, 9)),
        ]

        generate_site.generate_search_index(sample_days, outdir)

        idx_path = outdir / "search-index.json"
        assert idx_path.exists()

        data = json.loads(idx_path.read_text(encoding="utf-8"))
        assert isinstance(data, list)
        assert len(data) == 2

        entry = data[0]
        assert "url" in entry
        assert "fecha" in entry
        assert "nombre" in entry
        assert "color" in entry
        assert "citas" in entry
        assert "santos" in entry
        assert "titulos" in entry
        assert entry["url"].startswith("/")


class TestCalendarData:
    """Test calendar data generation."""

    def test_calendar_data_generation(self, outdir):
        """Generate calendar data, verify JSON structure."""
        outdir.mkdir(parents=True, exist_ok=True)

        sample_days = [
            generate_site.get_day_data(date(2026, 4, 5)),
            generate_site.get_day_data(date(2026, 4, 9)),
        ]

        generate_site.generate_calendar_data(sample_days, outdir)

        cal_path = outdir / "calendario" / "data.json"
        assert cal_path.exists()

        data = json.loads(cal_path.read_text(encoding="utf-8"))
        assert isinstance(data, dict)
        assert "2026-04-05" in data
        assert "2026-04-09" in data

        entry = data["2026-04-05"]
        assert "nombre" in entry
        assert "color" in entry
        assert "rank" in entry
        assert "url" in entry
        assert entry["url"] == "/2026/04/05/"
