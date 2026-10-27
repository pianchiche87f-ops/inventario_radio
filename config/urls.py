
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static

from core import views


urlpatterns = [
    path("admin/", admin.site.urls),

    path(
        "cuentas/iniciar-sesion/",
        auth_views.LoginView.as_view(
            template_name="registration/login.html"
        ),
        name="login",
    ),

    path(
        "cuentas/cerrar-sesion/",
        auth_views.LogoutView.as_view(next_page="login"),
        name="logout",
    ),

    path("", views.dashboard, name="dashboard"),

    path(
        "inventario/",
        views.lista_radios,
        name="lista_radios",
    ),

    path(
        "inventario/registrar/",
        views.registrar_radio,
        name="registrar_radio",
    ),

   
    path(
        "inventario/radio/<uuid:identificador_qr>/",
        views.detalle_radio,
        name="detalle_radio",
    ),

    path(
        "inventario/radio/<uuid:identificador_qr>/constatacion/",
        views.registrar_constatacion,
        name="registrar_constatacion",
    ),

    path(
        "inventario/generador-qr/",
        views.generador_qr,
        name="generador_qr",
    ),
    path(
        "trazabilidad/",
        views.trazabilidad,
        name="trazabilidad",
    ),

        
    path(
        "trazabilidad/radio/<uuid:identificador_qr>/orden/iniciar/",
        views.iniciar_orden,
        name="iniciar_orden",
    ),

    path(
        "trazabilidad/orden/<int:orden_id>/cerrar/",
        views.cerrar_orden,
        name="cerrar_orden",
    ),

]


if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT,
    )
