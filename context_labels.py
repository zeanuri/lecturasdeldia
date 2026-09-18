"""Etiquetas legibles para las claves del leccionario, por idioma.

Las paginas por libro (/libros/<slug>/, /eu/liburuak/<slug>/) listan cada
cita con su contexto liturgico. Ese contexto viene de la CLAVE del JSON
(`pentecostes_vigilia`, `navidad_17_dic`, `en_la_administracion_del_viatico`)
y hasta 2026-09-15 se pintaba con `slug.replace("_", " ").capitalize()`:
«Pentecostes vigilia», «Navidad XVII — dic» (que ademas es Adviento),
«Maria madre dios», y los rituales en minuscula y sin tilde. En euskera salia
lo mismo, en castellano.

Aqui vive la tabla clave -> etiqueta, con las dos columnas juntas para que
se revisen a la vez. Doctrina heredada de liturgical_names_eu.py: la columna
vasca es batua (la voz del sitio), se compone de piezas ya validadas alli y
lo que es composicion nueva va marcado REVIEW. Lo que no tiene traduccion
validada NO se inventa: los titulos de los rituales salen en castellano en
las dos lenguas, con su categoria (Itun Zaharra, salmoa...) si en batua.

Las claves numeradas (to_14, adviento_2, cuaresma_3_lunes, 14_martes) no
pasan por aqui: las compone generate_site._format_label a partir del numero.
"""

from __future__ import annotations

import re

from liturgical_names_eu import _MES_ES_TO_EU

# ── Claves de calendario (dominical + ferial_fuerte) ─────────────────────────
# slug -> {"es": ..., "eu": ...}. Los valores vascos sin REVIEW estan tomados
# tal cual de EXACT_NAME_ES_TO_EU (liturgical_names_eu.py).
CALENDAR_KEY_LABELS: dict[str, dict[str, str]] = {
    # Navidad
    "natividad_vigilia":    {"es": "Natividad del Señor — Misa vespertina de la vigilia",
                             "eu": "Jaunaren Jaiotza — Bezperako Meza"},            # REVIEW
    "natividad_medianoche": {"es": "Natividad del Señor — Misa de medianoche",
                             "eu": "Jaunaren Jaiotza — Gauerdiko Meza"},            # REVIEW
    "natividad_aurora":     {"es": "Natividad del Señor — Misa de la aurora",
                             "eu": "Jaunaren Jaiotza — Egunsentiko Meza"},          # REVIEW
    "natividad_dia":        {"es": "Natividad del Señor — Misa del día",
                             "eu": "Jaunaren Jaiotza — Eguneko Meza"},              # REVIEW
    "sagrada_familia":      {"es": "La Sagrada Familia de Jesús, María y José",
                             "eu": "Famili Santua: Jesus, Maria eta Jose"},
    "maria_madre_dios":     {"es": "Santa María, Madre de Dios",
                             "eu": "Jainkoaren Ama"},
    # Duplicado de maria_madre_dios en el ciclo C (artefacto del parser, mismas
    # tres citas). Se etiqueta igual hasta que se retire del JSON.
    "solemnidad_de_santa_mar_a": {"es": "Santa María, Madre de Dios",
                                  "eu": "Jainkoaren Ama"},
    "navidad_post_2":       {"es": "II Domingo de Navidad",
                             "eu": "Eguberri Ondorengo II Igandea"},
    "epifania":             {"es": "Epifanía del Señor",
                             "eu": "Jaunaren Agerkundea"},
    "bautismo":             {"es": "El Bautismo del Señor",
                             "eu": "Jaunaren Bataioa"},
    "presentacion":         {"es": "La Presentación del Señor",
                             "eu": "Jaunaren Aurkezpena"},
    # Cuaresma y Semana Santa
    "ceniza":               {"es": "Miércoles de Ceniza",
                             "eu": "Hauts Asteazkena"},
    "ramos":                {"es": "Domingo de Ramos en la Pasión del Señor",
                             "eu": "Jaunaren Nekaldiko Erramu Igandea"},
    "misa_crismal":         {"es": "Misa crismal",
                             "eu": "Krisma Meza"},                                  # REVIEW
    "jueves_santo":         {"es": "Jueves Santo — Misa vespertina de la Cena del Señor",
                             "eu": "Ostegun Santua: Jaunaren Afaria"},
    "viernes_santo":        {"es": "Viernes Santo — La Pasión del Señor",
                             "eu": "Jaunaren Nekaldiko Ostiral Santua"},
    "vigilia_pascual":      {"es": "Vigilia Pascual",
                             "eu": "Pazko Bijilia"},
    # Pascua
    "pascua_resurreccion":  {"es": "Domingo de Pascua de la Resurrección del Señor",
                             "eu": "Jaunaren Biztuerako Pazko Igandea"},
    "ascension":            {"es": "La Ascensión del Señor",
                             "eu": "Igokunde Igandea"},
    "pentecostes_vigilia":  {"es": "Pentecostés — Misa vespertina de la vigilia",
                             "eu": "Pentekoste — Bezperako Meza"},                  # REVIEW
    "pentecostes":          {"es": "Domingo de Pentecostés",
                             "eu": "Pentekoste Igandea"},
    "maria_madre_iglesia":  {"es": "Bienaventurada Virgen María, Madre de la Iglesia",
                             "eu": "Andre Maria, Elizaren Ama"},
    # Solemnidades del Tiempo Ordinario
    "trinidad":             {"es": "Santísima Trinidad",
                             "eu": "Hirutasun Igandea"},
    "corpus":               {"es": "Santísimo Cuerpo y Sangre de Cristo (Corpus Christi)",
                             "eu": "Kristoren Gorputz-Odol Santuak"},
    "sagrado_corazon":      {"es": "Sagrado Corazón de Jesús",
                             "eu": "Jesusen Bihotz Guztiz Santua"},
    "transfiguracion":      {"es": "La Transfiguración del Señor",
                             "eu": "Jaunaren Antzaldatzea"},
    "cristo_rey":           {"es": "Nuestro Señor Jesucristo, Rey del Universo",
                             "eu": "Kristo Errege"},
}

