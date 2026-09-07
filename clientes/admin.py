from django.contrib import admin

from .models import Aplicabilidad, Cliente


@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = ("nombre", "contacto_nombre", "activo", "fecha_inicio", "usuario")
    search_fields = ("nombre", "rut")
    autocomplete_fields = ["usuario"]


@admin.register(Aplicabilidad)
class AplicabilidadAdmin(admin.ModelAdmin):
    list_display = ("cliente", "control", "aplica", "actualizado_en")
    list_filter = ("cliente", "aplica", "control__tema")
    search_fields = ("control__codigo", "control__nombre", "cliente__nombre")
    autocomplete_fields = ["cliente", "control"]
