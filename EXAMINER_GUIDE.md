# 🎯 Guía para Examinadores - Proyecto Task Management System

## 📋 Pasos de Verificación Recomendados

### 1. Clonación y Configuración Inicial

```bash
# Clonar el repositorio
git clone <repository-url>
cd proyecto_sherpa

# Verificar que NO existe archivo .env (correcto por seguridad)
ls -la | grep .env
# Resultado esperado: solo debe aparecer .env.sample
```

### 2. Configuración de Variables de Entorno

```bash
# Copiar plantilla de configuración
cp .env.sample .env

# Verificar que el archivo se creó
ls -la .env

# OPCIONAL: Revisar contenido del .env generado
cat .env
```

**⚠️ IMPORTANTE**: El archivo `.env` contiene credenciales de desarrollo seguras pre-generadas. Para evaluación local, no es necesario cambiarlas.

### 3. Inicialización del Proyecto

```bash
# Construir e iniciar todos los servicios
docker-compose up -d

# Verificar que todos los contenedores están funcionando
docker-compose ps
```

**Resultado esperado**: Todos los servicios deben mostrar estado "healthy" o "running".

### 4. Verificación de Funcionalidad

#### Health Check del Sistema
```bash
curl http://localhost:8000/health/
```
**Respuesta esperada**: `{"status": "healthy", "database": "healthy", "redis": "healthy"}`

#### Verificación de la Web Interface
- **Dashboard**: http://localhost:8000/
- **Panel Admin**: http://localhost:8000/admin/
  - Usuario: `demo_admin`
  - Password: `demo123`

#### Verificación de APIs
- **Auth API**: http://localhost:8000/api/auth/docs
- **Users API**: http://localhost:8000/api/users/docs  
- **Tasks API**: http://localhost:8000/api/tasks/docs

### 5. Ejecución de Pruebas

```bash
# Ejecutar todas las pruebas del sistema
docker exec django_web python manage.py test --verbosity=2

# Resultado esperado: "Ran XX tests ... OK"
```

### 6. Verificación de Características Clave

#### 6.1 Sistema de Autenticación
- Registro de usuarios nuevos
- Login/logout
- Gestión de perfiles

#### 6.2 Gestión de Tareas
- Crear nuevas tareas
- Asignar usuarios
- Editar y actualizar estado
- Sistema de filtros

#### 6.3 Interfaz Web
- Dashboard responsivo
- Formularios funcionales
- Navegación intuitiva

## 🔧 Solución de Problemas Comunes

### Error: "Database connection failed"
```bash
# Reiniciar servicios con volúmenes limpios
docker-compose down -v
docker-compose up -d
```

### Error: "Port already in use"
```bash
# Verificar procesos en puerto 8000
lsof -i :8000
# Detener otros servicios o cambiar puerto en docker-compose.yml
```

### Error: "Permission denied"
```bash
# En sistemas Unix, asegurar permisos
chmod +x setup_env.sh
sudo chown -R $USER:$USER .
```

## 📊 Puntos de Evaluación Sugeridos

### ✅ Arquitectura y Configuración
- [x] Docker compose funcional
- [x] Separación de servicios (DB, Redis, Django, Celery)
- [x] Variables de entorno correctamente configuradas
- [x] Seguridad: .env no committeado

### ✅ Backend (Django + APIs)
- [x] API REST completamente funcional
- [x] Autenticación JWT implementada
- [x] Sistema de permisos robusto
- [x] Pruebas unitarias completas (82 tests)

### ✅ Frontend (Templates + Bootstrap)
- [x] Interfaz web responsive
- [x] Formularios de creación/edición
- [x] Dashboard con estadísticas
- [x] Sistema de filtros

### ✅ Características Avanzadas
- [x] Procesamiento asíncrono (Celery)
- [x] Sistema de notificaciones
- [x] Gestión de archivos/media
- [x] Logging y monitoreo

## 🚀 Comandos de Verificación Rápida

```bash
# Verificación completa en un solo script
./run_tests.sh

# Verificar logs en tiempo real
docker-compose logs -f django_web

# Acceso directo a la base de datos (si necesario)
docker exec -it postgres_db psql -U admin -d task_management_db
```

## 📞 Información de Contacto

Si encuentra algún problema durante la evaluación, por favor documentar:
1. Comando exacto ejecutado
2. Error completo recibido
3. Estado de los contenedores: `docker-compose ps`
4. Logs relevantes: `docker-compose logs service_name`

---

**✨ El proyecto está diseñado para funcionar "out of the box" siguiendo estos pasos.**
