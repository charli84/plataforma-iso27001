from django.contrib import admin

from .models import Evaluacion


@admin.register(Evaluacion)
class EvaluacionAdmin(admin.ModelAdmin):
    list_display = ("evidencia", "cumplimiento", "calificacion", "modelo_ia", "evaluado_en")
    list_filter = ("cumplimiento",)
