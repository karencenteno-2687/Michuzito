from django.urls import path, include
from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()
router.register(r"productos", views.ProductoViewSet)
router.register(r"categorias", views.CategoriaViewSet)

app_name = "productos"

urlpatterns = [
    # CRUD Productos
    path("", views.ProductoListView.as_view(), name="list"),
    path("crear/", views.ProductoCreateView.as_view(), name="create"),
    path("<int:pk>/editar/", views.ProductoUpdateView.as_view(), name="update"),
    path("<int:pk>/eliminar/", views.ProductoDeleteView.as_view(), name="delete"),
    path("<int:pk>/", views.ProductoDetailView.as_view(), name="detail"),
    # HTMX Productos
    path("htmx/buscar/", views.htmx_search, name="htmx_search"),
    path("htmx/filtrar/", views.htmx_filter, name="htmx_filter"),
    path(
        "htmx/producto/<int:pk>/",
        views.htmx_product_detail,
        name="htmx_product_detail",
    ),
    # Stock Alerts
    path("stock/alertas/", views.StockAlertView.as_view(), name="stock_alertas"),
    path(
        "htmx/stock-filtrar/",
        views.htmx_stock_filter,
        name="htmx_stock_filter",
    ),
    # Inventario
    path("inventario/", views.InventoryView.as_view(), name="inventario"),
    path(
        "inventario/exportar/pdf/",
        views.exportar_inventario_pdf,
        name="exportar_pdf",
    ),
    path(
        "htmx/inventario-filtrar/",
        views.htmx_inventario_filter,
        name="htmx_inventario_filter",
    ),
    # Dashboard
    path("dashboard/", views.DashboardView.as_view(), name="dashboard"),
    # CRUD Categorías
    path("categorias/", views.CategoriaListView.as_view(), name="categoria_list"),
    path(
        "categorias/crear/",
        views.CategoriaCreateView.as_view(),
        name="categoria_create",
    ),
    path(
        "categorias/<int:pk>/editar/",
        views.CategoriaUpdateView.as_view(),
        name="categoria_update",
    ),
    path(
        "categorias/<int:pk>/eliminar/",
        views.CategoriaDeleteView.as_view(),
        name="categoria_delete",
    ),
    # Registro
    path("registro/", views.signup_view, name="signup"),
    # API
    path("api/", include(router.urls)),
]
