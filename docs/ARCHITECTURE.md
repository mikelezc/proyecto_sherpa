# Architecture Documentation

## System Overview

This task management system uses a **container-based architecture** implemented with Docker Compose. The design is based on specialized containers that work together to provide a scalable and maintainable solution, with Django as the central core.

## Main Components

### 1. Django Web Application (`django_web`)
- **Technology**: Django 5.2.6 + Django Ninja 0.22.0
- **Port**: 8000 (directly exposed)
- **Function**: REST API + Web Frontend
- **Implemented Features**:
  - Complete authentication system with Django Auth
  - REST API with Django Ninja and automatic Swagger documentation
  - Web frontend with Django Templates + Bootstrap 5
  - Rate limiting implemented with Redis
  - Robust data validation with Pydantic (via Django Ninja)
  - Health checks at `/health/`

### 2. PostgreSQL Database (`postgres_db`)
- **Technology**: PostgreSQL 15
- **Port**: 5432
- **Function**: Main database
- **Implemented Optimizations**:
  - Full-text search with SearchVector and GinIndex
  - Composite indexes for complex queries
  - Database constraints for data integrity
  - Optimized configuration for development

### 3. Redis Cache (`redis_cache`)
- **Technology**: Redis 7-alpine
- **Port**: 6379
- **Active Functions**:
  - Django session cache
  - Message broker for Celery
  - Result backend for asynchronous tasks
  - Storage for rate limiting

### 4. Celery Worker (`celery_worker`)
- **Function**: Asynchronous background task processing
- **Implemented Tasks** (6 active):
  - `send_task_notification`: Email notification sending
  - `generate_daily_summary`: Daily summary generation
  - `check_overdue_tasks`: Overdue task verification
  - `cleanup_archived_tasks`: Automatic cleanup of archived data
  - `auto_assign_tasks`: Automatic task assignment
  - `calculate_team_velocity`: Team metrics calculation

### 5. Celery Beat (`celery_beat`)
- **Function**: Scheduler for periodic tasks
- **Configuration**: Django Celery Beat with PostgreSQL storage
- **Status**: Active and running with DatabaseScheduler
  - Daily summaries at 9:00 AM
  - Overdue task verification every hour
  - Data cleanup every Sunday at midnight

## Real Data Flow

```
Client/Browser → Django App (port 8000) → PostgreSQL
                      ↓ [Sessions/Cache]
                   Redis Cache
                      ↓ [Task Queue]
                 Celery Workers
```

**Note**: The system exposes Django directly on port 8000, without reverse proxy or load balancer.

## Security Architecture (Implemented)

### Active Protection Layers:
1. **Rate Limiting**: Implemented with RateLimitService using Redis
   - Login: 10 attempts every 5 minutes
   - Email verification: 10 attempts every 30 minutes
   - Profile updates: 5 attempts every hour
2. **Authentication**: Django Authentication + JWT for API
3. **Validation**: Strict validation with Pydantic (Django Ninja) and Django Forms
4. **Database**: Parameterized queries, SQL injection protection
5. **Containerization**: Service isolation with Docker

## Implemented Design Patterns

### 1. Repository Pattern
- Custom managers in Django for specific query logic
- Separation between business logic and data access

### 2. Observer Pattern  
- Django Signals to react to model changes
- Automatic search vector updates when tasks are modified

### 3. Factory Pattern
- Management commands for data initialization (`seed_data.py`)
- Consistent test data creation

### 4. Service Layer Pattern
- AuthService, ProfileService, RateLimitService
- Centralized business logic in services

## System Monitoring and Health

### Implemented Health Checks:
- **Main endpoint**: `/health/` - General system status
- **Database**: PostgreSQL connectivity verification
- **Cache**: Redis connectivity verification
- **Response Format**: JSON with status of each component

### Current Logging:
- **Format**: Standard Django logging (not structured JSON)
- **Levels**: DEBUG, INFO, WARNING, ERROR configurable
- **Destination**: Console output (no automatic rotation)