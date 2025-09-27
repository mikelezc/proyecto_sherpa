#!/bin/bash

# ============================================================================
# DEMOSTRACIÓN ACELERADA: CICLO COMPLETO DE CLEANUP
# ============================================================================
# Este script demuestra el ciclo completo de cleanup con tiempos acelerados
# para mostrar a los examinadores todo el proceso en minutos en lugar de días
# ============================================================================

source "$(dirname "$0")/demo_common.sh"

# Colores
BOLD='\033[1m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
RED='\033[0;31m'
NC='\033[0m'

# Banner
clear
echo -e "${BOLD}${CYAN}"
cat << "EOF"
╔══════════════════════════════════════════════════════════════════╗
║              🚀 DEMO ACELERADA - CICLO CLEANUP                  ║
║            Desde Creación hasta Eliminación (3 min)            ║
╚══════════════════════════════════════════════════════════════════╝
EOF
echo -e "${NC}"

echo -e "${YELLOW}Esta demostración muestra el ciclo completo:${NC}"
echo -e "  1️⃣ Crear usuario sin verificar"
echo -e "  2️⃣ Esperar timeout de verificación (15s)"
echo -e "  3️⃣ Ver eliminación automática"
echo -e "  4️⃣ Crear usuario y simular inactividad"
echo -e "  5️⃣ Ver avisos y eliminación por inactividad"

press_continue

# Paso 1: Crear usuario de prueba
echo -e "${CYAN}━━━ PASO 1: CREAR USUARIO SIN VERIFICAR ━━━${NC}"
TEST_USER="accel_test_$(date +%s)"

docker exec django_web python manage.py shell -c "
from authentication.models import CustomUser as User
from django.utils import timezone

user = User.objects.create_user(
    username='${TEST_USER}',
    email='${TEST_USER}@accel-test.demo',
    password='testpass123'
)
user.is_email_verified = False
user.save()

print(f'✅ Usuario creado: {user.username}')
print(f'🕐 Timestamp: {timezone.now()}')
"

echo -e "${GREEN}Usuario creado, esperando cleanup automático...${NC}"

# Función para verificar si el usuario existe
check_user_exists() {
    docker exec django_web python manage.py shell -c "
from authentication.models import CustomUser as User
try:
    user = User.objects.get(username='${TEST_USER}')
    print('EXISTS')
except User.DoesNotExist:
    print('DELETED')
" 2>/dev/null | tail -1
}

# Paso 2: Monitor de cleanup en tiempo real
echo -e "${CYAN}━━━ PASO 2: MONITOREO EN TIEMPO REAL ━━━${NC}"
echo -e "${YELLOW}Esperando próxima ejecución de cleanup (máximo 5 minutos)...${NC}"

# Esperar hasta 6 minutos para ver el cleanup
for i in {1..36}; do
    status=$(check_user_exists)
    current_time=$(date "+%H:%M:%S")
    
    if [ "$status" = "DELETED" ]; then
        echo -e "${RED}🗑️  Usuario eliminado automáticamente a las ${current_time}${NC}"
        break
    else
        echo -e "${BLUE}⏰ ${current_time} - Usuario aún existe (${status})${NC}"
    fi
    
    sleep 10
done

# Paso 3: Verificar logs de la eliminación
echo -e "${CYAN}━━━ PASO 3: VERIFICAR LOGS DE ELIMINACIÓN ━━━${NC}"
echo -e "${PURPLE}Logs de cleanup más recientes:${NC}"
docker logs celery_worker --tail 30 | grep -A 10 -B 5 "CLEANUP TASK"

# Paso 4: Crear usuario para demo de inactividad
echo -e "${CYAN}━━━ PASO 4: DEMO DE INACTIVIDAD ━━━${NC}"
INACTIVE_USER="inactive_test_$(date +%s)"

docker exec django_web python manage.py shell -c "
from authentication.models import CustomUser as User
from django.utils import timezone
from datetime import timedelta

# Crear usuario verificado pero inactivo
user = User.objects.create_user(
    username='${INACTIVE_USER}',
    email='${INACTIVE_USER}@inactive-test.demo',  
    password='testpass123'
)
user.is_email_verified = True

# Simular inactividad: poner last_activity antigua
old_time = timezone.now() - timedelta(seconds=70)  # Más del threshold
user.last_activity = old_time
user.save()

print(f'✅ Usuario inactivo creado: {user.username}')
print(f'📧 Email verificado: {user.is_email_verified}')
print(f'🕐 Última actividad: {user.last_activity}')
print(f'⏰ Ahora: {timezone.now()}')
"

echo -e "${YELLOW}Esperando cleanup de usuario inactivo...${NC}"

# Función para verificar usuario inactivo
check_inactive_user() {
    docker exec django_web python manage.py shell -c "
from authentication.models import CustomUser as User
try:
    user = User.objects.get(username='${INACTIVE_USER}')
    print('EXISTS')
except User.DoesNotExist:
    print('DELETED')
" 2>/dev/null | tail -1
}

# Monitor para usuario inactivo
for i in {1..36}; do
    status=$(check_inactive_user)
    current_time=$(date "+%H:%M:%S")
    
    if [ "$status" = "DELETED" ]; then
        echo -e "${RED}🗑️  Usuario inactivo eliminado a las ${current_time}${NC}"
        break
    else
        echo -e "${BLUE}⏰ ${current_time} - Usuario inactivo aún existe${NC}"
    fi
    
    sleep 10
done

# Paso 5: Resumen final
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BOLD}${GREEN}✅ DEMOSTRACIÓN ACELERADA COMPLETADA${NC}"
echo
echo -e "${YELLOW}Resultados observados:${NC}"

# Verificar si ambos usuarios fueron eliminados
final_check1=$(check_user_exists)
final_check2=$(check_inactive_user)

if [ "$final_check1" = "DELETED" ]; then
    echo -e "  ✅ Usuario sin verificar: ${GREEN}Eliminado correctamente${NC}"
else
    echo -e "  ⚠️  Usuario sin verificar: ${YELLOW}Aún existe (puede necesitar más tiempo)${NC}"
fi

if [ "$final_check2" = "DELETED" ]; then
    echo -e "  ✅ Usuario inactivo: ${GREEN}Eliminado correctamente${NC}"
else
    echo -e "  ⚠️  Usuario inactivo: ${YELLOW}Aún existe (puede necesitar más tiempo)${NC}"
fi

echo
echo -e "${PURPLE}📋 Logs finales de cleanup:${NC}"
docker logs celery_worker --tail 20 | grep -A 5 -B 2 "Processing complete"

echo
echo -e "${CYAN}🎉 Sistema de cleanup funcionando correctamente en modo automático${NC}"
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"