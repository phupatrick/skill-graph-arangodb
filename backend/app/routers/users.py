"""Router: người dùng, kỹ năng hiện có, nghề mục tiêu, khóa đã học."""

from __future__ import annotations

from fastapi import APIRouter, Depends, Query

from ..data.core import CatalogCore
from ..deps import core_from_request
from ..mappers import completed_out, has_skill_out, target_out, user_out
from ..models import CompletedOut, HasSkillOut, TargetCareerOut, UserDetail, UserList

router = APIRouter(prefix="/api/v1/users", tags=["users"])


def _course(core: CatalogCore, course_id: str) -> dict | None:
    return core.vertex_by_id(course_id)


@router.get("", response_model=UserList, summary="Danh sách người dùng")
def list_users(
    search: str = Query("", description="Tìm theo họ tên hoặc email"),
    core: CatalogCore = Depends(core_from_request),
) -> dict:
    rows = core.list_users(search)
    return {"items": [user_out(r) for r in rows], "total": len(rows)}


@router.get("/{user_key}", response_model=UserDetail, summary="Chi tiết người dùng + quan hệ")
def get_user(user_key: str, core: CatalogCore = Depends(core_from_request)) -> dict:
    user = core.get_user(user_key)
    user_id = f"users/{user_key}"
    return {
        "user": user_out(user),
        "skills": [has_skill_out(e) for e in core.user_skills(user_id)],
        "targets": [target_out(e) for e in core.user_targets(user_id)],
        "completed": [
            completed_out(e, _course(core, str(e["_to"])))
            for e in core.user_completed(user_id)
        ],
    }


@router.get("/{user_key}/skills", response_model=list[HasSkillOut], summary="Kỹ năng hiện có")
def user_skills(user_key: str, core: CatalogCore = Depends(core_from_request)) -> list:
    core.get_user(user_key)
    return [has_skill_out(e) for e in core.user_skills(f"users/{user_key}")]


@router.get("/{user_key}/targets", response_model=list[TargetCareerOut], summary="Nghề mục tiêu")
def user_targets(user_key: str, core: CatalogCore = Depends(core_from_request)) -> list:
    core.get_user(user_key)
    return [target_out(e) for e in core.user_targets(f"users/{user_key}")]


@router.get("/{user_key}/completed", response_model=list[CompletedOut], summary="Khóa học đã hoàn thành")
def user_completed(user_key: str, core: CatalogCore = Depends(core_from_request)) -> list:
    core.get_user(user_key)
    return [
        completed_out(e, _course(core, str(e["_to"])))
        for e in core.user_completed(f"users/{user_key}")
    ]
