
from django import forms
from django.utils import timezone

from .models import OrdenTrabajo, Mantenimiento
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



class MantenimientoForm(forms.ModelForm):

    radio = forms.ModelChoiceField(
        queryset=Radio.objects.all().order_by("codigo_interno"),
        label="Equipo",
        empty_label="Selecciona un equipo",
    )

    fecha_prevista = forms.DateField(
        label="Fecha prevista",
        input_formats=["%Y-%m-%d"],
        widget=forms.DateInput(
            format="%Y-%m-%d",
            attrs={"type": "date"},
        ),
    )

    class Meta:
        model = Mantenimiento
        fields = [
            "radio",
            "tipo_intervencion",
            "descripcion",
            "fecha_prevista",
        ]

        widgets = {
            "descripcion": forms.Textarea(
                attrs={
                    "rows": 4,
                    "placeholder": "Describe el mantenimiento que se realizará...",
                },
            ),
            "tipo_intervencion": forms.Select(
                attrs={"class": "form-select"},
            ),
        }

    def clean_radio(self):
        radio = self.cleaned_data["radio"]

        mantenimiento_activo = Mantenimiento.objects.filter(
            radio=radio,
            anulado=False,
            estado__in=[
                Mantenimiento.PENDIENTE,
                Mantenimiento.EN_PROCESO,
            ],
        ).exists()

        if mantenimiento_activo:
            raise forms.ValidationError(
                "Este equipo ya tiene un mantenimiento pendiente o en proceso. "
                "Debes finalizarlo o anularlo antes de registrar otro."
            )

        return radio

    def clean_fecha_prevista(self):
        fecha = self.cleaned_data["fecha_prevista"]

        if fecha < timezone.localdate():
            raise forms.ValidationError(
                "La fecha prevista no puede ser anterior al día de hoy."
            )

        return fecha
