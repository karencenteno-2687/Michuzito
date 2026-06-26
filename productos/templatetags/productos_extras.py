from django import template
from django.conf import settings

register = template.Library()


@register.filter
def formato_precio(value):
    try:
        return f"${value:,.2f}"
    except (ValueError, TypeError):
        return "$0.00"


@register.filter
def estado_stock(value):
    umbral = getattr(settings, "STOCK_MINIMO_ALERTA", 5)
    if value == 0:
        return "agotado"
    elif value <= umbral:
        return "bajo"
    return "normal"


@register.simple_tag
def stock_badge(value):
    umbral = getattr(settings, "STOCK_MINIMO_ALERTA", 5)
    if value == 0:
        return "bg-danger"
    elif value <= umbral:
        return "bg-warning text-dark"
    return "bg-success"
