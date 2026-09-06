from django.db import models
from pgvector.django import VectorField

# Dimensión del modelo de embeddings local usado en ia/embeddings.py
# (sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2). Si ese
# modelo cambia, hay que actualizar este número y regenerar los embeddings
# existentes.
EMBEDDING_DIM = 384


class Control(models.Model):
    class Tema(models.TextChoices):
        ORGANIZACIONAL = "ORG", "Organizacional"
        PERSONAS = "PER", "Personas"
        FISICO = "FIS", "Físico"
        TECNOLOGICO = "TEC", "Tecnológico"

    codigo = models.CharField(max_length=10, unique=True)  # ej. A.5.1
    nombre = models.CharField(max_length=255)
    descripcion = models.TextField()
    tema = models.CharField(max_length=3, choices=Tema.choices)
    norma_referencia = models.CharField(max_length=50, default="ISO/IEC 27002:2022")

    # Embedding semántico de "codigo + nombre + descripcion", precalculado
    # con el comando `generar_embeddings_controles`. Se usa como referencia
    # para el RAG: al evaluar una evidencia, se buscan los fragmentos del
    # documento más parecidos semánticamente a este vector.
    embedding = VectorField(dimensions=EMBEDDING_DIM, null=True, blank=True, editable=False)

    # Cada cuántos meses debería revisarse el cumplimiento de este control,
    # para los controles cuya naturaleza es de revisión recurrente (ej.
    # políticas, revisión independiente, gestión de vulnerabilidades). None
    # = este control no tiene un ciclo de revisión periódica definido (se
    # evalúa una vez con su evidencia y no vence). Los valores por defecto
    # se cargan en `cargar_controles_iso` como un criterio propio de partida;
    # cada organización debería poder ajustarlos según su propio programa
    # de revisiones.
    periodicidad_revision_meses = models.PositiveIntegerField(null=True, blank=True)

    class Meta:
        ordering = ["codigo"]

    def __str__(self):
        return f"{self.codigo} — {self.nombre}"
