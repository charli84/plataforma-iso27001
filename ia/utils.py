from pypdf import PdfReader


def extraer_texto(evidencia_archivo, limite=6000):
    """Extrae texto legible de un archivo de Evidencia (.txt, .md o .pdf)."""
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


def clasificar_evidencia_ia(evidencia):
    """Clasifica una Evidencia con Claude y crea/actualiza su Evaluacion.
    Devuelve la instancia de Evaluacion. Lanza excepción si algo falla
    (el llamador decide cómo mostrar el error)."""
    import anthropic
    from ia.models import Evaluacion

    MODEL = "claude-haiku-4-5-20251001"
    control = evidencia.control
    texto = extraer_texto(evidencia.archivo)

    prompt = f"""Eres un auditor experto en ISO/IEC 27001 e ISO/IEC 27002:2022.

Analiza si el siguiente documento de evidencia cumple con el control:

Código de control: {control.codigo}
Nombre del control: {control.nombre}
Descripción del control: {control.descripcion}

Contenido del documento de evidencia:
\"\"\"
{texto}
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