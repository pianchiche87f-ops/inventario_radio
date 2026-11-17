
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.shortcuts import render, redirect, get_object_or_404
from inventario.forms import RadioForm, ConstatacionForm
from inventario.models import Radio, MovimientoKardex
from .forms import OrdenTrabajoForm, MantenimientoForm
from .models import OrdenTrabajo, Mantenimiento
from inventario.qr import generar_qr_radio
from django.utils import timezone
from django.db.models import Q, OuterRef, Subquery

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
            radio = formulario.save()

            if not radio.imagen_qr:
                radio.imagen_qr = generar_qr_radio(radio, request)
                radio.save(update_fields=["imagen_qr"])

            messages.success(
                request,
                "Radio registrado correctamente."
            )

            return redirect("lista_constataciones")

    else:
        formulario = RadioForm()

    return render(
        request,
        "core/registrar_radio.html",
        {
            "formulario": formulario,
        },
    )


@login_required(login_url="login")
def ingresar_constatacion(request):
    error = None

    if request.method == "POST":
        identificador = request.POST.get(
            "identificador", ""
        ).strip()

        if not identificador:
            error = "Ingresa el código interno o escanea el QR."

        else:
            # Primero buscar por código interno.
            radio = Radio.objects.filter(
                codigo_interno__iexact=identificador
            ).first()

            # Si no existe, intentar identificarlo mediante UUID.
            if radio is None:
                from uuid import UUID

                identificador_qr = (
                    identificador.rstrip("/").split("/")[-1]
                )

                try:
                    uuid_validado = UUID(identificador_qr)

                    radio = Radio.objects.filter(
                        identificador_qr=uuid_validado
                    ).first()

                except ValueError:
                    radio = None

            # Si se encontró el equipo, abrir el formulario.
            if radio:
                return redirect(
                    "registrar_constatacion",
                    identificador_qr=radio.identificador_qr,
                )

            # Si no existe, mostrar mensaje.
            error = (
                "Equipo no registrado. Verifica el código interno "
                "o el código QR e inténtalo nuevamente."
            )

    return render(
        request,
        "core/ingresar_constatacion.html",
        {
            "error": error,
        },
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
    ordenes_abiertas = OrdenTrabajo.objects.none()
    ordenes_cerradas = OrdenTrabajo.objects.none()
    error = None

    if codigo:
        try:
            radio = Radio.objects.get(codigo_interno__iexact=codigo)

            movimientos = (
                radio.movimientos_kardex
                .select_related("registrado_por")
                .order_by("-fecha")
            )

            ordenes = OrdenTrabajo.objects.filter(radio=radio)

            ordenes_abiertas = ordenes.filter(
                estado=OrdenTrabajo.ESTADO_INICIADA
            ).order_by("-fecha_inicio")

            ordenes_cerradas = ordenes.filter(
                estado=OrdenTrabajo.ESTADO_CERRADA
            ).order_by("-fecha_terminado")

        except Radio.DoesNotExist:
            error = f"No se encontró ningún radio con el código {codigo}."

    contexto = {
        "codigo": codigo,
        "radio": radio,
        "movimientos": movimientos,
        "ordenes_abiertas": ordenes_abiertas,
        "ordenes_cerradas": ordenes_cerradas,
        "error": error,
    }

    return render(request, "core/trazabilidad.html", contexto)



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
            condicion_fisica = formulario.cleaned_data["condicion_fisica"]
            descripcion = formulario.cleaned_data["descripcion"]

            # Evitar que se registre dos veces la misma constatación
            # del mismo equipo dentro de un intervalo de 30 segundos.
            fecha_limite = timezone.now() - timezone.timedelta(seconds=30)

            duplicado = MovimientoKardex.objects.filter(
                radio=radio,
                tipo=MovimientoKardex.Tipo.CONSTATACION,
                ubicacion=ubicacion,
                responsable=responsable,
                condicion_fisica=condicion_fisica,
                descripcion=(
                    descripcion
                    or "Constatación física del equipo."
                ),
                registrado_por=request.user,
                fecha__gte=fecha_limite,
            ).exists()

            if duplicado:
                messages.warning(
                    request,
                    "Esta constatación ya fue registrada recientemente. "
                    "No se creó un registro duplicado."
                )
                return redirect("lista_constataciones")

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
                    condicion_fisica=condicion_fisica,
                    registrado_por=request.user,
                )

            messages.success(
                request,
                "Constatación física registrada correctamente."
            )

            return redirect("lista_constataciones")

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
def lista_constataciones(request):

    # Obtener las constataciones registradas.
    constataciones = MovimientoKardex.objects.filter(
        tipo=MovimientoKardex.Tipo.CONSTATACION
    ).select_related(
        "radio", "registrado_por"
    )

    codigo = request.GET.get("codigo", "").strip()
    desde = request.GET.get("desde", "").strip()
    hasta = request.GET.get("hasta", "").strip()

    # Aplicar filtros.
    if codigo:
        constataciones = constataciones.filter(
            radio__codigo_interno__icontains=codigo
        )

    if desde:
        constataciones = constataciones.filter(
            fecha__date__gte=desde
        )

    if hasta:
        constataciones = constataciones.filter(
            fecha__date__lte=hasta
        )

    # Obtener únicamente la última constatación de cada radio.
    ultima_por_equipo = constataciones.filter(
        radio_id=OuterRef("radio_id")
    ).order_by(
        "-fecha", "-id"
    )

    constataciones = constataciones.filter(
        pk__in=Subquery(
            ultima_por_equipo.values("pk")[:1]
        )
    ).order_by("-fecha", "-id")

    # Resumen general del inventario.
    total_equipos = Radio.objects.count()

    # Contar cada radio una sola vez.
    equipos_constatados = (
        MovimientoKardex.objects.filter(
            tipo=MovimientoKardex.Tipo.CONSTATACION
        )
        .values("radio_id")
        .distinct()
        .count()
    )

    equipos_pendientes = max(
        total_equipos - equipos_constatados,
        0
    )

    porcentaje_avance = (
        round((equipos_constatados / total_equipos) * 100, 1)
        if total_equipos > 0 else 0
    )

    return render(
        request,
        "core/lista_constataciones.html",
        {
            "constataciones": constataciones,
            "codigo": codigo,
            "fecha_desde": desde,
            "fecha_hasta": hasta,
            "total_constataciones": constataciones.count(),

            "total_equipos": total_equipos,
            "equipos_constatados": equipos_constatados,
            "equipos_pendientes": equipos_pendientes,
            "porcentaje_avance": porcentaje_avance,
        }
    )


