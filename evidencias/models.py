from django.db import models

from clientes.models import Cliente
from controles.models import Control


def ruta_evidencia(instance, filename):
    return f"evidencias/{instance.cliente_id}/{instance.control.codigo}/{filename}"


class Evidencia(models.Model):
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE, related_name="evidencias")
    control = models.ForeignKey(Control, on_delete=models.PROTECT, related_name="evidencias")
    archivo = models.FileField(upload_to=ruta_evidencia)
    descripcion = models.TextField(blank=True)
    subido_en = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.cliente} - {self.control.codigo}"