# 🎯 Media Picker

A modern web app for organizing your **games**, **movies**, and **TV shows** into lists—and letting fate decide what you should play or watch next with a spinning wheel.  

Built with **FastAPI** + **Tailwind CSS**.

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
- **Filter by tags** (e.g. “RPG, Action”)  
- Mark items as:
  - ✅ Done  
  - 📦 Archived  
- Edit and delete items  
- Dark 🌙 / Light ☀️ theme toggle  

---

## 📦 Requirements

- Python 3.10+  
- Dependencies (installed below):
  - `fastapi`
  - `uvicorn`
  - `jinja2`

---

## 🚀 Getting Started

Clone or copy the project, then install dependencies:

```bash
python3 -m venv .venv
source .venv/bin/activate   # macOS/Linux
# OR .venv\Scripts\activate on Windows

pip install fastapi uvicorn jinja2
```

### Run the server:

```bash
python app.py
```

### Visit:

http://127.0.0.1:9000


## 📝 Usage

Click Add to create a new item

Choose Game or Movie/TV, fill in details, add tags

Use the filter bar to filter by tags or type

Hit Spin to let the wheel choose!

Manage your list: Edit, Mark Done, Archive, or Delete items

## ⚠️ Notes / TODO

Cover Fetcher: Currently disabled. Future enhancement could integrate APIs like TMDB (movies/TV) or IGDB (games) to automatically fetch cover art.

Persistence: Items are stored in memory only. Restarting the server clears your list. A future version should use SQLite or PostgreSQL.

Accounts: No user system yet. Could add authentication and per-user lists later.

Wheel UI: Future enhancement could display cover thumbnails inside the wheel slices.
