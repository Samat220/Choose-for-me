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

## 🚀 Getting Started

### Installation

```bash
git clone <repository-url>
cd Choose-for-me

# Install uv if you haven't already
pip install uv

# Install dependencies and create virtual environment
uv sync

# Activate the virtual environment
# On Windows
.venv\Scripts\activate
# On macOS/Linux  
source .venv/bin/activate
```

### Initialize and Run

```bash
# Initialize the database
python scripts/migrate_to_new_structure.py init

# Run the server
python main.py
```

### Access the Application

- **Web Interface**: http://127.0.0.1:9000
- **API Documentation**: http://127.0.0.1:9000/docs

---

## 📁 Project Structure

```
Choose-for-me/
├── main.py                    # Application entry point
├── pyproject.toml            # Project configuration
├── data/                     # Database files
├── src/media_picker/         # Main application package
│   ├── api/                  # API endpoints
│   ├── core/                 # Configuration & utilities
│   ├── db/                   # Database models
│   ├── schemas/              # Data validation
│   └── services/             # Business logic
├── static/                   # Frontend assets
├── templates/               # HTML templates
├── scripts/                 # Utility scripts
└── tests/                   # Test suite
```

---

## 📝 Usage

1. Click **Add** to create a new item
2. Choose **Game** or **Movie/TV**, fill in details, add tags
3. Use the filter bar to filter by tags or type
4. Hit **Spin** to let the wheel choose!
5. Manage your list: Edit, Mark Done, Archive, or Delete items

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

---

## 🧪 Testing

```bash
# Run tests
uv run pytest tests/

# Run with coverage
uv run pytest tests/ --cov=src --cov-report=html
```

---

## 🔧 Development

### Code Quality

```bash
# Run linting and formatting checks
python scripts/run_checks.py

# Or run individually
uv run ruff check .
uv run ruff format .
uv run mypy src/
```

### Database Operations

```bash
# Initialize database
python scripts/migrate_to_new_structure.py init

# Validate database
python scripts/migrate_to_new_structure.py validate

# Export data
python scripts/migrate_to_new_structure.py export backup.json

# Import data
python scripts/migrate_to_new_structure.py migrate backup.json
```

---

## 🔧 Configuration

Copy `.env.example` to `.env` and configure:
- Database URL
- Debug settings
- CORS origins
- Server host and port

---

## 📄 License

MIT License

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests and quality checks
5. Submit a pull request
