from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.core.management.base import BaseCommand
from productos.models import Producto, Categoria, Auditoria
from cocina.models import Orden, DetalleOrden


class Command(BaseCommand):
    help = "Crea los grupos/roles del sistema con sus permisos"

    ROLES = {
        "Admin": {
            "descripcion": "Acceso total al sistema",
            "modelos": [Producto, Categoria, Auditoria, Orden, DetalleOrden],
            "permisos": ["add", "change", "delete", "view"],
        },
        "Cocina": {
            "descripcion": "Acceso a cocina y ver productos",
            "modelos": [Producto, Orden, DetalleOrden],
            "permisos": ["view", "change"],
        },
        "Cajero": {
            "descripcion": "Crear órdenes, ver productos e inventario",
            "modelos": [Producto, Orden, DetalleOrden, Categoria],
            "permisos": ["view", "add", "change"],
        },
    }

    def handle(self, *args, **options):
        for role_name, role_data in self.ROLES.items():
            group, created = Group.objects.get_or_create(name=role_name)
            perms = []
            for modelo in role_data["modelos"]:
                ct = ContentType.objects.get_for_model(modelo)
                for accion in role_data["permisos"]:
                    codename = f"{accion}_{modelo._meta.model_name}"
                    try:
                        p = Permission.objects.get(codename=codename, content_type=ct)
                        perms.append(p)
                    except Permission.DoesNotExist:
                        self.stdout.write(
                            self.style.WARNING(f"Permiso '{codename}' no encontrado")
                        )
            group.permissions.set(perms)
            group.save()
            status = "creado" if created else "actualizado"
            self.stdout.write(
                self.style.SUCCESS(
                    f"[{status.upper()}] {role_name} ({len(perms)} permisos)"
                )
            )

        self.stdout.write(self.style.SUCCESS("\nRoles listos."))
