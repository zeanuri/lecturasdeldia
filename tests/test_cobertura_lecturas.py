"""Cobertura de lecturas: ningun dia publicable puede salir sin texto.

Motivo (2026-08-07): el ciclo A del leccionario no tenia las claves `to_24` ni
`to_33`, y el XXIV y el XXXIII domingo del Tiempo Ordinario (13-sep y 15-nov de
2026) se generaban sin una sola lectura. El fallo era MUDO: `lookup_readings`
devuelve None y la pagina sale con cabecera y sin cuerpo, asi que solo se veia
abriendo esos dos dias concretos.

El barrido cubre los tres ciclos dominicales completos, no solo el ano en curso:
un hueco en el ciclo B no rompe nada hoy pero rompe el ano liturgico siguiente,
que es exactamente como llego el de este.
"""

import json
import sys
from datetime import date, timedelta
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import liturgia  # noqa: E402

SLOTS_OBLIGATORIAS = ("primera", "salmo", "evangelio")

# La Vigilia Pascual no tiene "primera": sus 7 lecturas del AT viven en
# `vigilia_lecturas` (ver test_vigilia_pascual.py). No es un hueco.
CLAVES_SIN_PRIMERA = {"vigilia_pascual"}

# Huecos tolerados. Vacio desde el 07-08-2026: los que habia (6 ferias del ciclo
# ferial I, cristo_rey y corpus del ciclo B, y 4 santos con el salmo remitido al
# Comun) se repararon con leccionarios/CEE/fill_missing_ferial.py y
# fill_santos_salmo_comun.py. Si algo vuelve a aparecer aqui, se repara, no se
# anade a esta lista.
HUECOS_CONOCIDOS = set()


@pytest.fixture(scope="module")
def leccionario():
    """El JSON inyectado a mano, como hace generate_site.

    No vale con llamar a lookup_readings sin cache: su fallback
    (_load_leccionario) apunta a un directorio que no existe y devuelve None
    para TODOS los dias, lo que convierte cualquier asercion en falso negativo.
    """
    with open(ROOT / "data" / "Leccionario_CL.json", encoding="utf-8") as f:
        return json.load(f)


def _dias(inicio, fin):
    d = inicio
    while d <= fin:
        yield d
        d += timedelta(days=1)


def test_tres_anos_liturgicos_sin_dias_mudos(leccionario):
    """Tres anos seguidos cubren los ciclos A, B y C y ambos ciclos feriales."""
    huecos, nuevos = [], []
    for d in _dias(date(2026, 1, 1), date(2028, 12, 31)):
        resultado = liturgia.calculate(d)
        lecturas = liturgia.lookup_readings(resultado, cache=leccionario)
        nombre = resultado.get("name", "")
        clave = liturgia._build_dominical_key(resultado)

        if not lecturas:
            fallo = f"{d} {nombre} — lookup_readings devuelve None"
        else:
            slots = [s for s in SLOTS_OBLIGATORIAS
                     if not (s == "primera" and clave in CLAVES_SIN_PRIMERA)]
            vacias = [s for s in slots if liturgia.is_empty_reading(lecturas.get(s))]
            fallo = f"{d} {nombre} — sin {', '.join(vacias)}" if vacias else None

        if fallo:
            huecos.append(fallo)
            if d.isoformat() not in HUECOS_CONOCIDOS:
                nuevos.append(fallo)

    assert not nuevos, "Dias sin lecturas NO registrados:\n  " + "\n  ".join(nuevos)

    # Si un hueco conocido se repara, hay que sacarlo de la lista: dejarlo
    # ahi encubre el siguiente que aparezca en esa misma fecha.
    vistos = {h.split()[0] for h in huecos}
    resueltos = HUECOS_CONOCIDOS - vistos
    assert not resueltos, (
        f"Huecos ya reparados, quitalos de HUECOS_CONOCIDOS: {sorted(resueltos)}")


def test_todos_los_domingos_del_to_en_los_tres_ciclos(leccionario):
    """Cada to_N debe existir en A, B y C.

    Comprobar solo el ano vigente deja pasar los huecos de los otros dos
    ciclos, que es como este fallo sobrevivio hasta produccion.
    """
    dominical = leccionario["dominical"]
    faltan = []
    for ciclo in ("A", "B", "C"):
        presentes = {int(k[3:]) for k in dominical[ciclo] if k.startswith("to_")}
        # El domingo 34 no usa clave to_34: es Cristo Rey, con clave propia.
        for n in range(2, 34):
            if n not in presentes:
                faltan.append(f"{ciclo}/to_{n}")

    assert not faltan, f"Domingos del Tiempo Ordinario ausentes: {faltan}"


def test_solemnidades_en_los_tres_ciclos(leccionario):
    dominical = leccionario["dominical"]
    faltan = [f"{c}/{k}" for c in "ABC" for k in ("cristo_rey", "corpus")
              if k not in dominical[c]]
    assert not faltan, f"Solemnidades ausentes: {faltan}"


def test_los_dos_domingos_que_fallaban(leccionario):
    """Guarda concreta del fallo original, con sus fechas reales."""
    for iso, esperado in (("2026-09-13", "Mt 18, 21-35"),
                          ("2026-11-15", "Mt 25, 14-15. 19-21")):
        resultado = liturgia.calculate(date.fromisoformat(iso))
        lecturas = liturgia.lookup_readings(resultado, cache=leccionario)
        assert lecturas, f"{iso}: sin lecturas"
        assert lecturas["evangelio"]["cita"] == esperado
        for slot in SLOTS_OBLIGATORIAS:
            assert not liturgia.is_empty_reading(lecturas.get(slot)), \
                f"{iso}: {slot} vacia"
