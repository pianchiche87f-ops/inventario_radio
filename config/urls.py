
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
        "inventario/exportar/excel/",
        views.exportar_inventario_excel,
        name="exportar_inventario_excel",
    ),

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
        "trazabilidad/exportar/excel/",
        views.exportar_trazabilidad_excel,
        name="exportar_trazabilidad_excel",
    ),

    path(
        "trazabilidad/exportar/csv/",
        views.exportar_trazabilidad_csv,
        name="exportar_trazabilidad_csv",
    ),

    path(
        "constataciones/",
        views.lista_constataciones,
        name="lista_constataciones",
    ),
    
    path(
        "constataciones/registrar/",
        views.ingresar_constatacion,
        name="ingresar_constatacion",
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

    path("mantenimiento/", views.mantenimiento, name="mantenimiento"),

    path(
        "salidas-terceros/registrar/",
        views.registrar_salida_terceros,
        name="registrar_salida_terceros",
    ),

    path(
        "salidas-terceros/",
        views.lista_salidas_terceros,
        name="lista_salidas_terceros",
    ),

    path(
        "salidas-terceros/<int:salida_id>/devolver/",
        views.devolver_salida_terceros,
        name="devolver_salida_terceros",
    ),

    path(
        "mantenimiento/<int:mantenimiento_id>/finalizar/",
        views.finalizar_mantenimiento,
        name="finalizar_mantenimiento",
    ),

    path(
        "mantenimiento/anular/<int:mantenimiento_id>/",
        views.anular_mantenimiento,
        name="anular_mantenimiento",
    ),


    path(
        "ordenes-trabajo/",
        views.lista_ordenes,
        name="lista_ordenes",
    ),

    path(
    "ordenes-trabajo/seleccionar-equipo/",
    views.seleccionar_radio_orden,
    name="seleccionar_radio_orden",
),


]


if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT,
    )
