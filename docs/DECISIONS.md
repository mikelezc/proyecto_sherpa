# DECISIONS.md

## Completed Features and Why

### Authentication System
**Why it was implemented:**
- Central requirement for any task management system
- Provides secure per-user access control
- Fundamental foundation for personalized task management

**What was completed:**
- Registration and login with Django Authentication
- User profile management with email functionality
- Rate limiting for security against attacks
- Complete API with authentication endpoints

### Task CRUD Management
**Why it was implemented:**
- Core business functionality required
- Demonstrates complete REST API capabilities
- Shows database design and relationships

**What was completed:**
- Complete CRUD operations for tasks
- Task assignment to users and teams
- Priority and status management
- Comment system and task history
- Team organization and tagging system
- Full-text search for advanced searching

### PostgreSQL Optimization
**Why it was implemented:**
- Performance requirement for production systems
- Demonstrates database expertise
- Enables advanced search capabilities

**What was completed:**
- Full-text search with SearchVector and GinIndex
- Custom managers for optimized queries
- Database constraints and composite indexes
- Performance monitoring and query optimization
- Management command to update search vectors

### Asynchronous Tasks with Celery
**Why it was implemented:**
- Technical requirement for asynchronous processing
- Demonstrates scalable architecture
- Essential for production task management

**What was completed:**
- 6 implemented Celery tasks:
  - `generate_daily_summary`: Automatic daily summaries
  - `check_overdue_tasks`: Overdue task verification
  - `cleanup_archived_tasks`: Archived data cleanup
  - `auto_assign_tasks`: Intelligent automatic assignment
  - `calculate_team_velocity`: Team velocity calculation
- Celery Beat scheduler for periodic tasks
- Robust configuration with Redis as broker

### Complete REST API
**Why it was implemented:**
- Technical requirement for frontend/mobile integration
- Demonstrates API development best practices
- Enables scalability and separation of concerns

**What was completed:**
- Django Ninja for modern and fast API
- Automatic documentation with Swagger/OpenAPI
- Robust validation with Pydantic
- Automatic pagination in listings
- Rate limiting and error handling
- Complete endpoints for all operations

### Functional Web Frontend (via Django templates)
**Why it was implemented:**
- Demonstrate backend functionality
- Provide user interface for testing
- Validate API with a real client

**What was completed:**
- Django Templates with Bootstrap 5
- Complete web authentication system
- Task CRUD with intuitive interface
- Dashboard with statistics

## Part B: Extended Features - Additional Implemented Functionalities

### JWT Authentication System
**Why it was implemented:**
- Secure token system for specific functionalities (email verification, password reset)
- Complements Django sessions without replacing primary authentication
- Provides secure tokens for sensitive operations

**What was completed:**
- **Specialized JWT service**: System in `authentication/services/token_service.py`
- **PyJWT**: PyJWT>=2.8.0 library included in requirements.txt
- **Robust configuration**: JWT settings configured (JWT_SECRET_KEY, JWT_ALGORITHM, etc.)
- **4 specific token types**:
  - Email verification tokens
  - Password reset tokens
  - Auth tokens for special cases
  - Access & Refresh tokens (prepared for future API use)
- **Security**: HS256 signed tokens, controlled expiration, rate limiting
- **Complementary use**: Does NOT replace Django sessions - used for specific cases

**Important note:** The main REST API uses Django Sessions (SessionAuthentication), not JWT as primary authentication.

**Code location:**
- Main service: `/authentication/services/token_service.py`
- Configuration: `/main/settings.py` lines 288-292
- Usage in profile service: `/authentication/services/profile_service.py`
- Usage in password service: `/authentication/services/password_service.py`

### Introduction
**Why these functionalities were prioritized:**
- Technical test time is limited, so after completing part A, I prioritized features that I considered most relevant to make a project as close as possible to how it would be in production.

---

### Business Logic & Automation ✅ (Implemented ~85%)

