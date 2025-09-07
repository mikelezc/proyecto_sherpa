# Task Management System

Sistema completo de gestión de tareas desarrollado con Django, con arquitectura de microservicios usando Docker y procesamiento asíncrono con Celery.

## 🏗️ Arquitectura

### Servicios Docker (5 contenedores):
- **django_web** - Aplicación Django principal
- **postgres_db** - Base de datos PostgreSQL 15  
- **redis_cache** - Sistema de caché y broker para Celery
- **celery_worker** - Procesamiento de tareas en segundo plano
- **celery_beat** - Programador de tareas periódicas

### Stack Tecnológico:
- **Backend**: Django 5.2.6, Python 3.10
- **Base de datos**: PostgreSQL 15.14
- **Cache & Message Broker**: Redis 7.4.5
- **Task Queue**: Celery 5.5.3
- **API**: Django REST Framework + django-ninja
- **Frontend**: Bootstrap 5, JavaScript ES6
- **Containerización**: Docker & Docker Compose

## 🚀 Quick Start

### 1. Clonar y configurar

```bash
git clone <repository-url>
cd proyecto_sherpa

# Configurar variables de entorno (opcional, tiene valores por defecto)
cp srcs/env_example.md .env
```

### 2. Ejecutar con Docker

```bash
# Construir y ejecutar todos los servicios
docker-compose up --build

# Ejecutar en segundo plano
docker-compose up --build -d
```

### 3. Configuración inicial

```bash
# Crear superusuario para el admin
docker-compose exec django_web python manage.py createsuperuser

# Ejecutar migraciones (opcional, se ejecutan automáticamente)
docker-compose exec django_web python manage.py migrate
```

### 4. Acceso a la aplicación

- **Aplicación web**: http://localhost:8000
- **Panel de administración**: http://localhost:8000/admin/
- **API Explorer**: http://localhost:8000/api/docs/

## 📋 Funcionalidades

### 🔐 Sistema de Autenticación
- Registro y login de usuarios
- Verificación por email (via logs del servidor durante desarrollo)
- Gestión de perfiles
- Sistema de rate limiting para seguridad
- Autenticación JWT para API

### ✅ Gestión de Tareas
- CRUD completo de tareas
- Sistema de prioridades (LOW, MEDIUM, HIGH, URGENT)
- Estados de tareas (PENDING, IN_PROGRESS, COMPLETED, ARCHIVED)
- Asignación de tareas a usuarios
- Organización por equipos y etiquetas
- Comentarios en tareas
- Historial de cambios

### 🔄 Procesamiento Asíncrono (Celery)
- `send_task_notification` - Notificaciones por email
- `check_overdue_tasks` - Revisión de tareas vencidas
- `auto_assign_tasks` - Asignación automática inteligente
- `calculate_team_velocity` - Métricas de rendimiento de equipos
- `generate_daily_summary` - Resúmenes diarios automatizados
- `cleanup_archived_tasks` - Limpieza de tareas archivadas
- `cleanup_inactive_users` - Limpieza de usuarios inactivos

### 🔒 Sistema de Seguridad
- Rate limiting configurable por endpoint
- Protección CSRF
- Validación de entrada robusta
- Logging de seguridad detallado

## 📁 Estructura del Proyecto

```
proyecto_sherpa/
├── docker-compose.yml              # Orquestación de servicios
├── makefile                        # Comandos útiles
└── srcs/
    ├── django/                     # Aplicación Django
    │   ├── authentication/         # Sistema de usuarios y autenticación
    │   │   ├── api/               # Endpoints API REST
    │   │   ├── web/               # Views y templates web
    │   │   ├── models/            # Modelos de usuario
    │   │   ├── services/          # Lógica de negocio
    │   │   └── tasks.py           # Tareas Celery
    │   ├── tasks/                  # Sistema de gestión de tareas
    │   │   ├── models.py          # Modelos (Task, Team, Priority, etc.)
    │   │   ├── api/               # API REST para tareas
    │   │   ├── web/               # Interface web
    │   │   ├── logic/             # Lógica de negocio
    │   │   └── tasks.py           # Tareas Celery
    │   ├── main/                   # Configuración Django
    │   │   ├── settings.py        # Configuraciones
    │   │   ├── celery.py          # Configuración Celery
    │   │   └── urls.py            # URLs principales
    │   ├── requirements.txt        # Dependencias Python
    │   └── manage.py              # Django CLI
    ├── db/                        # PostgreSQL
    ├── front/                     # Assets estáticos
    └── ssl/                       # Certificados SSL
```

## 🛠️ Comandos Útiles

### Docker
```bash
# Ver logs de servicios
docker-compose logs -f django_web
docker-compose logs -f celery_worker
docker-compose logs -f celery_beat

# Reiniciar servicios específicos
docker-compose restart django_web
docker-compose restart celery_worker

# Estado de contenedores
docker-compose ps

# Parar todos los servicios
docker-compose down

# Limpiar volúmenes
docker-compose down -v
```

