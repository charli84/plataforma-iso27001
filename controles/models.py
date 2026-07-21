from django.db import models


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

    class Meta:
        ordering = ["codigo"]

    def __str__(self):
        return f"{self.codigo} — {self.nombre}"
