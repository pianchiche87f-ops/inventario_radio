# Inventario de Radios

Sistema de gestión de inventario de radios y equipos de comunicación, desarrollado con Django.

## Características

- **Gestión completa de radios**: Registro, consulta y seguimiento del estado de cada equipo
- **Control de estados**: Disponible, Asignado, Mantenimiento, En terceros, Dado de baja
- **Historial de kardex**: Registro de todas los movimientos (asignaciones, devoluciones, mantenimiento, etc.)
- **Generación de QR**: Códigos QR automáticos para identificación rápida de equipos
- **Órdenes de trabajo**: Sistema para crear y cerrar órdenes de mantenimiento/reparación
- **Dashboard estadístico**: Vistas gráficas del inventario por estado
- **Trazabilidad**: Búsqueda y seguimiento completo del historial de cada radio
- **Autenticación de usuarios**: Sistema de login/logout con roles

## Prerequisitos

- **Python 3.12+**
- **Django 6.1.2+**
- **PostgreSQL 17**
- **Git** (opcional, para control de versiones)

### Dependencias Python

```bash
django
django-crispy-forms
phonenumbers
qrcode[pil]
pillow
python-decouple
psycopg3
```

## Pasos de Instalación

### 1. Clonar el repositorio

```bash
git clone <URL-del-repositorio>
cd inventario_radios
```

### 2. Crear y activar entorno virtual

```bash
python -m venv venv
.\venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac
```

### 3. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 4. Configurar variables de entorno

Copiar el archivo `.env` y configurar las credenciales:

```bash
copy .env.example .env  # o crear el archivo manualmente
```

Archivo `.env` debe contener:

```
DJANGO_SECRET_KEY=tu_clave_secreta_aquí
DB_NAME=inventario_radios
DB_USER=inventariorad
DB_PASSWORD=inventarioradio
DB_HOST=localhost
DB_PORT=5432
```

### 5. Configurar la base de datos PostgreSQL

```bash
createdb inventario_radios
```

### 6. Aplicar migraciones

```bash
python manage.py migrate
```

### 7. Crear superusuario (opcional, para admin)

```bash
python manage.py createsuperuser
```

### 8. Ejecutar el servidor de desarrollo

```bash
python manage.py runserver
```

## Ejecutar el Servidor de Desarrollo

```bash
python manage.py runserver
```

La aplicación estará disponible en: `http://127.0.0.1:8000/

## Acceso Administrativo

- **URL**: `http://127.0.0.1:8000/admin/`
- **Credenciales**: Usuario creado con `createsuperuser`

## URLs Principales

| Endpoint | Descripción |
|----------|-------------|
| `/` | Dashboard principal |
| `/inventario/` | Lista de radios |
| `/inventario/registrar/` | Registrar nuevo radio |
| `/inventario/radio/<uuid>/` | Detalle de radio |
| `/inventario/radio/<uuid>/constatacion/` | Registrar constatación física |
| `/trazabilidad/` | Trazabilidad por código |
| `/trazabilidad/radio/<uuid>/orden/iniciar/` | Iniciar orden de trabajo |
| `/trazabilidad/orden/<int>/cerrar/` | Cerrar orden de trabajo |
| `/cuentas/iniciar-sesion/` | Login |
| `/cuentas/cerrar-sesion/` | Logout |

## Descripción de Características

### Gestión de Radios

- **Registro**: Formulario completo con código interno, número de serie, marca, modelo, estado, ubicación y responsable
- **Estados disponibles**: 
  - Disponible: El equipo está en bodega y disponible para asignación
  - Asignado: El equipo fue entregado a un usuario
  - Mantenimiento: El equipo está en reparación o servicio técnico
  - En terceros: El equipo está fuera de la empresa (arriendo, préstamo, etc.)
  - Dado de baja: El equipo fue dado de baja permanentemente
- **Búsqueda**: Filtrar por código interno, marca, modelo o número de serie
- **QR generation**: Cada radio tiene un código QR único que redirige a su página de detalle

### Historial de Kardex

- **Tipos de movimiento**: Registro inicial, Asignación, Devolución, Traslado, Mantenimiento, Reparación, Constatación física, Orden iniciada, Orden cerrada, Baja
- **Registro automático**: Los movimientos se registran automáticamente al crear radio, cambiar estado, iniciar/cerrar órdenes
- **Responsable**: Cada movimiento registrado indica quién lo realizó
- **Ubicación**: Se puede registrar la ubicación física actual del equipo

