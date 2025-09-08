#!/bin/bash

# 🎯 Script de Verificación Rápida para Examinadores
# Task Management System - Verificación Automática

echo "🎯 Task Management System - Verificación para Examinadores"
echo "=========================================================="

# Colores para output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Función para mostrar éxito
success() {
    echo -e "${GREEN}✅ $1${NC}"
}

# Función para mostrar error
error() {
    echo -e "${RED}❌ $1${NC}"
}

# Función para mostrar información
info() {
    echo -e "${YELLOW}ℹ️  $1${NC}"
}

echo
echo "1. Verificando configuración inicial..."

# Verificar si existe .env
if [ -f ".env" ]; then
    success "Archivo .env encontrado"
else
    error "Archivo .env no encontrado"
    info "Ejecutando: cp .env.sample .env"
    cp .env.sample .env
    success "Archivo .env creado desde plantilla"
fi

echo
echo "2. Verificando Docker y servicios..."

# Verificar Docker
if command -v docker-compose &> /dev/null; then
    success "Docker Compose está instalado"
else
    error "Docker Compose no está instalado"
    exit 1
fi

# Iniciar servicios
info "Iniciando servicios con Docker Compose..."
docker-compose up -d

echo
echo "3. Esperando que los servicios estén listos..."
sleep 10

# Verificar servicios
echo
echo "4. Verificando estado de los contenedores..."
docker-compose ps

echo
echo "5. Verificando health check..."
HEALTH_RESPONSE=$(curl -s http://localhost:8000/health/ 2>/dev/null)
if echo "$HEALTH_RESPONSE" | grep -q "healthy"; then
    success "Sistema funcionando correctamente"
    echo "   Respuesta: $HEALTH_RESPONSE"
else
    error "El sistema no responde correctamente"
    info "Esperando más tiempo para que los servicios se inicializen..."
    sleep 15
    HEALTH_RESPONSE=$(curl -s http://localhost:8000/health/ 2>/dev/null)
    if echo "$HEALTH_RESPONSE" | grep -q "healthy"; then
        success "Sistema funcionando correctamente (después de espera adicional)"
        echo "   Respuesta: $HEALTH_RESPONSE"
    else
        error "El sistema aún no responde. Revisar logs con: docker-compose logs"
        exit 1
    fi
fi

echo
echo "6. Ejecutando pruebas del sistema..."
info "Esto puede tomar unos minutos..."
TEST_OUTPUT=$(docker exec django_web python manage.py test --verbosity=1 2>&1)
if echo "$TEST_OUTPUT" | grep -q "OK"; then
    success "Todas las pruebas pasaron exitosamente"
    # Extraer número de pruebas
    TEST_COUNT=$(echo "$TEST_OUTPUT" | grep "Ran .* tests" | head -1)
    echo "   $TEST_COUNT"
else
    error "Algunas pruebas fallaron"
    info "Ejecutar manualmente: docker exec django_web python manage.py test --verbosity=2"
fi

echo
echo "🎉 Verificación Completa"
echo "======================="
echo
echo "Accesos disponibles:"
echo "• Dashboard: http://localhost:8000/"
echo "• Admin Panel: http://localhost:8000/admin/ (demo_admin / demo123)"
echo "• API Docs: http://localhost:8000/api/auth/docs"
echo "• Tasks API: http://localhost:8000/api/tasks/docs"
echo
echo "Para detener los servicios: docker-compose down"
echo "Para ver logs en tiempo real: docker-compose logs -f"
echo
success "¡El proyecto está listo para evaluación!"
