from django.contrib import admin
from .models import Orden, DetalleOrden


class DetalleOrdenInline(admin.TabularInline):
    model = DetalleOrden
    extra = 1


@admin.register(Orden)
class OrdenAdmin(admin.ModelAdmin):
    list_display = ["id", "cliente", "mesa", "estado", "total", "creada", "usuario"]
    list_filter = ["estado", "creada"]
    inlines = [DetalleOrdenInline]
