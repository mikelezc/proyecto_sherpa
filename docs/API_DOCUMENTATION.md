# API Documentation

## Overview

RESTful API for task management built with Django Ninja. Provides comprehensive endpoints for authentication, user management, and task operations with automatic OpenAPI documentation.

## Interactive Documentation

- **Complete API Docs**: 
	http://localhost:8000/api/auth/docs
	http://localhost:8000/api/tasks/docs

- **Health Check**:
	http://localhost:8000/health/

## Quick Start

```bash
# Start the system
docker-compose up -d

# Verify health
curl http://localhost:8000/health/
# Response: {"status": "healthy", "database": "healthy", "redis": "healthy"}
```

## API Structure

### Authentication API (`/api/auth/`)
- User registration and login
- JWT token management
- User profile operations

### Tasks API (`/api/tasks/`)
- Task CRUD operations
- Advanced search and filtering
- Assignment management
- Comments and history tracking

## Key Features

### 🔍 Advanced Search
- Full-text search across title and description
- Multi-field filtering (status, priority, assigned user, tags)
- Relevance scoring for search results

### 🔒 Security
- JWT authentication with refresh tokens
- Permission-based access control
- Rate limiting protection

### 📊 Data Management
- Soft delete for data integrity
- Comprehensive audit trail
- Optimized database queries with indexing

### 🚀 Performance
- Pagination for large datasets
- Redis caching for frequent queries
- Database query optimization

## Authentication Flow

```bash
# 1. Register
POST /api/auth/register/
{
  "username": "john_doe",
  "email": "john@example.com",
  "password1": "secure_password",
  "password2": "secure_password"
}

# 2. Login
POST /api/auth/login/
{
  "username": "john_doe", 
  "password": "secure_password"
}
# Returns: JWT access_token and refresh_token

# 3. Use authenticated endpoints
# Include: Authorization: Bearer {access_token}
```

## Task Operations Example

```bash
# Create task
POST /api/tasks/tasks/
{
  "title": "Implement new feature",
  "description": "Add user dashboard functionality",
  "priority": "high",
  "due_date": "2025-09-15T15:30:00Z"
}

# Search tasks
GET /api/tasks/tasks/?search=dashboard&status=todo&priority=high

# Assign users
POST /api/tasks/{id}/assign/
{
  "user_ids": [1, 2],
  "is_primary": true
}
```

## Response Format

All API responses follow a consistent structure:

```json
{
  "success": true,
  "data": { ... },
  "message": "Optional descriptive message",
  "pagination": {
    "page": 1,
    "page_size": 10,
    "total": 50,
    "total_pages": 5
  }
}
```

## Error Handling

| Code | Description |
|------|-------------|
| 400 | Bad Request - Invalid data or parameters |
| 401 | Unauthorized - Missing or invalid authentication |
| 403 | Forbidden - Insufficient permissions |
| 404 | Not Found - Resource does not exist |
| 429 | Too Many Requests - Rate limit exceeded |
| 500 | Internal Server Error - Server-side error |

## Development Tools

### Interactive Testing
Visit the Swagger UI interfaces for complete API exploration:
- **Auth API**: http://localhost:8000/api/auth/docs
- **Tasks API**: http://localhost:8000/api/tasks/docs

### OpenAPI Specification
- **Auth Schema**: http://localhost:8000/api/auth/openapi.json
- **Tasks Schema**: http://localhost:8000/api/tasks/openapi.json

### Client Generation
Use the OpenAPI schemas to generate client SDKs for your preferred programming language.

## Production Considerations

- **Environment Variables**: Configure secure secrets in production
- **Rate Limiting**: Implement appropriate limits for public APIs
- **CORS**: Adjust CORS settings for production domains
- **Monitoring**: Set up logging and monitoring for API usage
- **Caching**: Tune Redis cache settings for optimal performance

## ⚠️ Important Notes

- **Dates**: Use ISO 8601 format (YYYY-MM-DDTHH:MM:SSZ)
- **Pagination**: Maximum 100 items per page
- **Soft Delete**: Deleted tasks are archived, not permanently removed
- **JWT Tokens**: Access token expires in 15 minutes, refresh token in 7 days
- **CORS**: Configured for local development
- **Rate Limiting**: Not implemented (recommended for production)

---

**💡 For detailed endpoint specifications, request/response schemas, and interactive testing, use the Swagger UI documentation linked above.**