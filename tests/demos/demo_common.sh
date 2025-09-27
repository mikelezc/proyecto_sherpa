#!/bin/bash
# Common functions for demo scripts

# Function to wait for user interaction
press_continue() {
    echo
    echo -e "\033[1;36m💡 Presiona ENTER para continuar con la siguiente demo...\033[0m"
    read -r
}

# Function to check if Docker containers are running
check_containers() {
    echo "🐳 Verificando contenedores Docker..."
    if ! docker ps | grep -q "django_web\|celery_worker\|redis"; then
        echo "❌ Error: Los contenedores Docker no están ejecutándose."
        echo "💡 Ejecuta 'docker-compose up -d' desde el directorio raíz del proyecto."
        exit 1
    fi
    echo "✅ Contenedores Docker ejecutándose correctamente."
}

# Function to show header
show_header() {
    local title="$1"
    echo -e "\033[1;34m"
    echo "════════════════════════════════════════════════════════════════"
    echo "  $title"
    echo "════════════════════════════════════════════════════════════════"
    echo -e "\033[0m"
}