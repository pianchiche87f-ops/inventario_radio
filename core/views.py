
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.shortcuts import render, redirect, get_object_or_404
from inventario.forms import RadioForm, ConstatacionForm
from inventario.models import Radio, MovimientoKardex
from .forms import OrdenTrabajoForm
from .models import OrdenTrabajo
from inventario.qr import generar_qr_radio
from django.utils import timezone
from django.db.models import Q

@login_required(login_url="login")
def dashboard(request):
    total_radios = Radio.objects.count()

    radios_disponibles = Radio.objects.filter(
        estado=Radio.Estado.DISPONIBLE
    ).count()

    radios_asignados = Radio.objects.filter(
        estado=Radio.Estado.ASIGNADO
    ).count()

    radios_mantenimiento = Radio.objects.filter(
        estado=Radio.Estado.MANTENIMIENTO
    ).count()

    radios_en_terceros = Radio.objects.filter(
        estado=Radio.Estado.EN_TERCEROS
    ).count()

    radios_dados_de_baja = Radio.objects.filter(
        estado=Radio.Estado.BAJA
    ).count()

    # Datos para el gráfico circular del inventario.
    estado_inventario = [
        {
            "nombre": "Operativos",
            "cantidad": radios_disponibles,
            "color": "#18a999",
        },
        {
            "nombre": "Asignados",
            "cantidad": radios_asignados,
            "color": "#f0ad4e",
        },
        {
            "nombre": "En mantenimiento",
            "cantidad": radios_mantenimiento,
            "color": "#e76f6f",
        },
        {
            "nombre": "En terceros",
            "cantidad": radios_en_terceros,
            "color": "#6f42c1",
        },
        {
            "nombre": "Baja",
            "cantidad": radios_dados_de_baja,
            "color": "#98a6b8",
        },
    ]

    # Últimos movimientos registrados.
    ultimos_movimientos = (
        MovimientoKardex.objects
        .select_related("radio", "registrado_por")
        .order_by("-fecha")[:5]
    )

    # Últimas constataciones físicas registradas.
    ultimas_constataciones = (
    MovimientoKardex.objects
    .filter(tipo=MovimientoKardex.Tipo.CONSTATACION)
    .select_related("radio", "registrado_por")
    .order_by("-fecha")[:5]
)

    # Equipos que están bajo custodia de terceros.
    equipos_en_terceros = Radio.objects.filter(
        estado=Radio.Estado.EN_TERCEROS
    ).order_by("codigo_interno")

    # Radios en terceros cuya fecha prevista de devolución ya venció.
    equipos_retorno_vencido = Radio.objects.filter(
        estado=Radio.Estado.EN_TERCEROS,
        fecha_devolucion_prevista__lt=timezone.localdate(),
    ).order_by("fecha_devolucion_prevista")

    # Equipos actualmente en mantenimiento.
    equipos_mantenimiento = Radio.objects.filter(
        estado=Radio.Estado.MANTENIMIENTO
    ).order_by("codigo_interno")

    contexto = {
        "total_radios": total_radios,
        "radios_disponibles": radios_disponibles,
        "radios_asignados": radios_asignados,
        "radios_mantenimiento": radios_mantenimiento,
        "radios_en_terceros": radios_en_terceros,
        "radios_dados_de_baja": radios_dados_de_baja,
        "estado_inventario": estado_inventario,
        "ultimos_movimientos": ultimos_movimientos,
        "equipos_en_terceros": equipos_en_terceros,
        "equipos_mantenimiento": equipos_mantenimiento,
        "ultimas_constataciones": ultimas_constataciones,
        "equipos_retorno_vencido": equipos_retorno_vencido,
    }

    return render(request, "core/dashboard.html", contexto)

@login_required(login_url="login")
def lista_radios(request):
    radios = Radio.objects.all().order_by("codigo_interno")

    buscar = request.GET.get("buscar", "").strip()

    if buscar:
        radios = radios.filter(
            Q(codigo_interno__icontains=buscar)
            | Q(marca__icontains=buscar)
            | Q(numero_serie__icontains=buscar)
        )

    return render(
        request,
        "core/lista_radios.html",
        {
            "radios": radios,
            "buscar": buscar,
            "total_radios": Radio.objects.count(),
        },
    )

