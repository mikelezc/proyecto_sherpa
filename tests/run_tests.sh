#!/bin/bash

# =============================================================================
# PROYECTO SHERPA - TESTS & DEMOS MASTER SCRIPT
# Central hub for all testing, setup, and demonstration scripts
# =============================================================================

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
PURPLE='\033[0;35m'
NC='\033[0m'

# Script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

clear
echo -e "${BLUE}"
echo "  ╔══════════════════════════════════════════════════════════════╗"
echo "  ║                                                              ║"
echo "  ║           🧪 PROYECTO SHERPA - TESTS & DEMOS 🧪            ║"
echo "  ║                                                              ║"
echo "  ║              Central Testing & Demo Hub                      ║"
echo "  ║                                                              ║"
echo "  ╚══════════════════════════════════════════════════════════════╝"
echo -e "${NC}\n"

echo -e "${YELLOW}📁 Available Test Categories:${NC}"
echo "=============================="
echo ""

# Function to show menu
show_menu() {
    echo -e "${GREEN}🎭 DEMOS & DEMONSTRATIONS:${NC}"
    echo "1. 🚀 Run Complete Celery Demo      - Full automated demonstration"
    echo "2. 📧 Show Email Outputs           - View generated notifications"
    echo "3. 📋 Show Demo Summary             - Overview of all demos"
    echo ""
    
    echo -e "${GREEN}⚙️  SETUP & CONFIGURATION:${NC}"
    echo "4. 🔧 Quick Project Setup           - Initialize project quickly"
    echo ""
    
    echo -e "${GREEN}🧪 UNIT TESTS:${NC}"
    echo "5. ✅ Run Unit Tests               - Execute Django test suite"
    echo ""
    
    echo -e "${GREEN}� API TESTS:${NC}"
    echo "6. 📡 Run API Tests                - Test Django Ninja endpoints"
    echo ""
    
    echo -e "${GREEN}�📊 PROJECT STATUS:${NC}"
    echo "7. 🐳 Check Docker Status          - Container health check"
    echo "8. 📈 Show Celery Status           - Worker and beat status"
    echo "9. 🗂️  Show Project Structure       - Directory tree"
    echo ""
    
    echo -e "${GREEN}🔍 UTILITIES:${NC}"
    echo "10. 📝 Show All Available Scripts   - List all test scripts"
    echo "0. ❌ Exit"
    echo ""
}

# Function to run demos
run_demo() {
    echo -e "${BLUE}🚀 Starting Complete Celery Demo...${NC}\n"
    cd "$PROJECT_ROOT" && ./tests/demos/demo_celery_simple.sh
}

# Function to show emails
show_emails() {
    echo -e "${BLUE}📧 Showing Email Outputs...${NC}\n"
    cd "$PROJECT_ROOT" && ./tests/demos/show_emails.sh
}

# Function to show demo summary
show_demo_summary() {
    echo -e "${BLUE}📋 Demo System Overview...${NC}\n"
    cd "$PROJECT_ROOT" && ./tests/demos/README_DEMOS.sh
}

# Function for quick setup
quick_setup() {
    echo -e "${BLUE}🔧 Running Quick Setup...${NC}\n"
    cd "$PROJECT_ROOT" && ./quick_setup.sh
}

# Function to run unit tests
run_unit_tests() {
    echo -e "${BLUE}✅ Running Unit Tests...${NC}\n"
    cd "$PROJECT_ROOT" && ./tests/unit/run_tests.sh
}

# Function to run API tests
run_api_tests() {
    echo -e "${BLUE}📡 Running API Tests...${NC}\n"
    cd "$PROJECT_ROOT" && ./tests/api/test_tasks_api.sh
}

# Function to check Docker status
check_docker() {
    echo -e "${BLUE}🐳 Docker Container Status:${NC}"
    echo "============================"
    cd "$PROJECT_ROOT" && docker-compose ps
}

# Function to show Celery status
show_celery_status() {
    echo -e "${BLUE}📈 Celery System Status:${NC}"
    echo "========================="
    
    echo -e "\n${YELLOW}🔧 Registered Tasks:${NC}"
    cd "$PROJECT_ROOT" && docker exec django_web celery -A main inspect registered 2>/dev/null || echo "❌ Cannot connect to Celery worker"
    
    echo -e "\n${YELLOW}📋 Active Scheduled Tasks:${NC}"
    cd "$PROJECT_ROOT" && docker exec django_web python manage.py shell -c "
from django_celery_beat.models import PeriodicTask
for task in PeriodicTask.objects.filter(enabled=True):
    print(f'✅ {task.name}')
" 2>/dev/null || echo "❌ Cannot connect to database"
}

# Function to show project structure
show_structure() {
    echo -e "${BLUE}🗂️  Project Structure:${NC}"
    echo "======================"
    cd "$PROJECT_ROOT" && tree -L 3 -I '__pycache__|*.pyc|node_modules' 2>/dev/null || find . -type d -not -path '*/\.*' | head -20
}

# Function to list all scripts
list_scripts() {
    echo -e "${BLUE}📝 Available Test Scripts:${NC}"
    echo "==========================="
    
    echo -e "\n${YELLOW}📁 Demos (tests/demos/):${NC}"
    for script in "$SCRIPT_DIR/demos/"*.sh; do
        [ -f "$script" ] && echo "   $(basename "$script")"
    done
    
    echo -e "\n${YELLOW}📁 Unit Tests (tests/unit/):${NC}"
    for script in "$SCRIPT_DIR/unit/"*.sh; do
        [ -f "$script" ] && echo "   $(basename "$script")"
    done
    
    echo -e "\n${YELLOW}📁 API Tests (tests/api/):${NC}"
    for script in "$SCRIPT_DIR/api/"*.sh; do
        [ -f "$script" ] && echo "   $(basename "$script")"
    done
    
    echo -e "\n${YELLOW}📁 Setup Scripts (project root):${NC}"
    echo "   quick_setup.sh"
    
    echo -e "\n${GREEN}💡 All scripts can be run directly or through this menu${NC}"
}

# Main menu loop
while true; do
    show_menu
    echo -e "${YELLOW}Choose an option (0-10): ${NC}"
    read -r choice
    
    case $choice in
        1)
            run_demo
            ;;
        2)
            show_emails
            ;;
        3)
            show_demo_summary
            ;;
        4)
            quick_setup
            ;;
        5)
            run_unit_tests
            ;;
        6)
            run_api_tests
            ;;
        7)
            check_docker
            ;;
        8)
            show_celery_status
            ;;
        9)
            show_structure
            ;;
        10)
            list_scripts
            ;;
        0)
            echo -e "${GREEN}👋 Goodbye!${NC}"
            exit 0
            ;;
        *)
            echo -e "${RED}❌ Invalid option. Please choose 0-10.${NC}"
            ;;
    esac
    
    echo -e "\n${YELLOW}Press ENTER to return to menu...${NC}"
    read -r
    clear
done