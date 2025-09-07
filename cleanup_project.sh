#!/bin/bash

# Script de limpieza automática para adaptar el proyecto a la prueba técnica
# Ejecuta: bash cleanup_project.sh

echo "🧹 Iniciando limpieza del proyecto..."

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Función para mostrar progreso
show_progress() {
    echo -e "${GREEN}✅ $1${NC}"
}

show_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

show_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Verificar que estamos en el directorio correcto
if [ ! -f "docker-compose.yml" ]; then
    show_error "No se encuentra docker-compose.yml. Ejecuta este script desde el directorio raíz del proyecto."
    exit 1
fi

echo "📁 Directorio de trabajo: $(pwd)"

# 1. Hacer backup del proyecto original
echo "🔄 Creando backup del proyecto original..."
if [ ! -d "../proyecto_sherpa_backup" ]; then
    cp -r . ../proyecto_sherpa_backup
    show_progress "Backup creado en ../proyecto_sherpa_backup"
else
    show_warning "El backup ya existe en ../proyecto_sherpa_backup"
fi

# 2. Reemplazar archivos principales
echo "🔄 Reemplazando archivos de configuración..."

# Docker Compose
if [ -f "docker-compose.yml.new" ]; then
    mv docker-compose.yml docker-compose.yml.old
    mv docker-compose.yml.new docker-compose.yml
    show_progress "docker-compose.yml actualizado"
fi

# Dockerfile
if [ -f "srcs/django/Dockerfile.new" ]; then
    mv srcs/django/Dockerfile srcs/django/Dockerfile.old
    mv srcs/django/Dockerfile.new srcs/django/Dockerfile
    show_progress "Dockerfile actualizado"
fi

# Entrypoint
if [ -f "srcs/django/entrypoint.py" ]; then
    mv srcs/django/django-entrypoint.py srcs/django/django-entrypoint.py.old
    mv srcs/django/entrypoint.py srcs/django/django-entrypoint.py
    show_progress "Entrypoint actualizado"
fi

# Requirements
if [ -f "srcs/django/requirements_new.txt" ]; then
    mv srcs/django/requirements.txt srcs/django/requirements.txt.old
    mv srcs/django/requirements_new.txt srcs/django/requirements.txt
    show_progress "requirements.txt actualizado"
fi

# Settings
if [ -f "srcs/django/main/settings_new.py" ]; then
    mv srcs/django/main/settings.py srcs/django/main/settings.py.old
    mv srcs/django/main/settings_new.py srcs/django/main/settings.py
    show_progress "settings.py actualizado"
fi

# URLs
if [ -f "srcs/django/main/urls_new.py" ]; then
    mv srcs/django/main/urls.py srcs/django/main/urls.py.old
    mv srcs/django/main/urls_new.py srcs/django/main/urls.py
    show_progress "urls.py actualizado"
fi

# 3. Configurar archivo de entorno
echo "🔄 Configurando archivo de entorno..."
if [ ! -f ".env" ]; then
    cp .env.sample .env
    show_progress "Archivo .env creado desde .env.sample"
    show_warning "¡Recuerda editar .env con tus configuraciones!"
else
    show_warning "El archivo .env ya existe, no se sobrescribe"
fi

# 4. Eliminar servicios innecesarios
echo "🔄 Eliminando servicios innecesarios..."

# Servicios Docker
services_to_remove=(
    "srcs/nginx"
    "srcs/vault"
    "srcs/ssl"
    "srcs/waf"
    "srcs/front"
)

for service in "${services_to_remove[@]}"; do
    if [ -d "$service" ]; then
        mv "$service" "${service}.removed"
        show_progress "Servicio $service eliminado (movido a ${service}.removed)"
    fi
done

# 5. Eliminar apps innecesarias de Django
echo "🔄 Eliminando apps Django innecesarias..."

apps_to_remove=(
    "srcs/django/game"
    "srcs/django/tournament"
    "srcs/django/dashboard"
    "srcs/django/chat"
)

for app in "${apps_to_remove[@]}"; do
    if [ -d "$app" ]; then
        mv "$app" "${app}.removed"
        show_progress "App $app eliminada (movida a ${app}.removed)"
    fi
done

# 6. Eliminar archivos de configuración obsoletos
echo "🔄 Eliminando archivos obsoletos..."

files_to_remove=(
    "security_tests"
    "configure_ip.sh"
    "setup_env.sh"
)

for file in "${files_to_remove[@]}"; do
    if [ -e "$file" ]; then
        mv "$file" "${file}.removed"
        show_progress "Archivo/directorio $file eliminado"
    fi
done

# 7. Limpiar contenedores Docker existentes
echo "🔄 Limpiando contenedores Docker..."
if command -v docker-compose &> /dev/null; then
    docker-compose down --remove-orphans 2>/dev/null || true
    show_progress "Contenedores Docker detenidos"
else
    show_warning "docker-compose no encontrado, omitiendo limpieza de contenedores"
fi

echo ""
echo "🎉 ¡Limpieza completada!"
echo ""
echo "📋 Próximos pasos:"
echo "1. Edita el archivo .env con tus configuraciones"
echo "2. Ejecuta: docker-compose up --build"
echo "3. En otra terminal: docker-compose exec web python manage.py createsuperuser"
echo ""
echo "📚 Consulta README_CLEAN.md para más detalles"
echo ""
echo "🌐 URLs disponibles:"
echo "   - Frontend: http://localhost:8000"
echo "   - Admin: http://localhost:8000/admin/"
echo "   - API: http://localhost:8000/api/"
echo ""
show_progress "¡Proyecto listo para la prueba técnica! 🚀"
