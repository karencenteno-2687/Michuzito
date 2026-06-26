# Arquitectura del Sistema — Mi Chuzito

## Tipo de Arquitectura: MVT (Model - View - Template)

Django usa el patrón **MVT**, que es una variante del clásico MVC:

| Capa      | En Django      | ¿Qué hace?                                      |
|-----------|----------------|-------------------------------------------------|
| Model     | `models.py`    | Define los datos y la lógica de negocio         |
| View      | `views.py`     | Procesa peticiones y decide qué responder        |
| Template  | archivos `.html` | Muestra la información al usuario              |

---

## Estructura de Carpetas

```
MiChuzito/                          ← carpeta raíz del proyecto
├── venv/                           ← entorno virtual Python
├── docs/                           ← documentación
├── .env                            ← variables de entorno (no se sube a GitHub)
├── .gitignore
└── MiChuzito/                      ← código del proyecto Django
    ├── manage.py                   ← comando principal de Django
    ├── db.sqlite3                  ← base de datos local (respaldo)
    ├── config/                     ← configuración general
    │   ├── settings.py             ← configuración de Django
    │   ├── urls.py                 ← URLs principales
    │   ├── wsgi.py
    │   └── asgi.py
    ├── productos/                  ← módulo principal
    │   ├── models.py               ← Producto, Categoria, Auditoria
    │   ├── views.py                ← CRUD, login, registro, dashboard
    │   ├── forms.py                ← formularios con validaciones
    │   ├── urls.py                 ← rutas del módulo
    │   ├── context_processors.py   ← stock crítico global
    │   ├── admin.py                ← panel de administración
    │   ├── static/productos/       ← Bootstrap local, CSS, JS
    │   ├── templates/productos/    ← archivos HTML
    │   └── management/commands/    ← comandos seed
    └── cocina/                     ← módulo de cocina/POS
        ├── models.py               ← Orden, DetalleOrden
        ├── views.py                ← dashboard cocina, POS
        ├── urls.py
        └── templates/cocina/       ← templates de cocina
```

---

## Flujo de una Petición

```
Usuario (navegador)
        |
        | HTTP Request (ej: GET /productos/)
        ▼
+------------------+
|   urls.py         |  ← decide qué view llama
+------------------+
        |
        ▼
+------------------+
|   views.py        |  ← procesa la lógica
|   (View)          |
+------------------+
        |         |
        |         ▼
        |  +------------------+
        |  |   models.py       |  ← consulta la base de datos
        |  |   (Model)         |
        |  +------------------+
        |         |
        |    datos obtenidos
        ▼
+------------------+
|  template .html   |  ← muestra los datos al usuario
|  (Template)       |
+------------------+
        |
        | HTTP Response
        ▼
Usuario (ve la página)
```

---

## Módulos del Sistema

### Módulo `productos`
Maneja todo lo relacionado con el inventario y la gestión de productos.

**Modelos:**
- `Categoria` — agrupa los productos
- `Producto` — nombre, precio, stock, imagen, categoría
- `Auditoria` — registra quién hizo qué acción y cuándo

**Vistas principales:**
- `list_view` — lista todos los productos
- `create_view` — crea un producto nuevo
- `update_view` — edita un producto
- `delete_view` — elimina un producto
- `dashboard_view` — panel principal con estadísticas
- `login_view` / `signup_view` — autenticación
- `stock_alertas_view` — productos con stock bajo

### Módulo `cocina`
Maneja las órdenes del punto de venta.

**Modelos:**
- `Orden` — una orden de pedido con estado y mesa
- `DetalleOrden` — cada producto dentro de una orden

**Vistas principales:**
- `dashboard` — panel de cocina con órdenes activas
- `pos_nueva_orden` — pantalla del cajero para crear órdenes

---

## Sistema de Roles

```
+-------------+        +-------------+        +-------------+
|    Admin    |        |   Cajero    |        |   Cocina    |
+-------------+        +-------------+        +-------------+
| - Ver todo  |        | - POS       |        | - Ver órd.  |
| - CRUD prod.|        | - Nueva ord.|        | - Cambiar   |
| - Usuarios  |        | - Ver prod. |        |   estado    |
| - Reportes  |        |             |        |             |
+-------------+        +-------------+        +-------------+
```

Los roles se controlan con grupos de Django (`django.contrib.auth.models.Group`) y se verifican en los templates:
```html
{% if is_admin %} ... {% endif %}
{% if is_cajero %} ... {% endif %}
{% if is_cocina %} ... {% endif %}
```

---

## Base de Datos

**Motor usado:** MySQL (via XAMPP / MariaDB)  
**ORM:** Django ORM (no se escribe SQL directamente)

### Diagrama de tablas principales

```
+------------------+       +------------------+
|    Categoria      |       |     Producto      |
+------------------+       +------------------+
| id (PK)          |◄──────| categoria (FK)    |
| nombre           |       | id (PK)           |
| descripcion      |       | nombre            |
+------------------+       | precio            |
                           | stock             |
                           | imagen            |
                           | activo            |
                           +------------------+
                                    |
                                    ▼
+------------------+       +------------------+
|    Auditoria      |       |   DetalleOrden   |
+------------------+       +------------------+
| accion           |       | orden (FK)       |
| usuario          |       | producto (FK)    |
| producto (FK)    |       | cantidad         |
| fecha            |       | precio_unitario  |
+------------------+       +------------------+
                                    ▲
                           +------------------+
                           |     Orden         |
                           +------------------+
                           | id (PK)          |
                           | estado           |
                           | mesa             |
                           | fecha            |
                           | cajero (FK)      |
                           +------------------+
```

---

## Tecnologías Usadas

| Tecnología      | Versión  | ¿Para qué?                        |
|-----------------|----------|-----------------------------------|
| Python          | 3.13     | Lenguaje base                     |
| Django          | 4.2      | Framework web                     |
| MySQL/MariaDB   | 10.4     | Base de datos                     |
| Bootstrap       | 5        | Estilos CSS (cargado localmente)  |
| djangorestframework | última | API REST                      |
| bleach          | última   | Sanitización de entradas          |
| reportlab       | última   | Generación de PDFs                |
| python-dotenv   | última   | Variables de entorno              |