@login_required(login_url="login")
def seleccionar_radio_orden(request):
    buscar = request.GET.get("buscar", "").strip()

    radios = Radio.objects.all().order_by("codigo_interno")

    if buscar:
        radios = radios.filter(
            Q(codigo_interno__icontains=buscar)
            | Q(numero_serie__icontains=buscar)
            | Q(marca__icontains=buscar)
            | Q(modelo__icontains=buscar)
        )

    contexto = {
        "radios": radios,
        "buscar": buscar,
    }

    return render(
        request,
        "core/seleccionar_radio_orden.html",
        contexto,
    )


@login_required(login_url="login")
def iniciar_orden(request, identificador_qr):
    radio = get_object_or_404(
        Radio,
        identificador_qr=identificador_qr,
    )

    # Evitar que un radio tenga dos órdenes abiertas.
    tiene_orden_activa = OrdenTrabajo.objects.filter(
        radio=radio,
        estado=OrdenTrabajo.ESTADO_INICIADA,
    ).exists()

    if tiene_orden_activa:
        messages.warning(
            request,
            f"El radio {radio.codigo_interno} ya tiene una orden de trabajo en proceso. "
            "Debe cerrarse antes de iniciar otra.",
        )
        return redirect("lista_ordenes")

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
                # Segunda comprobación antes de guardar.
                tiene_orden_activa = OrdenTrabajo.objects.filter(
                    radio=radio,
                    estado=OrdenTrabajo.ESTADO_INICIADA,
                ).exists()

                if tiene_orden_activa:
                    messages.warning(
                        request,
                        "Este radio ya tiene una orden de trabajo en proceso.",
                    )
                    return redirect("lista_ordenes")

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

            return redirect("lista_ordenes")

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



