from django.contrib import admin

from .models import Cliente


@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = ("nombre", "contacto_nombre", "activo", "fecha_inicio")
    search_fields = ("nombre", "rut")