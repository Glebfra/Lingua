# Development Setup Guide

This guide walks you through setting up the development environment for the Japanese language learning platform.

## Prerequisites

### Required Software

1. **Python 3.14**
   - Download from https://www.python.org/downloads/
   - Verify installation: `python --version`

2. **uv** (Package Manager)
   - Install: `curl -LsSf https://astral.sh/uv/install.sh | sh`
   - Add to PATH (if needed): `export PATH="$HOME/.local/bin:$PATH"`
   - Verify: `uv --version`

3. **Git**
   - Download from https://git-scm.com/
   - Verify: `git --version`

4. **Docker** (Optional, for development database)
   - Download from https://www.docker.com/
   - Verify: `docker --version`

5. **Node.js** (Optional, for development tools)
   - Download from https://nodejs.org/
   - Verify: `node --version`

### Operating System

This platform has been tested on:
- Ubuntu 22.04 LTS
- Windows 10/11 (WSL2)
- macOS 12+

## Quick Start

### 1. Clone Repository

```bash
git clone <repository-url>
cd lingua
```

### 2. Install Dependencies

```bash
# Using uv
uv sync
```

This will:
- Create a virtual environment
- Install all dependencies from `pyproject.toml`
- Create `.venv` directory

### 3. Configure Environment

```bash
# Copy environment template
cp .env.example .env

# Edit environment variables
nano .env
```

### 4. Set Environment Variables

Edit `.env` and set:

```env
# Required
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Database (SQLite for development)
DATABASE_URL=sqlite:///db.sqlite3

# Or PostgreSQL (recommended)
DATABASE_URL=postgresql://user:password@localhost:5432/lingua_dev
```

**Important:** Never commit `.env` to Git!

### 5. Run Migrations

```bash
# Activate virtual environment
source .venv/bin/activate  # Linux/macOS
# or
.venv\Scripts\activate  # Windows

# Run migrations
python manage.py migrate
```

### 6. Create Superuser

```bash
python manage.py createsuperuser
```

Enter username, email, and password.

### 7. Start Development Server

```bash
# Run development server
python manage.py runserver
```

Access at: http://localhost:8000

### 8. Access Admin Panel

```
http://localhost:8000/admin/
```

Login with the superuser credentials.

## Full Development Setup

### Step-by-Step Instructions

#### 1. Initial Setup

```bash
# Clone repository
git clone <repository-url>
cd lingua

# Create virtual environment using uv
uv sync

# Configure environment
cp .env.example .env
```

#### 2. Database Setup

**Option A: SQLite (Development Only)**

```bash
# No additional setup needed
# Uses db.sqlite3 file in project directory
DATABASE_URL=sqlite:///db.sqlite3
```

**Option B: PostgreSQL (Recommended)**

1. Install PostgreSQL:
   ```bash
   # Ubuntu/Debian
   sudo apt install postgresql postgresql-contrib

   # macOS (with Homebrew)
   brew install postgresql
   ```

2. Create database:
   ```bash
   sudo -u postgres psql
   CREATE DATABASE lingua_dev;
   CREATE USER lingua_dev_user WITH PASSWORD 'password';
   GRANT ALL PRIVILEGES ON DATABASE lingua_dev TO lingua_dev_user;
   \q
   ```

3. Update `.env`:
   ```env
   DATABASE_URL=postgresql://lingua_dev_user:password@localhost:5432/lingua_dev
   ```

#### 3. Run Initial Migrations

```bash
# Create superuser
python manage.py createsuperuser

# Run migrations
python manage.py migrate
```

#### 4. Verify Installation

```bash
# Check Django version
python -c "import django; print(django.VERSION)"

# Check database connection
python manage.py dbshell
```

## Running Tests

### Run All Tests

```bash
# Using pytest
pytest

# Or with Django test runner
python manage.py test
```

### Run Specific Test

```bash
# Run tests for specific app
pytest lingua_words/

# Run tests with coverage
pytest --cov=lingua_words --cov-report=html
```

### Generate Coverage Report

```bash
# HTML report
pytest --cov=lingua --cov-report=html

# Open in browser
open htmlcov/index.html  # macOS
start htmlcov\index.html  # Windows
```

## Linting and Formatting

### Format Code

```bash
# Format all files
ruff format

# Format specific file
ruff format lingua_words/
```

### Lint Code

```bash
# Check all files
ruff check

# Check specific file
ruff check lingua_words/

# Auto-fix linting issues
ruff check --fix
```

### Type Checking

```bash
# Check types with mypy
mypy lingua/

# Or use pyright
pyright lingua/
```

## Debugging

### Debug Mode

The `.env` file should have `DEBUG=True` for development.

### Debug Settings

