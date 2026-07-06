"""Tests for the SEO layer: evergreen ES homepage, /acerca/, feed.xml,
JSON-LD and the extended sitemap."""

import os
import tempfile
from datetime import date
from pathlib import Path

import pytest

import sys
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import generate_site


@pytest.fixture(scope="module")
def built_site():
    """One small build shared by every test in this module."""
    tmp = tempfile.TemporaryDirectory()
    generate_site.build_site(
        today=date(2026, 4, 9), days_back=3, days_forward=1, outdir=tmp.name,
    )
    yield tmp.name
    tmp.cleanup()


def _read(built, *parts):
    with open(os.path.join(built, *parts), encoding="utf-8") as f:
        return f.read()


class TestHomepage:
    def test_root_is_real_page_not_redirect(self, built_site):
        html = _read(built_site, "index.html")
        assert "http-equiv=\"refresh\"" not in html
        assert 'data-date="2026-04-09"' in html

    def test_root_is_self_canonical(self, built_site):
        html = _read(built_site, "index.html")
        assert '<link rel="canonical" href="https://lecturasdeldia.org/">' in html

    def test_root_title_targets_search_queries(self, built_site):
        html = _read(built_site, "index.html")
        assert "Evangelio de hoy y lecturas de la Misa" in html

    def test_root_has_website_jsonld_and_intro(self, built_site):
        html = _read(built_site, "index.html")
        assert '"@type": "WebSite"' in html
        assert '"@type": "SearchAction"' in html
        assert "home-intro" in html

    def test_eu_root_keeps_redirect(self, built_site):
        html = _read(built_site, "eu", "index.html")
        assert "http-equiv=\"refresh\"" in html


class TestDayPages:
    def test_day_page_has_article_jsonld_no_home_extras(self, built_site):
        html = _read(built_site, "2026", "04", "09", "index.html")
        assert '"@type": "Article"' in html
        assert '"datePublished": "2026-04-09"' in html
        assert '"@type": "WebSite"' not in html
        assert "home-intro" not in html

    def test_day_page_keeps_dated_canonical(self, built_site):
        html = _read(built_site, "2026", "04", "09", "index.html")
        assert '<link rel="canonical" href="https://lecturasdeldia.org/2026/04/09/">' in html

    def test_day_page_links_gospel_book(self, built_site):
        html = _read(built_site, "2026", "04", "09", "index.html")
        assert 'class="gospel-book-link"' in html
        assert 'href="/libros/' in html

    def test_eu_day_page_links_gospel_book_in_basque(self, built_site):
        html = _read(built_site, "eu", "2026", "04", "09", "index.html")
        assert 'href="/eu/liburuak/' in html


class TestAcerca:
    def test_acerca_exists_with_canonical(self, built_site):
        html = _read(built_site, "acerca", "index.html")
        assert '<link rel="canonical" href="https://lecturasdeldia.org/acerca/">' in html
        assert "Conferencia Episcopal" in html


class TestDomingo:
    # Fixture builds with today=2026-04-09 (Thursday); the upcoming Sunday is
    # 2026-04-12 (Domingo de Ramos) for any reasonable _next_sunday rule.
    def test_domingo_is_real_page_featuring_a_sunday(self, built_site):
        html = _read(built_site, "domingo", "index.html")
        assert "http-equiv=\"refresh\"" not in html
        assert 'data-date="2026-04-12"' in html

    def test_domingo_is_self_canonical(self, built_site):
        html = _read(built_site, "domingo", "index.html")
        assert '<link rel="canonical" href="https://lecturasdeldia.org/domingo/">' in html

    def test_domingo_title_targets_sunday_queries(self, built_site):
        html = _read(built_site, "domingo", "index.html")
        assert "Evangelio del domingo y lecturas de la Misa dominical" in html

    def test_domingo_is_article_not_website(self, built_site):
        # A section, not the site root: emits Article but not the WebSite/SearchAction.
        html = _read(built_site, "domingo", "index.html")
        assert '"@type": "Article"' in html
        assert '"@type": "WebSite"' not in html


class TestCalendario:
    # Fixture today=2026-04-09 → liturgical year 2025-2026, Ciclo A.
    def test_calendario_exists_self_canonical(self, built_site):
        html = _read(built_site, "calendario", "index.html")
        assert '<link rel="canonical" href="https://lecturasdeldia.org/calendario/">' in html

    def test_calendario_title_and_cycle(self, built_site):
        html = _read(built_site, "calendario", "index.html")
        assert "Calendario litúrgico 2025-2026" in html
        assert "Ciclo A" in html

    def test_calendario_lists_seasons_and_links_days(self, built_site):
        html = _read(built_site, "calendario", "index.html")
        for season in ("Adviento", "Navidad", "Cuaresma", "Triduo Pascual y Pascua"):
            assert season in html
        # hub: at least one linked day page + the next-year section
        import re
        assert re.search(r'href="/20\d\d/\d\d/\d\d/"', html)
        assert "2026-2027" in html  # próximo año

    def test_calendario_in_sitemap(self, built_site):
        xml = _read(built_site, "sitemap.xml")
        assert "<loc>https://lecturasdeldia.org/calendario/</loc>" in xml


class TestFeed:
    def test_feed_exists_with_recent_items_only(self, built_site):
        xml = _read(built_site, "feed.xml")
        assert "<rss" in xml
        # today and past days are items; future days are not
        assert "lecturasdeldia.org/2026/04/09/" in xml
        assert "lecturasdeldia.org/2026/04/10/" not in xml


class TestSitemap:
    def test_sitemap_includes_acerca_and_libros(self, built_site):
        xml = _read(built_site, "sitemap.xml")
        assert "<loc>https://lecturasdeldia.org/domingo/</loc>" in xml
        assert "<loc>https://lecturasdeldia.org/acerca/</loc>" in xml
        assert "<loc>https://lecturasdeldia.org/libros/</loc>" in xml
        # at least one per-book page with its EU counterpart slug
        assert "https://lecturasdeldia.org/libros/mateo/" in xml
