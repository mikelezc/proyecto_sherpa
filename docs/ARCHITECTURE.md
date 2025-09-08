# Architecture Documentation

## Descripción General del Sistema

Este sistema de gestión de tareas utiliza una **arquitectura basada en contenedores** implementada con Docker Compose. El diseño se basa en contenedores especializados que trabajan juntos para proporcionar una solución escalable y mantenible, con Django como núcleo central.

## Componentes Principales

### 1. Django Web Application (`django_web`)
- **Tecnología**: Django 5.2.6 + Django Ninja 0.22.0
- **Puerto**: 8000 (expuesto directamente)
- **Función**: API REST + Frontend Web
- **Características Implementadas**:
  - Sistema de autenticación completo con Django Auth
  - API REST con Django Ninja y documentación Swagger automática
  - Frontend web con Django Templates + Bootstrap 5
  - Rate limiting implementado con Redis
  - Validación robusta de datos con Pydantic (vía Django Ninja)
  - Health checks en `/health/`

### 2. PostgreSQL Database (`postgres_db`)
- **Tecnología**: PostgreSQL 15
- **Puerto**: 5432
- **Función**: Base de datos principal
- **Optimizaciones Implementadas**:
  - Full-text search con SearchVector y GinIndex
  - Índices compuestos para consultas complejas
  - Database constraints para integridad de datos
  - Configuración optimizada para desarrollo

### 3. Redis Cache (`redis_cache`)
- **Tecnología**: Redis 7-alpine
- **Puerto**: 6379
- **Funciones Activas**:
  - Cache de sesiones Django
  - Message broker para Celery
  - Result backend para tareas asíncronas
  - Storage para rate limiting

### 4. Celery Worker (`celery_worker`)
- **Función**: Procesamiento asíncrono de tareas en background
- **Tareas Implementadas** (6 activas):
  - `send_task_notification`: Envío de notificaciones por email
  - `generate_daily_summary`: Generación de resúmenes diarios
  - `check_overdue_tasks`: Verificación de tareas vencidas
  - `cleanup_archived_tasks`: Limpieza automática de datos archivados
  - `auto_assign_tasks`: Asignación automática de tareas
  - `calculate_team_velocity`: Cálculo de métricas de equipos

### 5. Celery Beat (`celery_beat`)
- **Función**: Scheduler para tareas periódicas
- **Configuración**: Django Celery Beat con almacenamiento en PostgreSQL
- **Estado**: Activo y funcionando con DatabaseScheduler
  - Resúmenes diarios a las 9:00 AM
  - Verificación de tareas vencidas cada hora
  - Limpieza de datos cada domingo a medianoche

## Flujo de Datos Real

```
Cliente/Browser → Django App (puerto 8000) → PostgreSQL
                      ↓ [Sessions/Cache]
                   Redis Cache
                      ↓ [Task Queue]
                 Celery Workers
```

**Nota**: El sistema expone Django directamente en el puerto 8000, sin proxy reverso ni load balancer.

## Arquitectura de Seguridad (Implementada)

### Capas de Protección Activas:
1. **Rate Limiting**: Implementado con RateLimitService usando Redis
   - Login: 10 intentos cada 5 minutos
   - Email verification: 10 intentos cada 30 minutos
   - Profile updates: 5 intentos cada hora
2. **Autenticación**: Django Authentication + JWT para API
3. **Validación**: Validación estricta con Pydantic (Django Ninja) y Django Forms
4. **Base de Datos**: Queries parametrizadas, protección contra SQL injection
5. **Conteneurización**: Aislamiento de servicios con Docker

## Patrones de Diseño Implementados

### 1. Repository Pattern
- Managers personalizados en Django para lógica de consultas específicas
- Separación entre lógica de negocio y acceso a datos

### 2. Observer Pattern  
- Django Signals para reaccionar a cambios en modelos
- Actualización automática de search vectors cuando se modifican tareas

### 3. Factory Pattern
- Management commands para inicialización de datos (`seed_data.py`)
- Creación consistente de datos de prueba

### 4. Service Layer Pattern
- AuthService, ProfileService, RateLimitService
- Lógica de negocio centralizada en servicios

## Monitoreo y Salud del Sistema

### Health Checks Implementados:
- **Endpoint principal**: `/health/` - Estado general del sistema
- **Base de datos**: Verificación de conectividad PostgreSQL
- **Cache**: Verificación de conectividad Redis
- **Response Format**: JSON con status de cada componente

### Logging Actual:
- **Formato**: Django logging estándar (no JSON estructurado)
- **Niveles**: DEBUG, INFO, WARNING, ERROR configurables
- **Destino**: Console output (no rotación automática)