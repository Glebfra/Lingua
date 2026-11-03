# Japanese Language Learning Platform - Architectural Decisions

## 1. Decision Log

This document records significant architectural decisions (ADRs) made during the planning phase.

### 1.1 Authentication: JWT Tokens

**Status:** Accepted

**Context:**
The platform needs to support multiple client applications (web, mobile, desktop) with stateless authentication. The choice of authentication mechanism affects:
- Cross-device session management
- Scalability of the backend
- Security of the authentication flow
- Client implementation complexity

**Considered Options:**
1. **Session Authentication (Django default)**
   - Pros: Simple to implement, server-managed sessions
   - Cons: Stateful, requires session storage, harder to scale across services, less mobile-friendly

2. **JWT (JSON Web Tokens)**
   - Pros: Stateless, portable across services, better mobile support, easier horizontal scaling
   - Cons: Token expiration management, potential for token leakage

3. **OAuth 2.0 / OpenID Connect**
   - Pros: Industry standard, social login support, delegated authorization
   - Cons: Overly complex for single-tenant, external dependencies

**Decision:**
Use JWT tokens via `djangorestframework-simplejwt`.

**Rationale:**
- Stateless architecture enables horizontal scaling
- Better support for mobile and cross-platform clients
- Simpler token management for single-tenant model
- Well-supported by the Django ecosystem
- No need for session storage

**Consequences:**
- Tokens must have appropriate expiration times
- Need token refresh mechanism
- Client must securely store tokens
- Cannot rely on server-side session invalidation

**References:**
- RFC 7519: JSON Web Token
- djangorestframework-simplejwt documentation

**Date:** 2026-11-02
**Author:** Architecture Team

---

### 1.2 Tenancy: Single-Tenant Per User

**Status:** Accepted

**Context:**
The platform will serve Russian-speaking users learning Japanese. We need to determine the tenancy model:
- How is user data isolated?
- Can users belong to multiple organizations/teams?
- What is the sharing model?

**Considered Options:**
1. **Multi-tenant (organizations)**
   - Users belong to organizations
   - Data shared within organization boundaries
   - Org-level settings and subscriptions

2. **Single-tenant (one user = one tenant)**
   - Each user account is their own tenant
   - All user data is private
   - Sharing is explicit (user-created collections)

3. **Hybrid (users + optional organizations)**
   - Default single-tenant
   - Organizations as an optional future feature

**Decision:**
Start with single-tenant per user model.

**Rationale:**
- Simpler initial implementation
- Clear data ownership boundaries
- Fits the learning-focused use case
- Sharing is user-initiated (collections)
- Can evolve to multi-tenant if needed later

**Consequences:**
- No organizational features in initial scope
- User identity is the primary boundary
- Future multi-tenant requires significant refactoring
- User data is always private unless explicitly shared

**References:**
- Multi-tenant vs Single-tenant patterns

**Date:** 2026-11-02
**Author:** Architecture Team

---

### 1.3 Role Model: Student-Only

**Status:** Accepted

**Context:**
Determine if the platform needs role-based access control (RBAC).

**Considered Options:**
1. **Full RBAC (Admin, Teacher, Student)**
   - Different permissions per role
   - Admin manages content, teachers create courses, students learn
   - Complex permission system

2. **Minimal RBAC (Student, Teacher)**
   - Teachers create content, students consume
   - Some admin functionality

3. **No RBAC, Permission-Based**
   - All users have same permissions
   - Data ownership determines access
   - Sharing is explicit

**Decision:**
Student-only model with no RBAC. All users have equal permissions.

**Rationale:**
- Platform is for individual learning, not institutional use
- No teachers or content creators needed
- Users create their own content (words, sentences, decks)
- Data ownership and sharing control access, not roles
- Simplifies permission system significantly

**Consequences:**
- No admin dashboard in initial scope
- All users can create, edit, delete their own data
- No content moderation needed
- Future roles would require permission redesign

**References:**
- RBAC vs ACL (Access Control Lists)

**Date:** 2026-11-02
**Author:** Architecture Team

---

### 1.4 Data Sharing: Explicit Collections

**Context:**
Determine how users can share learning content.

**Considered Options:**
1. **Automatic Sharing**
   - All user content is public by default
   - Privacy settings control who can see

2. **Explicit Sharing**
   - All content is private by default
   - User must explicitly share collections

3. **No Sharing**
   - All content is private
   - No sharing mechanism

**Decision:**
Explicit sharing via collections (decks and lists).

