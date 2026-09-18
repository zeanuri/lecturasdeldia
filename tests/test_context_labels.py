"""Etiquetas de contexto de las paginas por libro (/libros/, /eu/liburuak/).

Puerta contra el fallo del 2026-09-15: la clave cruda del JSON pintada como
etiqueta («Pentecostes vigilia», «Maria madre dios», «[3]», rituales en
minuscula y en castellano tambien en euskera). Recorre los MISMOS ficheros
que el build, asi que una clave nueva en el leccionario sin fila en la tabla
rompe aqui antes de salir a la web.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import generate_site as g  # noqa: E402
from context_labels import (  # noqa: E402
    CALENDAR_KEY_LABELS, CATEGORY_LABELS, calendar_key_label, ritual_title,
)

_NUMERADA = re.compile(r"^(to|adviento|cuaresma|pascua)_\d+$|^(adviento|cuaresma|pascua)_\d+_[a-z]+$")
_CLAVE_CRUDA = re.compile(r"_|\[\d+\]")


@pytest.fixture(scope="module")
def entries():
    lecs = g.load_leccionarios()
    alll = {"leccionario_cl": lecs["es"], "lezionarioa_cl": lecs["eu"]}
    for extra in ("Leccionario_Difuntos.json", "Leccionario_Necesidades.json",
                  "Leccionario_Rituales.json"):
        with open(g.DATA_DIR / extra, encoding="utf-8") as f:
            alll[extra.replace(".json", "").lower()] = json.load(f)
    by_book = g._collect_book_citas(alll)
    out = {}
    for lang in ("es", "eu"):
        vistos = {}
        for book_entries in g._books_for_lang(by_book, lang).values():
            for e in book_entries:
                vistos.setdefault((e["section"], e["slug"], e["slot"]), e)
        out[lang] = list(vistos.values())
    return out


def test_toda_clave_de_calendario_no_numerada_tiene_fila():
    """Ambos leccionarios (es + eu), dominical y ferial_fuerte."""
    faltan = set()
    for fichero in ("Leccionario_CL.json", "Lezionarioa_CL.json"):
        with open(g.DATA_DIR / fichero, encoding="utf-8") as f:
            L = json.load(f)
        claves = {k for c in L["dominical"].values() for k in c} | set(L["ferial_fuerte"])
        for k in claves:
            if _NUMERADA.match(k):
                continue
            if calendar_key_label(k, "es") is None:
                faltan.add(k)
    # `domingo` es un artefacto del parser (ciclo A) pendiente de retirar del JSON.
    assert faltan <= {"domingo"}, f"claves sin etiqueta: {sorted(faltan)}"


def test_tabla_tiene_las_dos_columnas():
    for k, v in CALENDAR_KEY_LABELS.items():
        assert v.get("es") and v.get("eu"), k
    for k, v in CATEGORY_LABELS.items():
        assert v.get("es") and v.get("eu"), k


@pytest.mark.parametrize("lang", ["es", "eu"])
def test_ninguna_etiqueta_es_clave_cruda(entries, lang):
    malas = []
    for e in entries[lang]:
        if e["section"] == "dominical" and e["slug"] == "domingo":
            continue  # artefacto del parser, ver arriba
        if e["section"] == "santos":
            continue  # etiqueta = fecha («3 de febrero», «otsailaren 3a»), ya legible
        label = g._format_label(e, lang)
        slot = g._slot_label(e["slot"], lang, e.get("n"))
        if _CLAVE_CRUDA.search(label) or _CLAVE_CRUDA.search(slot) or not (label[:1].isupper() or label[:1].isdigit()):
            malas.append((e["section"], e["slug"], e["slot"], label, slot))
    assert not malas, malas[:10]


def test_rituales_ranura_es_categoria_y_no_indice(entries):
    for e in entries["es"]:
        if e["section"] in ("rituales", "diversas_necesidades", "votivas"):
            assert e["slot"] in CATEGORY_LABELS, (e["slug"], e["slot"])
            assert isinstance(e.get("n"), int), (e["slug"], e["slot"])
            assert e["titulo"], e["slug"]


def test_difuntos_formulario_numerado(entries):
    nums = sorted({int(e["slug"]) for e in entries["es"] if e["section"] == "lecturas"})
    assert nums == list(range(1, len(nums) + 1))


def test_ferias_de_diciembre_son_adviento():
    assert calendar_key_label("navidad_17_dic", "es") == "Adviento — 17 de diciembre"
    assert calendar_key_label("navidad_29_dic", "es") == "Navidad — 29 de diciembre"
    assert calendar_key_label("navidad_2_ene", "eu") == "Eguberrialdia — urtarrilaren 2a"
    assert calendar_key_label("vigilia_pascual_lectura_3", "eu") == "Pazko Bijilia — 3. irakurgaia"


def test_euskera_usa_las_cadenas_ya_validadas():
    """La columna vasca de las fiestas mayores es la de liturgical_names_eu."""
    from liturgical_names_eu import EXACT_NAME_ES_TO_EU
    for k in ("epifania", "pentecostes", "trinidad", "corpus", "cristo_rey", "ceniza"):
        es, eu = CALENDAR_KEY_LABELS[k]["es"], CALENDAR_KEY_LABELS[k]["eu"]
        assert EXACT_NAME_ES_TO_EU.get(es) == eu, k


def test_ritual_title_baja_a_frase():
    assert ritual_title("En La Administración Del Viático").startswith("En la administración del ")
    assert ritual_title("Por Los Esposos") == "Por los esposos"
