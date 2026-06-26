# 🍔 Michusito — Sistema de Gestión de Comidas Rápidas

Sistema web completo para la gestión de restaurantes de comidas rápidas con módulos de **productos**, **inventario**, **cocina** (tablero Kanban) y **punto de venta (POS)**.

---

## ✨ Tecnologías

| Tecnología | Versión | Propósito |
|------------|---------|-----------|
| Python | 3.10+ | Lenguaje principal |
| Django | 4.2.30 | Framework web |
| Django REST Framework | 3.x | API REST |
| HTMX | 2.x | Interacciones dinámicas |
| Bootstrap 5 | 5.3.x | UI / CSS framework |
| ReportLab | 4.x | Generación de PDF |
| Pillow | 10.x | Procesamiento de imágenes |
| bleach | 6.x | Sanitización HTML |
| python-decouple | 3.x | Variables de entorno |
| SQLite / MySQL | — | Bases de datos |

---

## 📋 Estructura del Proyecto

```
MiChusito/
├── config/                  # Configuración Django
│   ├── settings.py          # Settings (DB, apps, middleware, etc.)
│   ├── urls.py              # URL raíz
│   └── wsgi.py / asgi.py    # Entry points de servidor
├── productos/               # App principal
│   ├── models.py            # Categoria, Producto, Auditoria
│   ├── views.py             # CRUD, HTMX, Dashboard, PDF, API
│   ├── forms.py             # ProductoForm, CategoriaForm, RegistroForm
│   ├── serializers.py       # DRF serializers
│   ├── roles.py             # get_user_role(), RoleRequiredMixin
│   ├── validators.py        # validate_special_chars(), validate_image_file()
│   ├── context_processors.py / context_processors_role.py
│   ├── templatetags/        # formato_precio, estado_stock, stock_badge
│   ├── management/commands/ # seed_categorias, seed_productos, seed_roles
│   ├── templates/productos/ # ~20 templates (list, create, update, etc.)
│   └── static/productos/    # CSS, JS, Bootstrap
├── cocina/                  # App de cocina
│   ├── models.py            # Orden, DetalleOrden
│   ├── views.py             # Kanban dashboard, POS, API
│   ├── serializers.py       # DRF serializers
│   ├── management/commands/ # seed_ordenes
│   ├── templates/cocina/    # dashboard, pos, partials
│   └── static/cocina/       # CSS, JS (auto-refresh polling)
├── media/productos/         # Imágenes subidas
├── staticfiles/             # Archivos estáticos recolectados
├── manage.py                # CLI de Django
├── requirements.txt         # Dependencias
└── Documentacion.docx       # Documentación completa
```

---

## 🚀 Instalación

```bash
# 1. Clonar
git clone https://github.com/tu-usuario/michusito.git
cd michusito

# 2. Entorno virtual
python -m venv venv
venv\Scripts\activate       # Windows
source venv/bin/activate    # Linux/macOS

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. Migraciones
python manage.py migrate

# 5. Superusuario
python manage.py createsuperuser

# 6. Datos semilla
python manage.py seed_categorias
python manage.py seed_productos
python manage.py seed_roles
python manage.py seed_ordenes

# 7. Ejecutar
python manage.py runserver
```

---

## ⚙️ Configuración

Variables de entorno (archivo `.env` en la raíz):

```env
DJANGO_SECRET_KEY=tu_clave_secreta
DJANGO_DEBUG=True
DJANGO_ALLOWED_HOSTS=127.0.0.1,localhost
DB_ENGINE=django.db.backends.sqlite3
DB_NAME=db.sqlite3
DB_USER=
DB_PASSWORD=
DB_HOST=
DB_PORT=
```

Configuraciones clave en `settings.py`:

| Variable | Default | Descripción |
|----------|---------|-------------|
| `STOCK_MINIMO_ALERTA` | `5` | Umbral para alertas de stock bajo |
| `MAX_IMAGE_SIZE` | `5MB` | Tamaño máximo de imágenes |
| `LOGIN_URL` | `/login/` | Redirección para usuarios no autenticados |
| `LANGUAGE_CODE` | `es-co` | Español (Colombia) |
| `TIME_ZONE` | `America/Bogota` | Zona horaria |

---

## 🔐 Roles de Usuario

