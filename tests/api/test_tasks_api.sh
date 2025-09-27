#!/bin/bash

# =============================================================================
# TASKS API TEST SUITE
# Complete API testing for Django Ninja Tasks endpoints
# =============================================================================

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
PURPLE='\033[0;35m'
NC='\033[0m'

# Test configuration
BASE_URL="http://localhost:8000"
COOKIES_FILE="/tmp/api_test_cookies.txt"
TEST_USER="demo_admin"
TEST_PASS="demo123"

# Functions
print_header() {
    echo -e "${BLUE}"
    echo "  ╔══════════════════════════════════════════════════════════════╗"
    echo "  ║                                                              ║"
    echo "  ║           🚀 TASKS API TEST SUITE 🚀                       ║"
    echo "  ║                                                              ║"
    echo "  ║      Testing Django Ninja API endpoints                     ║"
    echo "  ║                                                              ║"
    echo "  ╚══════════════════════════════════════════════════════════════╝"
    echo -e "${NC}\n"
}

print_test() {
    echo -e "${YELLOW}🔍 $1${NC}"
    echo "----------------------------------------"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}\n"
}

print_error() {
    echo -e "${RED}❌ $1${NC}\n"
}

print_info() {
    echo -e "${PURPLE}ℹ️  $1${NC}"
}

# Test functions
test_authentication() {
    print_test "Testing Authentication Login"
    
    LOGIN_RESPONSE=$(curl -s -c "$COOKIES_FILE" -X POST "$BASE_URL/api/auth/login" \
        -H "Content-Type: application/json" \
        -d "{
            \"username\": \"$TEST_USER\",
            \"password\": \"$TEST_PASS\"
        }")
    
    if [[ $LOGIN_RESPONSE == *"success"* ]]; then
        print_success "Authentication successful"
        print_info "Response: $LOGIN_RESPONSE"
    else
        print_error "Authentication failed"
        print_info "Response: $LOGIN_RESPONSE"
        return 1
    fi
    return 0
}

test_list_tasks() {
    print_test "Testing GET /api/tasks/ - List All Tasks"
    
    RESPONSE=$(curl -s -b "$COOKIES_FILE" "$BASE_URL/api/tasks/")
    
    # Check if response contains expected fields
    if [[ $RESPONSE == *"results"* ]] && [[ $RESPONSE == *"count"* ]]; then
        TASK_COUNT=$(echo "$RESPONSE" | sed -n 's/.*"count": *\([0-9]*\).*/\1/p')
        if [[ -z $TASK_COUNT ]]; then
            TASK_COUNT="N/A"
        fi
        print_success "Successfully retrieved tasks"
        print_info "Total tasks found: $TASK_COUNT"
    else
        print_error "Failed to retrieve tasks or invalid response format"
        print_info "Response: ${RESPONSE:0:200}..."
        return 1
    fi
    return 0
}

test_assigned_to_me_filter() {
    print_test "Testing GET /api/tasks/?assigned_to_me=true - User Filter"
    
    RESPONSE=$(curl -s -b "$COOKIES_FILE" "$BASE_URL/api/tasks/?assigned_to_me=true")
    
    if [[ $RESPONSE == *"results"* ]]; then
        ASSIGNED_COUNT=$(echo "$RESPONSE" | sed -n 's/.*"count": *\([0-9]*\).*/\1/p')
        if [[ -z $ASSIGNED_COUNT ]]; then
            ASSIGNED_COUNT="N/A"
        fi
        print_success "Successfully filtered assigned tasks"
        print_info "Tasks assigned to $TEST_USER: $ASSIGNED_COUNT"
    else
        print_error "Failed to filter assigned tasks"
        print_info "Response: ${RESPONSE:0:200}..."
        return 1
    fi
    return 0
}

test_create_task() {
    print_test "Testing POST /api/tasks/ - Create Task (CSRF Bypass)"
    
    # Generate a future date (7 days from now)
    FUTURE_DATE=$(date -u -v+7d '+%Y-%m-%dT%H:%M:%SZ' 2>/dev/null || date -u -d '+7 days' '+%Y-%m-%dT%H:%M:%SZ')
    
    RESPONSE=$(curl -s -b "$COOKIES_FILE" -X POST "$BASE_URL/api/tasks/" \
        -H "Content-Type: application/json" \
        -d "{
            \"title\": \"API Test Task - $(date '+%Y%m%d_%H%M%S')\",
            \"description\": \"Task created via API test suite\",
            \"due_date\": \"$FUTURE_DATE\",
            \"priority\": \"medium\",
            \"status\": \"todo\"
        }")
    
    if [[ $RESPONSE == *"\"id\":"* ]] && [[ $RESPONSE == *"\"title\":"* ]]; then
        TASK_ID=$(echo "$RESPONSE" | sed -n 's/.*"id": *\([0-9]*\).*/\1/p')
        if [[ -z $TASK_ID ]]; then
            TASK_ID="N/A"
        fi
        print_success "Successfully created task"
        print_info "New task ID: $TASK_ID"
        if [[ $TASK_ID != "N/A" ]]; then
            echo "$TASK_ID" > /tmp/last_created_task_id.txt  # Save for cleanup
        fi
    else
        print_error "Failed to create task"
        print_info "Response: ${RESPONSE:0:300}..."
        return 1
    fi
    return 0
}