@login_required(login_url="login")
def lista_ordenes(request):
    ahora = timezone.now()

    ordenes = (
        OrdenTrabajo.objects
        .select_related("radio")
        .order_by("-fecha_inicio")
    )

    # Indicadores del módulo.
    total_ordenes = ordenes.count()

    ordenes_en_proceso = ordenes.filter(
        estado=OrdenTrabajo.ESTADO_INICIADA
    ).count()

    ordenes_finalizadas = ordenes.filter(
        estado=OrdenTrabajo.ESTADO_CERRADA
    ).count()

    ordenes_vencidas = ordenes.filter(
        estado=OrdenTrabajo.ESTADO_INICIADA,
        fecha_limite__lt=ahora,
    ).count()

    contexto = {
        "ordenes": ordenes,
        "total_ordenes": total_ordenes,
        "ordenes_en_proceso": ordenes_en_proceso,
        "ordenes_finalizadas": ordenes_finalizadas,
        "ordenes_vencidas": ordenes_vencidas,
    }

    return render(
        request,
        "core/lista_ordenes.html",
        contexto,
    )

@login_required(login_url="login")
def mantenimiento(request):
    if request.method == "POST":
        form = MantenimientoForm(request.POST)

        if form.is_valid():
            radio = form.cleaned_data["radio"]

            # No permitir mantenimiento a equipos dados de baja
            # o que todavía están en poder de terceros.
            if radio.estado in [
                Radio.Estado.BAJA,
                Radio.Estado.EN_TERCEROS,
                Radio.Estado.MANTENIMIENTO,
            ]:
                messages.error(
                    request,
                    "No se puede registrar el mantenimiento: "
                    "el estado actual del equipo no lo permite."
                )
                return redirect("mantenimiento")

            with transaction.atomic():
                # Guardar el estado que tenía el radio antes
                # de entrar en mantenimiento.
                nuevo_mantenimiento = form.save(commit=False)
                nuevo_mantenimiento.estado_radio_anterior = radio.estado
                nuevo_mantenimiento.estado = Mantenimiento.EN_PROCESO
                nuevo_mantenimiento.save()

                # Cambiar el estado del equipo en el inventario.
                radio.estado = Radio.Estado.MANTENIMIENTO
                radio.save(update_fields=["estado"])

                # Registrar el movimiento en el Kardex.
                MovimientoKardex.objects.create(
                    radio=radio,
                    tipo=MovimientoKardex.Tipo.MANTENIMIENTO,
                    descripcion=(
                        f"Inicio de mantenimiento "
                        f"{nuevo_mantenimiento.get_tipo_intervencion_display()}. "
                        f"{nuevo_mantenimiento.descripcion}"
                    ),
                    ubicacion=radio.ubicacion,
                    responsable=radio.responsable or request.user.username,
                    registrado_por=request.user,
                )

            messages.success(
                request,
                f"El mantenimiento del equipo "
                f"{radio.codigo_interno} se registró correctamente. "
                f"El equipo ahora está en mantenimiento."
            )
            return redirect("mantenimiento")

    else:
        form = MantenimientoForm()

    mantenimientos = (
        Mantenimiento.objects
        .select_related("radio")
        .order_by("-fecha_registro")
    )

    mantenimientos_activos = mantenimientos.exclude(
        estado=Mantenimiento.FINALIZADO
    ).filter(anulado=False).count()

    mantenimientos_vencidos = sum(
        1 for item in mantenimientos if item.vencido
    )

    contexto = {
        "form": form,
        "mantenimientos": mantenimientos,
        "mantenimientos_activos": mantenimientos_activos,
        "mantenimientos_vencidos": mantenimientos_vencidos,
    }

    return render(request, "core/mantenimiento.html", contexto)