```python
# In lingua/settings.py
DEBUG = True

# Allowed hosts
ALLOWED_HOSTS = ['localhost', '127.0.0.1']

# Django debug toolbar (optional)
INSTALLED_APPS = [
    # ... other apps
    'debug_toolbar',
]

MIDDLEWARE = [
    # ... other middleware
    'debug_toolbar.middleware.DebugToolbarMiddleware',
]

DEBUG_TOOLBAR_CONFIG = {
    'SHOW_TOOLBAR_CALLBACK': lambda request: True,
}
```

Access debug toolbar at: `http://localhost:8000/_debug_toolbar/`

### Logging

Logs are written to console by default. To enable file logging:

```python
# In lingua/settings.py
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': 'logs/django.log',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file'],
            'level': 'DEBUG',
            'propagate': True,
        },
    },
}
```

## Database Management

### View Database

```bash
# Using Django shell
python manage.py dbshell
```

### Create New Database

```bash
# Using Django migrations
python manage.py migrate --empty

# Or manually with psql
psql lingua_db
CREATE TABLE ...
```

### Reset Database

**Warning:** This deletes all data!

```bash
# Delete all tables
python manage.py flush --no-input

# Or drop and recreate database
# (Use database-specific commands)
```

### Run Migrations

```bash
# Apply all migrations
python manage.py migrate

# Show migration status
python manage.py showmigrations

# Create new migration
python manage.py makemigrations

# Apply specific app migrations
python manage.py migrate lingua_words
```

## API Documentation

### OpenAPI Schema

Generate OpenAPI schema:

```bash
# Generate schema
python manage.py spectral

# Or use DRF built-in
python manage.py drfspectacular
```

Access at: `http://localhost:8000/api/schema/`

### Test API

Use tools like:
- Postman
- Insomnia
- curl
- HTTPie

Example:

```bash
# Test login
curl -X POST http://localhost:8000/api/token/ \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"password"}'
```

## Common Issues

### Issue: `ModuleNotFoundError: No module named 'lingua'`

**Solution:** Activate virtual environment

```bash
source .venv/bin/activate  # Linux/macOS
# or
.venv\Scripts\activate  # Windows
```

### Issue: Database connection error

**Solution:** Check database configuration

```bash
# Test database connection
python manage.py checkdb

# Or check PostgreSQL status
sudo systemctl status postgresql  # Linux
brew services list | grep postgres  # macOS
```

### Issue: Permission denied on db.sqlite3

**Solution:** Check file permissions

```bash
chmod 644 db.sqlite3
# or
chown $USER db.sqlite3
```

### Issue: Static files not found

**Solution:** Collect static files

```bash
# For development
python manage.py collectstatic --noinput

# Or use Django debug toolbar to see errors
```

## Development Workflow

### 1. Create Branch

```bash
git checkout -b feature/new-feature
```

### 2. Make Changes

- Write code
- Add tests
- Update documentation

### 3. Run Tests

```bash
pytest
```

### 4. Format and Lint

```bash
ruff format
ruff check
```

### 5. Type Check

```bash
mypy lingua/
```

### 6. Commit Changes

```bash
git add .
git commit -m "Add new feature"
```

### 7. Push to Remote

```bash
git push origin feature/new-feature
```

## Environment Variables Reference

| Variable | Description | Required | Default |
|----------|-------------|----------|---------|
| `SECRET_KEY` | Secret key for security | Yes | - |
| `DEBUG` | Debug mode | Yes | False |
| `ALLOWED_HOSTS` | Allowed hosts | Yes | - |
| `DATABASE_URL` | Database connection string | Yes | - |
| `JWT_SECRET_KEY` | JWT signing key | Yes | - |
| `JWT_ACCESS_TOKEN_LIFETIME` | Access token lifetime (seconds) | No | 900 |
| `JWT_REFRESH_TOKEN_LIFETIME` | Refresh token lifetime (seconds) | No | 604800 |
| `CORS_ALLOWED_ORIGINS` | Allowed CORS origins | Yes | - |
| `STATIC_URL` | Static files URL | Yes | /static/ |
| `MEDIA_URL` | Media files URL | Yes | /media/ |
| `STATIC_ROOT` | Static files collection directory | No | - |
| `MEDIA_ROOT` | Media files storage directory | No | - |

## Next Steps

1. **[Architecture Documentation](../architecture/overview.md)** - Understand the system architecture
2. **[API Design](../architecture/api-design.md)** - Learn the API endpoints
3. **[Domain Model](../architecture/domain-model.md)** - Understand the data model
4. **[Roadmap](../roadmap.md)** - See the implementation plan

## Support

For help:
- Check the [Architecture Documentation](../architecture/overview.md)
- Review [API Design](../architecture/api-design.md)
- Open an issue on GitHub
- Contact the development team
