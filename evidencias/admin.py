from django.contrib import admin, messages

from .models import Evidencia
from ia.utils import clasificar_evidencia_ia


@admin.register(Evidencia)
class EvidenciaAdmin(admin.ModelAdmin):
    list_display = ("cliente", "control", "subido_en")
    list_filter = ("cliente", "control__tema")
    actions = ["analizar_con_ia"]

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        try:
            evaluacion = clasificar_evidencia_ia(obj)
            self.message_user(
                request,
                f"IA: evidencia clasificada como {evaluacion.cumplimiento} "
                f"(calificación {evaluacion.calificacion}).",
            )
        except Exception as e:
            self.message_user(
                request,
                f"La evidencia se guardó, pero la clasificación con IA falló: {e}",
                level=messages.ERROR,
            )

    @admin.action(description="Analizar con IA")
    def analizar_con_ia(self, request, queryset):
        ok, fallidas = 0, 0
        for evidencia in queryset:
            try:
                clasificar_evidencia_ia(evidencia)
                ok += 1
            except Exception as e:
                fallidas += 1
                self.message_user(request, f"Error en {evidencia}: {e}", level=messages.ERROR)
        if ok:
            self.message_user(request, f"{ok} evidencia(s) clasificada(s) correctamente.")
        if fallidas:
            self.message_user(request, f"{fallidas} evidencia(s) fallaron.", level=messages.WARNING)