@login_required(login_url="login")
def finalizar_mantenimiento(request, mantenimiento_id):
    mantenimiento = get_object_or_404(
        Mantenimiento.objects.select_related("radio"),
        id=mantenimiento_id,
        anulado=False
    )

    if request.method != "POST":
        return redirect("mantenimiento")

    if mantenimiento.estado != Mantenimiento.EN_PROCESO:
        messages.error(
            request,
            "Este mantenimiento no se encuentra en proceso."
        )
        return redirect("mantenimiento")

    trabajo = request.POST.get("trabajo_realizado", "").strip()

    if not trabajo:
        messages.error(
            request,
            "Debes describir el trabajo realizado antes de finalizar."
        )
        return redirect("mantenimiento")

    radio = mantenimiento.radio

    # Evitar finalizar sin conocer el estado anterior del equipo.
    if not mantenimiento.estado_radio_anterior:
        messages.error(
            request,
            "No se puede restaurar el estado del equipo porque "
            "no se registró su estado anterior. "
            "Debes revisarlo antes de finalizar."
        )
        return redirect("mantenimiento")

    with transaction.atomic():

        # Finalizar el mantenimiento.
        mantenimiento.estado = Mantenimiento.FINALIZADO
        mantenimiento.fecha_finalizacion = timezone.now()
        mantenimiento.trabajo_realizado = trabajo
        mantenimiento.finalizado_por = request.user
        mantenimiento.resultado = "OPERATIVO"
        mantenimiento.save()

        # Restaurar el estado que tenía el radio anteriormente.
        if radio.estado == Radio.Estado.MANTENIMIENTO:
            radio.estado = mantenimiento.estado_radio_anterior
            radio.save(update_fields=["estado"])

        # Seleccionar el tipo de movimiento para el Kardex.
        if mantenimiento.tipo_intervencion == Mantenimiento.CORRECTIVO:
            tipo_movimiento = MovimientoKardex.Tipo.REPARACION
        else:
            tipo_movimiento = MovimientoKardex.Tipo.MANTENIMIENTO

        # Registrar la finalización en el Kardex.
        MovimientoKardex.objects.create(
            radio=radio,
            tipo=tipo_movimiento,
            descripcion=(
                f"Finalización de "
                f"{mantenimiento.get_tipo_intervencion_display()}. "
                f"Trabajo realizado: {trabajo}"
            ),
            ubicacion=radio.ubicacion,
            responsable=radio.responsable or request.user.username,
            registrado_por=request.user,
        )

    messages.success(
        request,
        f"El mantenimiento del equipo {radio.codigo_interno} "
        f"se finalizó correctamente. Se restauró su estado anterior."
    )

    return redirect("mantenimiento")

@login_required(login_url="login")
def anular_mantenimiento(request, mantenimiento_id):
    mantenimiento = get_object_or_404(
        Mantenimiento.objects.select_related("radio"),
        id=mantenimiento_id,
        anulado=False
    )

    if request.method != "POST":
        return redirect("mantenimiento")

    if mantenimiento.estado != Mantenimiento.EN_PROCESO:
        messages.error(
            request,
            "Solo se pueden anular mantenimientos que estén en proceso."
        )
        return redirect("mantenimiento")

    motivo = request.POST.get("motivo_anulacion", "").strip()

    if not motivo:
        messages.error(
            request,
            "Debes indicar el motivo de la anulación."
        )
        return redirect("mantenimiento")

    radio = mantenimiento.radio

    if not mantenimiento.estado_radio_anterior:
        messages.error(
            request,
            "No se puede anular porque no se registró el estado anterior "
            "del equipo. Debes revisarlo antes de continuar."
        )
        return redirect("mantenimiento")

    with transaction.atomic():

        # Registrar la anulación.
        mantenimiento.anulado = True
        mantenimiento.motivo_anulacion = motivo
        mantenimiento.fecha_anulacion = timezone.now()
        mantenimiento.anulado_por = request.user
        mantenimiento.save()

        # Restaurar el estado anterior del radio.
        if radio.estado == Radio.Estado.MANTENIMIENTO:
            radio.estado = mantenimiento.estado_radio_anterior
            radio.save(update_fields=["estado"])

        # Registrar la anulación en el Kardex.
        MovimientoKardex.objects.create(
            radio=radio,
            tipo=MovimientoKardex.Tipo.MANTENIMIENTO,
            descripcion=(
                f"Mantenimiento anulado. "
                f"Motivo: {motivo}"
            ),
            ubicacion=radio.ubicacion,
            responsable=radio.responsable or request.user.username,
            registrado_por=request.user,
        )

    messages.success(
        request,
        f"El mantenimiento del equipo {radio.codigo_interno} "
        f"fue anulado correctamente. Se restauró su estado anterior."
    )

    return redirect("mantenimiento")