### Django
```bash
# Shell interactivo
docker-compose exec django_web python manage.py shell

# Crear migraciones
docker-compose exec django_web python manage.py makemigrations

# Aplicar migraciones
docker-compose exec django_web python manage.py migrate

# Recopilar archivos estáticos
docker-compose exec django_web python manage.py collectstatic
```

### Celery
```bash
# Estado de workers
docker-compose exec celery_worker celery -A main inspect active

# Tareas programadas
docker-compose exec celery_worker celery -A main inspect scheduled

# Resetear rate limits (para desarrollo/testing)
docker exec redis_cache redis-cli FLUSHDB
```

## 📊 Monitoreo y Logs

### Rate Limiting
El sistema incluye protección contra ataques:
- **Login**: 10 intentos cada 5 minutos
- **Verificación email**: 10 intentos cada 30 minutos
- **Cambio email**: 5 intentos cada hora

Para resetear durante desarrollo:
```bash
docker exec redis_cache redis-cli FLUSHDB
docker-compose restart django_web
```

### Verificación de Email (Desarrollo)
Los emails de verificación se muestran en los logs del servidor:
```bash
docker-compose logs django_web -f
```

## 🧪 Testing

```bash
# Ejecutar todos los tests
docker-compose exec django_web python manage.py test

# Tests específicos de una app
docker-compose exec django_web python manage.py test authentication
docker-compose exec django_web python manage.py test tasks

# Con coverage
docker-compose exec django_web coverage run --source='.' manage.py test
docker-compose exec django_web coverage report
```

## 🌐 API Endpoints

### Autenticación
- `POST /api/auth/register/` - Registro de usuario
- `POST /api/auth/login/` - Login
- `POST /api/auth/logout/` - Logout
- `POST /api/auth/refresh/` - Renovar token JWT

### Usuarios
- `GET /api/users/` - Lista de usuarios
- `GET /api/users/{id}/` - Detalle de usuario
- `PUT /api/users/{id}/` - Actualizar usuario
- `GET /api/users/me/` - Perfil actual

### Tareas
- `GET /api/tasks/` - Lista de tareas
- `POST /api/tasks/` - Crear tarea
- `GET /api/tasks/{id}/` - Detalle de tarea
- `PUT /api/tasks/{id}/` - Actualizar tarea
- `DELETE /api/tasks/{id}/` - Eliminar tarea
- `POST /api/tasks/{id}/assign/` - Asignar tarea
- `POST /api/tasks/{id}/comments/` - Añadir comentario
- `GET /api/tasks/{id}/history/` - Historial de cambios

### Equipos
- `GET /api/teams/` - Lista de equipos
- `POST /api/teams/` - Crear equipo
- `GET /api/teams/{id}/` - Detalle de equipo
- `PUT /api/teams/{id}/` - Actualizar equipo

## ⚙️ Configuración

### Variables de Entorno

Las principales variables están configuradas con valores por defecto seguros. Para personalizar, crear archivo `.env`:

```bash
# Django
DEBUG=True
SECRET_KEY=tu-clave-secreta-personalizada

# Base de datos
POSTGRES_DB=task_management_db
POSTGRES_USER=postgres
POSTGRES_PASSWORD=tu-password-personalizada

# Redis
REDIS_URL=redis://redis:6379/0

# Celery
CELERY_BROKER_URL=redis://redis:6379/0
CELERY_RESULT_BACKEND=redis://redis:6379/0

# JWT
JWT_SECRET_KEY=tu-jwt-secret-personalizada
JWT_ALGORITHM=HS256
```

### Configuración de Producción

Para entorno de producción, modificar:
- `DEBUG=False`
- Configurar `ALLOWED_HOSTS`
- Usar base de datos externa
- Configurar email SMTP real
- Habilitar HTTPS/SSL
- Configurar logging avanzado

## 🚀 Despliegue

### Preparación para Producción
```bash
# Construir para producción
docker-compose -f docker-compose.prod.yml up --build

# Con variables de entorno de producción
docker-compose --env-file .env.prod up -d
```

### Optimizaciones
- Usar Gunicorn en lugar del servidor de desarrollo
- Configurar Nginx como proxy reverso
- Implementar caché de Redis más robusta
- Configurar monitoreo con Prometheus/Grafana

## 🤝 Contribución

1. Fork del proyecto
2. Crear rama para feature (`git checkout -b feature/AmazingFeature`)
3. Commit cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abrir Pull Request

## 📄 Licencia

Este proyecto está bajo la Licencia MIT - ver el archivo [LICENSE](LICENSE) para detalles.

## 📞 Soporte

Para reportar bugs o solicitar features, crear un issue en el repositorio del proyecto.

---

**Desarrollado con ❤️ usando Django y Docker**