**Rationale:**
- Privacy-first approach
- User controls what to share
- Collections provide context for sharing
- Natural learning workflow (create deck → share with friends)
- Reduces accidental content exposure

**Consequences:**
- Sharing is opt-in
- Collections are the sharing boundary
- Shared collections are read-only for viewers
- Users must actively manage sharing settings

**References:**
- Privacy by design principles

**Date:** 2026-11-02
**Author:** Architecture Team

---

### 1.5 Import Methods: Manual + File Upload

**Status:** Accepted

**Context:**
Determine how users can add dictionary content.

**Considered Options:**
1. **Manual Entry Only**
   - Users add words/sentences one by one
   - Simple, but time-consuming
   - Good for small dictionaries

2. **File Upload Only**
   - CSV/JSON import for bulk operations
   - Fast for large dictionaries
   - Users need to prepare files

3. **Hybrid Approach**
   - Both manual entry and file upload
   - Flexible for different use cases
   - More complex implementation

**Decision:**
Support both manual entry and file upload (CSV/JSON).

**Rationale:**
- Manual entry for quick additions and corrections
- File upload for importing large dictionaries
- Users have different preferences and workflows
- CSV/JSON are widely supported formats
- Allows gradual dictionary building

**Consequences:**
- More complex import validation
- Need file upload handling and storage
- Manual entry needs UI form
- Import jobs for background processing
- Duplicate detection required

**References:**
- Data import/export best practices

**Date:** 2026-11-02
**Author:** Architecture Team

---

### 1.6 Japanese Unicode Support: Full Unicode

**Status:** Accepted

**Context:**
Japanese language requires full Unicode support for:
- Hiragana (あいうえお)
- Katakana (アイウエオ)
- Kanji (漢字) - potentially thousands of characters
- Romaji (romanized)
- Furigana (pronunciation guides)

**Considered Options:**
1. **Limited Script Support**
   - Only basic Unicode
   - Some scripts not supported
   - Simplified rendering

2. **Full Unicode Support**
   - All Japanese scripts supported
   - Proper character encoding
   - Correct sorting and collation

3. **Third-Party Library**
   - Use specialized Japanese library
   - Handle character encoding internally
   - More complex dependencies

**Decision:**
Full Unicode support using standard Python/Django.

**Rationale:**
- Python and Django have excellent Unicode support
- PostgreSQL supports full Unicode (UTF-8)
- No need for specialized libraries
- Standard `str` type handles all Japanese scripts
- Proper collation via `collation='Japanese'` in PostgreSQL

**Consequences:**
- Must use UTF-8 everywhere
- Database must be configured for Unicode
- No character encoding issues expected
- Sorting requires proper collation rules

**References:**
- Unicode Standard for Japanese
- PostgreSQL Unicode collation

**Date:** 2026-11-02
**Author:** Architecture Team

---

### 1.7 Database: PostgreSQL

**Status:** Accepted

**Context:**
Select the database for production use.

**Considered Options:**
1. **SQLite**
   - Zero configuration
   - Fast for development
   - Not suitable for production

2. **PostgreSQL**
   - Full Unicode support
   - Robust and reliable
   - Excellent JSON support
   - Industry standard

3. **MySQL/MariaDB**
   - Widely used
   - Good performance
   - Slightly less Unicode features

**Decision:**
PostgreSQL for production, SQLite for development.

**Rationale:**
- PostgreSQL has best Unicode support
- JSONField support for flexible schemas
- Robust for concurrent access
- Industry standard for production
- SQLite for development (fast setup)

**Consequences:**
- Requires PostgreSQL for production
- Migration from SQLite to PostgreSQL needed
- PostgreSQL-specific features used
- Need connection pooling for scale

**References:**
- PostgreSQL documentation
- Django database backend comparison

**Date:** 2026-11-02
**Author:** Architecture Team

---

### 1.8 API Design: RESTful

**Status:** Accepted

**Context:**
Select API design style.

**Considered Options:**
1. **REST (Resource-Oriented)**
   - Standard CRUD operations
   - Resource-based URLs
   - Industry standard

2. **GraphQL**
   - Flexible queries
   - Single endpoint
   - Complex for simple use case

3. **GraphQL over REST**
   - Hybrid approach
   - REST for simplicity, GraphQL for flexibility

**Decision:**
RESTful API with Django REST Framework.

**Rationale:**
- Simple and predictable
- Standard HTTP methods
- Well-understood by clients
- DRF provides all needed features
- No need for GraphQL complexity

