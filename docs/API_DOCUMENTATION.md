# API Documentation

## Overview

**MUY BÁSICAMENTE**, esta API proporciona endpoints para gestión de tareas y autenticación de usuarios. La API está construida con Django Ninja e incluye documentación automática con Swagger.

## Documentación Interactiva

**Swagger UI** (Recomendado para pruebas):
- **API Completa**: http://localhost:8000/api/docs/
- **Health Check**: http://localhost:8000/health/

## Configuración Rápida

```bash
# Iniciar el sistema
docker-compose up

# Verificar que funciona
curl http://localhost:8000/health/
# Respuesta: {"status": "healthy", "database": "healthy", "redis": "healthy"}
```

## API de Autenticación

**Base URL**: `/api/auth/`

### Registro de Usuario
```bash
POST /api/auth/register/
{
  "username": "usuario_test",
  "email": "test@example.com", 
  "password1": "password123",
  "password2": "password123"
}
```

### Inicio de Sesión  
```bash
POST /api/auth/login/
{
  "username": "usuario_test",
  "password": "password123"
}
```

### Listar Usuarios (con búsqueda)
```bash
GET /api/auth/users/?search=test&page=1&page_size=10
```

## API de Gestión de Tareas

**Base URL**: `/api/tasks/`

### Listar Tareas
```bash
GET /api/tasks/tasks/?page=1&page_size=10&status=todo
```

### Crear Tarea
```bash
POST /api/tasks/tasks/
{
  "title": "Nueva Tarea",
  "description": "Descripción de la tarea",
  "status": "todo",
  "priority": "medium"
}
```

### Actualizar Tarea
```bash
PUT /api/tasks/tasks/{id}/
{
  "title": "Tarea Actualizada",
  "status": "in_progress"
}
```

### Eliminar Tarea
```bash
DELETE /api/tasks/tasks/{id}/
```

## Campos Principales

### Task (Tarea)
- `title` (string): Título de la tarea
- `description` (string): Descripción detallada
- `status` (string): "todo", "in_progress", "done", "cancelled"
- `priority` (string): "low", "medium", "high", "urgent"
- `assigned_to` (int): ID del usuario asignado
- `team` (int): ID del equipo
- `due_date` (datetime): Fecha límite
- `tags` (array): Lista de etiquetas

### User (Usuario)
- `username` (string): Nombre de usuario único
- `email` (string): Email del usuario
- `first_name` (string): Nombre
- `last_name` (string): Apellido

## Respuestas de Error

### 400 Bad Request
```json
{
  "detail": "Error de validación",
  "errors": {
    "title": ["Este campo es requerido"]
  }
}
```

### 401 Unauthorized
```json
{
  "detail": "Credenciales de autenticación no proporcionadas"
}
```

### 404 Not Found
```json
{
  "detail": "No encontrado"
}
```

## Ejemplos de Uso Completos

### Crear usuario y su primera tarea
```bash
# 1. Registrar usuario
curl -X POST http://localhost:8000/api/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "juan",
    "email": "juan@example.com",
    "password1": "mipassword123",
    "password2": "mipassword123"
  }'

# 2. Iniciar sesión
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "juan",
    "password": "mipassword123"
  }'

# 3. Crear tarea
curl -X POST http://localhost:8000/api/tasks/tasks/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "title": "Mi primera tarea",
    "description": "Descripción de mi tarea",
    "priority": "high",
    "status": "todo"
  }'
```

### Buscar y filtrar tareas
```bash
# Buscar tareas por título
GET /api/tasks/tasks/?search=proyecto

# Filtrar por estado
GET /api/tasks/tasks/?status=in_progress

# Filtrar por prioridad
GET /api/tasks/tasks/?priority=high

# Tareas asignadas a un usuario
GET /api/tasks/tasks/?assigned_to=1

# Combinar filtros
GET /api/tasks/tasks/?status=todo&priority=high&page=1
```

## Status Codes

- `200 OK`: Operación exitosa
- `201 Created`: Recurso creado exitosamente
- `400 Bad Request`: Error en los datos enviados
- `401 Unauthorized`: Sin autenticación
- `403 Forbidden`: Sin permisos
- `404 Not Found`: Recurso no encontrado
- `500 Internal Server Error`: Error del servidor

