# Patrones de Diseño — Mi Chuzito

## ¿Qué es un patrón de diseño?
Un patrón de diseño es una solución reutilizable a un problema común en el desarrollo de software. No es código copiado, sino una guía de cómo estructurar el código para que sea más fácil de mantener y entender.

---

## Patrón 1: Singleton — Conexión a la Base de Datos

### ¿Qué hace?
Garantiza que solo exista **una única instancia** de la conexión a la base de datos durante toda la ejecución del programa.

### ¿Dónde está en Mi Chuzito?
Django maneja esto internamente a través de `settings.py`. La configuración `DATABASES` se carga una sola vez y Django reutiliza esa misma conexión en toda la aplicación.

```python
# config/settings.py
DATABASES = {
    "default": {
        "ENGINE": os.environ.get("DB_ENGINE", "django.db.backends.sqlite3"),
        "NAME": os.environ.get("DB_NAME", str(BASE_DIR / "db.sqlite3")),
        "USER": os.environ.get("DB_USER", "root"),
        "PASSWORD": os.environ.get("DB_PASSWORD", ""),
        "HOST": os.environ.get("DB_HOST", "localhost"),
        "PORT": os.environ.get("DB_PORT", "3306"),
    }
}
```

### Diagrama UML
```
+----------------------+
|   DatabaseConnection  |
+----------------------+
| - instance: self      |
+----------------------+
| + get_instance()      |
| + connect()           |
+----------------------+
        ▲
        | usa (una sola vez)
        |
+----------------------+
|    Django ORM         |
+----------------------+
```

### ¿Por qué se usa?
- Evita abrir múltiples conexiones innecesarias a la base de datos.
- Ahorra memoria y recursos del servidor.

---

## Patrón 2: Observer — Alertas de Stock Crítico

### ¿Qué hace?
Cuando el stock de un producto baja del mínimo, el sistema **notifica automáticamente** al usuario mostrando una alerta en el menú. Es como un vigilante que observa el stock constantemente.

### ¿Dónde está en Mi Chuzito?
En `context_processors.py` el sistema cuenta los productos con stock crítico y los pasa a todos los templates automáticamente.

```python
# productos/context_processors.py
def stock_critico_count(request):
    if request.user.is_authenticated:
        MINIMO = settings.STOCK_MINIMO_ALERTA  # valor: 5
        count = Producto.objects.filter(
            activo=True, stock__lte=MINIMO
        ).count()
        return {'stock_criticos': count}
    return {'stock_criticos': 0}
```

En `base.html` aparece el badge rojo:
```html
{% if stock_criticos > 0 %}
  <span class="badge bg-danger">{{ stock_criticos }}</span>
{% endif %}
```

### Diagrama UML
```
+------------------+        observa        +------------------+
|    Producto       | --------------------> |  StockObserver   |
+------------------+                        +------------------+
| - stock: int      |                        | + notificar()    |
| - activo: bool    |                        +------------------+
+------------------+                                |
                                                    ▼
                                        +------------------+
                                        |  context_processor|
                                        +------------------+
                                        | + stock_criticos  |
                                        +------------------+
```

### ¿Por qué se usa?
- El usuario siempre sabe si hay productos con poco stock sin tener que buscarlos.
- El badge rojo aparece en tiempo real en el navbar.

---

## Patrón 3: Factory — Creación de Usuarios por Rol

### ¿Qué hace?
En lugar de crear usuarios manualmente con todos sus permisos, el sistema tiene una "fábrica" que crea el usuario y le asigna automáticamente el rol correcto (Admin, Cajero o Cocina).

### ¿Dónde está en Mi Chuzito?
En `views.py`, la función `signup_view` crea el usuario y lo asigna al grupo/rol seleccionado:

```python
# productos/views.py
def signup_view(request):
    if request.method == "POST":
        # Obtiene el rol seleccionado en el formulario
        rol = request.POST.get("rol", "Cajero")
        
        # Crea el usuario
        user = User.objects.create_user(
            username=username,
            password=password
        )
        
        # "Fábrica": asigna el rol automáticamente
        grupo = Group.objects.get(name=rol)
        user.groups.add(grupo)
```

### Diagrama UML
```
+------------------+
|   signup_view     |  ← recibe rol como parámetro
+------------------+
         |
         | crea según el rol
         ▼
+------------------+     +------------------+     +------------------+
|   UsuarioAdmin    |     |  UsuarioCajero   |     |  UsuarioCocina   |
+------------------+     +------------------+     +------------------+
| - grupo: Admin    |     | - grupo: Cajero  |     | - grupo: Cocina  |
| - permisos: todos |     | - permisos: POS  |     | - permisos: órd. |
+------------------+     +------------------+     +------------------+
```

### ¿Por qué se usa?
- No hay que configurar permisos manualmente para cada usuario nuevo.
- Es más fácil agregar nuevos roles en el futuro.

---

## Patrón 4: Decorator — Validadores de Campos

### ¿Qué hace?
"Decora" (envuelve) los campos del modelo con reglas de validación adicionales sin modificar el campo original. Es como poner un filtro encima del campo.

### ¿Dónde está en Mi Chuzito?
En `models.py` con `RegexValidator`, y en `forms.py` con `bleach.clean()`:

```python
# productos/models.py
nombre_validator = RegexValidator(
    regex=r"^[a-zA-ZáéíóúÁÉÍÓÚñÑ0-9\s]{3,100}$",
    message="El nombre solo permite letras, números y espacios (3-100 caracteres)."
)

precio_validator = RegexValidator(
    regex=r"^\d+(\.\d{1,2})?$",
    message="Ingrese un precio válido con máximo 2 decimales."
)

class Producto(models.Model):
    nombre = models.CharField(validators=[nombre_validator], max_length=100)
    precio = models.DecimalField(validators=[precio_validator], ...)
```

```python
# productos/forms.py
def clean_nombre(self):
    nombre = self.cleaned_data.get("nombre")
    return bleach.clean(nombre.strip())  # limpia HTML malicioso
```

### Diagrama UML
```
+------------------+
|  Campo original   |
|  (CharField)      |
+------------------+
         |
         ▼ decorado con
+------------------+
|  RegexValidator   |  ← valida formato
+------------------+
         |
         ▼ decorado con
+------------------+
|  bleach.clean()   |  ← limpia XSS
+------------------+
         |
         ▼
+------------------+
|  Dato seguro y    |
|  válido guardado  |
+------------------+
```

### ¿Por qué se usa?
- Protege la base de datos de datos mal formateados.
- Previene ataques XSS (Cross-Site Scripting).
- Las validaciones se pueden reutilizar en cualquier campo.

---

## Resumen de Patrones

| Patrón    | ¿Dónde?                        | ¿Para qué?                              |
|-----------|--------------------------------|-----------------------------------------|
| Singleton | `config/settings.py` + ORM     | Una sola conexión a la base de datos    |
| Observer  | `context_processors.py`        | Alertas automáticas de stock crítico    |
| Factory   | `productos/views.py`           | Crear usuarios con rol automáticamente  |
| Decorator | `models.py` + `forms.py`       | Validar y limpiar datos de entrada      |