@login_required(login_url="login")
def registrar_radio(request):
    if request.method == "POST":
        formulario = RadioForm(request.POST)

        if formulario.is_valid():
            with transaction.atomic():
                radio = formulario.save()

                imagen_qr = generar_qr_radio(radio, request)

                radio.imagen_qr.save(
                    imagen_qr.name,
                    imagen_qr,
                    save=True,
                )

                MovimientoKardex.objects.create(
                    radio=radio,
                    tipo=MovimientoKardex.Tipo.REGISTRO,
                    descripcion=(
                        "Registro inicial del equipo en el sistema."
                    ),
                    ubicacion=radio.ubicacion,
                    responsable=radio.responsable,
                    registrado_por=request.user,
                )

            messages.success(
                request,
                f"El radio {radio.codigo_interno} "
                "se registró correctamente.",
            )

            return redirect("lista_radios")

    else:
        formulario = RadioForm()

    return render(
        request,
        "core/registrar_radio.html",
        {"formulario": formulario},
    )


@login_required(login_url="login")
def detalle_radio(request, identificador_qr):
    radio = get_object_or_404(
        Radio,
        identificador_qr=identificador_qr,
    )

    movimientos = (
        radio.movimientos_kardex
        .select_related("registrado_por")
        .all()
    )

    return render(
        request,
        "core/detalle_radio.html",
        {
            "radio": radio,
            "movimientos": movimientos,
        },
    )

@login_required(login_url="login")
def generador_qr(request):
    radio = None
    error = None

    if request.method == "POST":
        codigo_interno = request.POST.get(
            "codigo_interno", ""
        ).strip()

        if not codigo_interno:
            error = "Introduce el código interno del radio."
        else:
            try:
                radio = Radio.objects.get(
                    codigo_interno__iexact=codigo_interno
                )

                if not radio.imagen_qr:
                    imagen_qr = generar_qr_radio(
                        radio,
                        request,
                    )

                    radio.imagen_qr.save(
                        imagen_qr.name,
                        imagen_qr,
                        save=True,
                    )

            except Radio.DoesNotExist:
                error = (
                    f"No se encontró ningún radio con el "
                    f"código {codigo_interno}."
                )

    return render(
        request,
        "core/generador_qr.html",
        {
            "radio": radio,
            "error": error,
        },
    )


@login_required(login_url="login")
def trazabilidad(request):
    codigo = request.GET.get("codigo", "").strip()

    radio = None
    movimientos = MovimientoKardex.objects.none()
    ordenes = OrdenTrabajo.objects.none()
    error = None

    if codigo:
        try:
            radio = Radio.objects.get(
                codigo_interno__iexact=codigo
            )

            movimientos = (
                radio.movimientos_kardex
                .select_related("registrado_por")
                .order_by("-fecha")
            )

            ordenes = (
                OrdenTrabajo.objects
                .filter(radio=radio)
                .order_by("-fecha_inicio")
            )

        except Radio.DoesNotExist:
            error = (
                f"No se encontró ningún radio con el "
                f"código {codigo}."
            )

    contexto = {
        "codigo": codigo,
        "radio": radio,
        "movimientos": movimientos,
        "ordenes": ordenes,
        "error": error,
    }

    return render(
        request,
        "core/trazabilidad.html",
        contexto,
    )

