from io import BytesIO
import random
from decimal import Decimal

from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand
from PIL import Image, ImageDraw, ImageFont

from productos.models import Categoria, Producto


def generar_placeholder(nombre, categoria):
    img = Image.new("RGB", (400, 300), color=(18, 18, 18))
    draw = ImageDraw.Draw(img)
    try:
        font = ImageFont.truetype("arial.ttf", 36)
        font_small = ImageFont.truetype("arial.ttf", 18)
    except Exception:
        font = ImageFont.load_default()
        font_small = ImageFont.load_default()

    bbox = draw.textbbox((0, 0), nombre[:12], font=font)
    tw = bbox[2] - bbox[0]
    th = bbox[3] - bbox[1]
    x = (400 - tw) // 2
    y = (300 - th) // 2 - 15
    draw.text((x, y), nombre[:12], fill=(255, 122, 0), font=font)
    draw.text(
        (x, y + 40),
        categoria,
        fill=(255, 255, 255),
        font=font_small,
    )

    buffer = BytesIO()
    img.save(buffer, format="WEBP", quality=85)
    return ContentFile(buffer.getvalue(), f"{nombre.lower().replace(' ', '_')}.webp")


PRODUCTOS = [
    # Salchipapas
    {"nombre": "Salchipapa Clásica", "precio": 8000, "stock": 50, "tiempo": 10, "categoria": "Salchipapas", "ingredientes": "Salchicha, Papas, Salsa de tomate, Mayonesa, Mostaza"},
    {"nombre": "Salchipapa Especial", "precio": 12000, "stock": 30, "tiempo": 12, "categoria": "Salchipapas", "ingredientes": "Salchicha, Papas, Queso derretido, Salsa de la casa, Tocineta"},
    {"nombre": "Salchipapa Ranchera", "precio": 15000, "stock": 0, "tiempo": 15, "categoria": "Salchipapas", "ingredientes": "Salchicha, Papas, Huevo, Chorizo, Plátano maduro, Salsa BBQ"},
    {"nombre": "Salchipapa Suprema", "precio": 18000, "stock": 15, "tiempo": 18, "categoria": "Salchipapas", "ingredientes": "Salchicha, Papas, Pollo desmechado, Queso, Tocineta, Salsa de la casa"},
    # Chuzos
    {"nombre": "Chuzo de Pollo", "precio": 10000, "stock": 40, "tiempo": 8, "categoria": "Chuzos", "ingredientes": "Pollo marinado, Cebolla, Tomate, Lechuga, Salsa de ajo"},
    {"nombre": "Chuzo de Res", "precio": 12000, "stock": 25, "tiempo": 10, "categoria": "Chuzos", "ingredientes": "Carne de res, Cebolla, Tomate, Lechuga, Salsa BBQ"},
    {"nombre": "Chuzo Mixto", "precio": 15000, "stock": 3, "tiempo": 12, "categoria": "Chuzos", "ingredientes": "Pollo y Res, Cebolla, Tomate, Lechuga, Salsa de la casa"},
    # Costillas
    {"nombre": "Costillas BBQ", "precio": 25000, "stock": 10, "tiempo": 25, "categoria": "Costillas", "ingredientes": "Costillas de cerdo, Salsa BBQ, Papas, Ensalada"},
    {"nombre": "Costillas BBQ Media", "precio": 15000, "stock": 8, "tiempo": 20, "categoria": "Costillas", "ingredientes": "Media porción costillas, Salsa BBQ, Papas"},
    {"nombre": "Costillas BBQ Full", "precio": 35000, "stock": 5, "tiempo": 30, "categoria": "Costillas", "ingredientes": "Costillas de cerdo, Salsa BBQ, Papas, Ensalada, Maduro"},
    # Hamburguesas
    {"nombre": "Hamburguesa Sencilla", "precio": 10000, "stock": 45, "tiempo": 8, "categoria": "Hamburguesas", "ingredientes": "Carne 150gr, Lechuga, Tomate, Cebolla, Queso"},
    {"nombre": "Hamburguesa Especial", "precio": 15000, "stock": 30, "tiempo": 12, "categoria": "Hamburguesas", "ingredientes": "Carne 200gr, Lechuga, Tomate, Queso, Tocineta, Huevo"},
    {"nombre": "Hamburguesa Doble Carne", "precio": 22000, "stock": 1, "tiempo": 15, "categoria": "Hamburguesas", "ingredientes": "Doble carne 300gr, Lechuga, Tomate, Queso, Tocineta, Cebolla caramelizada"},
    {"nombre": "Hamburguesa BBQ", "precio": 18000, "stock": 20, "tiempo": 12, "categoria": "Hamburguesas", "ingredientes": "Carne 200gr, Queso cheddar, Tocineta, Aros de cebolla, Salsa BBQ"},
    # Perros Calientes
    {"nombre": "Perro Caliente Sencillo", "precio": 7000, "stock": 60, "tiempo": 5, "categoria": "Perros Calientes", "ingredientes": "Salchicha, Pan, Salsa de tomate, Mayonesa, Mostaza, Cebolla"},
    {"nombre": "Perro Caliente Especial", "precio": 10000, "stock": 35, "tiempo": 8, "categoria": "Perros Calientes", "ingredientes": "Salchicha, Pan, Queso, Tocineta, Salsa de la casa, Cebolla, Piña"},
    {"nombre": "Perro Caliente Supremo", "precio": 14000, "stock": 0, "tiempo": 10, "categoria": "Perros Calientes", "ingredientes": "Salchicha, Pan, Queso, Tocineta, Huevo, Piña, Salsa BBQ, Papa ripio"},
    # Alitas
    {"nombre": "Alitas 6 Und", "precio": 12000, "stock": 25, "tiempo": 15, "categoria": "Alitas", "ingredientes": "6 Alitas de pollo, Salsa BBQ o Buffalo, Papas"},
    {"nombre": "Alitas 12 Und", "precio": 22000, "stock": 12, "tiempo": 25, "categoria": "Alitas", "ingredientes": "12 Alitas de pollo, Salsa BBQ o Buffalo, Papas"},
    {"nombre": "Alitas BBQ", "precio": 15000, "stock": 20, "tiempo": 18, "categoria": "Alitas", "ingredientes": "Alitas bañadas en salsa BBQ, Papas, Ensalada"},
    {"nombre": "Alitas Picantes", "precio": 15000, "stock": 18, "tiempo": 18, "categoria": "Alitas", "ingredientes": "Alitas con salsa Buffalo, Papas, Aderezo ranch"},
    # Bebidas
    {"nombre": "Gaseosa Personal", "precio": 3000, "stock": 100, "tiempo": 1, "categoria": "Bebidas", "ingredientes": "Gaseosa 350ml"},
    {"nombre": "Gaseosa 1.5L", "precio": 6000, "stock": 50, "tiempo": 1, "categoria": "Bebidas", "ingredientes": "Gaseosa 1.5 litros"},
    {"nombre": "Agua sin Gas", "precio": 2000, "stock": 80, "tiempo": 1, "categoria": "Bebidas", "ingredientes": "Agua 500ml"},
    {"nombre": "Jugo Natural", "precio": 5000, "stock": 0, "tiempo": 5, "categoria": "Bebidas", "ingredientes": "Jugo natural de fruta (mango, lulo, maracuyá)"},
]


