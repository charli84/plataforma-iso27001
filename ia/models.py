from django.db import models

from evidencias.models import Evidencia


class Evaluacion(models.Model):
    class Cumplimiento(models.TextChoices):
        CUMPLE = "CUMPLE", "Cumple"
        PARCIAL = "PARCIAL", "Cumple parcialmente"
        NO_CUMPLE = "NO_CUMPLE", "No cumple"
        PENDIENTE = "PENDIENTE", "Pendiente de revisión"

    evidencia = models.OneToOneField(Evidencia, on_delete=models.CASCADE, related_name="evaluacion")
    cumplimiento = models.CharField(max_length=10, choices=Cumplimiento.choices, default=Cumplimiento.PENDIENTE)
    calificacion = models.DecimalField(max_digits=4, decimal_places=1, null=True, blank=True)  # 0.0 a 10.0
    recomendaciones = models.TextField(blank=True)
    modelo_ia = models.CharField(max_length=50, blank=True)  # ej. "claude-sonnet-4-6"
    evaluado_en = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Evaluación {self.evidencia} — {self.cumplimiento}"
