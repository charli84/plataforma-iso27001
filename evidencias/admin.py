from django.contrib import admin

from .models import Evidencia


@admin.register(Evidencia)
class EvidenciaAdmin(admin.ModelAdmin):
    list_display = ("cliente", "control", "subido_en")
    list_filter = ("cliente", "control__tema")