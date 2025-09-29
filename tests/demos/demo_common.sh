#!/bin/bash
# Common functions for demo scripts

# Function to wait for user interaction
press_continue() {
    echo
    echo -e "\033[1;36m💡 Press ENTER to continue to the next demo...\033[0m"
    read -r
}

# Function to check if Docker containers are running
check_containers() {
    echo "🐳 Checking Docker containers..."
    if ! docker ps | grep -q "django_web\|celery_worker\|redis"; then
        echo "❌ Error: Docker containers are not running."
        echo "💡 Run 'docker-compose up -d' from the project root directory."
        exit 1
    fi
    echo "✅ Docker containers running correctly."
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