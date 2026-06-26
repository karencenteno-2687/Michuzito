from django.db import models
from django.core.validators import RegexValidator, MinValueValidator, MaxValueValidator
from django.contrib.auth.models import User


class Categoria(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    descripcion = models.TextField(blank=True, null=True)
    estado = models.BooleanField(default=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Categoría"
        verbose_name_plural = "Categorías"
        ordering = ["nombre"]

    def __str__(self):
        return self.nombre


class Producto(models.Model):
    ESTADO_CHOICES = [
        ("activo", "Activo"),
        ("inactivo", "Inactivo"),
    ]

    nombre_validator = RegexValidator(
        regex=r"^[a-zA-ZáéíóúÁÉÍÓÚñÑ0-9\s]{3,100}$",
        message="El nombre solo permite letras, números y espacios (3-100 caracteres).",
    )

    precio_validator = RegexValidator(
        regex=r"^\d+(\.\d{1,2})?$",
        message="Ingrese un precio válido (ej: 15000 o 15000.00).",
    )

    stock_validator = RegexValidator(
        regex=r"^[0-9]+$",
        message="El stock solo permite números enteros positivos.",
    )

    nombre = models.CharField(
        max_length=100,
        validators=[nombre_validator],
        db_index=True,
    )
    descripcion = models.TextField(blank=True, null=True)
    categoria = models.ForeignKey(
        Categoria,
        on_delete=models.PROTECT,
        related_name="productos",
    )
    precio = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[precio_validator, MinValueValidator(0.01)],
    )
    imagen = models.ImageField(
        upload_to="productos/",
        blank=True,
        null=True,
    )
    ingredientes = models.TextField(blank=True, null=True, help_text="Separar por comas")
    tiempo_preparacion = models.PositiveIntegerField(
        help_text="Tiempo en minutos",
        blank=True,
        null=True,
    )
    disponibilidad = models.BooleanField(default=True)
    stock = models.PositiveIntegerField(
        default=0,
        validators=[stock_validator],
    )
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    estado = models.CharField(max_length=10, choices=ESTADO_CHOICES, default="activo")

    class Meta:
        verbose_name = "Producto"
        verbose_name_plural = "Productos"
        ordering = ["-fecha_creacion"]
        indexes = [
            models.Index(fields=["nombre"]),
            models.Index(fields=["categoria"]),
            models.Index(fields=["estado"]),
            models.Index(fields=["disponibilidad"]),
        ]

    def __str__(self):
        return self.nombre

    def save(self, *args, **kwargs):
        if self.stock == 0:
            self.disponibilidad = False
        elif self.stock > 0:
            self.disponibilidad = True
        super().save(*args, **kwargs)


class Auditoria(models.Model):
    ACCIONES_CHOICES = [
        ("creacion", "Creación"),
        ("actualizacion", "Actualización"),
        ("eliminacion", "Eliminación"),
        ("cambio_precio", "Cambio de Precio"),
        ("cambio_stock", "Cambio de Stock"),
    ]

    usuario = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    accion = models.CharField(max_length=20, choices=ACCIONES_CHOICES)
    producto = models.ForeignKey(
        Producto, on_delete=models.SET_NULL, null=True, blank=True
    )
    detalle = models.TextField(blank=True, null=True)
    fecha = models.DateField(auto_now_add=True)
    hora = models.TimeField(auto_now_add=True)
    ip = models.GenericIPAddressField(blank=True, null=True)

    class Meta:
        verbose_name = "Auditoría"
        verbose_name_plural = "Auditorías"
        ordering = ["-fecha", "-hora"]

    def __str__(self):
        return f"{self.usuario} - {self.accion} - {self.fecha}"
