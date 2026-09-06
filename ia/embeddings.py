"""
Embeddings locales para el pipeline RAG.

Usa un modelo pequeño (sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2,
384 dimensiones) vía la librería `fastembed`, que corre sobre ONNX Runtime en
CPU. No requiere GPU ni llamadas a una API externa: el texto de los clientes
(evidencia, controles) nunca sale de la máquina/contenedor donde corre
Django. Solo el paso final de clasificación (ia/utils.py) llama a la API
de Anthropic, y solo con los fragmentos ya seleccionados por este módulo.

A diferencia de los modelos de la familia E5, este modelo es simétrico
(no distingue entre "consulta" y "documento"), así que no hace falta
prefijar el texto según su rol.

El modelo (~470 MB) se descarga la primera vez que se usa. Para no volver a
descargarlo en cada redeploy de Railway, se cachea dentro de MEDIA_ROOT
(el mismo volumen persistente `volume1` ya montado para los archivos de
Evidencia) en vez de la ubicación por defecto de fastembed, que vive en el
filesystem efímero del contenedor.
"""

from functools import lru_cache
from pathlib import Path

from django.conf import settings

MODEL_NAME = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
CACHE_DIR = Path(settings.MEDIA_ROOT) / ".embeddings_cache"


@lru_cache(maxsize=1)
def _get_model():
    from fastembed import TextEmbedding

    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    return TextEmbedding(model_name=MODEL_NAME, cache_dir=str(CACHE_DIR))


def embed_query(texto: str) -> list[float]:
    """Embedding de un texto de consulta (ej. codigo+nombre+descripcion de un Control)."""
    modelo = _get_model()
    vector = next(modelo.embed([texto]))
    return vector.tolist()


def embed_passages(textos: list[str]) -> list[list[float]]:
    """Embeddings de una lista de textos candidatos (ej. fragmentos de una evidencia)."""
    if not textos:
        return []
    modelo = _get_model()
    return [vector.tolist() for vector in modelo.embed(textos)]
