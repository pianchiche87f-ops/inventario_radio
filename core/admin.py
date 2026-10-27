
from django.contrib import admin
from .models import OrdenTrabajo


@admin.register(OrdenTrabajo)
class OrdenTrabajoAdmin(admin.ModelAdmin):
    list_display = (
        "codigo_radio",
        "descripcion",
        "responsable",
        "fecha_inicio",
        "fecha_limite",
        "estado",
    )

    list_filter = (
        "estado",
        "fecha_inicio",
        "fecha_limite",
    )

    search_fields = (
        "codigo_radio",
        "descripcion",
        "responsable",
    )

    ordering = ("-fecha_inicio",)

    readonly_fields = (
        "fecha_registro",
        "fecha_terminado",
    )
