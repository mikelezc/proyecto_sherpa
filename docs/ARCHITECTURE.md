# Architecture Documentation

## System Overview

Este sistema de gestión de tareas utiliza una **arquitectura de microservicios** implementada con Docker Compose, que incluye los siguientes componentes principales:

## Servicios Core

### 1. Django Web Application (`django_web`)
- **Tecnología**: Django 5.2.6 + Django Ninja
- **Puerto**: 8000
- **Función**: API REST + Frontend Templates
- **Características**:
  - Sistema de autenticación completo
  - API REST con documentación automática (Swagger)
  - Frontend con Django Templates + Bootstrap 5
  - Rate limiting y seguridad

### 2. PostgreSQL Database (`postgres_db`)
- **Tecnología**: PostgreSQL 15.14
- **Puerto**: 5432
- **Función**: Base de datos principal
- **Optimizaciones**:
  - Full-text search con SearchVector y GinIndex
  - Composite indexes para performance
  - Database constraints para integridad

### 3. Redis Cache (`redis_cache`)
- **Tecnología**: Redis 7-alpine
- **Puerto**: 6379
- **Función**: Cache + Message Broker para Celery
- **Uso**: Sessions, cache, Celery broker/backend

### 4. Celery Worker (`celery_worker`)
- **Función**: Procesamiento asíncrono de tareas
- **Tareas implementadas**:
  - Notificaciones por email
  - Resúmenes diarios
  - Limpieza de datos
  - Verificación de tareas vencidas

### 5. Celery Beat (`celery_beat`)
- **Función**: Scheduler para tareas periódicas
- **Configuración**: Database scheduler con Django Celery Beat

## Data Flow

```
Client Request → nginx/WAF → Django App → PostgreSQL
                              ↓
                           Redis Cache
                              ↓
                        Celery Workers
```

## Security Architecture

- **WAF**: Web Application Firewall con ModSecurity
- **Rate Limiting**: Implementado en Django
- **Authentication**: Django session-based + API tokens
- **SSL/TLS**: Certificates para comunicaciones seguras
- **Database**: Encrypted connections con SSL

## Scalability

- **Horizontal scaling**: Múltiples workers Celery
- **Database optimization**: Indexes y query optimization
- **Caching strategy**: Redis para sessions y cache
- **Containerization**: Docker para deployment consistente

## Monitoring & Health

- **Health checks**: Endpoint `/health/` para monitoreo
- **Logging**: Structured logging en todos los servicios
- **Metrics**: Celery task monitoring

Este diseño permite escalabilidad horizontal y mantiene separation of concerns entre componentes.
