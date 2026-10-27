
from django.contrib import admin
from .models import Radio, MovimientoKardex


@admin.register(Radio)
class RadioAdmin(admin.ModelAdmin):
    list_display = (
        "codigo_interno",
        "numero_serie",
        "marca",
        "modelo",
        "estado",
        "ubicacion",
        "responsable",
        "fecha_registro",
    )

    list_filter = (
        "estado",
        "marca",
        "fecha_registro",
    )

    search_fields = (
        "codigo_interno",
        "numero_serie",
        "marca",
        "modelo",
        "responsable",
    )

    readonly_fields = (
        "identificador_qr",
        "fecha_registro",
    )

    ordering = ("codigo_interno",)


@admin.register(MovimientoKardex)
class MovimientoKardexAdmin(admin.ModelAdmin):
    list_display = (
        "radio",
        "tipo",
        "fecha",
        "responsable",
        "registrado_por",
    )

    list_filter = (
        "tipo",
        "fecha",
    )

    search_fields = (
        "radio__codigo_interno",
        "radio__numero_serie",
        "descripcion",
        "responsable",
    )

    readonly_fields = ("fecha",)

    ordering = ("-fecha",)
