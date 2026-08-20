"""C.A.W.L. FastAPI server (Layer 3) — the speak_server.py port.

Endpoints mirror the original. Token-gated endpoints require the
``X-CAWL-Token`` header to match ``.cawl-token``.
"""

from __future__ import annotations

from pathlib import Path
from typing import Annotated

from fastapi import FastAPI, Header, HTTPException, Query
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from . import config, identity, priests, scheduler, settings, vault, wiki
from . import brain, images, voice
from .tools import SandboxFS, Terminal, fetch_url, search_ddg

app = FastAPI(title="C.A.W.L. — Archmagos Dominus", version="0.1.0")

STATIC_DIR = Path(__file__).parent / "static"


def _say_response(text: str) -> dict:
    out = voice.synthesize(text)
    out["url"] = f"/audio/{Path(out['audio']).name}"
    return out
_fs = SandboxFS()
_term = Terminal()


# ---------------------------------------------------------------------------
# Auth
# ---------------------------------------------------------------------------

def _require_token(x_cawl_token: str | None) -> None:
    if x_cawl_token != config.CAWL_TOKEN:
        raise HTTPException(status_code=401, detail="X-CAWL-Token missing or invalid")


# ---------------------------------------------------------------------------
# Schemas
# ---------------------------------------------------------------------------

class ChatIn(BaseModel):
    message: str
    system: str | None = None
    image: str | None = None
    deepthink: bool = False
    webfetch: bool = False
    verify: bool = False


class WriteIn(BaseModel):
    path: str
    content: str


class ExecIn(BaseModel):
    command: str


class LogIn(BaseModel):
    entry: str


class ScheduleIn(BaseModel):
    name: str
    command: str
    kind: str = "once"
    at: str = ""


class ImgIn(BaseModel):
    kind: str = "banner"
    text: str = "C.A.W.L. — Archmagos Dominus"
    width: int = 1024
    height: int = 384
    color: str = "mech"
    tag: str = ""


class WikiIn(BaseModel):
    lesson: str


class ResearchIn(BaseModel):
    finding: str
    confidence: str = "MEDIUM"
    source: str = ""


class OrChatIn(BaseModel):
    messages: list[dict]
    model: str | None = None


class SettingsIn(BaseModel):
    patch: dict


# ---------------------------------------------------------------------------
# Open endpoints
# ---------------------------------------------------------------------------

@app.get("/self")
def get_self():
    return identity.self_payload()


@app.get("/", include_in_schema=False)
def index():
    return FileResponse(STATIC_DIR / "index.html")


@app.get("/say")
def get_say(text: str = Query(min_length=1, max_length=4000)):
    return _say_response(text)


@app.post("/say")
def post_say(body: LogIn):
    return _say_response(body.entry)


@app.get("/settings")
def get_settings():
    return settings.payload()


@app.post("/settings")
def post_settings(body: SettingsIn):
    return settings.update(body.patch or {})


@app.get("/avatar")
def get_avatar():
    path = Path(config.AVATAR_IMAGE).resolve() if config.AVATAR_IMAGE else None
    if not path or not path.exists() or not path.suffix.lower() in {".png", ".jpg", ".jpeg", ".webp"}:
        fallback = Path(__file__).resolve().parent / "static" / "cawl_avatar.png"
        if fallback.exists():
            return FileResponse(fallback)
        raise HTTPException(status_code=404, detail="avatar image not set or missing")
    return FileResponse(path)


@app.get("/read")
def get_read(path: str = Query(default="vault/Index.md")):
    try:
        return {"path": path, "content": _fs.read(path)}
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.get("/fs")
def get_fs(path: str = ".", depth: int = 2):
    try:
        return {"entries": _fs.list(path, depth)}
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.get("/search")
def get_search(q: str = Query(min_length=1), n: int = 5):
    try:
        return {"query": q, "results": search_ddg(q, n)}
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=502, detail=f"search failed: {exc}") from exc


@app.get("/fetch")
def get_fetch(url: str = Query(min_length=4)):
    try:
        return fetch_url(url)
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=502, detail=f"fetch failed: {exc}") from exc


