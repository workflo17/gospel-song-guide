"""Build the paste-ready Grok songwriting prompt for a given day.

Takes the JSON that gospel.py wrote and wraps it in prompt 1 from the guide, with
the day's Gospel and commentary already pasted in. Use this when Grok cannot look
the day up itself: a future date, or before the Automation is set up.

    python make_prompt.py gospel-2026-08-19.json          # to stdout
    python make_prompt.py gospel-2026-08-19.json --out letras/2026-08-19.txt

The scripture translation is copyrighted, so the files this writes stay local and
gitignored, exactly like the JSON they come from.
"""

import argparse
import datetime as dt
import json
import os
import re

DIAS = ["lunes", "martes", "miercoles", "jueves", "viernes", "sabado", "domingo"]
DIAS_ACC = ["lunes", "martes", "miércoles", "jueves", "viernes",
            "sábado", "domingo"]
MESES = ["enero", "febrero", "marzo", "abril", "mayo", "junio", "julio",
         "agosto", "septiembre", "octubre", "noviembre", "diciembre"]

# the feed appends its own footer to every block; it is not scripture
FOOTER = re.compile(
    r"(Extraído de la Biblia.*|Para recibir cada mañana.*|"
    r"^\s*evangeliodeldia\.org\s*$)", re.M)

PLANTILLA = """Eres compositor de música cristiana en español.

### EDITA SOLO ESTAS LÍNEAS ###
MI CANAL: [nombre de tu canal]
IDIOMA: español neutro
DURACIÓN OBJETIVO: 3:30
ESTILO POR DEFECTO: latin worship ballad, acoustic guitar, male vocal, warm pads, 72 bpm
TONO: esperanzado, íntimo, nada triunfalista
### FIN DE LA EDICIÓN ###

Hoy es {fecha_larga}. {titulo_liturgico}
No busques nada en internet: el Evangelio y el comentario del día ya están aquí abajo.

===EVANGELIO DEL DÍA===
{cita_evangelio}
{texto_evangelio}

===COMENTARIO DEL DÍA===
{titulo_comentario}
{autor_comentario}
{texto_comentario}

TU TAREA
Escribe una canción ORIGINAL inspirada en ese Evangelio.

REGLAS DURAS
- NO cites ni traduzcas el texto bíblico palabra por palabra. Parafrasea con
  imágenes propias. La letra debe ser obra original mía.
- Toma el ángulo teológico DEL COMENTARIO de arriba, no un resumen genérico
  del pasaje. Ahí está lo que hace la canción distinta.
- Cantable: sílabas que caben en la respiración, sin rimas forzadas.
- Estructura: intro, verso 1, estribillo, verso 2, estribillo, puente,
  estribillo final.
- El estribillo se repite IDÉNTICO cada vez.
- Nada de lenguaje de máquina: si una línea suena a inteligencia
  artificial, reescríbela.

DEVUELVE EXACTAMENTE ESTE FORMATO, sin texto adicional:

===CITA===
(la cita bíblica, ej: Lucas 1,39-56)
===TITULO===
(título de la canción, máximo 45 caracteres)
===ESTILO===
(etiquetas EN INGLÉS separadas por comas para el modelo musical;
parte del ESTILO POR DEFECTO y ajústalo al tono del Evangelio de hoy)
===LETRA===
[verse]
...
[chorus]
...
[verse]
...
[chorus]
...
[bridge]
...
[chorus]
...
===YT_TITULO===
(título YouTube, incluye la cita y la fecha)
===YT_DESC===
(3 o 4 líneas + la cita completa + "Letra original inspirada en el
Evangelio del día." + 5 hashtags)
===MINIATURA===
(una frase de 4 a 6 palabras para la miniatura)
===UNA_LINEA_PARA_TI===
(una línea del estribillo que te sugiero reescribir con tus palabras)
"""


def limpiar(texto):
    texto = FOOTER.sub("", texto)
    return re.sub(r"\n{3,}", "\n\n", texto).strip()


def fecha_larga(iso):
    d = dt.date.fromisoformat(iso)
    return "%s %d de %s de %d" % (
        DIAS_ACC[d.weekday()], d.day, MESES[d.month - 1], d.year)


def construir(datos):
    g = datos["readings"]["gospel"]
    c = datos.get("commentary") or {}
    titulo = datos.get("liturgic_title", "").strip()
    fiesta = (datos.get("feast") or "").strip()
    if fiesta:
        titulo = (titulo + ". " + fiesta).strip(". ") + "."
    elif titulo:
        titulo += "."
    return PLANTILLA.format(
        fecha_larga=fecha_larga(datos["date"]),
        titulo_liturgico=titulo,
        cita_evangelio=g.get("title") or g.get("citation", ""),
        texto_evangelio=limpiar(g["text"]),
        titulo_comentario=c.get("title", ""),
        autor_comentario=c.get("author", ""),
        texto_comentario=limpiar(c.get("text", "")),
    )


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("json", help="file written by gospel.py")
    p.add_argument("--out", help="write here instead of stdout")
    a = p.parse_args()

    with open(a.json, encoding="utf-8") as fh:
        prompt = construir(json.load(fh))

    if a.out:
        os.makedirs(os.path.dirname(a.out) or ".", exist_ok=True)
        with open(a.out, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(prompt)
        print("%s -> %s (%d chars)" % (a.json, a.out, len(prompt)))
    else:
        print(prompt)


if __name__ == "__main__":
    main()