_VIGILIA_LECTURA = re.compile(r"^vigilia_pascual_lectura_(\d)$")
# navidad_17_dic .. navidad_24_dic son ferias de ADVIENTO (17-24 dic); el
# prefijo "navidad_" es solo el cajon del JSON.
_FERIA_NAVIDAD = re.compile(r"^navidad_(\d{1,2})_(dic|ene)$")

_MES = {"dic": "diciembre", "ene": "enero"}


def calendar_key_label(slug: str, lang: str) -> str | None:
    """Etiqueta de una clave de calendario no numerada; None si no es de aqui."""
    if slug in CALENDAR_KEY_LABELS:
        return CALENDAR_KEY_LABELS[slug][lang]
    m = _VIGILIA_LECTURA.match(slug)
    if m:
        n = m.group(1)
        return (f"Pazko Bijilia — {n}. irakurgaia" if lang == "eu"
                else f"Vigilia Pascual — lectura {n}")
    m = _FERIA_NAVIDAD.match(slug)
    if m:
        dia, mes_abr = int(m.group(1)), m.group(2)
        mes_es = _MES[mes_abr]
        adviento = mes_abr == "dic" and dia <= 24
        if lang == "eu":
            tiempo = "Abendualdia" if adviento else "Eguberrialdia"
            mes_eu = _MES_ES_TO_EU[mes_es]
            return f"{tiempo} — {mes_eu[:-1]}aren {dia}a"                            # REVIEW
        tiempo = "Adviento" if adviento else "Navidad"
        return f"{tiempo} — {dia} de {mes_es}"
    return None


# ── Rituales, difuntos y necesidades ─────────────────────────────────────────
# Categoria del leccionario (nivel bajo la formula) -> etiqueta.
CATEGORY_LABELS: dict[str, dict[str, str]] = {
    "antiguo_testamento": {"es": "Antiguo Testamento", "eu": "Itun Zaharra"},
    "nuevo_testamento":   {"es": "Nuevo Testamento",   "eu": "Itun Berria"},
    "primera_lectura":    {"es": "1ª lectura",         "eu": "1. irakurgaia"},
    "segunda_lectura":    {"es": "2ª lectura",         "eu": "2. irakurgaia"},
    "salmo":              {"es": "salmo",              "eu": "salmoa"},
    "aleluya":            {"es": "aleluya",            "eu": "aleluia"},
    "evangelio":          {"es": "evangelio",          "eu": "ebanjelioa"},
}

# Palabras que conservan mayuscula al pasar un titulo de ritual a frase
# (conjunto fijado por el usuario el 2026-09-18).
_MAYUSCULAS: set[str] = {
    "Señor", "Jesucristo", "Jesús", "Dios", "Espíritu", "Santo", "María",
    "Virgen", "Madre", "Iglesia", "Trinidad", "Eucaristía", "Cruz", "Vigilia",
    "Pascual", "Sagrado", "Corazón", "Santísima", "Santísimo", "Sangre", "Nombre",
    "Viático", "José", "Pedro", "Pablo",
}

# Titulos donde una palabra de _MAYUSCULAS va en minuscula por su sentido
# (iglesia = edificio). Clave = titulo tal como viene del JSON. «De Un Santo
# Apóstol» (santo = adjetivo) no esta: esa votiva solo tiene `ref`, sin
# lecturas propias, y nunca llega a /libros/.
_EXCEPCIONES: dict[str, str] = {
    "En La Dedicación De Una Iglesia": "En la dedicación de una iglesia",
}


def ritual_title(titulo: str) -> str:
    """«En La Administración Del Viático» -> «En la administración del Viático».

    Los JSON de rituales y necesidades traen el titulo en Title Case (asi
    salio del OCR). Se baja todo a minuscula salvo la primera palabra y las
    de _MAYUSCULAS. Sale en castellano en las dos lenguas: no hay traduccion
    validada de estas formulas y el sitio no inventa.
    """
    if titulo in _EXCEPCIONES:
        return _EXCEPCIONES[titulo]
    palabras = titulo.split()
    out = []
    for i, p in enumerate(palabras):
        nucleo = p.strip(",;:.")
        if i == 0 or nucleo in _MAYUSCULAS:
            out.append(p)
        else:
            out.append(p.lower())
    return " ".join(out)


def formulario_label(n: int, lang: str) -> str:
    """Formulario N de las Misas de difuntos (lista `lecturas` del JSON)."""
    return f"{n}. formularioa" if lang == "eu" else f"Formulario {n}"