## Notas Importantes

1. **Autenticación**: La mayoría de endpoints requieren autenticación
2. **Paginación**: Las listas incluyen paginación automática
3. **Validación**: Todos los campos son validados automáticamente
4. **Rate Limiting**: Hay límites de velocidad para prevenir abuso
5. **CORS**: Configurado para desarrollo local

## Swagger UI

Para una experiencia interactiva completa, visita:
**http://localhost:8000/api/docs/**

Aquí puedes:
- Probar todos los endpoints
- Ver esquemas de datos
- Autenticarte y hacer peticiones reales
- Descargar la especificación OpenAPI

### Delete Task
```bash
DELETE /api/tasks/ninja/tasks/{id}/
```

### Advanced Search
```bash
GET /api/tasks/ninja/tasks/search/?q=keyword&filters=status:todo,priority:high
```

## Response Format

All responses follow this format:
```json
{
  "status": "success|error",
  "data": { ... },
  "message": "Optional message"
}
```

## Authentication

Most endpoints require authentication. Include the session cookie or JWT token in requests.

## Error Handling

- **400**: Bad Request - Invalid data
- **401**: Unauthorized - Authentication required
- **403**: Forbidden - Insufficient permissions  
- **404**: Not Found - Resource not found
- **500**: Internal Server Error

For detailed interactive documentation with all endpoints, schemas, and examples, visit the Swagger UI links above.
```bash
curl -X POST "http://localhost:8000/api/auth/ninja/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "nuevo_usuario",
    "email": "usuario@email.com", 
    "password": "mi_password_seguro"
  }'
```

### 🔑 Login (Obtener JWT Token)
```bash
curl -X POST "http://localhost:8000/api/auth/ninja/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "nuevo_usuario",
    "password": "mi_password_seguro"
  }'
```

**Respuesta esperada:**
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbG...",
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbG...",
  "token_type": "Bearer",
  "expires_in": 900
}
```

### 🔄 Renovar Token
```bash
curl -X POST "http://localhost:8000/api/auth/ninja/auth/refresh" \
  -H "Content-Type: application/json" \
  -d '{
    "refresh_token": "tu_refresh_token_aqui"
  }'
```

### 🚪 Logout
```bash
curl -X POST "http://localhost:8000/api/auth/ninja/auth/logout" \
  -H "Content-Type: application/json"
```

## 👥 2. User Management API

**Base URL**: `http://localhost:8000/api/auth/ninja/users/`

### 📋 Listar Usuarios
```bash
# Básico
curl -X GET "http://localhost:8000/api/auth/ninja/users/"

# Con filtros y paginación
curl -X GET "http://localhost:8000/api/auth/ninja/users/?search=test&page=1&page_size=10"
```

### 👤 Obtener Usuario Específico
```bash
curl -X GET "http://localhost:8000/api/auth/ninja/users/1"
```

### 📝 Actualizar Usuario
```bash
curl -X PUT "http://localhost:8000/api/auth/ninja/users/1" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "nuevo_nombre",
    "email": "nuevo@email.com",
    "first_name": "Nombre",
    "last_name": "Apellido"
  }'
```

### 🔍 Perfil Actual
```bash
curl -X GET "http://localhost:8000/api/auth/ninja/users/me"
```

## 📋 3. Task Management API

**Base URL**: `http://localhost:8000/api/tasks/ninja/`

### 📋 Listar Tareas con Búsqueda Optimizada
```bash
# Búsqueda básica (compatible)
curl -X GET "http://localhost:8000/api/tasks/ninja/?search=proyecto&page=1&page_size=10"

# Búsqueda full-text (PostgreSQL optimizada)
curl -X GET "http://localhost:8000/api/tasks/ninja/?search=importante+urgente&page=1&page_size=10"

# Búsqueda con filtros combinados
curl -X GET "http://localhost:8000/api/tasks/ninja/?search=desarrollo&status=in_progress&priority=high"

# Con ordenamiento por relevancia (full-text)
curl -X GET "http://localhost:8000/api/tasks/ninja/?search=api+documentacion&page=1&page_size=5"
```

