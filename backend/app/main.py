"""FastAPI application entrypoint.

Chạy:
    uvicorn app.main:app --reload --port 8000
Mở tài liệu tự sinh:
    http://127.0.0.1:8000/docs
"""

from __future__ import annotations

import sys
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from .config import get_settings
from .deps import create_core
from .errors import register_exception_handlers
from .routers import analysis, careers, compat, courses, meta, skills, users

# Console Windows mặc định cp1258 -> in tiếng Việt bị lỗi khi log.
for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError):
        pass


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Nạp dữ liệu một lần khi server khởi động."""
    settings = get_settings()
    core, diagnostics = create_core(settings)
    app.state.core = core
    app.state.settings = settings
    mode = core.storage.mode
    total = sum(core.counts().values())
    print(f"[skillgraph] data_mode={mode} records={total}")
    if mode == "jsonl" and diagnostics.get("arango", {}).get("error"):
        print(f"[skillgraph] ArangoDB không dùng được: {diagnostics['arango']['error']}")
        print("[skillgraph] Đang chạy bằng JSONL. Đặt ARANGO_PASSWORD để dùng ArangoDB.")
    yield
    core.storage.close()


app = FastAPI(
    title="Skill Graph API",
    description=(
        "Backend cho đồ án **Hệ thống Skill Graph và đề xuất lộ trình học cá nhân hóa** "
        "(ArangoDB). Cung cấp Skill Gap, prerequisite nhiều tầng, career match, "
        "learning path và dữ liệu cho trang Skill Graph."
    ),
    version="1.0.0",
    lifespan=lifespan,
)

settings = get_settings()
app.add_middleware(
    CORSMiddleware,
    allow_origins=list(settings.cors_origins),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

register_exception_handlers(app)

app.include_router(meta.router)
app.include_router(users.router)
app.include_router(skills.router)
app.include_router(careers.router)
app.include_router(courses.router)
app.include_router(courses.providers_router)
app.include_router(analysis.analysis_router)
app.include_router(analysis.graph_router)

# Router tương thích cho frontend React trong gói bàn giao (NoSQL_Do_An-main).
# Nằm dưới tiền tố riêng /compat/api/v1 để KHÔNG đụng các route gốc ở trên:
# cùng đường dẫn /careers nhưng hai hình dạng dữ liệu khác nhau.
app.include_router(compat.router)


@app.get("/", include_in_schema=False)
def root() -> dict:
    return {
        "name": "Skill Graph API",
        "docs": "/docs",
        "demo": "/demo",
        "health": "/api/v1/meta/health",
    }


# ------------------------------------------------------------------
# Giao diện demo (1 file HTML, không cần build)
# ------------------------------------------------------------------
STATIC_DIR = Path(__file__).resolve().parent / "static"


@app.get("/demo", include_in_schema=False)
def demo_page() -> FileResponse:
    return FileResponse(STATIC_DIR / "index.html", media_type="text/html")
