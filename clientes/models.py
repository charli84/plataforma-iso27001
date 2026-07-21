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

    def __str__(self):
        return self.nombre
