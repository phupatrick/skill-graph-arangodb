"""Phụ thuộc dùng chung: một instance CatalogCore cho cả ứng dụng.

FastAPI hiện đại dùng lifespan thay cho @app.on_event (đã deprecated).
"""

from __future__ import annotations

from functools import lru_cache

from fastapi import Request

from .config import Settings, get_settings
from .data.core import CatalogCore
from .data.storage import build_storage


def create_core(settings: Settings | None = None) -> tuple[CatalogCore, dict]:
    """Tạo core + thông tin chẩn đoán. Test gọi trực tiếp hàm này."""
    settings = settings or get_settings()
    storage, diagnostics = build_storage(settings)
    return CatalogCore(storage, diagnostics), diagnostics


@lru_cache(maxsize=1)
def get_core() -> CatalogCore:
    core, _ = create_core()
    return core


def core_from_request(request: Request) -> CatalogCore:
    """Lấy core từ app.state (test có thể ghi đè dễ dàng)."""
    return request.app.state.core


def reset_core_cache() -> None:
    """Dùng trong test khi đổi biến môi trường."""
    get_core.cache_clear()
