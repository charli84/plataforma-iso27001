import datetime

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.utils import timezone

from controles.models import Control
from ia.models import Evaluacion

# Orden de urgencia para el Roadmap: lo peor primero.
PRIORIDAD_ESTADO = {
    "SIN_EVIDENCIA": 0,
    "NO_CUMPLE": 1,
    "PENDIENTE": 2,
    "PARCIAL": 3,
    "CUMPLE": 4,
}


def _cliente_del_usuario(request):
    """Devuelve el Cliente vinculado al usuario logueado, o None si no tiene uno
    (ej. un superusuario de staff que no representa a ningún cliente)."""
    return getattr(request.user, "cliente", None)


def _ultima_evaluacion_por_control(cliente):
    """Para cada control, la evaluación más reciente de ESTE cliente (si existe)."""
    evaluaciones = (
        Evaluacion.objects.filter(evidencia__cliente=cliente)
        .select_related("evidencia", "evidencia__control")
        .order_by("evidencia__control__codigo", "-evaluado_en")
    )
    ultima_por_codigo = {}
    for evaluacion in evaluaciones:
        codigo = evaluacion.evidencia.control.codigo
        # Como ya viene ordenado por -evaluado_en, la primera que encontramos
        # por código es la más reciente.
        ultima_por_codigo.setdefault(codigo, evaluacion)
    return ultima_por_codigo


@login_required
def gap(request):
    cliente = _cliente_del_usuario(request)
    if cliente is None:
        messages.info(
            request,
            "Tu usuario no está vinculado a ningún cliente. Si eres del equipo de "
            "Timed, usa el panel de administración.",
        )
        return redirect("admin:index")

    ultima_por_codigo = _ultima_evaluacion_por_control(cliente)

    filas = []
    for control in Control.objects.all():
        evaluacion = ultima_por_codigo.get(control.codigo)
        estado = evaluacion.cumplimiento if evaluacion else "SIN_EVIDENCIA"
        filas.append({"control": control, "evaluacion": evaluacion, "estado": estado})

    total = len(filas)
    resumen = {
        "CUMPLE": sum(1 for f in filas if f["estado"] == "CUMPLE"),
        "PARCIAL": sum(1 for f in filas if f["estado"] == "PARCIAL"),
        "NO_CUMPLE": sum(1 for f in filas if f["estado"] == "NO_CUMPLE"),
        "PENDIENTE": sum(1 for f in filas if f["estado"] == "PENDIENTE"),
        "SIN_EVIDENCIA": sum(1 for f in filas if f["estado"] == "SIN_EVIDENCIA"),
    }
    porcentaje_cumple = round(100 * resumen["CUMPLE"] / total, 1) if total else 0

    contexto = {
        "cliente": cliente,
        "filas": filas,
        "total": total,
        "resumen": resumen,
        "porcentaje_cumple": porcentaje_cumple,
    }
    return render(request, "clientes/gap.html", contexto)


@login_required
def roadmap(request):
    cliente = _cliente_del_usuario(request)
    if cliente is None:
        messages.info(
            request,
            "Tu usuario no está vinculado a ningún cliente. Si eres del equipo de "
            "Timed, usa el panel de administración.",
        )
        return redirect("admin:index")

    ultima_por_codigo = _ultima_evaluacion_por_control(cliente)

    pendientes = []
    for control in Control.objects.all():
        evaluacion = ultima_por_codigo.get(control.codigo)
        estado = evaluacion.cumplimiento if evaluacion else "SIN_EVIDENCIA"
        if estado == "CUMPLE":
            continue
        pendientes.append({
            "control": control,
            "evaluacion": evaluacion,
            "estado": estado,
            "prioridad": PRIORIDAD_ESTADO.get(estado, 9),
        })

    pendientes.sort(key=lambda f: (f["prioridad"], f["control"].codigo))

    contexto = {"cliente": cliente, "pendientes": pendientes}
    return render(request, "clientes/roadmap.html", contexto)


@login_required
def calendario(request):
    """Próxima fecha de revisión para los controles de revisión periódica
    (ej. políticas, revisión independiente, gestión de vulnerabilidades):
    última evaluación + periodicidad del control. Un control que nunca se
    ha evaluado todavía no tiene un ciclo que calcular, así que no aparece
    aquí hasta su primera evidencia (sí aparece en el GAP y el Roadmap).

    La fecha se aproxima con meses de 30 días -no meses calendario exactos-
    para no depender de una librería extra; es una estimación visible en el
    dashboard, no una notificación automática (eso requeriría una tarea
    programada, fuera de alcance por ahora)."""
    cliente = _cliente_del_usuario(request)
    if cliente is None:
        messages.info(
            request,
            "Tu usuario no está vinculado a ningún cliente. Si eres del equipo de "
            "Timed, usa el panel de administración.",
        )
        return redirect("admin:index")

    ultima_por_codigo = _ultima_evaluacion_por_control(cliente)
    hoy = timezone.localdate()

    items = []
    controles_con_periodicidad = Control.objects.filter(
        periodicidad_revision_meses__isnull=False
    )
    for control in controles_con_periodicidad:
        evaluacion = ultima_por_codigo.get(control.codigo)
        if evaluacion is None:
            continue

        proxima_revision = evaluacion.evaluado_en.date() + datetime.timedelta(
            days=control.periodicidad_revision_meses * 30
        )
        dias_restantes = (proxima_revision - hoy).days
        items.append({
            "control": control,
            "evaluacion": evaluacion,
            "proxima_revision": proxima_revision,
            "dias_restantes": dias_restantes,
            "vencida": dias_restantes < 0,
        })

    items.sort(key=lambda i: i["proxima_revision"])

    controles_sin_evaluar = [
        c for c in controles_con_periodicidad if c.codigo not in ultima_por_codigo
    ]

    contexto = {
        "cliente": cliente,
        "items": items,
        "controles_sin_evaluar": controles_sin_evaluar,
    }
    return render(request, "clientes/calendario.html", contexto)
