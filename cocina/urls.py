from django.urls import path, include
from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()
router.register(r"ordenes", views.OrdenViewSet)
router.register(r"cocina-ordenes", views.CocinaOrdenViewSet, basename="cocina-orden")

app_name = "cocina"

urlpatterns = [
    # Cocina Dashboard
    path("", views.CocinaDashboardView.as_view(), name="dashboard"),
    # POS
    path("pos/", views.POSCreateOrdenView.as_view(), name="pos"),
    path("pos/crear-orden/", views.crear_orden, name="crear_orden"),
    # Cambiar estado
    path(
        "orden/<int:pk>/cambiar-estado/",
        views.cambiar_estado_orden,
        name="cambiar_estado",
    ),
    # HTMX
    path(
        "htmx/ordenes/",
        views.htmx_cocina_ordenes,
        name="htmx_ordenes",
    ),
    path(
        "htmx/productos/",
        views.htmx_pos_productos,
        name="htmx_pos_productos",
    ),
    # API
    path(
        "api/ordenes-activas/",
        views.ordenes_activas_api,
        name="ordenes_activas_api",
    ),
    path("api/", include(router.urls)),
]
