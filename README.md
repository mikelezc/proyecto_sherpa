# Task Management System

Sistema completo de gestión de tareas desarrollado con Django, con arquitectura de microservicios usando Docker y procesamiento asíncrono con Celery.

La estructura de docker, la api de autenticación y manejo de usuarios están basadas en este otro repo que desarrollé usando este mismo framework.

https://github.com/mikelezc/42_Transcendence

Aquí se puede ver la misma base, pero aplicada con otras funciones interesantes como notificaciones vía mail, JWT, 2FA con claves, encriptación de datos antes de ser ingresados en la db, balanceador de carga, front que se sirve diréctamente de la API, un WAF, etc. Muy recomendable inspeccionarlo.

## Quick Start

### 1. Clonar el repositorio
```bash
git clone <repo>
cd <task-management-system>
```

### 2. Configurar variables de entorno
```bash
cp .env.sample .env
# Editar .env con nuevas credenciales si es necesario
```

### 3. Ejecutar con Docker
```bash
docker-compose up
```

### 4. Acceso a la aplicación
- **Aplicación Web**: http://localhost:8000
- **Panel Admin**: http://localhost:8000/admin/ (Usuario: `demo_admin`, Password: `demo123`)
- **Health Check**: http://localhost:8000/health/

## Documentación Completa

- **[Architecture](docs/ARCHITECTURE.md)** - Descripción de la arquitectura del sistema  
- **[Decisions](docs/DECISIONS.md)** - Decisiones técnicas y características implementadas
- **[API Documentation](docs/API_DOCUMENTATION.md)** - Guía completa de la API

- **Endpoints de la API en funcionamiento**:
  - Tasks API: http://localhost:8000/api/tasks/ninja/docs
  - Auth API: http://localhost:8000/api/auth/ninja/docs

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

### Autenticación (Django Ninja)
- `POST /api/auth/ninja/auth/register/` - Registro de usuario
- `POST /api/auth/ninja/auth/login/` - Login
- `POST /api/auth/ninja/auth/logout/` - Logout
- `GET /api/auth/ninja/users/` - Lista de usuarios

### Tareas (Django Ninja)
- `GET /api/tasks/ninja/tasks/` - Lista de tareas
- `POST /api/tasks/ninja/tasks/` - Crear tarea
- `GET /api/tasks/ninja/tasks/{id}/` - Detalle de tarea
- `PUT /api/tasks/ninja/tasks/{id}/` - Actualizar tarea
- `DELETE /api/tasks/ninja/tasks/{id}/` - Eliminar tarea

### Documentación Interactiva
- `GET /api/tasks/ninja/docs` - Swagger UI para Tasks API
- `GET /api/auth/ninja/docs` - Swagger UI para Auth API
- `GET /api/tasks/ninja/openapi.json` - Especificación OpenAPI Tasks
- `GET /api/auth/ninja/openapi.json` - Especificación OpenAPI Auth