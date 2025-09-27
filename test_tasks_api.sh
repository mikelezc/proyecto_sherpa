#!/bin/bash

# Test script for Tasks API - CSRF and Assigned-to-me issues

echo "=== Testing Tasks API ==="
echo

# 1. First, login to get session
echo "1. Testing login..."
LOGIN_RESPONSE=$(curl -s -c cookies.txt -X POST "http://localhost:8000/api/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "demo_admin",
    "password": "demo123"
  }')

echo "Login response: $LOGIN_RESPONSE"
echo

# 2. Test GET tasks (should work)
echo "2. Testing GET /api/tasks/ (should work)..."
GET_RESPONSE=$(curl -s -b cookies.txt "http://localhost:8000/api/tasks/")
echo "GET response: $GET_RESPONSE" | head -200
echo

# 3. Test GET tasks with assigned_to_me=true
echo "3. Testing GET /api/tasks/?assigned_to_me=true..."
ASSIGNED_RESPONSE=$(curl -s -b cookies.txt "http://localhost:8000/api/tasks/?assigned_to_me=true")
echo "Assigned to me response: $ASSIGNED_RESPONSE" | head -200
echo

# 4. Test POST create task (CSRF test)
echo "4. Testing POST /api/tasks/ (CSRF test)..."
POST_RESPONSE=$(curl -s -b cookies.txt -X POST "http://localhost:8000/api/tasks/" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Test Task via API",
    "description": "Testing CSRF fix",
    "due_date": "2025-10-01T12:00:00Z",
    "priority": "medium"
  }')

echo "POST response: $POST_RESPONSE"
echo

# Clean up cookies
rm -f cookies.txt

echo "=== Test completed ==="