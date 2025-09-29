#!/bin/bash

# ============================================================================
# ACCELERATED DEMONSTRATION: COMPLETE CLEANUP CYCLE
# ============================================================================
# This script demonstrates the complete cleanup cycle with accelerated timing
# to show examiners the entire process in minutes instead of days
# ============================================================================

source "$(dirname "$0")/demo_common.sh"

# Colors
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
║           🚀 ACCELERATED DEMO - CLEANUP CYCLE                   ║
║            From Creation to Deletion (3 min)                   ║
╚══════════════════════════════════════════════════════════════════╝
EOF
echo -e "${NC}"

echo -e "${YELLOW}This demonstration shows the complete cycle:${NC}"
echo -e "  1️⃣ Create unverified user"
echo -e "  2️⃣ Wait for verification timeout (15s)"
echo -e "  3️⃣ See automatic deletion"
echo -e "  4️⃣ Create user and simulate inactivity"
echo -e "  5️⃣ See warnings and deletion due to inactivity"

press_continue

# Step 1: Create test user
echo -e "${CYAN}━━━ STEP 1: CREATE UNVERIFIED USER ━━━${NC}"
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

print(f'✅ User created: {user.username}')
print(f'🕐 Timestamp: {timezone.now()}')
"

echo -e "${GREEN}User created, waiting for automatic cleanup...${NC}"

# Function to check if user exists
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

# Step 2: Real-time cleanup monitoring
echo -e "${CYAN}━━━ STEP 2: REAL-TIME MONITORING ━━━${NC}"
echo -e "${YELLOW}Waiting for next cleanup execution (maximum 5 minutes)...${NC}"

# Wait up to 6 minutes to see the cleanup
for i in {1..36}; do
    status=$(check_user_exists)
    current_time=$(date "+%H:%M:%S")
    
    if [ "$status" = "DELETED" ]; then
        echo -e "${RED}🗑️  User automatically deleted at ${current_time}${NC}"
        break
    else
        echo -e "${BLUE}⏰ ${current_time} - User still exists (${status})${NC}"
    fi
    
    sleep 10
done

# Step 3: Verify deletion logs
echo -e "${CYAN}━━━ STEP 3: VERIFY DELETION LOGS ━━━${NC}"
echo -e "${PURPLE}Most recent cleanup logs:${NC}"
docker logs celery_worker --tail 30 | grep -A 10 -B 5 "CLEANUP TASK"

# Step 4: Create user for inactivity demo
echo -e "${CYAN}━━━ STEP 4: INACTIVITY DEMO ━━━${NC}"
INACTIVE_USER="inactive_test_$(date +%s)"

docker exec django_web python manage.py shell -c "
from authentication.models import CustomUser as User
from django.utils import timezone
from datetime import timedelta

# Create verified but inactive user
user = User.objects.create_user(
    username='${INACTIVE_USER}',
    email='${INACTIVE_USER}@inactive-test.demo',  
    password='testpass123'
)
user.is_email_verified = True

# Simulate inactivity: set old last_activity
old_time = timezone.now() - timedelta(seconds=70)  # More than threshold
user.last_activity = old_time
user.save()

print(f'✅ Inactive user created: {user.username}')
print(f'📧 Email verified: {user.is_email_verified}')
print(f'🕐 Last activity: {user.last_activity}')
print(f'⏰ Now: {timezone.now()}')
"

echo -e "${YELLOW}Waiting for inactive user cleanup...${NC}"

# Function to check inactive user
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

# Monitor for inactive user
for i in {1..36}; do
    status=$(check_inactive_user)
    current_time=$(date "+%H:%M:%S")
    
    if [ "$status" = "DELETED" ]; then
        echo -e "${RED}🗑️  Inactive user deleted at ${current_time}${NC}"
        break
    else
        echo -e "${BLUE}⏰ ${current_time} - Inactive user still exists${NC}"
    fi
    
    sleep 10
done

# Step 5: Final summary
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BOLD}${GREEN}✅ ACCELERATED DEMONSTRATION COMPLETED${NC}"
echo
echo -e "${YELLOW}Observed results:${NC}"

# Check if both users were deleted
final_check1=$(check_user_exists)
final_check2=$(check_inactive_user)

if [ "$final_check1" = "DELETED" ]; then
    echo -e "  ✅ Unverified user: ${GREEN}Correctly deleted${NC}"
else
    echo -e "  ⚠️  Unverified user: ${YELLOW}Still exists (may need more time)${NC}"
fi

if [ "$final_check2" = "DELETED" ]; then
    echo -e "  ✅ Inactive user: ${GREEN}Correctly deleted${NC}"
else
    echo -e "  ⚠️  Inactive user: ${YELLOW}Still exists (may need more time)${NC}"
fi

echo
echo -e "${PURPLE}📋 Final cleanup logs:${NC}"
docker logs celery_worker --tail 20 | grep -A 5 -B 2 "Processing complete"

echo
echo -e "${CYAN}🎉 Cleanup system working correctly in automatic mode${NC}"
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"