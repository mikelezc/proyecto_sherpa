# Task Management System - Cleaned Version

Este es tu proyecto de gestión de tareas limpio, adaptado para cumplir con los requisitos de la prueba técnica.

## Cambios Realizados

### ✅ Componentes Mantenidos
- **Django** con autenticación personalizada
- **PostgreSQL** como base de datos
- **Redis** para caché y broker de Celery
- **Celery** para tareas en segundo plano
- **Celery Beat** para tareas programadas
- **App `authentication`** con todas sus funcionalidades
- **Templates Django** para frontend básico

### ❌ Componentes Eliminados
- **Nginx** (proxy inverso)
- **Vault** (gestión de secretos)
- **SSL/TLS** (certificados automáticos)
- **WAF** (Web Application Firewall)
- **Frontend JavaScript** (CSS/JS personalizado)
- **Apps innecesarias**: `game`, `tournament`, `dashboard`, `chat`

### 🆕 Componentes Nuevos
- **App `tasks`** - Sistema completo de gestión de tareas
- **Docker Compose simplificado** - Solo servicios esenciales
- **Configuración sin Vault** - Variables de entorno directas
- **Templates básicos** - Para demostrar funcionalidad frontend

## Arquitectura Simplificada

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│   Django    │◄──►│ PostgreSQL  │    │    Redis    │
│   Web App   │    │ Database    │    │   Cache     │
└─────────────┘    └─────────────┘    └─────────────┘
       │                                      ▲
       │                                      │
       ▼                                      │
┌─────────────┐    ┌─────────────┐           │
│   Celery    │◄───┤ Celery Beat │───────────┘
│   Worker    │    │ Scheduler   │
└─────────────┘    └─────────────┘
```

## Quick Start

### 1. Preparar el proyecto limpio

```bash
# Hacer backup del proyecto actual
cp -r proyecto_sherpa proyecto_sherpa_backup

# Ir al directorio del proyecto
cd proyecto_sherpa

# Reemplazar archivos principales
mv docker-compose.yml.new docker-compose.yml
mv srcs/django/Dockerfile.new srcs/django/Dockerfile
mv srcs/django/entrypoint.py srcs/django/django-entrypoint.py
mv srcs/django/requirements_new.txt srcs/django/requirements.txt
mv srcs/django/main/settings_new.py srcs/django/main/settings.py
mv srcs/django/main/urls_new.py srcs/django/main/urls.py

# Copiar archivo de entorno
cp .env.sample .env
```

### 2. Configurar variables de entorno

Edita el archivo `.env` con tus configuraciones:

```bash
# Configuración básica
DEBUG=True
DJANGO_SECRET_KEY=tu-clave-secreta-aqui

# Base de datos
POSTGRES_DB=task_management_db
POSTGRES_USER=admin
POSTGRES_PASSWORD=tu-password-seguro

# Celery
CELERY_BROKER_URL=redis://redis:6379/0
CELERY_RESULT_BACKEND=redis://redis:6379/0

# JWT
JWT_SECRET_KEY=tu-jwt-secret-key
```

### 3. Limpiar archivos innecesarios

```bash
# Eliminar servicios innecesarios
rm -rf srcs/nginx
rm -rf srcs/vault
rm -rf srcs/ssl
rm -rf srcs/waf
rm -rf srcs/front

# Eliminar apps innecesarias de Django
rm -rf srcs/django/game
rm -rf srcs/django/tournament
rm -rf srcs/django/dashboard
rm -rf srcs/django/chat

# Eliminar archivos de configuración obsoletos
rm -rf security_tests
rm -f configure_ip.sh
rm -f setup_env.sh
```

### 4. Ejecutar el proyecto

```bash
# Construir y ejecutar
docker-compose up --build

# En otra terminal, crear superusuario
docker-compose exec web python manage.py createsuperuser
```

## Estructura del Proyecto Limpio

```
proyecto_sherpa/
├── docker-compose.yml          # ✅ Simplificado
├── .env.sample                 # ✅ Nuevo
├── .env                        # ✅ Tu configuración
├── init-db.sql                 # ✅ Inicialización DB
└── srcs/
    └── django/
        ├── Dockerfile          # ✅ Simplificado
        ├── requirements.txt    # ✅ Limpio
        ├── entrypoint.py       # ✅ Sin Vault/SSL
        ├── manage.py
        ├── authentication/     # ✅ Mantenido completo
        │   ├── api/
        │   ├── web/
        │   │   └── templates/
        │   ├── models/
        │   └── tasks.py        # ✅ Celery tasks
        ├── tasks/              # 🆕 Nueva app
        │   ├── models.py       # ✅ Modelos requeridos
        │   ├── tasks.py        # ✅ Tareas Celery
        │   ├── api/            # ✅ REST API
        │   ├── web/            # ✅ Templates Django
        │   └── templates/
        └── main/
            ├── settings.py     # ✅ Simplificado
            ├── urls.py         # ✅ Limpio
            ├── celery.py       # ✅ Configuración Celery
            └── wsgi.py
```

## Funcionalidades Implementadas

### ✅ Requisitos Obligatorios (Part A)

1. **Docker Infrastructure** ✅
   - PostgreSQL 15+
   - Redis 7+
   - Django application server
   - Celery worker
   - Celery beat

2. **Django REST API** ✅
   - Authentication endpoints
   - User management
   - Task management CRUD
   - Task operations (assign, comments, history)

3. **PostgreSQL Database** ✅
   - Modelos requeridos (Task, Comment, Tag, etc.)
   - Django ORM
   - Índices optimizados

4. **Celery Background Tasks** ✅
   - `send_task_notification`
   - `generate_daily_summary`
   - `check_overdue_tasks`
   - `cleanup_archived_tasks`

5. **Frontend Application** ✅
   - Templates Django
   - Autenticación web
   - Lista de tareas
   - Formularios básicos

## Endpoints API Disponibles

### Autenticación
- `POST /api/auth/register/`
- `POST /api/auth/login/`
- `POST /api/auth/logout/`
- `POST /api/auth/refresh/`

### Usuarios
- `GET /api/users/`
- `GET /api/users/{id}/`
- `PUT /api/users/{id}/`
- `GET /api/users/me/`

### Tareas
- `GET /api/tasks/`
- `POST /api/tasks/`
- `GET /api/tasks/{id}/`
- `PUT /api/tasks/{id}/`
- `DELETE /api/tasks/{id}/`
- `POST /api/tasks/{id}/assign/`
- `POST /api/tasks/{id}/comments/`
- `GET /api/tasks/{id}/history/`

## Acceso Web

- **Frontend Principal**: http://localhost:8000
- **Admin Django**: http://localhost:8000/admin/
- **API Browse**: http://localhost:8000/api/

## Comandos Útiles

```bash
# Ver logs
docker-compose logs -f web
docker-compose logs -f celery-worker
docker-compose logs -f celery-beat

# Ejecutar migraciones
docker-compose exec web python manage.py migrate

# Crear superusuario
docker-compose exec web python manage.py createsuperuser

# Entrar al shell Django
docker-compose exec web python manage.py shell

# Monitorear Celery
docker-compose exec celery-worker celery -A main inspect active
```

## Próximos Pasos

Para completar la prueba técnica, puedes:

1. **Implementar más endpoints** de la API REST
2. **Mejorar las templates** del frontend
3. **Añadir tests** unitarios e integración
4. **Documentar la API** con Swagger/OpenAPI
5. **Añadir funcionalidades opcionales** (Kafka, Flask analytics, etc.)

¡Tu base está lista para la prueba técnica! 🚀
