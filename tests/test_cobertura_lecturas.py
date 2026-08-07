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

import generate_site  # noqa: E402  (SITE_EPOCH: la ventana no se clava a mano)
import liturgia  # noqa: E402

SLOTS_OBLIGATORIAS = ("primera", "salmo", "evangelio")

# Ventana barrida. Se deriva del generador en vez de fijar anos a mano: un rango
# clavado (estaba en 2026-2028) deja de cubrir el horizonte publicado en cuanto
# pasa el tiempo, y lo hace en silencio. Se toma el maximo entre lo que el sitio
# publica y tres anos liturgicos, que es lo que hace falta para visitar los tres
# ciclos dominicales y los dos feriales.
DIAS_ADELANTE = 365


def _ventana():
    # El MISMO reloj que produccion: generate_site fecha el sitio en
    # Europe/Madrid, y `date.today()` en el runner (UTC) daba un dia distinto
    # durante la franja entre ambas medianoches.
    hoy = generate_site.hoy_local()
    inicio = min(generate_site.SITE_EPOCH, hoy)
    fin = max(hoy + timedelta(days=DIAS_ADELANTE),
              inicio + timedelta(days=3 * 366))
    return inicio, fin

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

    Se inyecta a proposito en vez de dejar que lookup_readings use su fallback
    (_load_leccionario): asi el test comprueba el mismo camino que el
    generador. El fallback ya prueba los dos layouts del fichero, pero si
    volviera a fallar lo haria devolviendo None para TODOS los dias, y eso
    convierte cualquier asercion de este modulo en un falso negativo.
    """
    with open(ROOT / "data" / "Leccionario_CL.json", encoding="utf-8") as f:
        return json.load(f)


@pytest.fixture(scope="module")
def lezionarioa():
    with open(ROOT / "data" / "Lezionarioa_CL.json", encoding="utf-8") as f:
        return json.load(f)


def _dias(inicio, fin):
    d = inicio
    while d <= fin:
        yield d
        d += timedelta(days=1)


def test_tres_anos_liturgicos_sin_dias_mudos(leccionario):
    """Tres anos seguidos cubren los ciclos A, B y C y ambos ciclos feriales."""
    huecos, nuevos = [], []
    for d in _dias(*_ventana()):
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


def test_rejilla_ferial_completa(leccionario):
    """34 semanas x 6 dias x 2 ciclos feriales, y la tabla de evangelios.

    El barrido por fechas no basta para lo ferial, igual que no bastaba para
    lo dominical: una feria tapada por una fiesta en los tres anos del barrido
    no se visita nunca, y el hueco espera al ano en que la fiesta cae en otro
    dia. La rejilla se comprueba entera, al margen del calendario.
    """
    ferial = leccionario["ferial_to"]
    dias = ("lunes", "martes", "miercoles", "jueves", "viernes", "sabado")
    esperadas = {f"{s}_{d}" for s in range(1, 35) for d in dias}

    faltan = []
    for ciclo in ("I", "II"):
        faltan += [f"{ciclo}/{k}" for k in sorted(esperadas - set(ferial[ciclo]))]
    assert not faltan, f"Claves feriales ausentes: {faltan}"

    # El evangelio ferial no depende del ano: vive en su propia tabla y tiene
    # que cubrir la misma rejilla, o el dia sale con primera y salmo y sin
    # evangelio — otro fallo mudo.
    faltan_ev = sorted(esperadas - set(ferial["evangelio"]))
    assert not faltan_ev, f"Evangelios feriales ausentes: {faltan_ev}"


def test_paridad_estructural_euskera(leccionario, lezionarioa):
    """Toda clave del castellano existe en euskera.

    El euskera es cobertura parcial declarada (`meta.coverage_pct_calendar_texto`)
    y la politica prohibe traducir, asi que NO se exige texto. Lo que si se
    exige es la clave: cuando una lectura falta, `_build_readings_eu` emite el
    slot marcado `empty` con la cita (que es neutra) y el enlace a la pagina
    castellana — NUNCA copia el texto castellano. Pero si falta el nodo entero,
    la pagina vasca se queda sin esa celebracion sin avisar. Asi llegaron a produccion los mismos huecos
    dominicales que se reparon en castellano el 07-08-2026, intactos en el
    fichero vasco durante meses.
    """
    faltan = []
    for ciclo in ("A", "B", "C"):
        faltan += [f"dominical/{ciclo}/{k}"
                   for k in sorted(set(leccionario["dominical"][ciclo])
                                   - set(lezionarioa["dominical"][ciclo]))]
    # `evangelio` incluido a proposito: es una tabla hermana de I/II dentro de
    # ferial_to y se me escapo en la primera version de esta guarda — Codex
    # encontro 3 claves ausentes ahi que se repararon sin quedar vigiladas.
    for ciclo in ("I", "II", "evangelio"):
        faltan += [f"ferial_to/{ciclo}/{k}"
                   for k in sorted(set(leccionario["ferial_to"][ciclo])
                                   - set(lezionarioa["ferial_to"][ciclo]))]
    for bloque in ("ferial_fuerte", "santos"):
        faltan += [f"{bloque}/{k}"
                   for k in sorted(set(leccionario[bloque])
                                   - set(lezionarioa[bloque]))]

    assert not faltan, (
        "Claves presentes en castellano y ausentes en euskera "
        f"({len(faltan)}): {faltan[:20]}")


# Dias cuya pagina vasca sale sin UNA SOLA lectura, con su motivo. La cobertura
# parcial es politica declarada, pero "cero lecturas" no es cobertura parcial:
# es una pagina sin contenido. Cada excepcion se justifica o se repara.
SIN_EUSKERA_JUSTIFICADO = {
    "sagrada_familia": (
        "El corpus bizkaiera no trae ninguna de sus lecturas en los ciclos B y C. "
        "Los ficheros que aparentan traerlas (Sal83..._eu.txt, 1jn3,1-2.21-24_eu.txt) "
        "contienen texto CASTELLANO mal etiquetado y is_real_basque_reading los "
        "rechaza con razon. Traducir esta prohibido, asi que se queda."),
    "vigilia_pascual": (
        "Sus 7 lecturas del AT viven en `vigilia_lecturas`, no en los slots "
        "normales (ver test_vigilia_pascual.py). No es un hueco real."),
}


def test_ninguna_pagina_vasca_se_queda_sin_lecturas(leccionario, lezionarioa):
    """Cero lecturas en euskera no es cobertura parcial: es una pagina vacia.

    La guarda NO exige texto en cada lectura — el euskera es cobertura parcial
    declarada (`meta.coverage_pct_calendar_texto`) y la politica prohibe
    traducir, asi que un hueco suelto es legitimo y cae al enlace castellano.
    Lo que no es legitimo es que un dia entero salga sin nada: eso el lector lo
    vive como una pagina rota, no como una traduccion pendiente.

    Se comprueba la salida de `get_day_data`, que es lo que consume la
    plantilla, y no `lookup_readings` directamente: la version anterior hacia
    `continue` ante un resultado vacio, asi que una entrada estructural que
    existiera pero fuese `{}` producia la pagina vacia sin que este test la
    llegara a clasificar. La guarda saltaba por encima justo del caso que
    buscaba.
    """
    lectionaries = {"es": leccionario, "eu": lezionarioa}
    vacios, nuevos = [], []
    for d in _dias(*_ventana()):
        datos = generate_site.get_day_data(d, "eu", lectionaries)
        lecturas = datos.get("readings") or []
        if not lecturas:
            continue
        if all(r.get("empty") for r in lecturas):
            resultado = liturgia.calculate(d)
            clave = liturgia._build_dominical_key(resultado) or ""
            vacios.append(f"{d} {resultado.get('name', '')} [{clave}]")
            if clave not in SIN_EUSKERA_JUSTIFICADO:
                nuevos.append(vacios[-1])

    assert not nuevos, (
        "Dias cuya pagina vasca sale sin una sola lectura y sin motivo "
        "declarado:\n  " + "\n  ".join(nuevos))


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
