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

# 4. Run tests
info "Running system tests..."
if docker exec django_web python manage.py test --verbosity=1 >/dev/null 2>&1; then
    success "All tests passed"
else
    error "Some tests failed. Run manually: docker exec django_web python manage.py test"
fi

echo
echo "🎉 Setup Complete!"
echo "=================="
echo "• Dashboard: http://localhost:8000/"
echo "• Admin: http://localhost:8000/admin/ (demo_admin / demo123)"
echo "• API Docs: http://localhost:8000/api/auth/docs"
echo
echo "To stop: docker-compose down"
success "System ready for use!"
