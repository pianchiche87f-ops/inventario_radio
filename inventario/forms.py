
from django import forms
from .models import Radio


class RadioForm(forms.ModelForm):
    class Meta:
        model = Radio

        fields = [
            "codigo_interno",
            "numero_serie",
            "marca",
            "modelo",
            "estado",
            "ubicacion",
            "responsable",
            "observaciones",
        ]

        widgets = {
            "codigo_interno": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Ej. RAD-001",
            }),
            "numero_serie": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Número de serie del equipo",
            }),
            "marca": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Ej. Motorola",
            }),
            "modelo": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Modelo del radio",
            }),
            "estado": forms.Select(attrs={
                "class": "form-select",
            }),
            "ubicacion": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Ej. Bodega principal",
            }),
            "responsable": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Nombre del responsable",
            }),
            "observaciones": forms.Textarea(attrs={
                "class": "form-control",
                "rows": 3,
                "placeholder": "Observaciones adicionales (opcional)",
            }),
        }


class ConstatacionForm(forms.Form):
    ubicacion = forms.CharField(
        label="Ubicación actual",
        max_length=150,
        widget=forms.TextInput(attrs={
            "class": "form-control",
            "placeholder": "Ej. BIMJAM",
        }),
    )

    responsable = forms.CharField(
        label="Responsable del equipo",
        max_length=150,
        widget=forms.TextInput(attrs={
            "class": "form-control",
            "placeholder": "Nombre del responsable",
        }),
    )

    descripcion = forms.CharField(
        label="Observaciones de la constatación",
        required=False,
        widget=forms.Textarea(attrs={
            "class": "form-control",
            "rows": 3,
            "placeholder": "Describe la condición física del radio",
        }),
    )
