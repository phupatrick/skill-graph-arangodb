"""Router: nghề nghiệp, yêu cầu kỹ năng, mức độ phù hợp."""

from __future__ import annotations

from fastapi import APIRouter, Depends, Query

from ..data.core import CatalogCore
from ..deps import core_from_request
from ..mappers import career_out, requirement_out
from ..models import CareerDetail, CareerList

router = APIRouter(prefix="/api/v1/careers", tags=["careers"])


@router.get("", response_model=CareerList, summary="Danh sách nghề nghiệp")
def list_careers(
    search: str = Query("", description="Tìm theo tên nghề"),
    category: str = Query("", description="Lọc theo lĩnh vực (Data & Analytics...)"),
    core: CatalogCore = Depends(core_from_request),
) -> dict:
    rows = core.list_careers(search, category)
    return {"items": [career_out(r) for r in rows], "total": len(rows)}


@router.get("/{career_key}", response_model=CareerDetail, summary="Chi tiết nghề + yêu cầu kỹ năng")
def get_career(career_key: str, core: CatalogCore = Depends(core_from_request)) -> dict:
    career = core.get_career(career_key)
    career_id = f"careers/{career_key}"
    requirements = []
    for edge in core.career_requirements(career_id):
        skill = core.vertex_by_id(str(edge["_to"]))
        if skill:
            requirements.append(requirement_out(edge, skill))
    return {
        "career": career_out(career),
        "requirements": requirements,
        "followers": len(core.career_followers(career_id)),
    }
