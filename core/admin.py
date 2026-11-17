
from django.contrib import admin
from .models import OrdenTrabajo, Mantenimiento


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


@admin.register(Mantenimiento)
class MantenimientoAdmin(admin.ModelAdmin):

    list_display = (
        "radio",
        "tipo_intervencion",
        "fecha_registro",
        "fecha_prevista",
        "estado",
        "anulado",
        "finalizado_por",
    )

    list_filter = (
        "tipo_intervencion",
        "estado",
        "anulado",
        "fecha_prevista",
    )

    search_fields = (
        "radio__codigo_interno",
        "descripcion",
        "trabajo_realizado",
        "motivo_anulacion",
    )

    ordering = ("-fecha_registro",)

    readonly_fields = (
        "fecha_registro",
        "fecha_finalizacion",
        "fecha_anulacion",
        "finalizado_por",
        "anulado_por",
    )
