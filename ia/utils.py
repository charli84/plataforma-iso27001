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
