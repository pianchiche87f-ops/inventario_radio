
from django import forms
from django.utils import timezone

from .models import OrdenTrabajo
from inventario.models import Radio


class OrdenTrabajoForm(forms.ModelForm):
    radio = forms.ModelChoiceField(
        queryset=Radio.objects.all().order_by("codigo_interno"),
        label="Radio",
        empty_label="Selecciona un radio",
    )

    fecha_inicio = forms.DateTimeField(
        label="Fecha y hora de inicio",
        input_formats=["%Y-%m-%dT%H:%M"],
        widget=forms.DateTimeInput(
            format="%Y-%m-%dT%H:%M",
            attrs={"type": "datetime-local"},
        ),
    )

    fecha_limite = forms.DateTimeField(
        label="Fecha y hora límite",
        input_formats=["%Y-%m-%dT%H:%M"],
        widget=forms.DateTimeInput(
            format="%Y-%m-%dT%H:%M",
            attrs={"type": "datetime-local"},
        ),
    )

    class Meta:
        model = OrdenTrabajo
        fields = [
            "radio",
            "descripcion",
            "responsable",
            "fecha_inicio",
            "fecha_limite",
        ]

        widgets = {
            "descripcion": forms.Textarea(
                attrs={"rows": 3},
            ),
            "responsable": forms.TextInput(
                attrs={"placeholder": "Nombre del responsable"},
            ),
        }

    def clean(self):
        datos = super().clean()
        inicio = datos.get("fecha_inicio")
        limite = datos.get("fecha_limite")

        if inicio and limite and limite <= inicio:
            self.add_error(
                "fecha_limite",
                "La fecha límite debe ser posterior al inicio.",
            )

        return datos