**Consequences:**
- Standard REST patterns
- Pagination required for lists
- Filtering via query parameters
- Clear API documentation

**References:**
- REST API best practices
- Django REST Framework guides

**Date:** 2026-11-02
**Author:** Architecture Team

---

### 1.9 Progress Tracking: Normalized Design

**Status:** Accepted

**Context:**
Determine how to track user learning progress.

**Considered Options:**
1. **Denormalized (single table)**
   - All progress in one table per user
   - Fast reads, complex updates
   - Data duplication

2. **Normalized (separate tables)**
   - Progress tracked per entity
   - Clear data relationships
   - Multiple queries for overview

3. **Hybrid**
   - Aggregated overview + detailed tracking
   - Best of both approaches

**Decision:**
Normalized design with separate progress tables.

**Rationale:**
- Clear data relationships
- Accurate progress tracking
- Easy to query specific items
- Django ORM handles joins efficiently
- Consistent with domain model

**Consequences:**
- Multiple queries for user overview
- Need to aggregate data
- Clear separation of concerns
- Easier to add new progress metrics

**References:**
- Database normalization principles

**Date:** 2026-11-02
**Author:** Architecture Team

---

### 1.10 Collections: Decks and Lists

**Status:** Accepted

**Context:**
Determine collection types for organizing learning content.

**Considered Options:**
1. **Single Collection Type**
   - One generic collection type
   - Flexible but less specific
   - Simplified model

2. **Two Collection Types (Decks, Lists)**
   - Decks: structured study collections
   - Lists: simple reference collections
   - Different use cases

3. **Three Collection Types**
   - Add "Favorites" type
   - More specific but complex

**Decision:**
Two collection types: Decks and Lists.

**Rationale:**
- Decks for structured study (with settings)
- Lists for simple organization
- Clear distinction in use cases
- Flexible enough for future expansion
- Not overly complex

**Consequences:**
- Different settings per type
- Decks have more configuration
- Lists are simpler
- Users understand the distinction

**References:**
- Collection organization patterns

**Date:** 2026-11-02
**Author:** Architecture Team

---

### 1.11 User Model: AbstractUser

**Status:** Accepted

**Context:**
Choose Django user model implementation.

**Considered Options:**
1. **UserModel (custom model)**
   - Full control over fields
   - Requires migration to new model
   - Cannot be changed after deployment

2. **AbstractUser**
   - Extends default User
   - Can be used as base in settings
   - All new user accounts use custom model

3. **AbstractBaseUser**
   - Minimal User model
   - Full control
   - More complex implementation

**Decision:**
AbstractUser for user model.

**Rationale:**
- Extends standard Django User fields
- Can be used without breaking existing code
- Standard authentication flow works
- Can add custom fields easily
- No migration needed

**Consequences:**
- Username and email are required
- Password hashing uses Django default
- Standard authentication views work
- Custom fields added to model

**References:**
- Django User model documentation

**Date:** 2026-11-02
**Author:** Architecture Team

---

## 2. Technical Decisions

### 2.1 Django Version: Latest Stable

**Decision:** Use the latest stable Django version.

**Rationale:**
- Best security patches
- Latest features
- Long-term support
- Active development

**Impact:**
- Requires Python 3.10+
- May break compatibility with older packages
- Need to verify DRF compatibility

---

### 2.2 Django REST Framework Version: Latest Compatible

**Decision:** Use latest DRF version compatible with Django.

**Rationale:**
- Best features and security
- Active development
- Bug fixes and improvements

**Impact:**
- Standard DRF features available
- Pagination, filtering, authentication built-in
- OpenAPI schema generation

---

### 2.3 JWT Library: djangorestframework-simplejwt

**Decision:** Use `djangorestframework-simplejwt` for JWT authentication.

**Rationale:**
- Well-maintained and popular
- Easy configuration
- Access/Refresh token pattern
- Built-in token refresh

**Impact:**
- Two token types (access, refresh)
- Token rotation support
- Blacklisting not built-in (need separate table)

---

### 2.4 File Upload: Standard Django

**Decision:** Use Django's built-in file upload for dictionary imports.

**Rationale:**
- No additional dependencies
- Standard Django behavior
- Security features included
- Simple implementation

**Impact:**
- File storage in Django settings
- File type validation required
- File size limits configurable
- Need file cleanup after processing

---

### 2.5 Background Tasks: No Celery Initially

**Decision:** No background task queue initially.

