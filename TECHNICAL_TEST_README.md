# Proyecto Django Limpio - Prueba Técnica

## 🎯 Resumen del Proyecto

Este proyecto ha sido **completamente simplificado y limpiado** de un sistema Django complejo para adaptarlo como prueba técnica. Se han eliminado componentes innecesarios y se ha mantenido únicamente la funcionalidad esencial.

## ✅ Estado del Proyecto

**PROYECTO COMPLETAMENTE FUNCIONAL** ✅
- ✅ Contenedores Docker funcionando correctamente
- ✅ Base de datos PostgreSQL operativa
- ✅ Sistema de caché Redis funcionando
- ✅ Celery Worker y Beat configurados y operativos
- ✅ Aplicación Django ejecutándose en http://localhost:8000
- ✅ Panel de administración accesible en http://localhost:8000/admin/
- ✅ Sistema de gestión de tareas completamente implementado

## 🏗️ Arquitectura Simplificada

### Servicios Docker (5 contenedores):
1. **django_web** - Aplicación Django principal
2. **postgres_db** - Base de datos PostgreSQL 15
3. **redis_cache** - Sistema de caché y broker para Celery
4. **celery_worker** - Procesamiento de tareas en segundo plano
5. **celery_beat** - Programador de tareas periódicas

### Aplicaciones Django:
1. **authentication** - Sistema de autenticación personalizado
2. **tasks** - Sistema completo de gestión de tareas
3. **chat** - Sistema básico de chat (mantenido)

## 🚀 Cómo Ejecutar

### Requisitos Previos
- Docker y Docker Compose instalados
- Puerto 8000 disponible

### Ejecución
```bash
# Iniciar todos los servicios
docker-compose up --build

# La aplicación estará disponible en:
# - Web: http://localhost:8000
# - Admin: http://localhost:8000/admin/
```

## 📊 Sistema de Gestión de Tareas

### Modelos Implementados:
- **Task** - Tareas con prioridad, estado, fechas límite
- **TaskAssignment** - Asignación de tareas a usuarios
- **Team** - Equipos de trabajo
- **Tag** - Etiquetas para organización
- **Priority** - Niveles de prioridad
- **Status** - Estados de las tareas

### Funcionalidades:
- ✅ CRUD completo de tareas
- ✅ Asignación de tareas a usuarios
- ✅ Sistema de prioridades y estados
- ✅ Organización por equipos y etiquetas
- ✅ Notificaciones por email (Celery)
- ✅ Métricas y reportes automáticos
- ✅ API REST con django-ninja
- ✅ Interface web con Bootstrap

### Tareas Celery Disponibles:
1. `send_task_notification` - Notificaciones por email
2. `check_overdue_tasks` - Revisión de tareas vencidas
3. `auto_assign_tasks` - Asignación automática
4. `calculate_team_velocity` - Métricas de equipo
5. `generate_daily_summary` - Resúmenes diarios
6. `cleanup_archived_tasks` - Limpieza de tareas archivadas

## 🗑️ Componentes Eliminados

Durante la limpieza se eliminaron:
- ❌ Nginx (proxy reverso)
- ❌ HashiCorp Vault (gestión de secretos)
- ❌ SSL/TLS personalizado
- ❌ WAF (Web Application Firewall)
- ❌ Aplicación `game` (juegos)
- ❌ Aplicación `tournament` (torneos)
- ❌ Aplicación `dashboard` (dashboard complejo)
- ❌ Autenticación 42 OAuth
- ❌ Configuración compleja de seguridad

## ⚙️ Configuración Técnica

### Base de Datos:
- PostgreSQL 15.14
- Base de datos: `task_management_db`
- Usuario: `postgres`
- Puerto: 5432

### Redis:
- Redis 7.4.5
- Puerto: 6379
- Configurado para Celery y caché

### Django:
- Django 5.2.6
- Python 3.10
- Django REST Framework
- Bootstrap frontend
- Celery 5.5.3

## 📁 Estructura Final

```
srcs/
├── django/
│   ├── authentication/     # Sistema de usuarios
│   ├── tasks/             # Gestión de tareas
│   ├── chat/              # Chat básico
│   ├── main/              # Configuración principal
│   ├── requirements.txt   # Dependencias Python
│   └── manage.py          # Django management
├── db/                    # PostgreSQL
├── front/                 # Frontend estático
└── docker-compose.yml     # Orquestación
```

## 🔧 Configuración de Desarrollo

### Variables de Entorno:
```bash
DEBUG=True
SECRET_KEY=your-secret-key
DATABASE_URL=postgresql://postgres:postgres@postgres_db:5432/task_management_db
REDIS_URL=redis://redis:6379/0
```

### Comandos Útiles:
```bash
# Crear superusuario
docker-compose exec django_web python manage.py createsuperuser

# Ejecutar migraciones
docker-compose exec django_web python manage.py migrate

# Acceso a shell Django
docker-compose exec django_web python manage.py shell

# Ver logs
docker-compose logs -f django_web
```

## 🎯 Objetivo de la Prueba Técnica

Este proyecto simplificado permite evaluar:
1. **Desarrollo Django** - Modelos, vistas, templates
2. **API Development** - django-ninja REST API
3. **Procesamiento Asíncrono** - Celery tasks
4. **Gestión de Base de Datos** - PostgreSQL, migraciones
5. **Containerización** - Docker, docker-compose
6. **Frontend** - Bootstrap, JavaScript
7. **Testing** - Unit tests disponibles

## ✨ Próximos Pasos

Para continuar el desarrollo:
1. Implementar autenticación JWT
2. Añadir tests unitarios completos
3. Implementar WebSocket para chat en tiempo real
4. Añadir métricas avanzadas con Prometheus
5. Implementar CI/CD pipeline

---

**Estado:** ✅ PROYECTO COMPLETAMENTE FUNCIONAL Y LISTO PARA PRUEBA TÉCNICA

**Tiempo de setup:** ~5 minutos con `docker-compose up --build`

**Acceso:** http://localhost:8000
