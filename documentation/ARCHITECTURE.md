# 🏗️ Media Picker - Modern Architecture

This document describes the new modular architecture implemented for the Media Picker application.

## 📁 New Project Structure

```
Choose-for-me/
├── main.py                                    # Application entry point
├── migrate_to_new_structure.py               # Migration utilities
├── pyproject.toml                            # Modern Python project configuration
├── uv.lock                                   # Dependency lock file
├── .env.example                              # Environment configuration template
├── src/
│   └── media_picker/                         # Main application package
│       ├── __init__.py
│       ├── api/                              # API layer (FastAPI routes)
│       │   ├── __init__.py
│       │   ├── dependencies.py               # Dependency injection
│       │   ├── exception_handlers.py         # Error handling
│       │   └── media.py                      # Media item endpoints
│       ├── core/                             # Core utilities and configuration
│       │   ├── __init__.py
│       │   ├── config.py                     # Pydantic V2 settings
│       │   ├── exceptions.py                 # Custom exceptions
│       │   └── logging.py                    # Logging configuration
│       ├── db/                               # Database layer
│       │   ├── __init__.py
│       │   ├── database.py                   # Database connection & setup
│       │   ├── models.py                     # SQLAlchemy models
│       │   └── repository.py                 # Repository pattern
│       ├── schemas/                          # Pydantic V2 schemas
│       │   ├── __init__.py
│       │   ├── base.py                       # Base schema classes
│       │   └── media.py                      # Media item schemas
│       └── services/                         # Business logic layer
│           ├── __init__.py
│           └── media_service.py               # Media item service
├── static/                                   # Frontend assets
│   ├── app.js
│   └── styles.css
├── templates/                                # HTML templates
│   └── index.html
└── tests/                                    # Test suite
    └── test_api.py
```

## 🎯 Architecture Principles

### 1. **Layered Architecture**
- **API Layer**: FastAPI routes and HTTP handling
- **Service Layer**: Business logic and orchestration
- **Repository Layer**: Data access abstraction
- **Database Layer**: SQLAlchemy models and connections

### 2. **Dependency Injection**
- Clean separation of concerns
- Easy testing and mocking
- Explicit dependencies

### 3. **Modern Python Practices**
- **Pydantic V2**: Data validation and serialization
- **SQLAlchemy 2.0**: Modern ORM with type hints
- **UV Package Manager**: Fast, reliable dependency management
- **Ruff**: Comprehensive linting and formatting

### 4. **Configuration Management**
- Environment-based configuration
- Pydantic settings with validation
- Type-safe configuration access

## 🔧 Key Improvements

### **Pydantic V2 Integration**

```python
# Modern schema with advanced validation
class MediaItemCreate(MediaItemBase):
    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True,
        extra="forbid",
    )

    @field_validator("title")
    @classmethod
    def validate_title(cls, value: str) -> str:
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("Title cannot be empty")
        return cleaned
```

### **Repository Pattern**

```python
# Clean data access with proper error handling
class MediaItemRepository(BaseRepository[MediaItem]):
    def get_filtered(self, filter_params: MediaItemFilter) -> List[MediaItem]:
        try:
            query = self.db.query(MediaItem).filter(MediaItem.is_deleted == False)
            # Apply filters...
            return query.all()
        except Exception as e:
            logger.error(f"Error filtering items: {e}")
            raise DatabaseError(f"Failed to filter items: {e}") from e
```

### **Service Layer Abstraction**

```python
# Business logic with proper exception handling
class MediaItemService:
    def create_item(self, item_data: MediaItemCreate) -> MediaItemResponse:
        try:
            self._validate_create_data(item_data)
            data = item_data.model_dump(by_alias=True)
            item = self.repository.create(data)
            return self._item_to_response(item)
        except ValidationError:
            raise
        except Exception as e:
            raise ServiceError(f"Failed to create item: {e}") from e
```

### **Modern Configuration**

```python
# Type-safe, environment-aware configuration
class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    database_url: str = Field(default="sqlite:///./media_picker.db")
    debug: bool = Field(default=False)
    allowed_origins: list[str] = Field(default=["http://localhost:9000"])
```

## 🚀 Getting Started

### 1. **Environment Setup**

```bash
# Install UV (if not already installed)
pip install uv

# Install dependencies
python -m uv sync

# Copy environment configuration
cp .env.example .env
```

### 2. **Database Initialization**

```bash
# Initialize database with new structure
python -m uv run python migrate_to_new_structure.py init
```

### 3. **Migration from Old Structure**