| Rol | Acceso | Login redirect |
|-----|--------|----------------|
| **Admin** | Todo el sistema (productos, categorías, inventario, cocina, dashboard, PDF) | `productos:list` |
| **Cocina** | Dashboard cocina, POS, ver productos | `cocina:dashboard` |
| **Cajero** | CRUD productos, stock, inventario | `productos:list` |

**Usuarios demo:**
- `admin` / `admin123` — Admin
- `cocina1` / `cocina123` — Cocina
- `cajero1` / `cajero123` — Cajero

---

## 🔒 Seguridad (10 Capas)

1. **Autenticación obligatoria** — LoginRequiredMixin + @login_required en todas las vistas
2. **CSRF** — CsrfViewMiddleware global + tokens en todos los formularios
3. **Roles** — RoleRequiredMixin con grupos Django (Admin, Cocina, Cajero)
4. **Auditoría** — Modelo Auditoria registra cada acción con usuario, IP y detalle
5. **Validación** — RegexValidators, bleach.clean(), validate_special_chars()
6. **Auto-escapado** — Django templates escapan todo output (XSS prevention)
7. **Middleware** — SecurityMiddleware, XFrameOptionsMiddleware, CsrfViewMiddleware
8. **Eliminación lógica** — Productos pasan a `estado="inactivo"`, no se borran
9. **IP logging** — get_client_ip() registra dirección IP en cada auditoría
10. **Medidas adicionales** — Validadores de contraseña, DRF IsAuthenticated, @require_POST, integridad referencial

---

## 📡 API REST

| Endpoint | Métodos | Descripción |
|----------|---------|-------------|
| `/api/productos/` | GET, POST | CRUD productos (con filtros: search, disponible, categoria, ordering) |
| `/api/productos/{id}/` | GET, PUT, PATCH, DELETE | Producto individual |
| `/api/categorias/` | GET | Listar categorías activas |
| `/api/categorias/{id}/` | GET | Detalle categoría |
| `/api/ordenes/` | GET, POST | CRUD órdenes (filtro: estado) |
| `/api/ordenes/{id}/` | GET, PUT, PATCH, DELETE | Orden individual |
| `/api/cocina-ordenes/` | GET | Órdenes activas (no entregadas) |
| `/cocina/api/ordenes-activas/` | GET | Vista simplificada de órdenes activas |

Todas las rutas requieren autenticación (Session o Basic). Formato: JSON. Paginación: 12 ítems/página.

---

## 🧠 Patrones de Diseño Implementados

| # | Patrón | Implementación |
|---|--------|----------------|
| 1 | **Singleton** | `django.conf.settings` — configuración global única |
| 2 | **Factory** | `get_serializer_class()` retorna serializador según contexto |
| 3 | **Strategy** | `SearchFilter` / `OrderingFilter` intercambiables en ViewSets |
| 4 | **Observer** | Modelo `Auditoria` registra cambios en productos |
| 5 | **Repository** | Django ORM — `Producto.objects.filter(estado='activo')` |
| 6 | **Adapter** | DRF Serializers adaptan modelos a JSON |
| 7 | **Facade** | `DashboardView` unifica 8 consultas en un contexto simple |
| 8 | **Builder** | `exportar_inventario_pdf()` construye PDF paso a paso |
| 9 | **Template Method** | Vistas genéricas Django (ListView, CreateView, etc.) |
| 10 | **DI** | Django inyecta modelos, formularios, serializers y permisos |

---

## 📊 Funcionalidades Principales

- **Productos** — CRUD completo con búsqueda HTMX, filtros, modales, imágenes
- **Categorías** — CRUD con protección (Admin-only, on_delete=PROTECT)
- **Inventario** — Tabla paginada con filtros, valor total, exportación PDF
- **Stock Alerts** — Vista de 3 columnas (agotados/pocas/en stock) con badge en navbar
- **Dashboard** — KPIs, productos recientes, auditorías en tiempo real
- **Cocina Kanban** — Tablero de 3 estados, polling 10s, cambio de estado con 1 clic
- **POS** — Punto de venta con búsqueda de productos, carrito, notas
- **API REST** — Endpoints completos con filtros, paginación y autenticación
- **Roles** — 3 roles con permisos granulares y navegación adaptativa
- **Auditoría** — Trazabilidad completa de cambios con IP y timestamp

---

## 👤 Autor

Desarrollado por — 2026

---

## 📄 Licencia

Todos los derechos reservados. Este software no puede ser distribuido, modificado o usado comercialmente sin autorización expresa del autor.
