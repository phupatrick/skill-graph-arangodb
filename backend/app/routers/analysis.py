"""Router nghiệp vụ — phần "ăn điểm" của đồ án.

    /users/{u}/skill-gap             : phân tích kỹ năng còn thiếu
    /users/{u}/learning-path         : sinh lộ trình học có thứ tự
    /users/{u}/career-match          : điểm phù hợp với từng nghề
    /graph/neighborhood              : đồ thị con cho trang Skill Graph
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, Query

from ..data.core import CatalogCore
from ..deps import core_from_request
from ..mappers import career_out, course_out, skill_out, user_out
from ..models import (
    CareerMatchReport,
    GraphNeighborhood,
    LearningPath,
    SkillGapReport,
)
from ..schema import DEFAULT_GRAPH_LIMIT, MAX_GRAPH_LIMIT, MIN_GRAPH_LIMIT

analysis_router = APIRouter(prefix="/api/v1/users", tags=["analysis"])
graph_router = APIRouter(prefix="/api/v1/graph", tags=["graph"])


@analysis_router.get(
    "/{user_key}/skill-gap",
    response_model=SkillGapReport,
    summary="Phân tích Skill Gap: nghề yêu cầu gì, bạn còn thiếu gì",
)
def skill_gap(
    user_key: str,
    career: str = Query("", description="Mã nghề; bỏ trống thì lấy nghề mục tiêu của user"),
    core: CatalogCore = Depends(core_from_request),
) -> dict:
    report = core.skill_gap(user_key, career or None)
    return {
        "user": user_out(report["user"]),
        "career": career_out(report["career"]),
        "items": [
            {
                "skill": skill_out(item["skill"]),
                "requirementType": item["requirementType"],
                "requiredLevel": item["requiredLevel"],
                "currentLevel": item["currentLevel"],
                "gapLevel": item["gapLevel"],
                "importance": item["importance"],
                "status": item["status"],
            }
            for item in report["items"]
        ],
        "totalRequired": report["totalRequired"],
        "missingCount": report["missingCount"],
        "belowLevelCount": report["belowLevelCount"],
        "okCount": report["okCount"],
        "coveragePct": report["coveragePct"],
    }


@analysis_router.get(
    "/{user_key}/career-match",
    response_model=CareerMatchReport,
    summary="Điểm phù hợp của người dùng với từng nghề (xếp hạng)",
)
def career_match(user_key: str, core: CatalogCore = Depends(core_from_request)) -> dict:
    report = core.career_match(user_key)
    return {
        "user": user_out(report["user"]),
        "items": [
            {
                "career": career_out(item["career"]),
                "matchPct": item["matchPct"],
                "requiredTotal": item["requiredTotal"],
                "satisfiedTotal": item["satisfiedTotal"],
                "missingEssential": item["missingEssential"],
            }
            for item in report["items"]
        ],
    }


@analysis_router.get(
    "/{user_key}/learning-path",
    response_model=LearningPath,
    summary="Sinh lộ trình học cá nhân hóa (đã sắp xếp theo prerequisite)",
)
def learning_path(
    user_key: str,
    career: str = Query("", description="Mã nghề mục tiêu; bỏ trống thì lấy nghề ưu tiên 1"),
    max_steps: int = Query(20, ge=1, le=50, description="Số bước tối đa"),
    core: CatalogCore = Depends(core_from_request),
) -> dict:
    path = core.learning_path(user_key, career or None, max_steps=max_steps)
    return {
        "user": user_out(path["user"]),
        "career": career_out(path["career"]),
        "steps": [
            {
                "order": step["order"],
                "skill": skill_out(step["skill"]),
                "reason": step["reason"],
                "gapLevel": step["gapLevel"],
                "requiredLevel": step["requiredLevel"],
                "prerequisiteOf": step["prerequisiteOf"],
                "recommendedCourses": [course_out(c) for c in step["recommendedCourses"]],
            }
            for step in path["steps"]
        ],
        "skippedCompletedCourses": path["skippedCompletedCourses"],
        "note": path["note"],
    }


@graph_router.get(
    "/neighborhood",
    response_model=GraphNeighborhood,
    summary="Đồ thị con quanh một đỉnh (user/career/skill/course/provider)",
)
def neighborhood(
    focus_id: str = Query(
        ..., alias="focusId", description="Ví dụ: users/user_001 hoặc careers/data_analyst"
    ),
    mode: str = Query("career", description="user | career | skill | course | provider"),
    edge_types: str = Query(
        "", alias="edgeTypes", description="Danh sách loại cạnh, phân tách bằng dấu phẩy"
    ),
    limit: int = Query(
        DEFAULT_GRAPH_LIMIT, ge=MIN_GRAPH_LIMIT, le=MAX_GRAPH_LIMIT, description="Số node tối đa"
    ),
    core: CatalogCore = Depends(core_from_request),
) -> dict:
    if "/" not in focus_id:
        from ..errors import bad_request

        raise bad_request("focusId phải có dạng '<collection>/<key>', ví dụ careers/data_analyst.")
    collection, key = focus_id.split("/", 1)
    expected_mode = {
        "users": "user",
        "careers": "career",
        "skills": "skill",
        "courses": "course",
        "providers": "provider",
    }.get(collection)
    if expected_mode is None:
        from ..errors import bad_request

        raise bad_request(f"Collection '{collection}' không hỗ trợ hiển thị graph.")

    edge_list = [e.strip() for e in edge_types.split(",") if e.strip()]
    return core.graph_neighborhood(key, expected_mode, edge_list or None, limit=limit)
