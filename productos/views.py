import io
import json
from decimal import Decimal
from datetime import datetime

from django.conf import settings
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import Group
from django.db.models import Count, Q, Sum, F, Value
from django.db.models.functions import Coalesce
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.template.loader import render_to_string
from django.contrib import messages
from django.urls import reverse_lazy
from django.views.decorators.http import require_POST
from django.views.generic import (
    ListView,
    CreateView,
    UpdateView,
    DeleteView,
    DetailView,
    TemplateView,
)

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, landscape
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate,
    Table,
    TableStyle,
    Paragraph,
    Spacer,
    Image,
)

from rest_framework import viewsets, permissions, filters
from rest_framework.pagination import PageNumberPagination

from .forms import ProductoForm, CategoriaForm, RegistroForm
from .models import Producto, Categoria, Auditoria
from .serializers import ProductoSerializer, ProductoListSerializer, CategoriaSerializer
from .roles import get_user_role, role_redirect, RoleRequiredMixin


def get_client_ip(request):
    x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    if x_forwarded_for:
        return x_forwarded_for.split(",")[0].strip()
    return request.META.get("REMOTE_ADDR")


# ─── CRUD Productos ───────────────────────────────────────────────────────────

class ProductoListView(LoginRequiredMixin, ListView):
    model = Producto
    template_name = "productos/list.html"
    context_object_name = "productos"
    paginate_by = 12

    def get_queryset(self):
        return Producto.objects.filter(estado="activo").select_related("categoria")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["categorias"] = Categoria.objects.filter(estado=True)
        context["total_productos"] = Producto.objects.count()
        context["activos"] = Producto.objects.filter(estado="activo").count()
        context["agotados"] = Producto.objects.filter(
            disponibilidad=False, estado="activo"
        ).count()
        return context


class ProductoCreateView(RoleRequiredMixin, CreateView):
    allowed_roles = ["Admin", "Cajero"]
    model = Producto
    form_class = ProductoForm
    template_name = "productos/create.html"
    success_url = reverse_lazy("productos:list")

    def form_valid(self, form):
        response = super().form_valid(form)
        Auditoria.objects.create(
            usuario=self.request.user,
            accion="creacion",
            producto=self.object,
            detalle=f"Producto creado: {self.object.nombre}",
            ip=get_client_ip(self.request),
        )
        return response

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["titulo"] = "Crear Producto"
        return context


class ProductoUpdateView(RoleRequiredMixin, UpdateView):
    allowed_roles = ["Admin", "Cajero"]
    model = Producto
    form_class = ProductoForm
    template_name = "productos/update.html"
    success_url = reverse_lazy("productos:list")

    def form_valid(self, form):
        old = Producto.objects.get(pk=self.object.pk)
        changes = []
        if old.precio != form.cleaned_data["precio"]:
            changes.append(
                f"Precio cambiado de {old.precio} a {form.cleaned_data['precio']}"
            )
            Auditoria.objects.create(
                usuario=self.request.user,
                accion="cambio_precio",
                producto=self.object,
                detalle=f"Precio: {old.precio} → {form.cleaned_data['precio']}",
                ip=get_client_ip(self.request),
            )
        if old.stock != form.cleaned_data["stock"]:
            changes.append(
                f"Stock cambiado de {old.stock} a {form.cleaned_data['stock']}"
            )
            Auditoria.objects.create(
                usuario=self.request.user,
                accion="cambio_stock",
                producto=self.object,
                detalle=f"Stock: {old.stock} → {form.cleaned_data['stock']}",
                ip=get_client_ip(self.request),
            )
        response = super().form_valid(form)
        Auditoria.objects.create(
            usuario=self.request.user,
            accion="actualizacion",
            producto=self.object,
            detalle=f"Producto actualizado: {self.object.nombre}. Cambios: {'; '.join(changes) if changes else 'Sin cambios detectados'}",
            ip=get_client_ip(self.request),
        )
        return response

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["titulo"] = "Editar Producto"
        return context