class Command(BaseCommand):
    help = "Crea productos demo para todas las categorías"

    def handle(self, *args, **options):
        created = 0
        for data in PRODUCTOS:
            try:
                categoria = Categoria.objects.get(nombre=data["categoria"])
            except Categoria.DoesNotExist:
                self.stdout.write(
                    self.style.WARNING(
                        f"Categoría '{data['categoria']}' no encontrada. Saltando '{data['nombre']}'."
                    )
                )
                continue

            if Producto.objects.filter(nombre=data["nombre"]).exists():
                self.stdout.write(f"Producto ya existe: {data['nombre']}")
                continue

            producto = Producto(
                nombre=data["nombre"],
                descripcion=f"{data['nombre']} de {data['categoria']}. Ingredientes: {data['ingredientes']}",
                categoria=categoria,
                precio=Decimal(str(data["precio"])),
                ingredientes=data["ingredientes"],
                tiempo_preparacion=data["tiempo"],
                stock=data["stock"],
                estado="activo",
            )
            placeholder = generar_placeholder(data["nombre"], data["categoria"])
            producto.imagen.save(
                f"{data['nombre'].lower().replace(' ', '_')}.webp",
                placeholder,
                save=False,
            )
            producto.save()
            created += 1
            ok = "+" if data["stock"] > 0 else "-"
            self.stdout.write(
                self.style.SUCCESS(
                    f"[{ok}] {data['nombre']} (${data['precio']}) - Stock: {data['stock']}"
                )
            )

        self.stdout.write(
            self.style.SUCCESS(f"\nTotal productos creados: {created}")
        )
