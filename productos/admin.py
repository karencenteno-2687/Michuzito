from django.contrib import admin
from .models import Categoria, Producto, Auditoria


@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ["nombre", "estado", "fecha_creacion"]
    search_fields = ["nombre"]
    list_filter = ["estado"]


@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = [
        "nombre",
        "categoria",
        "precio",
        "stock",
        "disponibilidad",
        "estado",
    ]
    list_filter = ["categoria", "disponibilidad", "estado"]
    search_fields = ["nombre", "descripcion", "ingredientes"]
    readonly_fields = ["fecha_creacion", "fecha_actualizacion"]


@admin.register(Auditoria)
class AuditoriaAdmin(admin.ModelAdmin):
    list_display = ["usuario", "accion", "producto", "fecha", "hora"]
    list_filter = ["accion", "fecha"]
    readonly_fields = ["usuario", "accion", "producto", "detalle", "fecha", "hora", "ip"]
