#!/bin/bash

# Task Management System - Quick Setup
# Automated project initialization and verification

set -e

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

success() { echo -e "${GREEN}✅ $1${NC}"; }
error() { echo -e "${RED}❌ $1${NC}"; }
info() { echo -e "${YELLOW}ℹ️  $1${NC}"; }

echo "🚀 Task Management System - Quick Setup"
echo "======================================="

# 1. Environment setup
if [ ! -f ".env" ]; then
    info "Creating .env from template..."
    cp .env.sample .env
    success "Environment configuration created"
else
    success "Environment configuration found"
fi

# 2. Docker setup
info "Starting services with Docker Compose..."
docker-compose up -d

# 3. Health check
info "Waiting for services to be ready..."
sleep 15

HEALTH=$(curl -s http://localhost:8000/health/ 2>/dev/null || echo "failed")
if echo "$HEALTH" | grep -q "healthy"; then
    success "System is healthy and ready"
else
    error "System not responding. Check logs: docker-compose logs"
    exit 1
fi

# 4. Final verification
info "System verification complete"

echo
echo "🎉 Setup Complete!"
echo "=================="
echo "• Dashboard: http://localhost:8000/"
echo "• Admin: http://localhost:8000/admin/ (demo_admin / demo123)"
echo "• API Documentation:"
echo "  - Auth API: http://localhost:8000/api/auth/docs"
echo "  - Users API: http://localhost:8000/api/users/docs"
echo "  - Tasks API: http://localhost:8000/api/tasks/docs"
echo
echo "• Run tests: ./run_tests.sh"
echo "• Stop services: docker-compose down"
success "System ready for use!"
