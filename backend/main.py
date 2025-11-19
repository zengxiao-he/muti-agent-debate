from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from .debate import run_debate
from .models import DebateRequest, DebateResponse

from .config import get_settings

BASE_DIR = Path(__file__).resolve().parent.parent
FRONTEND_DIR = BASE_DIR / "frontend"

app = FastAPI(title="Multi-Agent Debate System", version="0.1.0")

# Simple CORS config for local front-end development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health():
    settings = get_settings()
    return {
        "status": "ok",
        "model": settings.openai_model,
        "openai_key_configured": bool(settings.openai_api_key),
    }


# Serve static front-end
if FRONTEND_DIR.exists():
    # Static assets (CSS, JS, etc.)
    app.mount(
        "/static",
        StaticFiles(directory=FRONTEND_DIR, html=False),
        name="static",
    )


@app.get("/")
async def index():
    """Serve the main front-end HTML file."""
    index_file = FRONTEND_DIR / "index.html"
    return FileResponse(index_file)


@app.post("/api/debate", response_model=DebateResponse)
async def debate(req: DebateRequest) -> DebateResponse:
    """Run a full multi-agent debate for the given topic."""
    result = await run_debate(
        topic=req.topic,
        config=req.config,
        language=req.language,
    )
    return DebateResponse(result=result)