class ProductoDeleteView(RoleRequiredMixin, DeleteView):
    allowed_roles = ["Admin"]
    model = Producto
    template_name = "productos/delete.html"
    success_url = reverse_lazy("productos:list")

    def delete(self, request, *args, **kwargs):
        producto = self.get_object()
        producto.estado = "inactivo"
        producto.save()
        Auditoria.objects.create(
            usuario=request.user,
            accion="eliminacion",
            producto=producto,
            detalle=f"Producto eliminado (lógico): {producto.nombre}",
            ip=get_client_ip(request),
        )
        return redirect(self.success_url)


class ProductoDetailView(LoginRequiredMixin, DetailView):
    model = Producto
    template_name = "productos/detail.html"
    context_object_name = "producto"


# ─── HTMX Productos ───────────────────────────────────────────────────────────

@login_required
def htmx_search(request):
    q = request.GET.get("q", "").strip()
    productos = Producto.objects.filter(estado="activo").select_related("categoria")
    if q:
        productos = productos.filter(
            Q(nombre__icontains=q)
            | Q(categoria__nombre__icontains=q)
            | Q(ingredientes__icontains=q)
        )
    html = render_to_string(
        "productos/_product_cards.html",
        {"productos": productos[:50]},
        request=request,
    )
    return JsonResponse({"html": html, "count": productos.count()})


@login_required
def htmx_filter(request):
    filtro = request.GET.get("filtro", "")
    categoria_id = request.GET.get("categoria", "")
    productos = Producto.objects.filter(estado="activo").select_related("categoria")

    if filtro == "disponibles":
        productos = productos.filter(disponibilidad=True)
    elif filtro == "agotados":
        productos = productos.filter(disponibilidad=False)
    elif filtro == "menor_precio":
        productos = productos.order_by("precio")
    elif filtro == "mayor_precio":
        productos = productos.order_by("-precio")
    elif filtro == "recientes":
        productos = productos.order_by("-fecha_creacion")

    if categoria_id and categoria_id.isdigit():
        productos = productos.filter(categoria_id=int(categoria_id))

    html = render_to_string(
        "productos/_product_cards.html",
        {"productos": productos[:50]},
        request=request,
    )
    return JsonResponse({"html": html})


@login_required
def htmx_product_detail(request, pk):
    producto = get_object_or_404(
        Producto.objects.select_related("categoria"), pk=pk
    )
    html = render_to_string(
        "productos/_product_modal.html",
        {"producto": producto},
        request=request,
    )
    return JsonResponse({"html": html})


# ─── Stock Alerts ─────────────────────────────────────────────────────────────

class StockAlertView(LoginRequiredMixin, TemplateView):
    template_name = "productos/stock_alertas.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        umbral = getattr(settings, "STOCK_MINIMO_ALERTA", 5)
        agotados = Producto.objects.filter(
            estado="activo", stock=0
        ).select_related("categoria")
        pocas_unidades = Producto.objects.filter(
            estado="activo", stock__gt=0, stock__lte=umbral
        ).select_related("categoria")
        en_stock = Producto.objects.filter(
            estado="activo", stock__gt=umbral
        ).select_related("categoria")
        context["agotados"] = agotados
        context["pocas_unidades"] = pocas_unidades
        context["en_stock"] = en_stock
        context["categorias"] = Categoria.objects.filter(estado=True)
        context["umbral"] = umbral
        return context


@login_required
def htmx_stock_filter(request):
    filtro = request.GET.get("filtro", "")
    categoria_id = request.GET.get("categoria", "")
    umbral = getattr(settings, "STOCK_MINIMO_ALERTA", 5)
    qs = Producto.objects.filter(estado="activo").select_related("categoria")

    if filtro == "agotados":
        qs = qs.filter(stock=0)
    elif filtro == "pocas":
        qs = qs.filter(stock__gt=0, stock__lte=umbral)
    elif filtro == "en_stock":
        qs = qs.filter(stock__gt=umbral)
    elif filtro == "criticos":
        qs = qs.filter(stock__lte=umbral)

    if categoria_id and categoria_id.isdigit():
        qs = qs.filter(categoria_id=int(categoria_id))

    html = render_to_string(
        "productos/_stock_cards.html",
        {"productos": qs[:100], "umbral": umbral},
        request=request,
    )
    return JsonResponse({"html": html})


# ─── Inventario ────────────────────────────────────────────────────────────────

