from django.db import models
from django.contrib.auth.models import User
from productos.models import Producto


class Orden(models.Model):
    ESTADOS = [
        ("pendiente", "Pendiente"),
        ("preparacion", "En Preparación"),
        ("listo", "Listo"),
        ("entregado", "Entregado"),
    ]

    cliente = models.CharField(max_length=100, blank=True, null=True)
    mesa = models.PositiveIntegerField(blank=True, null=True)
    estado = models.CharField(max_length=20, choices=ESTADOS, default="pendiente")
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    nota = models.TextField(blank=True, null=True)
    creada = models.DateTimeField(auto_now_add=True)
    actualizada = models.DateTimeField(auto_now=True)
    usuario = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True
    )

    class Meta:
        verbose_name = "Orden"
        verbose_name_plural = "Órdenes"
        ordering = ["-creada"]

    def __str__(self):
        return f"Orden #{self.id} - {self.get_estado_display()}"


class DetalleOrden(models.Model):
    orden = models.ForeignKey(
        Orden, on_delete=models.CASCADE, related_name="detalles"
    )
    producto = models.ForeignKey(Producto, on_delete=models.PROTECT)
    cantidad = models.PositiveIntegerField(default=1)
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2)
    nota = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        verbose_name = "Detalle de Orden"
        verbose_name_plural = "Detalles de Órdenes"

    def __str__(self):
        return f"{self.cantidad}x {self.producto.nombre}"

    @property
    def subtotal(self):
        return self.cantidad * self.precio_unitario
