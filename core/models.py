
from django.db import models
from inventario.models import Radio
from django.conf import settings


class OrdenTrabajo(models.Model):

    ESTADO_INICIADA = "INICIADA"
    ESTADO_CERRADA = "CERRADA"

    ESTADOS = [
        (ESTADO_INICIADA, "Iniciada"),
        (ESTADO_CERRADA, "Cerrada"),
    ]

    codigo_radio = models.CharField(
        max_length=50,
        verbose_name="Código interno del radio",
        db_index=True,
    )
    radio = models.ForeignKey(
        Radio,
        on_delete=models.PROTECT,
        related_name="ordenes_trabajo",
        null=True,
        blank=True,
        verbose_name="Radio relacionado",
    )

    descripcion = models.TextField(
        verbose_name="Descripción del trabajo",
    )

    responsable = models.CharField(
        max_length=150,
        verbose_name="Responsable",
    )

    fecha_inicio = models.DateTimeField(
        verbose_name="Fecha y hora de inicio",
    )

    fecha_limite = models.DateTimeField(
        verbose_name="Fecha y hora límite",
    )

    fecha_terminado = models.DateTimeField(
        verbose_name="Fecha y hora de terminación",
        null=True,
        blank=True,
    )

    estado = models.CharField(
        max_length=10,
        choices=ESTADOS,
        default=ESTADO_INICIADA,
        db_index=True,
    )

    fecha_registro = models.DateTimeField(
        auto_now_add=True,
    )

    class Meta:
        ordering = ["-fecha_inicio"]
        verbose_name = "Orden de trabajo"
        verbose_name_plural = "Órdenes de trabajo"

    @property
    def vencida(self):
        from django.utils import timezone

        return (
            self.estado == self.ESTADO_INICIADA
            and timezone.now() > self.fecha_limite
        )

    def __str__(self):
        return f"{self.codigo_radio} - {self.get_estado_display()}"

    

class Mantenimiento(models.Model):

    # Tipos de intervención
    PREVENTIVO = "PREVENTIVO"
    CORRECTIVO = "CORRECTIVO"

    TIPOS_INTERVENCION = [
        (PREVENTIVO, "Mantenimiento preventivo"),
        (CORRECTIVO, "Mantenimiento correctivo"),
    ]

    # Estados del mantenimiento
    PENDIENTE = "PENDIENTE"
    EN_PROCESO = "EN_PROCESO"
    FINALIZADO = "FINALIZADO"

    ESTADOS = [
        (PENDIENTE, "Pendiente"),
        (EN_PROCESO, "En proceso"),
        (FINALIZADO, "Finalizado"),
    ]

    # Equipo relacionado con el inventario
    radio = models.ForeignKey(
        Radio,
        on_delete=models.PROTECT,
        related_name="mantenimientos",
        verbose_name="Equipo"
    )

    # Información del mantenimiento
    tipo_intervencion = models.CharField(
        max_length=20,
        choices=TIPOS_INTERVENCION,
        verbose_name="Tipo de intervención"
    )

    descripcion = models.TextField(
        verbose_name="Descripción del mantenimiento"
    )

    fecha_registro = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Fecha de registro"
    )

    fecha_prevista = models.DateField(
        verbose_name="Fecha prevista"
    )

    # Estado del mantenimiento
    estado = models.CharField(
        max_length=15,
        choices=ESTADOS,
        default=EN_PROCESO,
        verbose_name="Estado"
    )

    # Estado que tenía el radio antes del mantenimiento
    estado_radio_anterior = models.CharField(
        max_length=20,
        choices=Radio.Estado.choices,
        blank=True,
        verbose_name="Estado anterior del equipo"
    )

    # Control de anulación
    anulado = models.BooleanField(
        default=False,
        verbose_name="Anulado"
    )

    motivo_anulacion = models.TextField(
        blank=True,
        verbose_name="Motivo de anulación"
    )

    fecha_anulacion = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Fecha de anulación"
    )

    anulado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="mantenimientos_anulados",
        verbose_name="Anulado por"
    )

    # Control de finalización
    fecha_finalizacion = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Fecha y hora de finalización"
    )

    trabajo_realizado = models.TextField(
        blank=True,
        verbose_name="Trabajo realizado"
    )

    finalizado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="mantenimientos_finalizados",
        verbose_name="Finalizado por"
    )

    resultado = models.CharField(
        max_length=20,
        default="OPERATIVO",
        choices=[
            ("OPERATIVO", "Equipo operativo"),
        ],
        verbose_name="Resultado del mantenimiento"
    )

    # Comprobar si el mantenimiento está vencido
    @property
    def vencido(self):
        from django.utils import timezone

        return (
            self.estado != self.FINALIZADO
            and not self.anulado
            and timezone.localdate() > self.fecha_prevista
        )

    class Meta:
        ordering = ["fecha_prevista", "-fecha_registro"]
        verbose_name = "Mantenimiento"
        verbose_name_plural = "Mantenimientos"

    def __str__(self):
        return (
            f"{self.radio.codigo_interno} - "
            f"{self.get_tipo_intervencion_display()}"
        )
