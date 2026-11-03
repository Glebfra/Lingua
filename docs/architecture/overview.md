# Japanese Language Learning Platform - Architecture Overview

## 1. System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        Client Layer                              │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐     │
│  │   Web App   │  │   Mobile    │  │    Desktop Client   │     │
│  │   (React)   │  │  (React)    │  │   (Electron/Tauri)  │     │
│  └─────────────┘  └─────────────┘  └─────────────────────┘     │
└─────────────────────────────────────────────────────────────────┘
                              │
                              │ HTTPS / REST API
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                      Django REST Framework                       │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │              Django REST Framework                       │   │
│  │  ┌─────────────┐  ┌─────────────┐  ┌──────────────┐    │   │
│  │  │   JWT Auth  │  │  Permission │  │   Serializers│    │   │
│  │  │    System   │  │   Classes   │  │      System  │    │   │
│  │  └─────────────┘  └─────────────┘  └──────────────┘    │   │
│  └─────────────────────────────────────────────────────────┘   │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │                    ViewSets                              │   │
│  └─────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                       Service Layer                              │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │                  Business Logic Services                 │   │
│  │  ┌─────────────┐  ┌─────────────┐  ┌──────────────┐    │   │
│  │  │   Learning  │  │  Dictionary │  │   Collection │    │   │
│  │  │  Progress   │  │   Manager   │  │     Service  │    │   │
│  │  └─────────────┘  └─────────────┘  └──────────────┘    │   │
│  │  ┌─────────────┐  ┌─────────────┐  ┌──────────────┐    │   │
│  │  │   Quiz/Exercise│ │   Translation│ │   User Data │    │   │
│  │  │   Generator  │ │     Service  │  │    Service   │    │   │
│  │  └─────────────┘  └─────────────┘  └──────────────┘    │   │
│  └─────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                       Data Layer                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │                    PostgreSQL Database                   │   │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌────────┐  │   │
│  │  │ users    │  │ words    │  │ sentences│  │ decks  │  │   │
│  │  └──────────┘  └──────────┘  └──────────┘  └────────┘  │   │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌────────┐  │   │
│  │  │ progress │  │ quizzes  │  │ exercises│  │ notes  │  │   │
│  │  └──────────┘  └──────────┘  └──────────┘  └────────┘  │   │
│  └─────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
```

## 2. Technology Stack

### Backend
- **Python 3.14**: Latest stable version with comprehensive Unicode support (essential for Japanese characters)
- **Django 5.x**: Full-featured web framework with ORM
- **Django REST Framework 3.x**: REST API framework with built-in pagination, authentication, and serialization
- **PostgreSQL**: Production-grade relational database with full Unicode support
- **JWT (JSON Web Tokens)**: Stateless authentication via `djangorestframework-simplejwt`

### Client-Side Technologies (Future)
- **React**: Web and mobile applications
- **Electron/Tauri**: Desktop applications
- **SQLite (Development)**: Local database for development

### Development Tools
- **uv**: Fast Python package manager and virtual environment tool
- **Ruff**: Fast Python linter and formatter
- **Pytest**: Testing framework with `pytest-django`
- **mypy/Pyright**: Static type checking

## 3. Core Principles

### 3.1 Single-Tenant Architecture
- Each user account represents a single learner
- No organizational or multi-tenant boundaries
- User data is private and not shared with other users
- Shared learning occurs through user-created collections (decks, lists)

### 3.2 Authentication Model
- JWT-based stateless authentication
- No role-based access control (RBAC)
- All users have the same permissions (student role)
- Data isolation at the user level through Django's user model

### 3.3 Data Ownership
- Users own their own data exclusively
- Collections (decks, lists) are user-owned but can be marked as "shared"
- Shared content is read-only for other users
- No cross-user data modification possible

### 3.4 Japanese Language Support
- Full Unicode support for all Japanese scripts:
  - Hiragana (あいうえお)
  - Katakana (アイウエオ)
  - Kanji (漢字) with various stroke orders
  - Romaji (romanized Japanese)
  - Furigana (pronunciation guides over kanji)
- Support for complex Japanese character encoding
- Proper handling of full-width/half-width characters
- Support for Japanese punctuation and spacing conventions

## 4. API Design Philosophy

### 4.1 Resource-Oriented URLs
- RESTful resource naming conventions
- Plural resource names (e.g., `/api/words/`, `/api/sentences/`)
- Nested resources for relationships (e.g., `/api/decks/{id}/words/`)

### 4.2 Consistent Response Structure
```json
{
  "count": 10,
  "next": "https://api.example.com/api/words/?page=2",
  "previous": null,
  "results": [...]
}
```

### 4.3 Error Handling
- Standardized error responses
- Appropriate HTTP status codes
- Detailed error messages in development, generic in production

### 4.4 Pagination
- Default page size: 100 items
- Configurable page size with reasonable limits
- Cursor-based or offset-based pagination

## 5. Security Considerations

### 5.1 Authentication
- JWT tokens with appropriate expiration
- Token refresh mechanism
- Secure token storage recommendations for clients

### 5.2 Authorization
- Object-level permissions (users can only access their own data)
- Collection sharing permissions (owner controls who can read shared collections)
- CSRF protection for state-changing operations

### 5.3 Data Protection
- Password hashing using Django's built-in mechanisms
- SQL injection prevention through ORM
- XSS prevention through proper serialization
- Rate limiting for API endpoints

### 5.4 Input Validation
- Strict validation at API boundaries
- Sanitization of user-generated content
- File upload validation (type, size, content)

## 6. Performance Considerations

### 6.1 Database Optimization
- Indexed queries on frequently filtered fields
- `select_related()` and `prefetch_related()` to prevent N+1 queries
- Appropriate data types (e.g., `DecimalField` for scores)

### 6.2 API Optimization
- Pagination to limit response sizes
- Efficient queryset construction
- Caching strategies for frequently accessed data

### 6.3 Unicode Performance
- Efficient Unicode string handling
- Proper collation for Japanese text sorting
- Memory-efficient storage of large text fields

## 7. Scalability Considerations

### 7.1 Current State
- Single-instance deployment sufficient for initial launch
- PostgreSQL handles concurrent reads efficiently
- JWT statelessness enables horizontal scaling

### 7.2 Future Considerations
- Database connection pooling
- CDN for static assets
- Message queues for background tasks (future)
- Caching layers (future)

## 8. Extensibility

### 8.1 Multi-Language Support
- Architecture designed to support additional languages
- Language model as first-class entity
- Language-specific fields and configurations

### 8.2 Feature Evolution
- Modular service architecture
- Clear separation of concerns
- Plugin-ready design for future features

## 9. Deployment Considerations

### 9.1 Development
- Docker Compose for local development
- SQLite for development database
- Environment-based configuration

### 9.2 Production
- PostgreSQL with connection pooling
- Reverse proxy (Nginx)
- HTTPS termination
- Environment-based secrets management

## 10. Documentation Structure

```
docs/
├── architecture/
│   ├── overview.md              # This file
│   ├── domain-model.md          # Detailed data model
│   ├── api-design.md            # API specification
│   └── decisions.md             # ADRs and design decisions
├── development/
│   ├── roadmap.md               # Implementation phases
│   ├── setup.md                 # Development setup
│   └── testing.md               # Testing guidelines
├── api/
│   └── openapi.yaml             # Auto-generated API spec
├── operational/
│   ├── deployment.md            # Deployment guide
│   └── monitoring.md            # Monitoring and observability
└── README.md                    # Project readme
```

## 11. Glossary

- **Deck**: A collection of words or sentences for learning
- **List**: A simpler collection type, may be a subset of a deck
- **Word**: A single word with Japanese and possibly English definitions
- **Sentence**: A sentence with Japanese text and possibly English translation
- **Progress**: Learning progress tracking (mastery level, review count, etc.)
- **Collection**: Generic term for decks and lists

## 12. Revision History

| Version | Date | Author | Description |
|---------|------|--------|-------------|
| 1.0 | 2026-11-02 | Architecture Team | Initial architecture design |