@app.post("/chat")
def post_chat(body: ChatIn):
    extra = ""
    if body.deepthink:
        extra += "\n\n## DeepThink Mode (ACTIVE)\nShow your step-by-step reasoning inside <thinking>...</thinking> tags before giving the final answer. Break complex problems into smaller steps. Label each step."
    if body.webfetch:
        extra += "\n\n## WebFetch Mode (ACTIVE)\nAlways verify information from the web before answering. Use webfetch to look up current data. Do NOT answer from memory alone — fetch first, then answer."
    if body.verify:
        extra += "\n\n## Verify Mode (ACTIVE)\nRe-check every claim before outputting it. Label each fact with [HIGH], [MEDIUM], or [LOW] confidence. If unsure, say so explicitly."
    system = body.system or identity.system_prompt(extra)
    image_paths = [body.image] if body.image else None
    try:
        text, results = brain.run_with_tools(system, body.message, image_paths)
    except brain.BrainError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    except Exception as exc:  # noqa: BLE001 — keep the comms line alive with a real reason
        print(f"[cawl] /chat failed: {type(exc).__name__}: {exc}", flush=True)
        raise HTTPException(status_code=502, detail=f"{type(exc).__name__}: {exc}") from exc
    return {"reply": text, "tools": [r.__dict__ for r in results]}


@app.post("/or/chat")
def post_or_chat(body: OrChatIn):
    try:
        model = body.model or brain.resolve_model("brain")
        return {"reply": brain.chat_openrouter(body.messages, model)}
    except brain.BrainError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.post("/oc/chat")
def post_oc_chat(body: ChatIn):
    system = body.system or identity.system_prompt()
    try:
        return {"reply": brain.chat_opencode(body.message, system)}
    except brain.BrainError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.post("/dsh/chat")
def post_dsh_chat(body: ChatIn):
    system = body.system or priests.DSH_SYSTEM
    messages = [{"role": "system", "content": system}, {"role": "user", "content": body.message}]
    try:
        return {"reply": brain.chat_dsh(messages)}
    except brain.BrainError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


# ---------------------------------------------------------------------------
# Token-gated endpoints
# ---------------------------------------------------------------------------

@app.get("/token")
def get_token(x_cawl_token: Annotated[str | None, Header()] = None):
    _require_token(x_cawl_token)
    return {"token": config.CAWL_TOKEN}


@app.post("/write")
def post_write(body: WriteIn, x_cawl_token: Annotated[str | None, Header()] = None):
    _require_token(x_cawl_token)
    try:
        return _fs.write(body.path, body.content)
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.post("/exec")
def post_exec(body: ExecIn, x_cawl_token: Annotated[str | None, Header()] = None):
    _require_token(x_cawl_token)
    return _term.run(body.command)


@app.post("/log")
def post_log(body: LogIn, x_cawl_token: Annotated[str | None, Header()] = None):
    _require_token(x_cawl_token)
    path = vault.journal(body.entry)
    return {"ok": True, "journal": path.name}


@app.post("/research/save")
def post_research(body: ResearchIn, x_cawl_token: Annotated[str | None, Header()] = None):
    _require_token(x_cawl_token)
    path = vault.research_save(body.finding, body.confidence, body.source)
    return {"ok": True, "file": path.name}


@app.get("/schedule")
def get_schedule(x_cawl_token: Annotated[str | None, Header()] = None):
    _require_token(x_cawl_token)
    return {"tasks": scheduler.list_tasks()}


@app.post("/schedule")
def post_schedule(body: ScheduleIn, x_cawl_token: Annotated[str | None, Header()] = None):
    _require_token(x_cawl_token)
    try:
        return scheduler.add(body.name, body.command, body.kind, body.at)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.delete("/schedule/{task_id}")
def delete_schedule(task_id: str, x_cawl_token: Annotated[str | None, Header()] = None):
    _require_token(x_cawl_token)
    if not scheduler.delete(task_id):
        raise HTTPException(status_code=404, detail="task not found")
    return {"ok": True}


@app.post("/schedule/{task_id}/run")
def run_schedule(task_id: str, x_cawl_token: Annotated[str | None, Header()] = None):
    _require_token(x_cawl_token)
    return scheduler.run_now(task_id)


