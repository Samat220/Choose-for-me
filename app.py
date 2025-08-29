from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import random, time, uuid

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def uid():
    return uuid.uuid4().hex

PLATFORMS = {
    "game": ["PC", "PlayStation", "Xbox", "Nintendo"],
    "movie": ["Netflix", "Amazon", "Apple TV", "Crunchyroll", "Ororo.tv"],
}

items = []

@app.get("/api/items")
async def get_items(
    type: str | None = None,
    tags: str | None = None,
    includeArchived: bool = False,
    status: str | None = None,
):
    tag_set = set([t.strip().lower() for t in (tags.split(",") if tags else []) if t.strip()])

    def matches(it):
        if type and it["type"] != type:
            return False
        if tag_set and not tag_set.issubset({t.lower() for t in it.get("tags", [])}):
            return False
        if not includeArchived and it.get("status", "active") == "archived":
            return False
        if status and it.get("status", "active") != status:
            return False
        return True

    return JSONResponse([it for it in items if matches(it)])

@app.post("/api/items")
async def add_item(request: Request):
    data = await request.json()
    t = (data.get("type") or "").strip().lower()
    title = (data.get("title") or "").strip()
    platform = (data.get("platform") or "").strip()
    cover = (data.get("coverUrl") or "").strip() or None
    tags = data.get("tags") or []
    if t not in ("game", "movie"):
        return JSONResponse({"error": "type must be 'game' or 'movie'"}, status_code=400)
    if not title:
        return JSONResponse({"error": "title required"}, status_code=400)
    if platform and platform not in PLATFORMS[t]:
        return JSONResponse({"error": f"invalid platform for {t}"}, status_code=400)
    new_item = {
        "id": uid(),
        "type": t,
        "title": title,
        "platform": platform or None,
        "coverUrl": cover,
        "tags": [str(x).strip() for x in tags if str(x).strip()],
        "status": "active",
        "addedAt": int(time.time()),
    }
    items.insert(0, new_item)
    return JSONResponse(new_item)

@app.delete("/api/items")
async def delete_item(id: str):
    global items
    items = [it for it in items if it["id"] != id]
    return JSONResponse({"status": "deleted"})

@app.patch("/api/items/{item_id}")
async def update_item(item_id: str, request: Request):
    data = await request.json()
    for it in items:
        if it["id"] == item_id:
            for key in ("title", "platform", "coverUrl", "tags", "type", "status"):
                if key in data:
                    if key == "type" and data[key] not in ("game", "movie"):
                        return JSONResponse({"error": "invalid type"}, status_code=400)
                    if key == "platform":
                        typ = data.get("type", it.get("type"))
                        if typ in PLATFORMS and data[key] and data[key] not in PLATFORMS[typ]:
                            return JSONResponse({"error": "invalid platform for type"}, status_code=400)
                    it[key] = data[key]
            return JSONResponse(it)
    return JSONResponse({"error": "not found"}, status_code=404)

@app.get("/api/spin")
async def spin(type: str | None = None, tags: str | None = None):
    tag_set = set([t.strip().lower() for t in (tags.split(",") if tags else []) if t.strip()])

    def matches(it):
        if type and it["type"] != type:
            return False
        if tag_set and not tag_set.issubset({t.lower() for t in it.get("tags", [])}):
            return False
        if it.get("status", "active") != "active":
            return False
        return True

    pool = [it for it in items if matches(it)]
    if not pool:
        return JSONResponse({"winner": None, "pool": []})
    winner = random.choice(pool)
    return JSONResponse({"winner": winner, "pool": pool})

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=9000, reload=True)
