"""
Localization tables for lecturasdeldia.org (ES / EU bilingual site).

Phase 1 contains only I18N_ES (no behaviour change). I18N_EU will be added
in Phase 2 when the Basque variant of the site is wired up.

Strings here are pure text — HTML entities (e.g. emoji glyphs like
&#128197;) stay inside the Jinja templates so autoescape never touches
them and ES output remains byte-identical with the previous f-string and
hardcoded-template version.
"""

# ── Color map (language-agnostic, lives here for cohesion) ────────────────────
COLOR_CSS = {
    "Blanco": "white",
    "Rojo": "red",
    "Morado": "purple",
    "Verde": "green",
    "Rosa": "pink",
}


# ── Spanish ───────────────────────────────────────────────────────────────────

I18N_ES = {
    "lang": "es",

    # Site chrome
    "site_title": "Lecturas del Día",
    "today_btn": "Hoy",
    "date_btn": "Fecha",
    "date_btn_aria": "Elegir otra fecha",

    # Meta / OG
    "meta_description_default": "Lecturas de la Misa del día — Conferencia Episcopal Española",
    "og_description_default": "Lecturas de la Misa del día — CEE",
    "dia_title_prefix": "Lecturas del",
    "search_page_title_prefix": "Buscar",
    "search_meta_description": "Busca lecturas por fecha, cita bíblica, santo o tema",
    "not_found_title": "Fecha no disponible",
    "not_found_description": "La fecha solicitada no está disponible.",

    # dia.html
    "prev_aria": "Día anterior",
    "next_aria": "Día siguiente",
    "alt_readings_link": "Lecturas alternativas",
    "expand_all_collapse": "Contraer todas",
    "download_txt": "Descargar lecturas (.txt)",
    "search_btn": "Buscar",
    "aclamacion_label_prefix": "Aclamación",

    # buscar.html
    "search_h1": "Buscar lecturas",
    "search_help_intro": "Busca entre todas las lecturas del año litúrgico por:",
    "search_help_cita_label": "Cita bíblica",
    "search_help_cita_examples": "Salmo 23, Mateo 5, Génesis 1...",
    "search_help_dia_label": "Día litúrgico",
    "search_help_dia_examples": "Domingo de Pascua, Miércoles de Ceniza...",
    "search_help_santo_label": "Santo o memoria",
    "search_help_santo_examples": "San José, Santa Teresa...",
    "search_help_fecha_label": "Fecha",
    "search_help_fecha_examples": "25 de diciembre, abril...",
    "search_help_tema_label": "Tema",
    "search_help_tema_examples": "palabras del título de las lecturas",
    "search_placeholder": "Ej: Sal 23, Domingo de Pascua, San José...",
    "search_back": "Volver a las lecturas de hoy",

    # 404.html
    "not_found_h1": "Fecha no disponible",
    "not_found_body": "La fecha solicitada no tiene lecturas generadas.",
    "not_found_link": "Ir a las lecturas de hoy",

    # Reading labels (ordinario)
    "READING_LABELS": {
        "primera": "Primera Lectura",
        "salmo": "Salmo Responsorial",
        "segunda": "Segunda Lectura",
        "evangelio": "Evangelio",
    },

    # Vigilia Pascual labels
    "vigilia_lectura_format": "Lectura {n}ª",
    "vigilia_salmo": "Salmo Responsorial",
    "vigilia_cantico": "Cántico",
    "vigilia_epistola": "Epístola",

    # Date formatting
    "month_names": [
        "enero", "febrero", "marzo", "abril", "mayo", "junio",
        "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre",
    ],
    "month_abbr": [
        "ene", "feb", "mar", "abr", "may", "jun",
        "jul", "ago", "sep", "oct", "nov", "dic",
    ],
    # Composed inside get_day_data: i18n["fecha_larga_format"].format(...)
    "fecha_larga_format": "{day_name}, {day} de {month} de {year}",
    "prev_next_format": "{day} {month_abbr}",

    # index_redirect.html
    "redirect_msg": "Redirigiendo a las",
    "redirect_link": "lecturas de hoy",

    # Footer
    "diocese_aria": "Diócesis de Bilbao — bizkeliza.org",
    "diocese_alt": "Bilboko Elizbarrutia — Diócesis de Bilbao",

    # Strings consumed by app.js (calendar, expand/collapse, search, download)
    "expand_all_open": "Expandir todas",
    "search_no_results": "La búsqueda no ha dado resultados",
    "alt_readings_back": "Lecturas del día",
    "download_filename_suffix": "_lecturas",
    "download_footer": "Fuente: lecturasdeldia.org — Textos CEE",
    "calendar_month_names": [
        "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
        "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre",
    ],
    "calendar_day_headers": ["Lu", "Ma", "Mi", "Ju", "Vi", "Sá", "Do"],
    "calendar_legend": {
        "purple": "Morado", "green": "Verde", "red": "Rojo",
        "white": "Blanco", "pink": "Rosa",
    },
}