@login_required(login_url="login")
def registrar_constatacion(request, identificador_qr):
    radio = get_object_or_404(
        Radio,
        identificador_qr=identificador_qr,
    )

    if request.method == "POST":
        formulario = ConstatacionForm(request.POST)

        if formulario.is_valid():
            ubicacion = formulario.cleaned_data["ubicacion"]
            responsable = formulario.cleaned_data["responsable"]
            descripcion = formulario.cleaned_data["descripcion"]

            with transaction.atomic():
                radio.ubicacion = ubicacion
                radio.responsable = responsable
                radio.save(
                    update_fields=["ubicacion", "responsable"]
                )

                MovimientoKardex.objects.create(
                    radio=radio,
                    tipo=MovimientoKardex.Tipo.CONSTATACION,
                    descripcion=(
                        descripcion
                        or "Constatación física del equipo."
                    ),
                    ubicacion=ubicacion,
                    responsable=responsable,
                    registrado_por=request.user,
                )

            messages.success(
                request,
                "Constatación física registrada correctamente.",
            )

            return redirect(
                "detalle_radio",
                identificador_qr=radio.identificador_qr,
            )
    else:
        formulario = ConstatacionForm(
            initial={
                "ubicacion": radio.ubicacion,
                "responsable": radio.responsable,
            }
        )

    return render(
        request,
        "core/registrar_constatacion.html",
        {
            "radio": radio,
            "formulario": formulario,
        },
    )

@login_required(login_url="login")
def iniciar_orden(request, identificador_qr):
    radio = get_object_or_404(
        Radio,
        identificador_qr=identificador_qr,
    )

    if request.method != "POST":
        formulario = OrdenTrabajoForm(
            initial={
                "radio": radio,
                "responsable": radio.responsable,
                "fecha_inicio": timezone.localtime().strftime(
                    "%Y-%m-%dT%H:%M"
                ),
            }
        )

        return render(
            request,
            "core/orden_trabajo.html",
            {
                "radio": radio,
                "formulario": formulario,
            },
        )

    formulario = OrdenTrabajoForm(request.POST)

    if formulario.is_valid():
        radio_seleccionado = formulario.cleaned_data["radio"]

        if radio_seleccionado.pk != radio.pk:
            formulario.add_error(
                "radio",
                "El radio seleccionado no coincide con el equipo consultado.",
            )
        else:
            with transaction.atomic():
                orden = formulario.save(commit=False)
                orden.radio = radio
                orden.codigo_radio = radio.codigo_interno
                orden.estado = OrdenTrabajo.ESTADO_INICIADA
                orden.fecha_terminado = None
                orden.save()

                MovimientoKardex.objects.create(
                    radio=radio,
                    tipo=MovimientoKardex.Tipo.ORDEN_INICIADA,
                    descripcion=(
                        f"Orden iniciada: {orden.descripcion}. "
                        f"Fecha límite: "
                        f"{timezone.localtime(orden.fecha_limite):%d/%m/%Y %H:%M}."
                    ),
                    ubicacion=radio.ubicacion,
                    responsable=orden.responsable,
                    registrado_por=request.user,
                )

            messages.success(
                request,
                "La orden de trabajo se registró correctamente.",
            )

            return redirect(
                "trazabilidad"
            )

    return render(
        request,
        "core/orden_trabajo.html",
        {
            "radio": radio,
            "formulario": formulario,
        },
    )

@login_required(login_url="login")
def cerrar_orden(request, orden_id):
    if request.method != "POST":
        return redirect("trazabilidad")

    orden = get_object_or_404(
        OrdenTrabajo.objects.select_related("radio"),
        pk=orden_id,
    )

    if orden.estado == OrdenTrabajo.ESTADO_CERRADA:
        messages.info(
            request,
            "Esta orden ya está cerrada.",
        )
    else:
        with transaction.atomic():
            orden.estado = OrdenTrabajo.ESTADO_CERRADA
            orden.fecha_terminado = timezone.now()
            orden.save(
                update_fields=["estado", "fecha_terminado"]
            )

            radio = orden.radio

            if radio is not None:
                MovimientoKardex.objects.create(
                    radio=radio,
                    tipo=MovimientoKardex.Tipo.ORDEN_CERRADA,
                    descripcion=(
                        f"Orden cerrada: {orden.descripcion}. "
                        f"Fecha real de terminación: "
                        f"{timezone.localtime(orden.fecha_terminado):%d/%m/%Y %H:%M}."
                    ),
                    ubicacion=radio.ubicacion,
                    responsable=orden.responsable,
                    registrado_por=request.user,
                )

        messages.success(
            request,
            "La orden se cerró correctamente.",
        )

    if orden.radio is not None:
        return redirect(
            f"/trazabilidad/?codigo={orden.radio.codigo_interno}"
        )

    return redirect("trazabilidad")
