"""Model Pydantic cho response.

Dùng alias kiểu camelCase để JSON trả về khớp với frontend (fullName,
requiredLevel, durationHours...). Nhờ vậy frontend đổi sang chế độ API
mà không phải sửa lại toàn bộ component.
"""

from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field
from pydantic.alias_generators import to_camel


class CamelModel(BaseModel):
    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
        extra="ignore",
    )


# --------------------------------------------------------------------------
# Metadata / health
# --------------------------------------------------------------------------
class ReleaseInfo(CamelModel):
    database: str
    graph: str
    data_mode: Literal["jsonl", "arango"]
    arango_server_version: str | None = None
    counts: dict[str, int]
    total_records: int


class ArangoHealth(CamelModel):
    configured: bool
    connected: bool
    host: str
    database: str
    server_version: str | None = None
    error: str | None = None


class HealthInfo(CamelModel):
    status: Literal["ok", "degraded"]
    data_mode: Literal["jsonl", "arango"]
    arango: ArangoHealth
    counts: dict[str, int]
    total_records: int


# --------------------------------------------------------------------------
# Vertex
# --------------------------------------------------------------------------
class UserOut(CamelModel):
    key: str
    id: str
    full_name: str
    email: str | None = None
    education_level: str | None = None
    major: str | None = None
    experience_years: float | None = None
    account_status: str | None = None
    data_origin: str | None = None


class SkillOut(CamelModel):
    key: str
    id: str
    name: str
    category: str | None = None
    description: str | None = None
    difficulty: str | None = None
    active: bool | None = None
    reference_sources: list[str] = Field(default_factory=list)


class CareerOut(CamelModel):
    key: str
    id: str
    name: str
    category: str | None = None
    description: str | None = None
    active: bool | None = None
    reference_sources: list[str] = Field(default_factory=list)


class CourseOut(CamelModel):
    key: str
    id: str
    title: str
    description: str | None = None
    level: str | None = None
    language: str | None = None
    duration_hours: float | None = None
    provider_name: str | None = None
    provider_id: str | None = None
    active: bool | None = None


class ProviderOut(CamelModel):
    key: str
    id: str
    name: str
    type: str | None = None
    active: bool | None = None
    course_count: int = 0


# --------------------------------------------------------------------------
# Quan hệ
# --------------------------------------------------------------------------
class HasSkillOut(CamelModel):
    id: str
    user_id: str
    skill_id: str
    proficiency: int | None = None
    assessment_method: str | None = None


class TargetCareerOut(CamelModel):
    id: str
    user_id: str
    career_id: str
    priority: int | None = None


class RequirementOut(CamelModel):
    id: str
    career_id: str
    skill_id: str
    requirement_type: str | None = None
    required_level: int | None = None
    importance: int | None = None
    skill: SkillOut


class PrerequisiteOut(CamelModel):
    id: str
    from_skill_id: str
    to_skill_id: str
    strength: str | None = None
    relation: str | None = None
    depth: int = 0
    skill: SkillOut


class TeachesOut(CamelModel):
    id: str
    course_id: str
    skill_id: str
    role: str | None = None
    course: CourseOut | None = None


class CompletedOut(CamelModel):
    id: str
    user_id: str
    course_id: str
    progress: int | None = None
    score: int | None = None
    status: str | None = None
    completed_at: str | None = None
    course: CourseOut | None = None


# --------------------------------------------------------------------------
# Trang danh sách
# --------------------------------------------------------------------------
class UserList(CamelModel):
    items: list[UserOut]
    total: int


class SkillList(CamelModel):
    items: list[SkillOut]
    total: int


class CareerList(CamelModel):
    items: list[CareerOut]
    total: int


class CourseList(CamelModel):
    items: list[CourseOut]
    total: int


class ProviderList(CamelModel):
    items: list[ProviderOut]
    total: int


class UserDetail(CamelModel):
    user: UserOut
    skills: list[HasSkillOut]
    targets: list[TargetCareerOut]
    completed: list[CompletedOut]


class CareerDetail(CamelModel):
    career: CareerOut
    requirements: list[RequirementOut]
    followers: int


class SkillDetail(CamelModel):
    skill: SkillOut
    required_by: list[RequirementOut]
    prerequisites: list[PrerequisiteOut]
    unlocks: list[PrerequisiteOut]
    courses: list[TeachesOut]
    holders: int


class CourseDetail(CamelModel):
    course: CourseOut
    skills: list[TeachesOut]
    provider: ProviderOut | None = None
    completions: int


class ProviderDetail(CamelModel):
    provider: ProviderOut
    courses: list[CourseOut]


# --------------------------------------------------------------------------
# Phân tích nghiệp vụ
# --------------------------------------------------------------------------
class SkillGapItem(CamelModel):
    """Một kỹ năng của nghề mục tiêu mà người dùng chưa đạt."""

    skill: SkillOut
    requirement_type: str | None = None
    required_level: int | None = None
    current_level: int | None = None
    gap_level: int | None = None
    importance: int | None = None
    status: Literal["missing", "below_level", "ok"]


class SkillGapReport(CamelModel):
    user: UserOut
    career: CareerOut
    items: list[SkillGapItem]
    total_required: int
    missing_count: int
    below_level_count: int
    ok_count: int
    coverage_pct: float


class CareerMatchItem(CamelModel):
    career: CareerOut
    match_pct: float
    required_total: int
    satisfied_total: int
    missing_essential: int


class CareerMatchReport(CamelModel):
    user: UserOut
    items: list[CareerMatchItem]


class LearningPathStep(CamelModel):
    """Một bước trong lộ trình học đề xuất."""

    order: int
    skill: SkillOut
    reason: str
    gap_level: int | None = None
    required_level: int | None = None
    prerequisite_of: list[str] = Field(default_factory=list)
    recommended_courses: list[CourseOut] = Field(default_factory=list)


class LearningPath(CamelModel):
    user: UserOut
    career: CareerOut
    steps: list[LearningPathStep]
    skipped_completed_courses: int
    note: str


class PrerequisiteTree(CamelModel):
    """Toàn bộ kỹ năng nền cần có trước một kỹ năng (traversal nhiều tầng)."""

    skill: SkillOut
    nodes: list[SkillOut]
    edges: list[PrerequisiteOut]
    depth: int


# --------------------------------------------------------------------------
# Graph
# --------------------------------------------------------------------------
class GraphNode(CamelModel):
    id: str
    type: str
    label: str
    data: dict[str, Any] | None = None


class GraphEdge(CamelModel):
    id: str
    source: str
    target: str
    type: str
    label: str | None = None
    data: dict[str, Any] | None = None


class GraphNeighborhood(CamelModel):
    focus: GraphNode
    nodes: list[GraphNode]
    edges: list[GraphEdge]
    mode: str
    truncated: bool
    limit: int
    available_edge_types: list[str]