class InventoryView(LoginRequiredMixin, ListView):
    model = Producto
    template_name = "productos/inventario.html"
    context_object_name = "productos"
    paginate_by = 20

    def get_queryset(self):
        return Producto.objects.filter(estado="activo").select_related("categoria")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        qs = list(Producto.objects.filter(estado="activo"))
        total_valor = sum(p.stock * p.precio for p in qs)
        total_unidades = sum(p.stock for p in qs)
        context["total_productos"] = len(qs)
        context["total_unidades"] = total_unidades
        context["valor_total_inventario"] = total_valor
        context["categorias"] = Categoria.objects.filter(estado=True)
        context["umbral"] = getattr(settings, "STOCK_MINIMO_ALERTA", 5)
        return context


@login_required
def htmx_inventario_filter(request):
    q = request.GET.get("q", "").strip()
    categoria_id = request.GET.get("categoria", "")
    stock_filter = request.GET.get("stock", "")
    umbral = getattr(settings, "STOCK_MINIMO_ALERTA", 5)

    qs = Producto.objects.filter(estado="activo").select_related("categoria")
    if q:
        qs = qs.filter(
            Q(nombre__icontains=q) | Q(categoria__nombre__icontains=q)
        )
    if categoria_id and categoria_id.isdigit():
        qs = qs.filter(categoria_id=int(categoria_id))
    if stock_filter == "agotados":
        qs = qs.filter(stock=0)
    elif stock_filter == "bajo":
        qs = qs.filter(stock__gt=0, stock__lte=umbral)
    elif stock_filter == "disponible":
        qs = qs.filter(stock__gt=umbral)

    html = render_to_string(
        "productos/_inventario_table.html",
        {"productos": qs[:200], "umbral": umbral},
        request=request,
    )
    return JsonResponse({"html": html})


# ─── Exportar PDF ──────────────────────────────────────────────────────────────

@login_required
@login_required
def exportar_inventario_pdf(request):
    from .roles import get_user_role
    if get_user_role(request.user) != "Admin":
        messages.error(request, "Solo el administrador puede exportar el inventario.")
        return redirect("productos:inventario")
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=40,
        leftMargin=40,
        topMargin=50,
        bottomMargin=40,
    )
    elements = []
    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        "CustomTitle",
        parent=styles["Heading1"],
        fontSize=22,
        textColor=colors.HexColor("#FF7A00"),
        spaceAfter=4,
        alignment=1,
    )
    subtitle_style = ParagraphStyle(
        "Subtitle",
        parent=styles["Normal"],
        fontSize=10,
        textColor=colors.gray,
        alignment=1,
        spaceAfter=20,
    )

    elements.append(Paragraph("MICHUZITO", title_style))
    elements.append(Paragraph("Reporte de Inventario", subtitle_style))
    now = datetime.now()
    elements.append(
        Paragraph(
            f"Generado: {now.strftime('%d/%m/%Y %H:%M')} | Usuario: {request.user.username}",
            subtitle_style,
        )
    )
    elements.append(Spacer(1, 12))

    qs = (
        Producto.objects.filter(estado="activo")
        .select_related("categoria")
        .order_by("categoria__nombre", "nombre")
    )

    data = [["#", "Producto", "Categoría", "Precio", "Stock", "Subtotal", "Estado"]]
    total_valor = Decimal("0.00")
    total_und = 0

    for i, p in enumerate(qs, 1):
        subtotal = p.precio * p.stock
        total_valor += subtotal
        total_und += p.stock
        if p.stock == 0:
            estado = "Agotado"
        elif p.stock <= getattr(settings, "STOCK_MINIMO_ALERTA", 5):
            estado = "Bajo"
        else:
            estado = "Stock"
        data.append(
            [
                str(i),
                p.nombre,
                p.categoria.nombre,
                f"${p.precio:,.2f}",
                str(p.stock),
                f"${subtotal:,.2f}",
                estado,
            ]
        )

    data.append(["", "", "", "", "", "", ""])
    data.append(
        [
            "",
            "TOTALES",
            "",
            "",
            str(total_und),
            f"${total_valor:,.2f}",
            f"{len(qs)} productos",
        ]
    )

    table = Table(data, colWidths=[30, 150, 90, 70, 50, 80, 60])
    style = TableStyle(
        [
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#FF7A00")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTSIZE", (0, 0), (-1, 0), 10),
            ("FONTSIZE", (0, 1), (-1, -2), 8),
            ("FONTSIZE", (0, -1), (-1, -1), 10),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTNAME", (0, -1), (-1, -1), "Helvetica-Bold"),
            ("BACKGROUND", (0, -1), (-1, -1), colors.HexColor("#FF7A00")),
            ("TEXTCOLOR", (0, -1), (-1, -1), colors.white),
            ("ALIGN", (3, 1), (-2, -1), "RIGHT"),
            ("ALIGN", (4, 1), (4, -1), "CENTER"),
            ("ALIGN", (0, 0), (0, -1), "CENTER"),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
            ("ROWBACKGROUNDS", (0, 1), (-1, -2), [colors.white, colors.HexColor("#FFF5EB")]),
        ]
    )
    table.setStyle(style)
    elements.append(table)

    info_style = ParagraphStyle(
        "Info", parent=styles["Normal"], fontSize=8, textColor=colors.gray
    )
    elements.append(Spacer(1, 20))
    elements.append(
        Paragraph(
            f"Resumen: {len(qs)} productos activos | {total_und} unidades en total | "
            f"Valor del inventario: ${total_valor:,.2f}",
            info_style,
        )
    )

    doc.build(elements)
    buffer.seek(0)
    filename = f"inventario_{now.strftime('%Y%m%d_%H%M')}.pdf"
    response = HttpResponse(buffer, content_type="application/pdf")
    response["Content-Disposition"] = f'attachment; filename="{filename}"'
    return response