# ── Basque (bizkaiera) ────────────────────────────────────────────────────────
#
# Strings marked "# REVIEW" are the bizkaiera/batua choices most likely to
# need human validation before publishing. They render fine but the dialect
# fit may be improvable.

I18N_EU = {
    "lang": "eu",

    # Site chrome
    "site_title": "Egunaren Irakurgaiak",
    "today_btn": "Gaur",
    "date_btn": "Eguna",
    "date_btn_aria": "Beste egun bat aukeratu",  # REVIEW

    # Meta / OG
    "meta_description_default": "Eguneroko Mezako irakurgaiak -- Espainiako Gotzainen Batzarra",  # REVIEW
    "og_description_default": "Eguneroko Mezako irakurgaiak -- CEE",
    "dia_title_prefix": "Irakurgaiak,",
    "search_page_title_prefix": "Bilatu",
    "search_meta_description": "Bilatu irakurgaiak data, bibliako aipamen, santu edo gaiaren arabera",  # REVIEW
    "not_found_title": "Egun hori ez dago eskuragarri",
    "not_found_description": "Eskatutako egunak ez dauka irakurgairik sortuta.",

    # dia.html
    "prev_aria": "Aurreko eguna",
    "next_aria": "Hurrengo eguna",
    "alt_readings_link": "Beste irakurgaiak",  # REVIEW
    "expand_all_collapse": "Guztiak tolestu",
    "download_txt": "Irakurgaiak deskargatu (.txt)",
    "search_btn": "Bilatu",
    "aclamacion_label_prefix": "Aldarria",  # REVIEW (Aldarrikapena? Aklamazioa?)

    # buscar.html / bilatu.html
    "search_h1": "Irakurgaiak bilatu",
    "search_help_intro": "Bilatu urteko liturgiako irakurgai guztietan, honela:",
    "search_help_cita_label": "Bibliako aipamena",
    "search_help_cita_examples": "Sal 23, Mt 5, Has 1...",
    "search_help_dia_label": "Liturgiako eguna",
    "search_help_dia_examples": "Pazko Igandea, Hauts Asteazkena...",
    "search_help_santo_label": "Santua edo oroitzapena",
    "search_help_santo_examples": "Joseba santua, Teresa santa...",  # REVIEW
    "search_help_fecha_label": "Data",
    "search_help_fecha_examples": "abenduaren 25a, apirila...",
    "search_help_tema_label": "Gaia",
    "search_help_tema_examples": "irakurgaien izenburuetako berbak",
    "search_placeholder": "Adib.: Sal 23, Pazko Igandea, Joseba santua...",
    "search_back": "Itzuli gaurko irakurgaietara",

    # 404.html
    "not_found_h1": "Egun hori ez dago eskuragarri",
    "not_found_body": "Eskatutako egunak ez dauka irakurgairik sortuta.",
    "not_found_link": "Joan gaurko irakurgaietara",

    # Reading labels (ordinary)
    "READING_LABELS": {
        "primera": "Lehen Irakurgaia",
        "salmo": "Salmoa",
        "segunda": "Bigarren Irakurgaia",
        "evangelio": "Ebanjelioa",
    },

    # Vigilia Pascual labels
    "vigilia_lectura_format": "{n}. Irakurgaia",
    "vigilia_salmo": "Salmoa",
    "vigilia_cantico": "Kantua",  # REVIEW (Kantika?)
    "vigilia_epistola": "Epistola",

    # Date formatting -- bizkaiera/batua month names share most forms
    "month_names": [
        "urtarrila", "otsaila", "martxoa", "apirila",
        "maiatza", "ekaina", "uztaila", "abuztua",
        "iraila", "urria", "azaroa", "abendua",
    ],
    "month_abbr": [
        "urt", "ots", "mar", "api", "mai", "eka",
        "uzt", "abu", "ira", "urr", "aza", "abe",
    ],
    # Bizkaiera weekday/long-date pattern: "Astelehena, 2026ko apirilaren 28a"
    # day_name comes from liturgia.calculate() in Spanish; we map it via DAY_ES_TO_EU below.
    "fecha_larga_format": "{day_name}, {year}ko {month}ren {day}a",
    "prev_next_format": "{month_abbr} {day}",

    # index_redirect.html
    "redirect_msg": "Gaurko irakurgaietara birbidaltzen",
    "redirect_link": "gaurko irakurgaiak",

    # Footer
    "diocese_aria": "Bilboko Elizbarrutia -- bizkeliza.org",
    "diocese_alt": "Bilboko Elizbarrutia -- Diocesis de Bilbao",

    # EU-specific: rendered when the Basque lectionary has no text for a slot
    "empty_reading_msg": "Itzulpen ofizialik ez dago oraindik bizkaieraz.",
    "read_in_spanish": "Irakurri gaztelaniaz",

    # Language toggle labels (same in BOTH variants)
    "toggle_label_es": "Lecturas",
    "toggle_label_eu": "Irakurgaiak",

    # Strings consumed by app.js
    "expand_all_open": "Guztiak zabaldu",
    "search_no_results": "Bilaketak ez dau emaitzarik eman",  # REVIEW
    "alt_readings_back": "Eguneko irakurgaiak",
    "download_filename_suffix": "_irakurgaiak",
    "download_footer": "Iturria: lecturasdeldia.org -- CEE testuak",  # REVIEW
    "calendar_month_names": [
        "Urtarrila", "Otsaila", "Martxoa", "Apirila",
        "Maiatza", "Ekaina", "Uztaila", "Abuztua",
        "Iraila", "Urria", "Azaroa", "Abendua",
    ],
    # Bizkaiera weekday short forms
    "calendar_day_headers": ["Al", "As", "Az", "Eg", "Ba", "Za", "Do"],
    "calendar_legend": {
        "purple": "Morea",
        "green": "Berdea",
        "red": "Gorria",
        "white": "Zuria",
        "pink": "Arrosa",
    },
}


