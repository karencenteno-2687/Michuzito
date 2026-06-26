from django.conf import settings
from .models import Producto


def stock_alert_count(request):
    if request.user.is_authenticated:
        umbral = getattr(settings, "STOCK_MINIMO_ALERTA", 5)
        agotados = Producto.objects.filter(estado="activo", stock=0).count()
        bajo_stock = Producto.objects.filter(
            estado="activo", stock__gt=0, stock__lte=umbral
        ).count()
        return {"stock_criticos": agotados + bajo_stock}
    return {"stock_criticos": 0}
