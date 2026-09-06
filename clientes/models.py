from django.conf import settings
from django.db import models


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
