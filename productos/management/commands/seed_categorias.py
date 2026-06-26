from django.core.management.base import BaseCommand
from productos.models import Categoria


class Command(BaseCommand):
    help = "Crea las categorías iniciales del sistema"

    CATEGORIAS = [
        {"nombre": "Salchipapas", "descripcion": "Salchipapas y papas preparadas"},
        {"nombre": "Chuzos", "descripcion": "Chuzos de carne y pollo"},
        {"nombre": "Costillas", "descripcion": "Costillas de cerdo y res"},
        {"nombre": "Hamburguesas", "descripcion": "Hamburguesas artesanales"},
        {"nombre": "Perros Calientes", "descripcion": "Perros calientes especiales"},
        {"nombre": "Alitas", "descripcion": "Alitas de pollo"},
        {"nombre": "Bebidas", "descripcion": "Bebidas y refrescos"},
    ]

    def handle(self, *args, **options):
        created = 0
        for cat in self.CATEGORIAS:
            _, was_created = Categoria.objects.get_or_create(
                nombre=cat["nombre"],
                defaults={"descripcion": cat["descripcion"]},
            )
            if was_created:
                created += 1
                self.stdout.write(self.style.SUCCESS(f"Categoría creada: {cat['nombre']}"))
            else:
                self.stdout.write(f"Categoría ya existe: {cat['nombre']}")
        self.stdout.write(self.style.SUCCESS(f"\nTotal categorías creadas: {created}"))
