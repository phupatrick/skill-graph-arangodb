"""Router: khóa học, nhà cung cấp."""

from __future__ import annotations

from fastapi import APIRouter, Depends, Query

from ..data.core import CatalogCore
from ..deps import core_from_request
from ..mappers import course_out, provider_out, teaches_out
from ..models import CourseDetail, CourseList, ProviderDetail, ProviderList

router = APIRouter(prefix="/api/v1/courses", tags=["courses"])


@router.get("", response_model=CourseList, summary="Danh sách khóa học")
def list_courses(
    search: str = Query("", description="Tìm theo tên khóa học"),
    level: str = Query("", description="Lọc theo cấp độ (Beginner...)"),
    core: CatalogCore = Depends(core_from_request),
) -> dict:
    rows = core.list_courses(search, level)
    return {"items": [course_out(r) for r in rows], "total": len(rows)}


@router.get("/{course_key}", response_model=CourseDetail, summary="Chi tiết khóa học")
def get_course(course_key: str, core: CatalogCore = Depends(core_from_request)) -> dict:
    course = core.get_course(course_key)
    course_id = f"courses/{course_key}"
    skills = []
    for edge in core.course_skills(course_id):
        skill = core.vertex_by_id(str(edge["_to"]))
        if skill:
            skills.append(teaches_out(edge, skill))
    provider_doc = core.course_provider(course_id)
    return {
        "course": course_out(course),
        "skills": skills,
        "provider": provider_out(provider_doc) if provider_doc else None,
        "completions": len(core.course_completions(course_id)),
    }


providers_router = APIRouter(prefix="/api/v1/providers", tags=["providers"])


@providers_router.get("", response_model=ProviderList, summary="Danh sách nhà cung cấp")
def list_providers(
    search: str = Query("", description="Tìm theo tên nhà cung cấp"),
    core: CatalogCore = Depends(core_from_request),
) -> dict:
    rows = core.list_providers(search)
    items = []
    for row in rows:
        provider_id = f"providers/{row['_key']}"
        items.append(provider_out(row, course_count=len(core.provider_courses(provider_id))))
    return {"items": items, "total": len(items)}


@providers_router.get("/{provider_key}", response_model=ProviderDetail, summary="Chi tiết nhà cung cấp")
def get_provider(provider_key: str, core: CatalogCore = Depends(core_from_request)) -> dict:
    provider = core.get_provider(provider_key)
    provider_id = f"providers/{provider_key}"
    courses = []
    for edge in core.provider_courses(provider_id):
        course = core.vertex_by_id(str(edge["_from"]))
        if course:
            courses.append(course_out(course))
    return {"provider": provider_out(provider, course_count=len(courses)), "courses": courses}