**Respuesta optimizada (incluye ranking de relevancia):**
```json
{
  "status": "success",
  "data": {
    "results": [
      {
        "id": 1,
        "title": "API Documentation Update",
        "description": "Update API documentation with new endpoints",
        "search_rank": 0.9876,  // ⭐ Nuevo: relevancia de búsqueda
        "status": "in_progress",
        "priority": "high",
        "created_by": {
          "id": 1,
          "username": "admin"
        },
        "tags": ["documentation", "api"],
        "estimated_hours": "8.00",
        "due_date": "2025-09-10T18:00:00Z"
      }
    ],
    "total": 1,
    "page": 1,
    "page_size": 10,
    "total_pages": 1
  }
}
```

**Filtros disponibles:**
- `search`: Buscar en título y descripción
- `status`: `todo`, `in_progress`, `review`, `done`, `cancelled`
- `priority`: `low`, `medium`, `high`, `critical`
- `assigned_to`: ID del usuario asignado
- `created_by`: ID del creador
- `tag`: Nombre del tag
- `is_overdue`: `true` o `false`

### ➕ Crear Tarea
```bash
curl -X POST "http://localhost:8000/api/tasks/ninja/" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Nueva Tarea",
    "description": "Descripción de la tarea",
    "status": "todo",
    "priority": "medium",
    "due_date": "2025-09-15T15:30:00Z",
    "estimated_hours": 5.5,
    "metadata": {"source": "api"}
  }'
```

### 🔍 Obtener Tarea Específica
```bash
curl -X GET "http://localhost:8000/api/tasks/ninja/1"
```

### 📝 Actualizar Tarea Completa (PUT)
```bash
curl -X PUT "http://localhost:8000/api/tasks/ninja/1" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Tarea Actualizada",
    "description": "Nueva descripción",
    "status": "in_progress",
    "priority": "high",
    "due_date": "2025-09-20T10:00:00Z",
    "estimated_hours": 8,
    "actual_hours": 2.5
  }'
```

### 🔧 Actualizar Tarea Parcial (PATCH)
```bash
curl -X PATCH "http://localhost:8000/api/tasks/ninja/1" \
  -H "Content-Type: application/json" \
  -d '{
    "status": "done",
    "actual_hours": 6.5
  }'
```

### 🗑️ Eliminar Tarea (Soft Delete)
```bash
curl -X DELETE "http://localhost:8000/api/tasks/ninja/1"
```

## 🔧 4. Task Operations API

**Base URL**: `http://localhost:8000/api/tasks/ninja/{task_id}/`

### 👥 Asignar Usuarios a Tarea
```bash
curl -X POST "http://localhost:8000/api/tasks/ninja/1/assign/" \
  -H "Content-Type: application/json" \
  -d '{
    "user_ids": [1, 2],
    "is_primary": false
  }'
```

### 💬 Agregar Comentario
```bash
curl -X POST "http://localhost:8000/api/tasks/ninja/1/comments/" \
  -H "Content-Type: application/json" \
  -d '{
    "content": "Este es mi comentario sobre la tarea"
  }'
```

### 📋 Listar Comentarios
```bash
# Básico
curl -X GET "http://localhost:8000/api/tasks/ninja/1/comments/"

# Con paginación
curl -X GET "http://localhost:8000/api/tasks/ninja/1/comments/?page=1&page_size=10"
```

### 📊 Historial de Tarea
```bash
# Básico
curl -X GET "http://localhost:8000/api/tasks/ninja/1/history/"

# Filtrado por acción
curl -X GET "http://localhost:8000/api/tasks/ninja/1/history/?action=assigned"

# Con paginación
curl -X GET "http://localhost:8000/api/tasks/ninja/1/history/?page=1&page_size=5"
```

**Acciones disponibles en historial:**
- `created`: Tarea creada
- `updated`: Tarea actualizada
- `assigned`: Usuario asignado
- `unassigned`: Usuario desasignado
- `status_changed`: Cambio de estado
- `archived`: Tarea archivada

## 📝 5. Ejemplos de Flujo Completo

