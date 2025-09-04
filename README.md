# 🎯 Media Picker

A modern web app for organizing your **games**, **movies**, and **TV shows** into lists—and letting fate decide what you should play or watch next with a spinning wheel.  

Built with **FastAPI** + **SQLite** + **Tailwind CSS**.

---

## ✨ Features

- Add **games** and **movies/TV** with:
  - Title  
  - Platform (PC, PlayStation, Xbox, Nintendo, Netflix, Amazon, etc.)  
  - Cover image URL  
  - Custom tags (genres, moods, categories)  
- Organize into:
  - Game list  
  - Movie/TV list  
  - Combined list  
- **Spin wheel** animation to randomly pick from your filtered list  
- **Filter by tags** (e.g. "RPG, Action")  
- Mark items as:
  - ✅ Done  
  - 📦 Archived  
- Edit and delete items  
- Dark 🌙 / Light ☀️ theme toggle  
- **Persistent storage** with SQLite database
- **Input validation** and error handling
- **API documentation** with FastAPI automatic docs

---

## 📦 Requirements

- Python 3.10+  
- Dependencies listed in `requirements.txt`

---

## 🚀 Getting Started

### Option 1: Using pip

Clone the repository and install dependencies:

```bash
git clone <repository-url>
cd Choose-for-me

# Create virtual environment
python -m venv .venv
source .venv/bin/activate   # macOS/Linux
# OR .venv\Scripts\activate on Windows

# Install dependencies
pip install -r requirements.txt
```

### Option 2: Using pip-tools (recommended for development)

```bash
# Install pip-tools
pip install pip-tools

# Install dependencies from pyproject.toml
pip-sync requirements.txt

# For development dependencies
pip install -e ".[dev]"
```

### Initialize the database:

```bash
python migration.py init
```

### Run the server:

```bash
# Using the original app
python app.py

# Using the improved app (recommended)
python app_improved.py
```

### Visit:

http://127.0.0.1:9000

### API Documentation:

Visit http://127.0.0.1:9000/docs for interactive API documentation.

---

## 📝 Usage

1. Click **Add** to create a new item
2. Choose **Game** or **Movie/TV**, fill in details, add tags
3. Use the filter bar to filter by tags or type
4. Hit **Spin** to let the wheel choose!
5. Manage your list: Edit, Mark Done, Archive, or Delete items

---

## 🧪 Testing

Run the test suite:

```bash
pytest tests/
```

Run with coverage:

```bash
pytest tests/ --cov=. --cov-report=html
```

---

## 📁 Project Structure

```
Choose-for-me/
├── app.py                 # Original application
├── app_improved.py        # Improved application with database
├── database.py           # Database models and configuration
├── models.py            # Pydantic models for validation
├── migration.py         # Database migration utilities
├── requirements.txt     # Python dependencies
├── pyproject.toml      # Project configuration
├── static/
│   ├── app.js          # Frontend JavaScript (improved with error handling)
│   └── styles.css      # CSS styles
├── templates/
│   └── index.html      # HTML template
└── tests/
    └── test_api.py     # API tests
```

---

## 🔧 Configuration

Copy the example environment file and configure as needed:

```bash
cp .env.example .env
```

Edit `.env` to configure:
- Database URL
- Debug settings
- Allowed origins for CORS
- Server host and port

---

## 📊 API Endpoints

### Items
- `GET /api/items` - Get filtered list of items
- `POST /api/items` - Add a new item
- `PATCH /api/items/{id}` - Update an item
- `DELETE /api/items?id={id}` - Delete an item

### Wheel
- `GET /api/spin` - Get a random item from filtered pool

### Utility
- `GET /health` - Health check
- `GET /docs` - API documentation

---

## 🚀 Improvements Made

### ✅ **Completed Improvements**

1. **Persistent Storage**: SQLite database instead of in-memory storage
2. **Input Validation**: Pydantic models with comprehensive validation
3. **Error Handling**: Proper exception handling and user feedback
4. **Code Organization**: Separated concerns into multiple modules
5. **Security**: More restrictive CORS, input sanitization
6. **Testing**: Comprehensive test suite
7. **Documentation**: API docs and improved README
8. **Development Setup**: pyproject.toml, requirements.txt, .env configuration
9. **Frontend Improvements**: Error handling, user feedback, confirmation dialogs
10. **Migration Tools**: Utilities to migrate from old format

### 🎯 **Future Enhancements**

1. **Cover Art Integration**: Auto-fetch from TMDB (movies) or IGDB (games)
2. **User Authentication**: Multi-user support with accounts
3. **Advanced Filtering**: Date ranges, ratings, custom fields
4. **Export/Import**: Backup and restore functionality
5. **Mobile App**: React Native or Flutter companion app
6. **Recommendations**: AI-powered suggestions based on preferences
7. **Social Features**: Share lists, collaborative filtering

---

## 🛠️ Development

### Code Quality

```bash
# Format code
black .

# Sort imports
isort .

# Lint code
flake8 .

# Type checking
mypy .
```

### Database Operations

```bash
# Initialize database
python migration.py init

# Migrate from JSON backup
python migration.py migrate backup.json

# Export to JSON
python migration.py export backup.json
```

---

## ⚠️ Migration from Original Version

If you're upgrading from the original version:

1. **Backup your data** (if you have any running instance)
2. Install the new requirements: `pip install -r requirements.txt`
3. Initialize the database: `python migration.py init`
4. Use the improved app: `python app_improved.py`

The original `app.py` is preserved for compatibility, but `app_improved.py` is recommended for new installations.

---

## 📄 License

MIT License - feel free to use this project for personal or commercial purposes.

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Run the test suite
6. Submit a pull request

---

## 🐛 Bug Reports & Feature Requests

Please use the GitHub issues page to report bugs or request new features.
