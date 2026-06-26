from rest_framework import serializers
from .models import Producto, Categoria
from .validators import validate_image_file


class CategoriaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Categoria
        fields = ["id", "nombre", "descripcion", "estado", "fecha_creacion"]


class ProductoListSerializer(serializers.ModelSerializer):
    categoria_nombre = serializers.CharField(source="categoria.nombre", read_only=True)

    class Meta:
        model = Producto
        fields = [
            "id",
            "nombre",
            "descripcion",
            "categoria",
            "categoria_nombre",
            "precio",
            "imagen",
            "ingredientes",
            "tiempo_preparacion",
            "disponibilidad",
            "stock",
            "estado",
            "fecha_creacion",
        ]


class ProductoSerializer(serializers.ModelSerializer):
    categoria_nombre = serializers.CharField(source="categoria.nombre", read_only=True)

    class Meta:
        model = Producto
        fields = [
            "id",
            "nombre",
            "descripcion",
            "categoria",
            "categoria_nombre",
            "precio",
            "imagen",
            "ingredientes",
            "tiempo_preparacion",
            "disponibilidad",
            "stock",
            "estado",
            "fecha_creacion",
            "fecha_actualizacion",
        ]
        read_only_fields = ["disponibilidad", "fecha_creacion", "fecha_actualizacion"]

    def validate_nombre(self, value):
        from .validators import validate_special_chars

        validate_special_chars(value)
        import bleach

        return bleach.clean(value.strip())

    def validate_imagen(self, value):
        if value:
            validate_image_file(value)
        return value