# Spanish day-name -> batua (for fecha_larga). liturgia.calculate() returns
# Spanish day_name; we map at the presentation boundary so calculate() stays
# untouched as the canonical liturgical model. Batua throughout to match the
# liturgical day names in liturgical_names_eu.py — no dialect mixing in titles.
DAY_ES_TO_EU = {
    "Lunes": "Astelehena",
    "Martes": "Asteartea",
    "Miercoles": "Asteazkena",
    "Miércoles": "Asteazkena",
    "Jueves": "Osteguna",
    "Viernes": "Ostirala",
    "Sabado": "Larunbata",
    "Sábado": "Larunbata",
    "Domingo": "Igandea",
}


# Same fields exist in ES (no_op there) so templates can read i18n.toggle_label_*
I18N_ES["toggle_label_es"] = "Lecturas"
I18N_ES["toggle_label_eu"] = "Irakurgaiak"
I18N_ES["empty_reading_msg"] = ""  # never rendered in ES
I18N_ES["read_in_spanish"] = ""    # never rendered in ES


I18N = {
    "es": I18N_ES,
    "eu": I18N_EU,
}


def get(lang: str) -> dict:
    """Fetch the i18n table for a language; falls back to ES."""
    return I18N.get(lang, I18N_ES)


def localize_day_name(day_name: str, lang: str) -> str:
    """Translate liturgia.calculate()'s Spanish day_name to the target language."""
    if lang == "eu":
        return DAY_ES_TO_EU.get(day_name, day_name)
    return day_name