# ─── Dashboard ─────────────────────────────────────────────────────────────────

class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = "productos/dashboard.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        umbral = getattr(settings, "STOCK_MINIMO_ALERTA", 5)
        total = Producto.objects.count()
        activos = Producto.objects.filter(estado="activo").count()
        agotados = Producto.objects.filter(
            disponibilidad=False, estado="activo"
        ).count()
        bajo_stock = Producto.objects.filter(
            stock__gt=0, stock__lte=umbral, estado="activo"
        ).count()

        categoria_counts = (
            Categoria.objects.filter(estado=True, productos__estado="activo")
            .annotate(total_productos=Count("productos"))
            .order_by("-total_productos")
        )
        categoria_mas_usada = categoria_counts.first()

        ultimos_productos = Producto.objects.filter(estado="activo").select_related(
            "categoria"
        )[:5]

        auditorias_recientes = Auditoria.objects.select_related("usuario", "producto")[
            :10
        ]

        qs = Producto.objects.filter(estado="activo")
        total_valor_inventario = sum(p.stock * p.precio for p in qs)

        context.update(
            {
                "total_productos": total,
                "productos_activos": activos,
                "productos_agotados": agotados,
                "productos_bajo_stock": bajo_stock,
                "categoria_mas_usada": categoria_mas_usada,
                "ultimos_productos": ultimos_productos,
                "auditorias_recientes": auditorias_recientes,
                "valor_total_inventario": total_valor_inventario,
            }
        )
        return context


# ─── CRUD Categorías ──────────────────────────────────────────────────────────

class CategoriaListView(RoleRequiredMixin, ListView):
    allowed_roles = ["Admin"]
    model = Categoria
    template_name = "productos/categoria_list.html"
    context_object_name = "categorias"

    def get_queryset(self):
        return Categoria.objects.all().order_by("nombre")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        for c in context["categorias"]:
            c.total_productos = Producto.objects.filter(categoria=c, estado="activo").count()
        return context


class CategoriaCreateView(RoleRequiredMixin, CreateView):
    allowed_roles = ["Admin"]
    model = Categoria
    form_class = CategoriaForm
    template_name = "productos/categoria_form.html"
    success_url = reverse_lazy("productos:categoria_list")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["titulo"] = "Crear Categoría"
        return context


