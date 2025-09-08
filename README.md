# Task Management System

Sistema completo de gestión de tareas desarrollado con Django, con arquitectura de microservicios usando Docker y procesamiento asíncrono con Celery.

La estructura de docker, la api de autenticación y manejo de usuarios están basadas en este otro repo que desarrollé usando este mismo framework.

https://github.com/mikelezc/42_Transcendence

Aquí se puede ver la misma base, pero aplicada con otras funciones interesantes como notificaciones vía mail, JWT, 2FA con claves, encriptación de datos antes de ser ingresados en la db, balanceador de carga, front que se sirve diréctamente de la API, un WAF, etc. Muy recomendable inspeccionarlo.

## 🎯 Para Examinadores - Verificación Rápida

```bash
# Opción 1: Script automatizado (recomendado)
./verify_for_examiners.sh

# Opción 2: Manual
cp .env.sample .env
docker-compose up -d
curl http://localhost:8000/health/
```

**📋 Ver [EXAMINER_GUIDE.md](EXAMINER_GUIDE.md) para instrucciones detalladas**

## Quick Start

### 1. Clonar el repositorio
```bash
git clone <repo>
cd <task-management-system>
```

### 2. Configurar variables de entorno
```bash
cp .env.sample .env
# IMPORTANTE: Editar .env con credenciales seguras únicas
# NUNCA usar las credenciales de ejemplo en producción
```

**⚠️ IMPORTANTE PARA SEGURIDAD:**
- El archivo `.env` contiene credenciales sensibles y NO debe committearse
- Generar nuevas claves secretas: `python3 -c "import secrets; print(secrets.token_urlsafe(50))"`
- Cambiar todas las passwords por valores seguros únicos
- El archivo `.env.sample` sirve solo como plantilla

### 3. Ejecutar con Docker
```bash
docker-compose up
```

### 4. Acceso a la aplicación
- **Aplicación Web**: http://localhost:8000
- **Panel Admin**: http://localhost:8000/admin/ (Usuario: `demo_admin`, Password: `demo123`)
- **Health Check**: http://localhost:8000/health/

## Documentación Completa

- **[🎯 EXAMINER GUIDE](EXAMINER_GUIDE.md)** - **Guía paso a paso para evaluadores**
- **[Architecture](docs/ARCHITECTURE.md)** - Descripción de la arquitectura del sistema  
- **[Decisions](docs/DECISIONS.md)** - Decisiones técnicas y características implementadas
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