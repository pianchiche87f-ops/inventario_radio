
from django.db import models
from inventario.models import Radio


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
