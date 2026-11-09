"""Router: sức khoẻ hệ thống và metadata."""

from __future__ import annotations

from fastapi import APIRouter, Depends

from ..config import get_settings
from ..data.core import CatalogCore
from ..deps import core_from_request
from ..models import HealthInfo, ReleaseInfo
from ..schema import DATABASE_NAME, GRAPH_NAME

router = APIRouter(prefix="/api/v1/meta", tags=["metadata"])


@router.get("/release", response_model=ReleaseInfo, summary="Thông tin database đang dùng")
def release_info(core: CatalogCore = Depends(core_from_request)) -> dict:
    settings = get_settings()
    counts = core.counts()
    return {
        "database": DATABASE_NAME,
        "graph": GRAPH_NAME,
        "dataMode": core.storage.mode,
        "arangoServerVersion": core.diagnostics.get("arango", {}).get("server_version"),
        "counts": counts,
        "totalRecords": sum(counts.values()),
    }


@router.get("/health", response_model=HealthInfo, summary="Kiểm tra backend và kết nối ArangoDB")
def health(core: CatalogCore = Depends(core_from_request)) -> dict:
    return core.health()