**Rationale:**
- Import jobs can use threading or async
- No complex background processes needed
- Keep initial implementation simple
- Can add Celery later if needed

**Impact:**
- Import jobs run synchronously
- Long imports block request
- Can add Celery later for scaling
- No message broker needed

---

### 2.6 Caching: No Caching Initially

**Decision:** No caching layer initially.

**Rationale:**
- Simple implementation
- No cache invalidation complexity
- Can add Redis/Memcached later
- Good for initial launch

**Impact:**
- Database queries for all data
- Potential performance bottlenecks
- Can scale to caching later
- No cache coherence issues

---

### 2.7 Image Storage: Default Local

**Decision:** Use default local file storage for now.

**Rationale:**
- Simple setup
- No S3 or cloud storage needed
- Can migrate later
- Works for development

**Impact:**
- Files stored on server
- Need to configure storage for production
- Can add cloud storage later
- File cleanup on server delete

---

## 3. Security Decisions

### 3.1 Authentication: JWT with Refresh Tokens

**Decision:** JWT access tokens with refresh token rotation.

**Rationale:**
- Stateless authentication
- Secure token refresh
- Token rotation prevents replay attacks
- Standard pattern

**Implementation:**
- Access tokens: short-lived (15 minutes)
- Refresh tokens: longer-lived (7 days), rotated on use
- Refresh tokens stored in database for invalidation
- Blacklist table for revoked tokens

**Security Impact:**
- Mitigates token leakage risk
- Limits damage from stolen tokens
- Standard security pattern

---

### 3.2 Authorization: Object-Level Permissions

**Decision:** Object-level permissions for data access.

**Rationale:**
- Prevents IDOR attacks
- Clear ownership boundaries
- Server-enforced access control
- No reliance on client

**Implementation:**
- Custom permission classes
- Queryset filtering by user
- Object-level checks in viewsets
- Permissions on serializers

**Security Impact:**
- Prevents unauthorized data access
- Protects against BOLA attacks
- Clear audit trail

---

### 3.3 Input Validation: Strict at API Boundary

**Decision:** Strict validation at all API boundaries.

**Rationale:**
- Prevents injection attacks
- Validates all user input
- Type safety
- Clear error messages

**Implementation:**
- Django forms for validation
- DRF validators
- Custom validators for Japanese text
- File type and size validation

**Security Impact:**
- Prevents SQL injection
- Prevents XSS
- Prevents file upload attacks
- Input sanitization

---

### 3.4 Secret Management: Environment Variables

**Decision:** All secrets via environment variables.

**Rationale:**
- No secrets in code
- Different per environment
- Secure deployment
- Standard practice

**Implementation:**
- `.env` file for development
- Environment variables for production
- `SECRET_KEY` via environment
- Database credentials via environment

**Security Impact:**
- Secrets not in source control
- Clear separation of environments
- Production security best practice

---

### 3.5 CORS: Explicit Origins

**Decision:** Explicit CORS origins, not wildcard.

**Rationale:**
- Security best practice
- Prevents unauthorized access
- Clear allowed origins
- Production security

**Implementation:**
- Configure `CORS_ALLOWED_ORIGINS`
- Separate dev and prod origins
- No wildcard in production
- Development allows localhost

**Security Impact:**
- Prevents unauthorized cross-origin access
- Clear security boundary
- Standard CORS configuration

---

## 4. Performance Decisions

### 4.1 Database Indexes: Selective

**Decision:** Indexes only on frequently queried fields.

**Rationale:**
- Write performance impact
- Storage overhead
- Query-specific optimization
- Avoid over-indexing

**Implementation:**
- Index on `kanji`, `romaji` for lookups
- Index on `created_at` for chronological queries
- Index on `owner` for user queries
- Composite indexes for filtering

**Performance Impact:**
- Faster queries
- Slightly slower writes
- Reduced storage
- Need to monitor query plans

---

### 4.2 QuerySets: Avoid N+1

**Decision:** Use `select_related()` and `prefetch_related()`.

**Rationale:**
- Prevent N+1 queries
- Efficient database access
- Django ORM optimization
- Better performance

**Implementation:**
- `select_related()` for foreign keys
- `prefetch_related()` for many-to-many
- Custom manager methods
- Query optimization

**Performance Impact:**
- Significantly fewer queries
- Faster API responses
- Better user experience
- Reduced database load

---

### 4.3 Pagination: Default 100 Items

**Decision:** Default page size of 100 items, max 1000.

