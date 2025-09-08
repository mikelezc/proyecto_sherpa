# Task Management System

Sistema completo de gestión de tareas desarrollado con Django, con arquitectura de microservicios usando Docker y procesamiento asíncrono con Celery.

La estructura de docker, la api de autenticación y manejo de usuarios están basadas en este otro repo que desarrollé usando este mismo framework.

https://github.com/mikelezc/42_Transcendence

Aquí se puede ver la misma base, pero aplicada con otras funciones interesantes como notificaciones vía mail, JWT, 2FA con claves, encriptación de datos antes de ser ingresados en la db, balanceador de carga, front que se sirve diréctamente de la API, un WAF, etc. Muy recomendable inspeccionarlo.

## 🚀 Quick Start

### Verificación Automática (Recomendado)
```bash
git clone <repository-url>
cd proyecto_sherpa
./quick_setup.sh
```

### Setup Manual
```bash
# 1. Configurar variables de entorno
cp .env.sample .env

# 2. Iniciar servicios
docker-compose up -d

# 3. Verificar funcionamiento
curl http://localhost:8000/health/
```

### Acceso a la Aplicación
- **Dashboard**: http://localhost:8000/
- **Admin Panel**: http://localhost:8000/admin/ (`demo_admin` / `demo123`)
- **API Documentation**: http://localhost:8000/api/auth/docs

**✅ El archivo `.env` se genera automáticamente con credenciales seguras para desarrollo**

## Documentación

- **[Architecture](docs/ARCHITECTURE.md)** - Arquitectura del sistema  
- **[Decisions](docs/DECISIONS.md)** - Decisiones técnicas e implementación
- **[API Documentation](docs/API_DOCUMENTATION.md)** - Guía completa de la API

- **Endpoints de la API en funcionamiento**:
  - Auth API: http://localhost:8000/api/auth/docs
  - Users API: http://localhost:8000/api/users/docs  
  - Tasks API: http://localhost:8000/api/tasks/docs

## Características Principales

- **Sistema de Autenticación Completo**
- Registro y login de usuarios
- Gestión de perfiles
- Rate limiting por seguridad

- **Gestión de Tareas CRUD**
- Crear, leer, actualizar y eliminar tareas
- Asignación a usuarios y equipos
- Prioridades, estados y comentarios
- Sistema de etiquetas y categorías

- **Optimización de Base de Datos**
- Full-text search con PostgreSQL
- Índices optimizados para rendimiento
- Constraints para integridad de datos

- **Procesamiento Asíncrono**
- Celery para tareas en background
- Limpieza automática de datos

- **API REST Profesional**
- Django Ninja con Swagger automático
- Validación robusta de datos
- Documentación interactiva

## Tecnologías Utilizadas

- **Backend**: Django 5.2.6, Django Ninja
- **Base de Datos**: PostgreSQL 15 
- **Cache**: Redis 7
- **Procesamiento**: Celery + Redis
- **Frontend**: Django Templates + Bootstrap 5
- **Conteneurización**: Docker + Docker Compose

## Troubleshooting

**Puerto ocupado**: `docker-compose down && docker-compose up -d`  
**Problemas de DB**: `docker-compose down -v && docker-compose up -d`  
**Ver logs**: `docker-compose logs django_web`

## Testing
```bash
# Ejecutar todos los tests automáticamente
./run_tests.sh
```

## Rate Limiting
El sistema incluye protección contra ataques:
- **Login**: 10 intentos cada 5 minutos
- **Verificación email**: 10 intentos cada 30 minutos
- **Cambio email**: 5 intentos cada hora

## API Endpoints

### Autenticación
- `POST /api/auth/register/` - Registro de usuario
- `POST /api/auth/login/` - Login
- `POST /api/auth/logout/` - Logout
- `POST /api/auth/refresh/` - Refresh token

### Gestión de Usuarios
- `GET /api/users/` - Lista de usuarios con paginación
- `GET /api/users/{id}/` - Obtener usuario específico
- `PUT /api/users/{id}/` - Actualizar usuario específico
- `GET /api/users/me/` - Perfil del usuario actual

### Gestión de Tareas
- `GET /api/tasks/` - Lista de tareas (con filtros, búsqueda, paginación)
- `POST /api/tasks/` - Crear nueva tarea
- `GET /api/tasks/{id}/` - Obtener tarea específica
- `PUT /api/tasks/{id}/` - Actualizar tarea (completa)
- `PATCH /api/tasks/{id}/` - Actualizar tarea (parcial)
- `DELETE /api/tasks/{id}/` - Eliminar tarea

### Operaciones de Tareas
- `POST /api/tasks/{id}/assign/` - Asignar tarea a usuario
- `POST /api/tasks/{id}/comments/` - Añadir comentario a tarea
- `GET /api/tasks/{id}/comments/` - Obtener comentarios de tarea
- `GET /api/tasks/{id}/history/` - Obtener historial de tarea

### Documentación Interactiva
- `GET /api/auth/docs` - Swagger UI para Authentication API
- `GET /api/users/docs` - Swagger UI para User Management API  
- `GET /api/tasks/docs` - Swagger UI para Task Management API
- `GET /api/auth/openapi.json` - Especificación OpenAPI Auth
- `GET /api/users/openapi.json` - Especificación OpenAPI Users
- `GET /api/tasks/openapi.json` - Especificación OpenAPI Tasks