class CategoriaUpdateView(RoleRequiredMixin, UpdateView):
    allowed_roles = ["Admin"]
    model = Categoria
    form_class = CategoriaForm
    template_name = "productos/categoria_form.html"
    success_url = reverse_lazy("productos:categoria_list")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["titulo"] = "Editar Categoría"
        return context


class CategoriaDeleteView(RoleRequiredMixin, DeleteView):
    allowed_roles = ["Admin"]
    model = Categoria
    template_name = "productos/categoria_confirm_delete.html"
    success_url = reverse_lazy("productos:categoria_list")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["total_productos"] = Producto.objects.filter(
            categoria=self.object, estado="activo"
        ).count()
        return context


# ─── Registro ──────────────────────────────────────────────────────────────────

def signup_view(request):
    if request.user.is_authenticated:
        return redirect(role_redirect(request.user))
    if request.method == "POST":
        form = RegistroForm(request.POST)
        if form.is_valid():
            user = form.save()
            user.groups.add(Group.objects.get(name="Cajero"))
            login(request, user)
            messages.success(request, f"Bienvenido {user.username}")
            return redirect("productos:list")
    else:
        form = RegistroForm()
    return render(request, "productos/register.html", {"form": form})


# ─── Auth ──────────────────────────────────────────────────────────────────────

def login_view(request):
    if request.user.is_authenticated:
        return redirect(role_redirect(request.user))
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f"Bienvenido {user.username}")
            return redirect(role_redirect(user))
    else:
        form = AuthenticationForm()
    return render(request, "productos/login.html", {"form": form})


def logout_view(request):
    logout(request)
    return redirect("login")


# ─── API Views ─────────────────────────────────────────────────────────────────

class ProductoPagination(PageNumberPagination):
    page_size = 12
    page_size_query_param = "page_size"
    max_page_size = 100


class ProductoViewSet(viewsets.ModelViewSet):
    queryset = Producto.objects.filter(estado="activo").select_related("categoria")
    pagination_class = ProductoPagination
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["nombre", "descripcion", "ingredientes", "categoria__nombre"]
    ordering_fields = ["precio", "fecha_creacion", "nombre", "stock"]

    def get_serializer_class(self):
        if self.action == "list":
            return ProductoListSerializer
        return ProductoSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        disponible = self.request.query_params.get("disponible")
        if disponible is not None:
            queryset = queryset.filter(disponibilidad=disponible.lower() == "true")
        categoria = self.request.query_params.get("categoria")
        if categoria:
            queryset = queryset.filter(categoria__nombre__iexact=categoria)
        return queryset

    def perform_create(self, serializer):
        producto = serializer.save()
        Auditoria.objects.create(
            usuario=self.request.user,
            accion="creacion",
            producto=producto,
            detalle=f"Producto creado vía API: {producto.nombre}",
            ip=self.request.META.get("REMOTE_ADDR"),
        )

    def perform_update(self, serializer):
        old = Producto.objects.get(pk=self.get_object().pk)
        producto = serializer.save()
        if old.precio != producto.precio:
            Auditoria.objects.create(
                usuario=self.request.user,
                accion="cambio_precio",
                producto=producto,
                detalle=f"Precio vía API: {old.precio} → {producto.precio}",
                ip=self.request.META.get("REMOTE_ADDR"),
            )
        if old.stock != producto.stock:
            Auditoria.objects.create(
                usuario=self.request.user,
                accion="cambio_stock",
                producto=producto,
                detalle=f"Stock vía API: {old.stock} → {producto.stock}",
                ip=self.request.META.get("REMOTE_ADDR"),
            )
        Auditoria.objects.create(
            usuario=self.request.user,
            accion="actualizacion",
            producto=producto,
            detalle=f"Producto actualizado vía API: {producto.nombre}",
            ip=self.request.META.get("REMOTE_ADDR"),
        )

    def perform_destroy(self, instance):
        instance.estado = "inactivo"
        instance.save()
        Auditoria.objects.create(
            usuario=self.request.user,
            accion="eliminacion",
            producto=instance,
            detalle=f"Producto eliminado (lógico) vía API: {instance.nombre}",
            ip=self.request.META.get("REMOTE_ADDR"),
        )


class CategoriaViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Categoria.objects.filter(estado=True)
    serializer_class = CategoriaSerializer
    pagination_class = None
