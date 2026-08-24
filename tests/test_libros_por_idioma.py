"""Las paginas de /libros/ no mezclan idiomas ni repiten filas.

_collect_book_citas junta en una sola bolsa los leccionarios castellanos y los
vascos. Esa bolsa se renderizaba entera en las dos lenguas, con dos efectos
visibles en el sitio publicado: la pagina castellana ensenaba citas en forma
vasca venidas de lezionarioa_cl, y la vasca repetia cada cita dos veces (la
castellana se localiza al renderizar y acaba siendo identica a la vasca).

Estas pruebas fallan con el codigo anterior a _books_for_lang.
"""
import re
import pytest

from generate_site import _books_for_lang, localize_cita_full

FORMA_VASCA = re.compile(r"\b(eta|ik\.)\b")


@pytest.fixture
def bolsa():
    """Dos fuentes que dicen lo mismo, una en cada idioma, mas una solo-ES."""
    def e(source, cita, slug="dom_01", slot="salmo", section="dominical"):
        return {"cita": cita, "group": "domingos_a", "section": section,
                "cycle": "A", "slug": slug, "slot": slot, "source": source}
    return {
        "Sal": [
            e("leccionario_cl", "Sal 88, 4-5. 27 y 29 (R.: cf. 2a)"),
            e("lezionarioa_cl", "Sal 88, 4-5. 27 eta 29 (R.: ik. 2a)"),
            e("leccionario_rituales", "Sal 22, 1-3a", slug="por_los_esposos",
              section="rituales"),
        ],
    }


def test_es_sin_formas_vascas(bolsa):
    for entries in _books_for_lang(bolsa, "es").values():
        for entry in entries:
            assert not FORMA_VASCA.search(entry["cita"]), (
                f"cita en forma vasca en la pagina castellana: {entry['cita']!r} "
                f"(fuente {entry['source']})")


def test_eu_no_repite_la_misma_cita(bolsa):
    vistas = [
        (book, localize_cita_full(x["cita"], "eu"), x["section"], x["slug"], x["slot"])
        for book, entries in _books_for_lang(bolsa, "eu").items() for x in entries
    ]
    assert len(vistas) == len(set(vistas)), "filas duplicadas en la pagina vasca"


def test_eu_prefiere_la_fuente_vasca(bolsa):
    sal = _books_for_lang(bolsa, "eu")["Sal"]
    par = [x for x in sal if x["slug"] == "dom_01"]
    assert len(par) == 1
    assert par[0]["source"] == "lezionarioa_cl"


def test_ningun_idioma_pierde_contextos(bolsa):
    todos = {(b, e["section"], e["slug"], e["slot"])
             for b, v in bolsa.items() for e in v}
    for lang in ("es", "eu"):
        vista = {(b, e["section"], e["slug"], e["slot"])
                 for b, v in _books_for_lang(bolsa, lang).items() for e in v}
        assert vista == todos, f"{lang} pierde contextos: {todos - vista}"
