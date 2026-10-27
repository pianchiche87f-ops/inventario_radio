
import qrcode
from io import BytesIO
from django.core.files.base import ContentFile
from django.urls import reverse


def generar_qr_radio(radio, request):
    """
    Genera una imagen QR que apunta a la página
    de detalles del radio.
    """
    ruta = reverse(
        "detalle_radio",
        kwargs={"identificador_qr": radio.identificador_qr},
    )

    url = request.build_absolute_uri(ruta)

    imagen = qrcode.make(url)

    buffer = BytesIO()
    imagen.save(buffer, format="PNG")

    return ContentFile(
        buffer.getvalue(),
        name=f"QR_{radio.codigo_interno}.png",
    )