### Ejemplo 1: Crear y Gestionar una Tarea
```bash
# 1. Crear tarea
curl -X POST "http://localhost:8000/api/tasks/ninja/" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Implementar nueva funcionalidad",
    "description": "Desarrollar el módulo de reportes",
    "status": "todo",
    "priority": "high",
    "due_date": "2025-09-25T17:00:00Z",
    "estimated_hours": 16
  }'

# 2. Asignar usuarios (asumiendo que la tarea creada tiene ID 2)
curl -X POST "http://localhost:8000/api/tasks/ninja/2/assign/" \
  -H "Content-Type: application/json" \
  -d '{"user_ids": [1], "is_primary": true}'

# 3. Agregar comentario
curl -X POST "http://localhost:8000/api/tasks/ninja/2/comments/" \
  -H "Content-Type: application/json" \
  -d '{"content": "Iniciando análisis de requisitos"}'

# 4. Actualizar progreso
curl -X PATCH "http://localhost:8000/api/tasks/ninja/2" \
  -H "Content-Type: application/json" \
  -d '{"status": "in_progress", "actual_hours": 4}'

# 5. Ver historial
curl -X GET "http://localhost:8000/api/tasks/ninja/2/history/"
```

### Ejemplo 2: Buscar y Filtrar Tareas
```bash
# Buscar tareas pendientes de alta prioridad
curl -X GET "http://localhost:8000/api/tasks/ninja/?status=todo&priority=high"

# Buscar tareas asignadas a un usuario específico
curl -X GET "http://localhost:8000/api/tasks/ninja/?assigned_to=1"

# Buscar tareas con texto específico
curl -X GET "http://localhost:8000/api/tasks/ninja/?search=bug"

# Buscar tareas vencidas
curl -X GET "http://localhost:8000/api/tasks/ninja/?is_overdue=true"
```

## 📋 6. Códigos de Respuesta

| Código | Descripción |
|--------|-------------|
| 200 | OK - Operación exitosa |
| 201 | Created - Recurso creado exitosamente |
| 400 | Bad Request - Error en los datos enviados |
| 401 | Unauthorized - Token inválido o expirado |
| 404 | Not Found - Recurso no encontrado |
| 500 | Internal Server Error - Error del servidor |

## 🛠️ 7. Herramientas Recomendadas

### Para Pruebas Manuales:
1. **Swagger UI** (Incluido): http://localhost:8000/api/tasks/ninja/docs
2. **Postman**: Importar las URLs de OpenAPI JSON
3. **curl**: Ejemplos incluidos en esta documentación

### Para Desarrollo:
1. **OpenAPI Specification**: Disponible en `/openapi.json`
2. **Generadores de Cliente**: Usar OpenAPI para generar SDKs
3. **Validación**: Los schemas están incluidos en las respuestas

## 🔍 8. Debugging y Logs

### Verificar Logs del Servicio
```bash
# Logs generales
docker-compose logs web --tail=50

# Logs en tiempo real
docker-compose logs -f web
```

### Verificar Estado de Servicios
```bash
docker-compose ps
```

### Acceder al Shell de Django
```bash
docker-compose exec web python manage.py shell
```

## ⚠️ 9. Notas Importantes

1. **Fechas**: Usar formato ISO 8601 (YYYY-MM-DDTHH:MM:SSZ)
2. **Paginación**: Máximo 100 elementos por página
3. **Soft Delete**: Las tareas eliminadas se archivan, no se borran
4. **JWT Tokens**: Access token expira en 15 minutos, refresh en 7 días
5. **CORS**: Configurado para desarrollo local
6. **Rate Limiting**: No implementado (recomendado para producción)

## 🎯 10. Próximos Pasos

Para usar en producción, considerar:
- Implementar autenticación JWT completa
- Configurar HTTPS
- Implementar rate limiting
- Configurar CORS para dominios específicos
- Optimizar queries con cache
- Implementar logging estructurado
- Configurar monitoreo

---

**¡API completamente funcional y lista para usar! 🚀**

Para cualquier duda, consultar la documentación interactiva en Swagger o revisar los ejemplos incluidos.
