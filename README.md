# lecturasdeldia.org

Lecturas de la Misa del día según el calendario litúrgico de la Conferencia Episcopal Española (CEE), en castellano y euskera (bizkaiera).

Sitio estático generado automáticamente cada noche. Muestra las lecturas del día con contexto litúrgico completo: temporada, color, ciclo, rango y memorias opcionales.

## Funcionalidades

- **Lecturas del día** — castellano en `/`, euskera en `/eu/`, con ventana de 30 días atrás y 365 adelante
- **Buscador** (`/buscar/`, `/eu/bilatu/`) — por cita bíblica, libro o texto, con índice estático por idioma
- **Navegación por libro** (`/libros/`, `/eu/liburuak/`) — todas las apariciones de cada libro bíblico agrupadas por contexto litúrgico (domingos, tiempos fuertes, ferial, santos, misas rituales)
- **Calendario** — navegación por fechas con datos litúrgicos precalculados

## Datos

Los textos provienen del Leccionario oficial de la CEE, procesados offline en formato JSON. La versión en euskera procede del Leccionario en bizkaiera. Los datos (`data/*.json`) y el motor litúrgico (`liturgia.py`) se sincronizan automáticamente desde el repositorio privado de origen mediante GitHub Actions; las correcciones de contenido se hacen allí, no aquí.

Además de los leccionarios del calendario (`Leccionario_CL.json`, `Lezionarioa_CL.json`), `data/` publica los leccionarios rituales (Difuntos, Necesidades, Rituales — incluido `Lezionarioa_Difuntos.json` en euskera) como dataset reutilizable por otros proyectos; el sitio solo usa sus citas para las páginas por libro.

## Tecnología

- Python 3.14 + Jinja2 para la generación del sitio (`generate_site.py`)
- HTML/CSS/JS vanilla para el frontend
- GitHub Pages para el hosting
- GitHub Actions para la generación nocturna (2:00 UTC) y en cada push

## Licencia

Los textos litúrgicos son propiedad de la Conferencia Episcopal Española.
El código del generador es open source bajo MIT.