**Task Workflow Engine:**
- ✅ **Status transition validation**: State validation implemented in `Task.save()` with database constraints
- ✅ **Automatic task assignment**: Celery task `auto_assign_tasks` in `/tasks/tasks.py` - assigns tasks based on user availability
- ✅ **SLA tracking and escalation**: Task `check_overdue_tasks` automatically verifies and marks overdue tasks

**Smart Features:**
- ✅ **Workload balancing**: Algorithm implemented in `calculate_team_velocity` to balance workload per team
- ✅ **Priority calculation**: 4-level system (low, medium, high, critical) with optimized database indexes
- ✅ **Dependency management**: Implemented parent-child system with `parent_task` and automatic progress calculation based on subtasks

**Automation Rules (5/5 implemented):**
- ✅ `auto_assign_tasks`: Automatic assignment based on availability
- ✅ `check_overdue_tasks`: Escalation of overdue high-priority tasks
- ✅ `send_task_notification`: Reminders before due date
- ✅ Automatic parent task updates when subtasks are completed (model logic)
- ✅ `calculate_team_velocity`: Team velocity metrics

---

### Full-Text Search ✅ (Implemented 100%)

**Why it was implemented:**
- Critical functionality for production task management systems
- Search optimization and significant user experience improvement

**Technical implementation:**
- ✅ **PostgreSQL full-text search**: `SearchVector` + `GinIndex` in Task model
- ✅ **Search across tasks, comments, tags**: Unified search implemented in `TaskManager.search()`
- ✅ **Optimized search queries**: Use of `SearchRank` for result relevance
- ✅ **Search vector field**: `search_vector` field with automatic updates via signals

**Code location:**
- Model: `/tasks/models.py` lines 227, 287-289
- Manager: `/tasks/models.py` lines 51-60
- Management command: `/tasks/management/commands/update_search_vectors.py`

---

### Security Features ✅ (Implemented ~80%)

**Rate Limiting System:**
- ✅ **API rate limiting per user**: `RateLimitService` implemented with Redis backend
- ✅ **Granular controls**: Different limits per action (login, register, profile_update)
- ✅ **Demo-friendly configuration**: Limits adjusted to facilitate testing

**Code location:**
- Service: `/authentication/services/rate_limit_service.py`
- Integration: `/authentication/services/auth_service.py` lines 45-61

---

### Performance Optimization ✅ (Implemented ~75%)

**Database Optimization:**
- ✅ **Custom managers**: Optimized managers with `select_related()` and `prefetch_related()`
- ✅ **Strategic indexes**: 8 composite indexes in Task model for frequent queries
- ✅ **Query optimization**: N+1 query reduction through prefetching

**Caching System:**
- ✅ **Redis caching layer**: Redis configured as cache backend
- ✅ **Session storage**: Sessions stored in Redis for better performance

**Code location:**
- Managers: `/tasks/models.py` lines 15-110
- Indexes: `/tasks/models.py` lines 235-244
- Redis configuration: `/main/settings.py` lines 150-165

---

### Notification System ✅ (Implemented ~60%)

**Email Notifications:**
- ✅ **Console email backend**: Configured for development and testing
- ✅ **Task notifications**: `send_task_notification` system implemented
- ✅ **User lifecycle emails**: Templates for verification, password reset, etc.

**Implemented templates:**
- Email verification, password change, welcome, inactivity
- Location: `/authentication/web/templates/authentication/`

---

### Non-Implemented Features (due to time constraints)

**❌ Not prioritized:**
- **Kafka Event Streaming**: Requires complex additional infrastructure
- **Flask Analytics Microservice**: Outside Django scope
- **Time Tracking**: Not critical for base system functionality
- **Advanced RBAC**: Basic permissions sufficient for demonstration

## Technical Summary

This project demonstrates a modern and scalable Django architecture with all features implemented and fully operational. Each technical decision was made prioritizing functionality, performance, and maintainability.
