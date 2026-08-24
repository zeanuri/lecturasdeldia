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
    "home_title_prefix": "Evangelio de hoy y lecturas de la Misa",
    "home_meta_description": "Evangelio de hoy y lecturas de la Misa del día, con los textos oficiales del leccionario de la Conferencia Episcopal Española",

    # Los tres siguientes llevan marcado inline y se pintan con |safe. Es
    # deliberado: en castellano el enlace envuelve "citas del leccionario libro
    # por libro", y en euskera el verbo `arakatu` queda FUERA del enlace. Las
    # fronteras del <a> no coinciden entre los dos idiomas, asi que trocear la
    # frase en fragmentos interpolables obligaria al euskera a copiar el orden
    # castellano. Son constantes de autor, no entrada de usuario.
    "home_intro_h2": "Lecturas de la Misa de hoy",
    "home_intro_p1": "Cada día encontrarás aquí el evangelio de hoy y todas las "
                     "lecturas de la Misa —primera lectura, salmo responsorial y "
                     "segunda lectura cuando corresponde— con los textos oficiales "
                     "del leccionario de la Conferencia Episcopal Española.",
    "home_intro_p2": 'Puedes consultar las lecturas de cualquier fecha del '
                     'calendario litúrgico, <a href="/buscar/">buscar por cita '
                     'bíblica, santo o celebración</a>, explorar las '
                     '<a href="/libros/">citas del leccionario libro por libro</a> '
                     'o leer las lecturas <a href="/eu/">en euskera</a>. '
                     'Más información en <a href="/acerca/">Acerca de</a>.',
    "domingo_title_prefix": "Evangelio del domingo y lecturas de la Misa dominical",
    "domingo_meta_description": "Evangelio del domingo y lecturas de la Misa dominical, con los textos oficiales del leccionario de la Conferencia Episcopal Española",
    # Meta-descripción base para páginas de día de diario (feria). Se antepone a
    # "{nombre litúrgico}: {citas}" en dia.html. Lidera con "Lecturas y evangelio"
    # para captar ambos términos de búsqueda; "del día" (no "de hoy") porque son
    # páginas de fecha concreta. Cierra con la autoridad CEE, como home/domingo.
    "dia_meta_description": "Lecturas y evangelio de la Misa del día, con los textos oficiales del leccionario de la Conferencia Episcopal Española",
    "acerca_link": "Acerca de",
    "libros_footer_link": "Libros del leccionario",
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
    "gospel_book_lead": "Todas las lecturas de este libro en el leccionario:",
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


    # Footer
    "diocese_aria": "Diócesis de Bilbao — bizkeliza.org",
    "diocese_alt": "Bilboko Elizbarrutia — Diócesis de Bilbao",

    # /libros/ — browse-by-book
    "libros_page_title": "Libros del leccionario",
    "libros_meta_description": "Índice de libros bíblicos del leccionario CEE — explora las citas de cada libro a lo largo del año litúrgico",
    "libros_h1": "Libros del leccionario",
    "libros_intro": "Explora las citas de cada libro bíblico tal como aparecen en el leccionario, agrupadas por contexto litúrgico (domingos, ferias, solemnidades, santos).",
    "libros_book_meta_prefix": "Citas del libro de",
    "libros_citas_label": "citas en el leccionario",
    "search_back_to_search": "Volver a la búsqueda",

    # Strings consumed by app.js (calendar, expand/collapse, search, download)
    "expand_all_open": "Expandir todas",
    "search_no_results": "La búsqueda no ha dado resultados",
    "search_results_count_one": "1 resultado",
    "search_results_count_many": "{n} resultados",
    "search_truncated": "Mostrando {shown} de {total} — refina tu búsqueda",
    "search_redirect_book_known": "“{q}” es {book}. No hay lecturas de {book} en el rango actual, pero puedes ver todas sus citas en el leccionario:",
    "search_redirect_book_link": "Ver todas las citas de {book}",
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
    "dia_meta_description": "Eguneroko Mezako irakurgaiak eta ebanjelioa",
    "dia_title_prefix": "Irakurgaiak,",
    # Verificadas en batua.eus (2026-08-23) en las dos direcciones: la
    # retrotraduccion devuelve el castellano original casi literal y el contraste
    # de forma coincide. Quedan dos elecciones lexicas DELIBERADAS contra las que
    # la maquina propone 'irakurketak' y 'Mezaren': se mantienen 'irakurgaiak'
    # (el leccionario vasco oficial se titula IRAKURGAIAK, y es el termino de
    # site_title y de las etiquetas de lectura) y 'Mezako' (ya en
    # meta_description_default y dia_meta_description). Sigue el # REVIEW: falta
    # el hablante nativo, que es otra cosa que la maquina.
    "home_title_prefix": "Gaurko ebanjelioa eta Mezako irakurgaiak",  # REVIEW
    "home_meta_description": "Gaurko ebanjelioa eta Mezako irakurgaiak, Espainiako Gotzainen Batzarreko lezionarioko testu ofizialekin",  # REVIEW
    # Traducidos con /euskeratu (Itzulpena, batua) y verificados en batua.eus el
    # 2026-08-24. Estaban cableados en castellano dentro de templates/dia.html,
    # asi que la portada /eu/ servia dos parrafos en castellano. Los destinos de
    # los enlaces siguen siendo las paginas castellanas (/buscar/, /libros/,
    # /acerca/): no existe version vasca de esas secciones. El unico que se
    # invierte es el de idioma — en /eu/ apunta a "/" y dice "gaztelaniaz".
    "home_intro_h2": "Gaurko Mezako irakurgaiak",  # REVIEW
    "home_intro_p1": "Egunero aurkituko dituzu hemen gaurko ebanjelioa eta "
                     "Mezako irakurgai guztiak —lehen irakurgaia, erantzun-salmoa "
                     "eta, dagokionean, bigarren irakurgaia—, Espainiako Gotzainen "
                     "Batzarreko lezionarioko testu ofizialekin.",  # REVIEW
    "home_intro_p2": 'Liturgia-egutegiko edozein egunetako irakurgaiak kontsulta '
                     'ditzakezu, <a href="/buscar/">aipu biblikoaren, santuaren '
                     'edo ospakizunaren arabera bilatu</a>, '
                     '<a href="/libros/">lezionarioko aipuak liburuz liburu</a> '
                     'arakatu edo irakurgaiak <a href="/">gaztelaniaz irakurri</a>. '
                     'Informazio gehiago <a href="/acerca/">Honi buruz</a> atalean.',  # REVIEW
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
    "gospel_book_lead": "Liburu honen irakurgai guztiak lezionarioan:",
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


    # Footer
    "diocese_aria": "Bilboko Elizbarrutia -- bizkeliza.org",
    "diocese_alt": "Bilboko Elizbarrutia -- Diocesis de Bilbao",

    # EU-specific: rendered when the Basque lectionary has no text for a slot
    "empty_reading_msg": "Itzulpen ofizialik ez dago oraindik bizkaieraz.",
    "read_in_spanish": "Irakurri gaztelaniaz",

    # Language toggle labels (same in BOTH variants)
    "toggle_label_es": "Lecturas",
    "toggle_label_eu": "Irakurgaiak",

    # /libros/ — liburuak biltegia
    "libros_page_title": "Lezionarioko liburuak",
    "libros_meta_description": "Lezionarioko liburu biblikoen aurkibidea — liburu bakoitzaren aipuak liturgia-urtean zehar",
    "libros_h1": "Lezionarioko liburuak",
    "libros_intro": "Ikusi liburu bakoitzeko aipuak lezionarioan agertzen diren bezala, liturgia-testuinguruaren arabera taldekatuta (igandeak, asteguneko mezak, jaiak, santuak).",
    "libros_book_meta_prefix": "Liburuaren aipuak:",
    "libros_citas_label": "aipu lezionarioan",
    "search_back_to_search": "Bilaketara itzuli",

    # Strings consumed by app.js
    "expand_all_open": "Guztiak zabaldu",
    "search_no_results": "Bilaketak ez dau emaitzarik eman",  # REVIEW
    "search_results_count_one": "Emaitza 1",
    "search_results_count_many": "{n} emaitza",
    "search_truncated": "{total}-tik {shown} agertzen — bilaketa zehaztu",
    "search_redirect_book_known": "“{q}” = {book}. Ez dago {book} liburuko irakurgairik tarte honetan, baina lezionarioko aipu guztiak ikus ditzakezu:",
    "search_redirect_book_link": "{book}-ren aipu guztiak ikusi",
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