**Rationale:**
- Reasonable default
- Configurable
- Prevents large responses
- Performance protection

**Implementation:**
- DRF pagination classes
- Query parameter override
- Max page size limit
- Server-side enforcement

**Performance Impact:**
- Controlled response sizes
- Better client experience
- Reduced bandwidth
- Faster transfers

---

### 4.4 File Upload: Streaming

**Decision:** Stream file uploads for large files.

**Rationale:**
- Memory efficient
- Handle large files
- Progress reporting
- Better resource usage

**Implementation:**
- Streaming uploads
- Chunked processing
- Progress tracking
- Background processing

**Performance Impact:**
- Reduced memory usage
- Handle large files
- Better resource utilization
- Can process while streaming

---

## 5. Extensibility Decisions

### 5.1 Language Support: Extensible

**Decision:** Design for multiple target languages.

**Rationale:**
- Current focus: Japanese
- Future: Multiple languages
- Language as first-class entity
- Easy extension

**Implementation:**
- Language model
- User has target language
- Language-specific fields
- Language configuration

**Extensibility Impact:**
- Easy to add new languages
- Minimal code changes
- Clear separation
- Scalable architecture

---

### 5.2 Feature Evolution: Modular

**Decision:** Modular design for feature additions.

**Rationale:**
- Clear boundaries
- Easy to add features
- Minimal impact on existing code
- Testable components

**Implementation:**
- Separate apps per domain
- Clear interfaces
- Dependency injection
- Plugin-ready design

**Extensibility Impact:**
- Easy to add new features
- Minimal refactoring
- Clear ownership
- Better maintainability

---

## 6. Future Considerations

### 6.1 Spaced Repetition

**Consideration:** Add SRS algorithm.

**Status:** Not in scope for Phase 1

**Rationale:**
- Complex algorithm implementation
- Requires additional data fields
- Can be added later
- Not core to platform

**Future Implementation:**
- Ease factor
- Interval tracking
- Review scheduling
- SRS algorithm library

---

### 6.2 Social Features

**Consideration:** User profiles, leaderboards.

**Status:** Not in scope for Phase 1

**Rationale:**
- Adds complexity
- Privacy concerns
- Can be added later
- Not core to learning

**Future Implementation:**
- User profiles
- Activity feeds
- Leaderboards
- Friend system

---

### 6.3 Gamification

**Consideration:** Achievements, streaks, badges.

**Status:** Not in scope for Phase 1

**Rationale:**
- Adds complexity
- Motivational features
- Can be added later
- Not core to learning

**Future Implementation:**
- Achievement system
- Study streaks
- Level progression
- Badge system

---

### 6.4 Multi-Tenant Evolution

**Consideration:** Add organizational support.

**Status:** Not in scope for Phase 1

**Rationale:**
- Significant refactoring
- Complex permission model
- Can be added later
- Not needed initially

**Future Implementation:**
- Organization model
- User-organization relationship
- Org-level permissions
- Org-specific settings

---

## 7. Glossary

| Term | Definition |
|------|------------|
| **Single-Tenant** | Each user has their own data boundary |
| **Multi-Tenant** | Users grouped into organizations/tenants |
| **JWT** | JSON Web Token for stateless authentication |
| **RBAC** | Role-Based Access Control |
| **ACL** | Access Control List |
| **SRS** | Spaced Repetition System |
| **N+1** | Database query pattern inefficiency |
| **IDOR** | Insecure Direct Object Reference vulnerability |
| **BOLA** | Broken Object Level Authorization |
| **CORS** | Cross-Origin Resource Sharing |

---

## 8. Revision History

| Version | Date | Author | Description |
|---------|------|--------|-------------|
| 1.0 | 2026-11-02 | Architecture Team | Initial architectural decisions |

---

## 9. Open Questions

### 9.1 Spaced Repetition Algorithm

**Question:** Which SRS algorithm to use (SuperMemo-2, FSRS, etc.)?

**Status:** Not decided

**Impact:** Medium (affects progress tracking)

**Next Decision:** During Phase 1 implementation

---

### 9.2 Offline Support

**Question:** Should the platform support offline learning?

**Status:** Not decided

**Impact:** High (affects architecture significantly)

**Next Decision:** Based on client requirements

---

### 9.3 Real-Time Features

**Question:** Should we support real-time collaboration (e.g., shared study sessions)?

**Status:** Not decided

**Impact:** Medium (requires WebSocket or polling)

**Next Decision:** Based on product requirements

---
