"""Cấu hình backend, đọc từ biến môi trường.

Mặc định chạy được ngay không cần cấu hình gì:
    uvicorn app.main:app --reload
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parents[1]
PROJECT_DIR = BACKEND_DIR.parent
DEFAULT_DATA_DIR = PROJECT_DIR / "data"


def _env_bool(name: str, default: bool) -> bool:
    raw = os.getenv(name)
    if raw is None:
        return default
    return raw.strip().lower() in {"1", "true", "yes", "on"}


def _env_float(name: str, default: float) -> float:
    try:
        return float(os.getenv(name, "").strip() or default)
    except ValueError:
        return default


@dataclass(frozen=True)
class Settings:
    """Toàn bộ tham số vận hành của backend."""

    # auto   = thử ArangoDB trước, lỗi thì rơi về JSONL (an toàn khi demo)
    # jsonl  = luôn đọc file JSONL trong data/ (không cần database)
    # arango = bắt buộc dùng ArangoDB, lỗi thì dừng ngay
    data_mode: str = field(
        default_factory=lambda: os.getenv("SKILLGRAPH_DATA_MODE", "auto").strip().lower()
    )
    data_dir: Path = field(
        default_factory=lambda: Path(os.getenv("SKILLGRAPH_DATA_DIR", str(DEFAULT_DATA_DIR)))
    )

    arango_host: str = field(
        default_factory=lambda: os.getenv("ARANGO_HOST", "http://127.0.0.1:8529").strip()
    )
    arango_user: str = field(default_factory=lambda: os.getenv("ARANGO_USER", "root").strip())
    arango_password: str = field(default_factory=lambda: os.getenv("ARANGO_PASSWORD", ""))
    arango_database: str = field(
        default_factory=lambda: os.getenv("ARANGO_DATABASE", "skill_graph_db").strip()
    )
    arango_timeout: float = field(
        default_factory=lambda: _env_float("ARANGO_TIMEOUT", 3.0)
    )

    cors_origins: tuple[str, ...] = field(
        default_factory=lambda: tuple(
            origin.strip()
            for origin in os.getenv(
                "SKILLGRAPH_CORS_ORIGINS",
                "http://localhost:5173,http://127.0.0.1:5173,http://localhost:4173,http://127.0.0.1:4173",
            ).split(",")
            if origin.strip()
        )
    )

    @property
    def mode(self) -> str:
        return self.data_mode if self.data_mode in {"auto", "jsonl", "arango"} else "auto"


def get_settings() -> Settings:
    """Tạo Settings mỗi lần gọi để test có thể monkeypatch biến môi trường."""
    return Settings()
