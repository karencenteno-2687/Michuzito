from decimal import Decimal
from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
import random

from productos.models import Producto
from cocina.models import Orden, DetalleOrden


class Command(BaseCommand):
    help = "Crea órdenes demo para la cocina"

    def handle(self, *args, **options):
        user = User.objects.filter(is_superuser=True).first()
        if not user:
            user = User.objects.create_superuser("cocina", "cocina@test.com", "cocina123")

        productos = list(Producto.objects.filter(estado="activo"))
        if not productos:
            self.stdout.write(self.style.WARNING("No hay productos. Ejecuta seed_productos primero."))
            return

        clientes = ["Carlos", "María", "Pedro", "Ana", "Luis", "Sofía", "Juan", "Valentina"]
        mesas = [1, 2, 3, 4, 5, 6, 7, 8]
        notas = ["Sin cebolla", "Bien cocido", "Extra queso", "Salsa aparte", "", ""]

        ordenes_data = [
            {"estado": "pendiente", "delta_hours": 0.1},
            {"estado": "pendiente", "delta_hours": 0.3},
            {"estado": "preparacion", "delta_hours": 0.5},
            {"estado": "preparacion", "delta_hours": 0.8},
            {"estado": "preparacion", "delta_hours": 1.2},
            {"estado": "listo", "delta_hours": 1.5},
            {"estado": "listo", "delta_hours": 2.0},
            {"estado": "entregado", "delta_hours": 3.0},
            {"estado": "entregado", "delta_hours": 4.0},
            {"estado": "entregado", "delta_hours": 5.0},
        ]

        created = 0
        for odata in ordenes_data:
            cliente = random.choice(clientes)
            mesa = random.choice(mesas)
            ahora = timezone.now()
            creada = ahora - timedelta(hours=odata["delta_hours"])

            orden = Orden(
                cliente=cliente,
                mesa=mesa,
                estado=odata["estado"],
                nota=random.choice(notas),
                usuario=user,
            )
            orden.save()
            orden.creada = creada
            orden.save()

            num_items = random.randint(1, 4)
            total = Decimal("0.00")
            seleccionados = random.sample(productos, min(num_items, len(productos)))
            for prod in seleccionados:
                cant = random.randint(1, 3)
                DetalleOrden.objects.create(
                    orden=orden,
                    producto=prod,
                    cantidad=cant,
                    precio_unitario=prod.precio,
                    nota=random.choice(notas) if random.random() < 0.3 else "",
                )
                total += prod.precio * cant

            orden.total = total
            orden.save()
            created += 1

        self.stdout.write(self.style.SUCCESS(f"{created} órdenes demo creadas."))