```bash
# Migrate from existing JSON data (if you have it)
python -m uv run python migrate_to_new_structure.py migrate backup.json

# Validate the migration
python -m uv run python migrate_to_new_structure.py validate
```

### 4. **Run the Application**

```bash
# Start the server
python -m uv run python main.py

# Or use the script entry point
python -m uv run media-picker
```

### 5. **Development Workflow**

```bash
# Run linting
python -m uv run ruff check .

# Format code
python -m uv run ruff format .

# Run tests
python -m uv run pytest

# Run with coverage
python -m uv run pytest --cov=src --cov-report=html
```

## 🔍 API Documentation

The API now includes comprehensive documentation and examples:

- **Interactive Docs**: http://127.0.0.1:9000/docs
- **ReDoc**: http://127.0.0.1:9000/redoc
- **Health Check**: http://127.0.0.1:9000/health
- **Statistics**: http://127.0.0.1:9000/api/statistics

### **Enhanced Endpoints**

```python
# Advanced filtering with pagination
GET /api/items?type=game&tags=rpg,fantasy&limit=10&offset=0

# Statistics endpoint
GET /api/statistics
{
  "total": 150,
  "active": 120,
  "done": 25,
  "archived": 5,
  "games": 80,
  "movies": 70
}

# Enhanced spin with detailed response
GET /api/spin?type=game&tags=rpg
{
  "winner": {...},
  "pool": [...],
  "total_pool_size": 15
}
```

## 🧪 Testing

The new architecture supports comprehensive testing:

```python
# Test with dependency injection
def test_create_item(mock_service):
    # Service layer testing
    pass

def test_api_endpoint(client, mock_db):
    # API layer testing
    pass
```

## 🔧 Configuration Options

### **Environment Variables**

```bash
# Application
APP_NAME="Media Picker"
VERSION="1.0.0"
DEBUG=false
LOG_LEVEL="INFO"

# Database
DATABASE_URL="sqlite:///./media_picker.db"

# Security
SECRET_KEY="your-secret-key-here"
ALLOWED_ORIGINS="http://localhost:9000,http://127.0.0.1:9000"

# Server
HOST="127.0.0.1"
PORT=9000

# Media Configuration
MAX_TAGS_PER_ITEM=10
MAX_TAG_LENGTH=30
MAX_TITLE_LENGTH=200
```

## 📊 Performance Improvements

### **Database Optimizations**
- WAL mode for better SQLite concurrency
- Connection pooling and optimization
- Proper indexes and foreign key constraints
- Soft delete pattern for data integrity

### **Application Optimizations**
- Lazy loading of dependencies
- Efficient query patterns with repository
- Proper error handling and logging
- Memory-efficient data processing

## 🔮 Future Enhancements

The new architecture enables:

1. **Easy Testing**: Dependency injection makes unit testing simple
2. **Scalability**: Service layer can be easily extracted to microservices
3. **API Versioning**: Clean separation allows for API evolution
4. **Database Migrations**: Alembic integration for schema changes
5. **Authentication**: Easy to add JWT/OAuth with the current structure
6. **Caching**: Redis integration through repository pattern
7. **Background Tasks**: Celery integration through service layer

## 🔄 Migration Guide

### **From Old Structure**

1. **Backup your data**: `python migration.py export backup.json`
2. **Install new dependencies**: `python -m uv sync`
3. **Initialize new database**: `python migrate_to_new_structure.py init`
4. **Migrate data**: `python migrate_to_new_structure.py migrate backup.json`
5. **Validate**: `python migrate_to_new_structure.py validate`
6. **Test**: `python -m uv run python main.py`

### **Breaking Changes**

- **Import paths**: All imports now use `src.media_picker.*`
- **Configuration**: Now uses Pydantic settings instead of direct variables
- **Database**: Enhanced schema with audit fields and soft delete
- **API responses**: More consistent error handling and response format

### **Compatibility**

- **API endpoints**: Same URLs and request/response format
- **Database data**: Fully compatible through migration script
- **Frontend**: No changes required to existing JavaScript

## 💡 Best Practices

### **Development**
1. Always use type hints
2. Follow the repository pattern for data access
3. Use services for business logic
4. Handle errors at appropriate layers
5. Use dependency injection for testability

### **Configuration**
1. Use environment variables for secrets
2. Validate configuration with Pydantic
3. Provide sensible defaults
4. Document all configuration options

### **Testing**
1. Test each layer independently
2. Use dependency injection for mocking
3. Test both success and error cases
4. Maintain high test coverage

This new architecture provides a solid foundation for scaling the Media Picker application while maintaining clean, testable, and maintainable code! 🚀
