from django.conf import settings
from django.db import models

from controles.models import Control


class Cliente(models.Model):
    nombre = models.CharField(max_length=200)
    rut = models.CharField(max_length=20, blank=True)
    contacto_nombre = models.CharField(max_length=200)
    contacto_email = models.EmailField()
    contacto_cargo = models.CharField(max_length=150, blank=True)
    fecha_inicio = models.DateField()
    activo = models.BooleanField(default=True)
    notas = models.TextField(blank=True)
    creado_en = models.DateTimeField(auto_now_add=True)

    # Usuario de Django con el que este cliente inicia sesión en el portal
    # (/portal/). Un usuario del portal ve solo el GAP y el Roadmap de SU
    # propio Cliente, a diferencia del staff, que ve todo desde /admin/.
    usuario = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="cliente",
    )

    def __str__(self):
        return self.nombre


class Aplicabilidad(models.Model):
    """Declaración de Aplicabilidad (SOA): no todos los 93 controles de
    ISO/IEC 27002 aplican a todo cliente (ej. los controles de ciclo de
    desarrollo seguro no corresponden si el cliente no desarrolla software
    internamente). Por defecto, si no existe un registro para un par
    cliente+control, se asume que SÍ aplica — solo hace falta crear un
    registro para marcar excepciones, justificadas.

    Esto se usa en el GAP y el Roadmap del portal de cliente para no contar
    como "brecha pendiente" un control que ni siquiera corresponde evaluar
    para ese cliente."""

    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE, related_name="aplicabilidades")
    control = models.ForeignKey(Control, on_delete=models.CASCADE, related_name="aplicabilidades")
    aplica = models.BooleanField(
        default=True,
        help_text="Desmarca si este control no corresponde para este cliente.",
    )
    justificacion = models.TextField(
        blank=True,
        help_text="Por qué aplica o no aplica (exigido por ISO/IEC 27001 en la SOA real).",
    )
    actualizado_en = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Declaración de aplicabilidad"
        verbose_name_plural = "Declaraciones de aplicabilidad"
        constraints = [
            models.UniqueConstraint(fields=["cliente", "control"], name="unico_cliente_control")
        ]

    def __str__(self):
        estado = "Aplica" if self.aplica else "No aplica"
        return f"{self.cliente} — {self.control.codigo}: {estado}"
