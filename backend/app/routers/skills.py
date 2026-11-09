"""Router: kỹ năng, prerequisite nhiều tầng, khóa học dạy kỹ năng."""

from __future__ import annotations

from fastapi import APIRouter, Depends, Query

from ..data.core import CatalogCore
from ..deps import core_from_request
from ..mappers import prerequisite_out, requirement_out, skill_out
from ..models import PrerequisiteTree, SkillDetail, SkillList

router = APIRouter(prefix="/api/v1/skills", tags=["skills"])


@router.get("", response_model=SkillList, summary="Danh sách kỹ năng")
def list_skills(
    search: str = Query("", description="Tìm theo tên kỹ năng"),
    category: str = Query("", description="Lọc theo nhóm (Programming, Data...)"),
    core: CatalogCore = Depends(core_from_request),
) -> dict:
    rows = core.list_skills(search, category)
    return {"items": [skill_out(r) for r in rows], "total": len(rows)}


@router.get("/{skill_key}", response_model=SkillDetail, summary="Chi tiết kỹ năng + quan hệ")
def get_skill(skill_key: str, core: CatalogCore = Depends(core_from_request)) -> dict:
    skill = core.get_skill(skill_key)
    skill_id = f"skills/{skill_key}"

    required_by = []
    for edge in core.storage.edges("requires_skill", to_id=skill_id):
        career = core.vertex_by_id(str(edge["_from"]))
        if career:
            required_by.append(requirement_out(edge, skill))

    prerequisites = []
    for edge in core.skill_prerequisites(skill_id):
        prereq = core.vertex_by_id(str(edge["_to"]))
        if prereq:
            prerequisites.append(prerequisite_out(edge, prereq, depth=1))

    unlocks = []
    for edge in core.skill_unlocks(skill_id):
        target = core.vertex_by_id(str(edge["_from"]))
        if target:
            unlocks.append(prerequisite_out(edge, target, depth=1))

    from ..mappers import teaches_out

    courses = [teaches_out(e) for e in core.skill_courses(skill_id)]

    return {
        "skill": skill_out(skill),
        "requiredBy": required_by,
        "prerequisites": prerequisites,
        "unlocks": unlocks,
        "courses": courses,
        "holders": len(core.skill_holders(skill_id)),
    }


@router.get(
    "/{skill_key}/prerequisites",
    response_model=PrerequisiteTree,
    summary="Duyệt TOÀN BỘ kỹ năng nền (nhiều tầng)",
)
def skill_prerequisites(
    skill_key: str,
    max_depth: int = Query(5, ge=1, le=10, description="Số tầng tối đa khi duyệt"),
    strength: str = Query("", description="Lọc theo độ mạnh: required / recommended"),
    core: CatalogCore = Depends(core_from_request),
) -> dict:
    result = core.prerequisite_closure(skill_key, max_depth=max_depth, strength=strength or None)
    return {
        "skill": skill_out(result["skill"]),
        "nodes": [skill_out(n) for n in result["nodes"]],
        "edges": [
            prerequisite_out(e, core.vertex_by_id(str(e["_to"])), depth=int(e.get("depth", 0)))
            for e in result["edges"]
            if core.vertex_by_id(str(e["_to"]))
        ],
        "depth": result["depth"],
    }


@router.get("/{skill_key}/courses", summary="Khóa học dạy kỹ năng này")
def skill_courses(
    skill_key: str,
    limit: int = Query(10, ge=1, le=50),
    core: CatalogCore = Depends(core_from_request),
) -> dict:
    from ..mappers import course_out

    courses = core.courses_for_skill(skill_key, limit=limit)
    return {"items": [course_out(c) for c in courses], "total": len(courses)}