### Órdenes de Trabajo

- **Creación**: Se puede iniciar una orden desde la página de detalle de un radio
- **Estados**: Iniciada → Cerrada
- **Fecha límite**: Cada orden tiene una fecha límite para su completación
- **Vencidas**: El sistema identifica automáticamente las órdenes cuya fecha límite ha pasado
- **Historial**: Cada cambio de estado se registra en el kardex

### Dashboard

- **Estadísticas generales**: Total de radios, conteo por estado
- **Gráfico circular**: Distribución del inventario por estado
- **Últimos movimientos**: Los 5 movimientos de kardex más recientes
- **Equipos en terceros**: Lista de radios en terceros con fecha de devolución
- **Fecha vencida**: Identifica equipos en terceros cuya fecha de devolución ya expiró
- **Mantenimiento**: Lista de equipos actualmente en mantenimiento

## Modelos de Base de Datos

El proyecto tiene **3 modelos personalizados**:

1. **`Radio`** (app `inventario`)
   - Campos: codigo_interno (unique), numero_serie (unique), marca, modelo, estado, ubicacion, responsable, fecha_devolucion_prevista, identificador_qr, imagen_qr, fecha_registro, observaciones
   - 5 estados: Disponible, Asignado, Mantenimiento, En terceros, Dado de baja
   - Tabla en BD: `inventario_radio`

2. **`MovimientoKardex`** (app `inventario`)
   - Campos: radio (FK), tipo, descripcion, ubicacion, responsable, fecha, registrado_por (FK a User)
   - 10 tipos de movimiento: Registro, Asignación, Devolución, Traslado, Mantenimiento, Reparación, Constatación física, Orden iniciada, Orden cerrada, Baja
   - Tabla en BD: `inventario_movimentokardex`

3. **`OrdenTrabajo`** (app `core`)
   - Campos: codigo_radio, radio (FK a Radio), descripcion, responsable, fecha_inicio, fecha_limite, fecha_terminado, estado
   - 2 estados: Iniciada, Cerrada
   - Campo calculado: `vencida` (propiedad)
   - Tabla en BD: `core_ordentrabajo`

## Archivos HTML del Proyecto

El proyecto tiene **10 archivos HTML** (plantillas Django) ubicados en:

- `core/templates/core/` (9 archivos):
  - `base.html` - Plantilla base
  - `dashboard.html` - Dashboard principal con gráficos
  - `detalle_radio.html` - Detalle de un radio con su historial
  - `generador_qr.html` - Generador de códigos QR
  - `lista_radios.html` - Lista de radios con búsqueda
  - `orden_trabajo.html` - Formulario de órdenes de trabajo
  - `registrar_constatacion.html` - Formulario de constatación física
  - `registrar_radio.html` - Formulario de registro de radio
  - `trazabilidad.html` - Trazabilidad por código interno

- `core/templates/registration/` (1 archivo):
  - `login.html` - Página de login

**Total: 10 archivos HTML** del proyecto (excluyendo archivos de venv y Django).

## Problemas Conocidos o Items Pendientes

### Pendientes de implementación

1. **`inventario/views.py`**: Archivo actualmente vacío. Las vistas principales están en `core/views.py`, pero pueden necesitarse vistas específicas para la app `inventario`

2. **README.md**: Documentación inicial - necesita ser mantenida actualizada

3. **Tests**: Los archivos `core/tests.py` e `inventario/tests.py` están vacíos - se recomienda añadir tests unitarios

4. **Validación de fechas**: El sistema identifica radios vencidos en terceros, pero podría añadirse notificación automática por email

5. **Archivos estáticos**: Algunos assets en `core/static/imagen/` podrían necesar optimización

6. **Internationalización**: Actualmente configurado en español (`es`), pero podría extenderse a otros idiomas

7. **API REST**: No hay endpoints de API documentados - posible futura extensión

8. **Despliegue producción**: Configuración para producción (Gunicorn, Nginx, etc.) no está incluida

### Bugs reportados

- Ningún bug crítico reportado en la versión actual

### Mejoras sugeridas

- Sistema de notificaciones por email para órdenes vencidas
- Reportes exportables (PDF/Excel) del inventario
- Módulo de préstamos con fechas de devolución automáticas
- Integración con sistema de facturación
- Aplicación móvil para escaneo de QR