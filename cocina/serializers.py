from rest_framework import serializers
from .models import Orden, DetalleOrden


class DetalleOrdenSerializer(serializers.ModelSerializer):
    producto_nombre = serializers.CharField(source="producto.nombre", read_only=True)

    class Meta:
        model = DetalleOrden
        fields = [
            "id",
            "producto",
            "producto_nombre",
            "cantidad",
            "precio_unitario",
            "subtotal",
            "nota",
        ]


class OrdenSerializer(serializers.ModelSerializer):
    detalles = DetalleOrdenSerializer(many=True, read_only=True)
    tiempo_transcurrido = serializers.SerializerMethodField()

    class Meta:
        model = Orden
        fields = [
            "id",
            "cliente",
            "mesa",
            "estado",
            "total",
            "nota",
            "detalles",
            "creada",
            "actualizada",
            "usuario",
            "tiempo_transcurrido",
        ]

    def get_tiempo_transcurrido(self, obj):
        from django.utils import timezone
        delta = timezone.now() - obj.creada
        minutos = int(delta.total_seconds() // 60)
        if minutos < 1:
            return "Ahora"
        elif minutos < 60:
            return f"{minutos} min"
        else:
            horas = minutos // 60
            mins = minutos % 60
            return f"{horas}h {mins}min"
