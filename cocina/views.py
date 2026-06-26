from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect
from django.template.loader import render_to_string
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.decorators.http import require_POST
from django.views.generic import TemplateView, ListView, CreateView, UpdateView

from rest_framework import viewsets, permissions
from rest_framework.pagination import PageNumberPagination

from .models import Orden, DetalleOrden
from .serializers import OrdenSerializer
from productos.models import Producto
from productos.roles import RoleRequiredMixin, get_user_role


# ─── Cocina Dashboard ──────────────────────────────────────────────────────────

class CocinaDashboardView(RoleRequiredMixin, TemplateView):
    allowed_roles = ["Admin", "Cocina"]
    template_name = "cocina/dashboard.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["pendientes"] = Orden.objects.filter(
            estado="pendiente"
        ).prefetch_related("detalles__producto")
        context["en_preparacion"] = Orden.objects.filter(
            estado="preparacion"
        ).prefetch_related("detalles__producto")
        context["listos"] = Orden.objects.filter(
            estado="listo"
        ).prefetch_related("detalles__producto")
        context["productos"] = Producto.objects.filter(
            estado="activo", disponibilidad=True
        ).select_related("categoria")
        return context


# ─── POS / Nueva Orden ─────────────────────────────────────────────────────────

class POSCreateOrdenView(RoleRequiredMixin, TemplateView):
    allowed_roles = ["Admin", "Cocina"]
    template_name = "cocina/pos_nueva_orden.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["productos"] = Producto.objects.filter(
            estado="activo", disponibilidad=True
        ).select_related("categoria")
        context["categorias"] = (
            Producto.objects.filter(estado="activo", disponibilidad=True)
            .values_list("categoria__nombre", flat=True)
            .distinct()
        )
        return context


@login_required
@require_POST
def crear_orden(request):
    import json
    data = json.loads(request.body)
    items = data.get("items", [])
    cliente = data.get("cliente", "")
    mesa = data.get("mesa")
    nota = data.get("nota", "")

    if not items:
        return JsonResponse({"error": "La orden debe tener al menos un item"}, status=400)

    orden = Orden.objects.create(
        cliente=cliente or None,
        mesa=int(mesa) if mesa else None,
        nota=nota or None,
        usuario=request.user,
    )

    total = 0
    for item in items:
        producto = get_object_or_404(Producto, pk=item["producto_id"])
        cantidad = int(item.get("cantidad", 1))
        precio = producto.precio
        DetalleOrden.objects.create(
            orden=orden,
            producto=producto,
            cantidad=cantidad,
            precio_unitario=precio,
            nota=item.get("nota", ""),
        )
        total += precio * cantidad
        if producto.stock >= cantidad:
            producto.stock -= cantidad
            producto.save()

    orden.total = total
    orden.save()

    return JsonResponse({"success": True, "orden_id": orden.id})


@login_required
def ordenes_activas_api(request):
    ordenes = Orden.objects.exclude(estado="entregado").prefetch_related(
        "detalles__producto"
    )
    data = []
    for o in ordenes:
        delta = timezone.now() - o.creada
        minutos = int(delta.total_seconds() // 60)
        data.append(
            {
                "id": o.id,
                "cliente": o.cliente or f"Mesa {o.mesa}" if o.mesa else f"#{o.id}",
                "mesa": o.mesa,
                "estado": o.estado,
                "total": str(o.total),
                "tiempo": f"{minutos} min" if minutos > 0 else "<1 min",
                "detalles": [
                    {
                        "producto": d.producto.nombre,
                        "cantidad": d.cantidad,
                        "nota": d.nota,
                    }
                    for d in o.detalles.all()
                ],
            }
        )
    return JsonResponse({"ordenes": data})


@login_required
@require_POST
def cambiar_estado_orden(request, pk):
    orden = get_object_or_404(Orden, pk=pk)
    nuevo_estado = request.POST.get("estado")
    if nuevo_estado in dict(Orden.ESTADOS):
        orden.estado = nuevo_estado
        orden.save()
    return redirect("cocina:dashboard")


# ─── HTMX Views ────────────────────────────────────────────────────────────────

@login_required
def htmx_cocina_ordenes(request):
    pendientes = Orden.objects.filter(estado="pendiente").prefetch_related(
        "detalles__producto"
    )
    en_preparacion = Orden.objects.filter(estado="preparacion").prefetch_related(
        "detalles__producto"
    )
    listos = Orden.objects.filter(estado="listo").prefetch_related("detalles__producto")

    html_pendientes = render_to_string(
        "cocina/_orden_column.html",
        {"ordenes": pendientes, "columna": "pendiente", "titulo": "Pendientes"},
        request=request,
    )
    html_preparacion = render_to_string(
        "cocina/_orden_column.html",
        {"ordenes": en_preparacion, "columna": "preparacion", "titulo": "En Preparación"},
        request=request,
    )
    html_listos = render_to_string(
        "cocina/_orden_column.html",
        {"ordenes": listos, "columna": "listo", "titulo": "Listos"},
        request=request,
    )
    return JsonResponse(
        {
            "pendientes": html_pendientes,
            "preparacion": html_preparacion,
            "listos": html_listos,
        }
    )


@login_required
def htmx_pos_productos(request):
    q = request.GET.get("q", "").strip()
    categoria = request.GET.get("categoria", "")
    qs = Producto.objects.filter(estado="activo", disponibilidad=True).select_related(
        "categoria"
    )
    if q:
        qs = qs.filter(
            Q(nombre__icontains=q) | Q(categoria__nombre__icontains=q)
        )
    if categoria:
        qs = qs.filter(categoria__nombre=categoria)
    html = render_to_string(
        "cocina/_pos_productos.html",
        {"productos": qs[:50]},
        request=request,
    )
    return JsonResponse({"html": html})


# ─── API ──────────────────────────────────────────────────────────────────────

class OrdenPagination(PageNumberPagination):
    page_size = 20


class OrdenViewSet(viewsets.ModelViewSet):
    queryset = Orden.objects.all().prefetch_related("detalles__producto")
    serializer_class = OrdenSerializer
    pagination_class = OrdenPagination
    filterset_fields = ["estado"]


class CocinaOrdenViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Orden.objects.exclude(estado="entregado").prefetch_related(
        "detalles__producto"
    )
    serializer_class = OrdenSerializer
    pagination_class = None