@app.get("/img/{kind}")
def get_img(kind: str, text: str = "C.A.W.L.", w: int = 512, h: int = 512,
            color: str = "mech"):
    try:
        return images.forge(kind, text=text, width=w, height=h, color=color)
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.post("/img")
def post_img(body: ImgIn, x_cawl_token: Annotated[str | None, Header()] = None):
    _require_token(x_cawl_token)
    try:
        return images.forge(body.kind, text=body.text, width=body.width,
                            height=body.height, color=body.color, tag=body.tag)
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.get("/wiki/read")
def get_wiki(x_cawl_token: Annotated[str | None, Header()] = None):
    _require_token(x_cawl_token)
    return {"content": wiki.read(), "entries": wiki.count()}


@app.post("/wiki/write")
def post_wiki(body: WikiIn, x_cawl_token: Annotated[str | None, Header()] = None):
    _require_token(x_cawl_token)
    return wiki.append(body.lesson)


@app.post("/notion/search")
def post_notion_search(body: ChatIn, x_cawl_token: Annotated[str | None, Header()] = None):
    _require_token(x_cawl_token)
    if not config.NOTION_API_KEY:
        raise HTTPException(status_code=501, detail="NOTION_API_KEY not set")
    return {"detail": "Notion bridge configured; search requires the API key at runtime"}


@app.post("/notion/create")
@app.post("/notion/update")
def post_notion_write(body: ChatIn, x_cawl_token: Annotated[str | None, Header()] = None):
    _require_token(x_cawl_token)
    if not config.NOTION_API_KEY:
        raise HTTPException(status_code=501, detail="NOTION_API_KEY not set")
    return {"detail": "Notion bridge configured; writes require the API key at runtime"}


@app.get("/audio/{name}")
def get_audio(name: str):
    path = (config.AUDIO_DIR / name).resolve()
    if not str(path).startswith(str(config.AUDIO_DIR.resolve())) or not path.exists():
        raise HTTPException(status_code=404, detail="not found")
    return FileResponse(path)


# ---------------------------------------------------------------------------
# WorldWideView integration
# ---------------------------------------------------------------------------

class WwvSearchIn(BaseModel):
    query: str
    plugin_id: str = ""
    limit: int = 20


class WwvInvestigateIn(BaseModel):
    place: str
    entity_type: str = ""
    radius_km: int = 100


class WwvGeocodeIn(BaseModel):
    query: str


class WwvFlyToIn(BaseModel):
    lat: float
    lon: float
    altitude: float = 500000


class WwvLayerIn(BaseModel):
    plugin_id: str
    visible: bool | None = None


class WwvRegionIn(BaseModel):
    north: float
    south: float
    east: float
    west: float
    plugin_id: str = ""
    limit: int = 100


@app.get("/wwv/status")
def get_wwv_status():
    from . import worldwideview
    return worldwideview.status()


@app.get("/wwv/health")
def get_wwv_health():
    from . import worldwideview
    return worldwideview.health_check()


@app.get("/wwv/plugins")
def get_wwv_plugins():
    from . import worldwideview
    return worldwideview.list_plugins()


@app.post("/wwv/search")
def post_wwv_search(body: WwvSearchIn):
    from . import worldwideview
    return worldwideview.search_entities(body.query, body.plugin_id, body.limit)


@app.post("/wwv/investigate")
def post_wwv_investigate(body: WwvInvestigateIn):
    from . import worldwideview
    return worldwideview.investigate_area(body.place, body.entity_type, body.radius_km)


@app.post("/wwv/geocode")
def post_wwv_geocode(body: WwvGeocodeIn):
    from . import worldwideview
    return worldwideview.geocode_location(body.query)


@app.post("/wwv/fly-to")
def post_wwv_fly_to(body: WwvFlyToIn):
    from . import worldwideview
    return worldwideview.fly_to(body.lat, body.lon, body.altitude)


@app.post("/wwv/layer")
def post_wwv_layer(body: WwvLayerIn):
    from . import worldwideview
    return worldwideview.toggle_layer(body.plugin_id, body.visible)


@app.post("/wwv/region")
def post_wwv_region(body: WwvRegionIn):
    from . import worldwideview
    return worldwideview.get_entities_in_region(body.north, body.south, body.east, body.west, body.plugin_id, body.limit)


@app.get("/wwv/context")
def get_wwv_context():
    from . import worldwideview
    return worldwideview.get_globe_context()


app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
