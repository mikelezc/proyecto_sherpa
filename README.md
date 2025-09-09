# Task Management System

Complete task management system developed with Django, featuring microservices architecture using Docker and asynchronous processing with Celery.

The Docker structure, authentication API, and user management are based on this other repository I developed using the same framework.

https://github.com/mikelezc/42_Transcendence

Here you can see the same base, but applied with other interesting features like email notifications, JWT, 2FA with keys, data encryption before database insertion, load balancer, frontend served directly from the API, a WAF, etc. Highly recommended to inspect it.

## 🚀 Quick Start

### Automatic Verification (Recommended)
```bash
git clone <repository-url>
cd proyecto_sherpa
./quick_setup.sh
```

### Manual Setup
```bash
# 1. Configure environment variables
cp .env.sample .env

# 2. Start services
docker-compose up -d

# 3. Verify functionality
curl http://localhost:8000/health/
```

### Application Access
- **Dashboard**: http://localhost:8000/
- **Admin Panel**: http://localhost:8000/admin/ (`demo_admin` / `demo123`)
- **API Documentation**:
  - Auth API: http://localhost:8000/api/auth/docs
  - Users API: http://localhost:8000/api/users/docs  
  - Tasks API: http://localhost:8000/api/tasks/docs

**✅ The `.env` file is automatically generated with secure credentials for development**

## Documentation

- **[Architecture](docs/ARCHITECTURE.md)** - System architecture  
- **[Decisions](docs/DECISIONS.md)** - Technical decisions and implementation
- **[API Documentation](docs/API_DOCUMENTATION.md)** - Complete API guide

- **Functional API Endpoints**:
  - Auth API: http://localhost:8000/api/auth/docs
  - Users API: http://localhost:8000/api/users/docs  
  - Tasks API: http://localhost:8000/api/tasks/docs

## Main Features

- **Complete Authentication System**
- User registration and login
- Profile management
- Rate limiting for security

- **Task CRUD Management**
- Create, read, update and delete tasks
- Assignment to users and teams
- Priorities, statuses and comments
- Tagging and category system

- **Database Optimization**
- Full-text search with PostgreSQL
- Performance-optimized indexes
- Data integrity constraints

- **Asynchronous Processing**
- Celery for background tasks
- Automatic data cleanup

- **Professional REST API**
- Django Ninja with automatic Swagger
- Robust data validation
- Interactive documentation

## Technologies Used

- **Backend**: Django 5.2.6, Django Ninja
- **Database**: PostgreSQL 15 
- **Cache**: Redis 7
- **Processing**: Celery + Redis
- **Frontend**: Django Templates + Bootstrap 5
- **Containerization**: Docker + Docker Compose

## Troubleshooting

**Port occupied**: `docker-compose down && docker-compose up -d`  
**DB problems**: `docker-compose down -v && docker-compose up -d`  
**View logs**: `docker-compose logs django_web`

## Testing
```bash
# Run all tests automatically
./run_tests.sh
```

## Rate Limiting
The system includes protection against attacks:
- **Login**: 10 attempts every 5 minutes
- **Email verification**: 10 attempts every 30 minutes
- **Email change**: 5 attempts every hour
