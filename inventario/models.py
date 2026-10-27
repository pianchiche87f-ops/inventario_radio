
import uuid

from django.conf import settings
from django.db import models


class Radio(models.Model):
    class Estado(models.TextChoices):
        DISPONIBLE = "disponible", "Disponible"
        ASIGNADO = "asignado", "Asignado"
        MANTENIMIENTO = "mantenimiento", "En mantenimiento"
        EN_TERCEROS = "en_terceros", "En terceros"
        BAJA = "baja", "Dado de baja"

    codigo_interno = models.CharField(
        max_length=20,
        unique=True,
        verbose_name="Código interno",
    )

    numero_serie = models.CharField(
        max_length=100,
        unique=True,
        verbose_name="Número de serie",
    )

    marca = models.CharField(
        max_length=100,
        verbose_name="Marca",
    )

    modelo = models.CharField(
        max_length=100,
        verbose_name="Modelo",
    )

    estado = models.CharField(
        max_length=20,
        choices=Estado.choices,
        default=Estado.DISPONIBLE,
        verbose_name="Estado",
    )

    ubicacion = models.CharField(
        max_length=150,
        blank=True,
        verbose_name="Ubicación",
    )

    responsable = models.CharField(
        max_length=150,
        blank=True,
        verbose_name="Responsable asignado",
    )

    
    fecha_devolucion_prevista = models.DateField(
        null=True,
        blank=True,
        verbose_name="Fecha prevista de devolución",
        help_text="Fecha límite para devolver el radio cuando está en terceros.",
    )
    
    identificador_qr = models.UUIDField(
    default=uuid.uuid4,
    unique=True,
    editable=False,
    verbose_name="Identificador QR",
    )

    imagen_qr = models.ImageField(
    upload_to="codigos_qr/",
    blank=True,
    null=True,
    verbose_name="Imagen del código QR",
    )

    fecha_registro = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Fecha de registro",
    )

    observaciones = models.TextField(
        blank=True,
        verbose_name="Observaciones",
    )

    class Meta:
        verbose_name = "Radio"
        verbose_name_plural = "Radios"
        ordering = ["codigo_interno"]

    def __str__(self):
        return f"{self.codigo_interno} - {self.marca} {self.modelo}"


class MovimientoKardex(models.Model):
    class Tipo(models.TextChoices):
        REGISTRO = "registro", "Registro inicial"
        ASIGNACION = "asignacion", "Asignación"
        DEVOLUCION = "devolucion", "Devolución"
        TRASLADO = "traslado", "Cambio de ubicación"
        MANTENIMIENTO = "mantenimiento", "Mantenimiento"
        REPARACION = "reparacion", "Reparación"
        CONSTATACION = "constatacion", "Constatación física"
        ORDEN_INICIADA = "orden_iniciada", "Orden iniciada"
        ORDEN_CERRADA = "orden_cerrada", "Orden cerrada"
        BAJA = "baja", "Baja del equipo"

    radio = models.ForeignKey(
        Radio,
        on_delete=models.PROTECT,
        related_name="movimientos_kardex",
        verbose_name="Radio",
    )

    tipo = models.CharField(
        max_length=20,
        choices=Tipo.choices,
        verbose_name="Tipo de movimiento",
    )

    descripcion = models.TextField(
        verbose_name="Descripción de la actividad",
    )

    ubicacion = models.CharField(
        max_length=150,
        blank=True,
        verbose_name="Ubicación",
    )

    responsable = models.CharField(
        max_length=150,
        blank=True,
        verbose_name="Responsable",
    )

    fecha = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Fecha del movimiento",
    )

    registrado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Registrado por",
    )

    class Meta:
        verbose_name = "Movimiento de Kardex"
        verbose_name_plural = "Movimientos de Kardex"
        ordering = ["-fecha"]

    def __str__(self):
        return (
            f"{self.radio.codigo_interno} - "
            f"{self.get_tipo_display()} - "
            f"{self.fecha:%d/%m/%Y %H:%M}"
        )