test_get_task_detail() {
    print_test "Testing GET /api/tasks/tasks/{id} - Task Details"
    
    # Get first available task ID from the list
    TASK_LIST=$(curl -s -b "$COOKIES_FILE" "$BASE_URL/api/tasks/")
    TASK_ID=$(echo "$TASK_LIST" | grep -o '"id": [0-9]*' | head -1 | grep -o '[0-9]*')
    
    if [[ -n $TASK_ID ]] && [[ $TASK_ID != "" ]]; then
        RESPONSE=$(curl -s -b "$COOKIES_FILE" "$BASE_URL/api/tasks/tasks/$TASK_ID")
        
        if [[ $RESPONSE == *"\"id\":$TASK_ID"* ]] || [[ $RESPONSE == *"\"id\": $TASK_ID"* ]]; then
            print_success "Successfully retrieved task details"
            print_info "Task ID: $TASK_ID"
        else
            print_error "Failed to retrieve task details"
            print_info "Response: ${RESPONSE:0:200}..."
            return 1
        fi
    else
        # Skip this test if no tasks available
        print_success "No tasks available - skipping detail test"
        print_info "This is normal if database is empty"
    fi
    return 0
}

test_search_functionality() {
    print_test "Testing GET /api/tasks/?search=test - Search"
    
    RESPONSE=$(curl -s -b "$COOKIES_FILE" "$BASE_URL/api/tasks/?search=test")
    
    if [[ $RESPONSE == *"results"* ]]; then
        SEARCH_COUNT=$(echo "$RESPONSE" | sed -n 's/.*"count": *\([0-9]*\).*/\1/p')
        if [[ -z $SEARCH_COUNT ]]; then
            SEARCH_COUNT="N/A"
        fi
        print_success "Search functionality working"
        print_info "Search results for 'test': $SEARCH_COUNT tasks"
    else
        print_error "Search functionality failed"
        print_info "Response: ${RESPONSE:0:200}..."
        return 1
    fi
    return 0
}

check_docker_status() {
    print_test "Checking Docker Container Status"
    
    if ! command -v docker-compose &> /dev/null; then
        print_error "docker-compose not found"
        return 1
    fi
    
    # Check if containers are running
    CONTAINERS_STATUS=$(docker-compose ps --services --filter "status=running" 2>/dev/null)
    
    if [[ $CONTAINERS_STATUS == *"web"* ]]; then
        print_success "Docker containers are running"
    else
        print_error "Docker containers not running. Please start with: docker-compose up -d"
        return 1
    fi
    return 0
}

cleanup() {
    print_info "Cleaning up temporary files..."
    rm -f "$COOKIES_FILE" /tmp/last_created_task_id.txt
}

# Main execution
main() {
    print_header
    
    # Trap to ensure cleanup on exit
    trap cleanup EXIT
    
    local failed_tests=0
    local total_tests=0
    
    # Pre-flight checks
    if ! check_docker_status; then
        exit 1
    fi
    
    # Run all tests
    tests=(
        "test_authentication"
        "test_list_tasks" 
        "test_assigned_to_me_filter"
        "test_create_task"
        "test_get_task_detail"
        "test_search_functionality"
    )
    
    for test in "${tests[@]}"; do
        ((total_tests++))
        if ! $test; then
            ((failed_tests++))
        fi
    done
    
    # Final report
    echo -e "${BLUE}"
    echo "  ╔══════════════════════════════════════════════════════════════╗"
    echo "  ║                        TEST SUMMARY                          ║"
    echo "  ╚══════════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
    
    local passed_tests=$((total_tests - failed_tests))
    echo -e "${GREEN}✅ Passed: $passed_tests/$total_tests${NC}"
    
    if [[ $failed_tests -gt 0 ]]; then
        echo -e "${RED}❌ Failed: $failed_tests/$total_tests${NC}"
        echo -e "${YELLOW}💡 Check the error messages above for details${NC}"
        exit 1
    else
        echo -e "${GREEN}🎉 All tests passed successfully!${NC}"
        echo -e "${YELLOW}💡 Tasks API is fully functional${NC}"
    fi
}

# Execute if run directly
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi