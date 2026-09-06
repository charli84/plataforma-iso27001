import math

from pypdf import PdfReader


def extraer_texto(evidencia_archivo, limite=40000):
    """Extrae texto legible de un archivo de Evidencia (.txt, .md o .pdf).

    El límite se subió de 6000 a 40000 caracteres respecto de la versión
    anterior: ahora que el texto se recorta por relevancia semántica (ver
    `_fragmentos_relevantes` más abajo) en vez de recortarse a ciegas por
    posición, tiene sentido extraer más texto fuente antes de seleccionar
    qué parte enviarle al modelo.
    """
    nombre = evidencia_archivo.name.lower()

    if nombre.endswith(".pdf"):
        with evidencia_archivo.open("rb") as f:
            reader = PdfReader(f)
            texto = "\n".join(page.extract_text() or "" for page in reader.pages)
        if not texto.strip():
            return (
                "(El PDF no tiene texto extraible; probablemente es un documento "
                "escaneado. Requiere OCR, aun no implementado en esta version.)"
            )
        return texto[:limite]

    with evidencia_archivo.open("r") as f:
        return f.read()[:limite]


def chunk_texto(texto: str, tam: int = 700, solape: int = 100) -> list[str]:
    """Divide un texto largo en fragmentos de ~`tam` caracteres, con `solape`
    caracteres de traslape entre fragmentos consecutivos para no cortar ideas
    justo por la mitad. Si el texto ya es corto, lo devuelve como un único
    fragmento."""
    texto = (texto or "").strip()
    if not texto:
        return []
    if len(texto) <= tam:
        return [texto]

    fragmentos = []
    inicio = 0
    while inicio < len(texto):
        fin = min(inicio + tam, len(texto))
        fragmentos.append(texto[inicio:fin])
        if fin == len(texto):
            break
        inicio = fin - solape
    return fragmentos


def _similitud_coseno(a: list[float], b: list[float]) -> float:
    producto = sum(x * y for x, y in zip(a, b))
    norma_a = math.sqrt(sum(x * x for x in a))
    norma_b = math.sqrt(sum(y * y for y in b))
    if norma_a == 0 or norma_b == 0:
        return 0.0
    return producto / (norma_a * norma_b)


def _fragmentos_relevantes(texto: str, control, k: int = 5) -> tuple[str, bool]:
    """Selecciona, mediante búsqueda semántica (RAG), los `k` fragmentos del
    texto de evidencia más relevantes para el control que se está evaluando.

    Devuelve (texto_seleccionado, uso_rag). Si algo fallara (modelo de
    embeddings no disponible, control sin embedding precalculado, texto muy
    corto, etc.) cae de vuelta al comportamiento anterior: los primeros 6000
    caracteres del texto, sin usar RAG.
    """
    fragmentos = chunk_texto(texto)

    if len(fragmentos) <= 1:
        return texto[:6000], False

    if control.embedding is None:
        # El control todavía no tiene embedding precalculado
        # (falta correr `python manage.py generar_embeddings_controles`).
        return texto[:6000], False

    try:
        from ia.embeddings import embed_passages

        embeddings_fragmentos = embed_passages(fragmentos)
        control_embedding = list(control.embedding)

        puntajes = [
            (_similitud_coseno(control_embedding, emb), i)
            for i, emb in enumerate(embeddings_fragmentos)
        ]
        puntajes.sort(reverse=True)
        indices_top = sorted(i for _, i in puntajes[:k])
        seleccion = "\n\n[...]\n\n".join(fragmentos[i] for i in indices_top)
        return seleccion, True
    except Exception:
        # No dejamos que una falla del modelo de embeddings local
        # (ej. primera descarga del modelo, memoria, etc.) bloquee la
        # clasificación: seguimos con el recorte simple anterior.
        return texto[:6000], False


def clasificar_evidencia_ia(evidencia):
    """Clasifica una Evidencia con Claude y crea/actualiza su Evaluacion.
    Devuelve la instancia de Evaluacion. Lanza excepción si algo falla
    (el llamador decide cómo mostrar el error).

    Desde esta versión, el texto de evidencia que se envía al modelo ya no
    es un recorte ciego de los primeros caracteres del documento: se parte
    en fragmentos, se generan embeddings locales de cada uno (sin llamar a
    ninguna API externa) y se seleccionan los fragmentos semánticamente más
    parecidos al control evaluado (RAG real, con pgvector como almacén de
    los embeddings de los controles)."""
    import anthropic
    from ia.models import Evaluacion

    MODEL = "claude-haiku-4-5-20251001"
    control = evidencia.control
    texto_completo = extraer_texto(evidencia.archivo)

    contexto_evidencia, uso_rag = _fragmentos_relevantes(texto_completo, control)

    nota_rag = (
        "\nNota: el documento es extenso; a continuación se muestran solo los "
        "fragmentos más relevantes para este control específico, seleccionados "
        "mediante búsqueda semántica (RAG) sobre el documento completo.\n"
        if uso_rag
        else ""
    )

    prompt = f"""Eres un auditor experto en ISO/IEC 27001 e ISO/IEC 27002:2022.

Analiza si el siguiente documento de evidencia cumple con el control:

Código de control: {control.codigo}
Nombre del control: {control.nombre}
Descripción del control: {control.descripcion}
{nota_rag}
Contenido del documento de evidencia:
\"\"\"
{contexto_evidencia}
\"\"\"

Responde EXACTAMENTE en este formato, sin texto adicional:
CUMPLIMIENTO: [CUMPLE|PARCIAL|NO_CUMPLE|PENDIENTE]
CALIFICACION: [número del 1 al 10]
RECOMENDACIONES: [texto breve con recomendaciones concretas]
"""

    client = anthropic.Anthropic()
    respuesta = client.messages.create(
        model=MODEL,
        max_tokens=1000,
        messages=[{"role": "user", "content": prompt}],
    )
    texto_respuesta = respuesta.content[0].text

    cumplimiento = "PENDIENTE"
    calificacion = None
    recomendaciones = ""

    for linea in texto_respuesta.splitlines():
        linea = linea.strip()
        if linea.startswith("CUMPLIMIENTO:"):
            cumplimiento = linea.replace("CUMPLIMIENTO:", "").strip()
        elif linea.startswith("CALIFICACION:"):
            valor = linea.replace("CALIFICACION:", "").strip()
            try:
                calificacion = int(valor)
            except ValueError:
                calificacion = None
        elif linea.startswith("RECOMENDACIONES:"):
            recomendaciones = linea.replace("RECOMENDACIONES:", "").strip()

    evaluacion, _ = Evaluacion.objects.update_or_create(
        evidencia=evidencia,
        defaults={
            "cumplimiento": cumplimiento,
            "calificacion": calificacion,
            "recomendaciones": recomendaciones,
            "modelo_ia": MODEL,
        },
    )
    return evaluacion
