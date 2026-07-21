from django.contrib import admin

from .models import Control


@admin.register(Control)
class ControlAdmin(admin.ModelAdmin):
    list_display = ("codigo", "nombre", "tema")
    list_filter = ("tema",)
    search_fields = ("codigo", "nombre")
