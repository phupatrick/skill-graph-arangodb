"""Chuyển document thô của ArangoDB sang model trả về cho client.

Tách riêng để router ngắn gọn và để mọi nơi map field theo cùng một quy tắc.
"""

from __future__ import annotations

from typing import Any

from .models import (
    CareerOut,
    CompletedOut,
    CourseOut,
    HasSkillOut,
    PrerequisiteOut,
    ProviderOut,
    RequirementOut,
    SkillOut,
    TargetCareerOut,
    TeachesOut,
    UserOut,
)

Raw = dict[str, Any]


def user_out(doc: Raw) -> dict[str, Any]:
    key = str(doc.get("_key", ""))
    return {
        "key": key,
        "id": f"users/{key}",
        "fullName": doc.get("full_name") or "",
        "email": doc.get("email"),
        "educationLevel": doc.get("education_level"),
        "major": doc.get("major"),
        "experienceYears": doc.get("experience_years"),
        "accountStatus": doc.get("account_status"),
        "dataOrigin": doc.get("data_origin"),
    }


def skill_out(doc: Raw) -> dict[str, Any]:
    key = str(doc.get("_key", ""))
    return {
        "key": key,
        "id": f"skills/{key}",
        "name": doc.get("name") or "",
        "category": doc.get("category"),
        "description": doc.get("description"),
        "difficulty": doc.get("difficulty"),
        "active": doc.get("active"),
        "referenceSources": doc.get("reference_sources") or [],
    }


def career_out(doc: Raw) -> dict[str, Any]:
    key = str(doc.get("_key", ""))
    return {
        "key": key,
        "id": f"careers/{key}",
        "name": doc.get("name") or "",
        "category": doc.get("category"),
        "description": doc.get("description"),
        "active": doc.get("active"),
        "referenceSources": doc.get("reference_sources") or [],
    }


def course_out(doc: Raw) -> dict[str, Any]:
    key = str(doc.get("_key", ""))
    return {
        "key": key,
        "id": f"courses/{key}",
        "title": doc.get("title") or "",
        "description": doc.get("description"),
        "level": doc.get("level"),
        "language": doc.get("language"),
        "durationHours": doc.get("duration_hours"),
        "providerName": doc.get("provider"),
        "active": doc.get("active"),
    }


def provider_out(doc: Raw, course_count: int = 0) -> dict[str, Any]:
    key = str(doc.get("_key", ""))
    return {
        "key": key,
        "id": f"providers/{key}",
        "name": doc.get("name") or "",
        "type": doc.get("type"),
        "active": doc.get("active"),
        "courseCount": course_count,
    }


def has_skill_out(edge: Raw) -> dict[str, Any]:
    return {
        "id": str(edge.get("_key", "")),
        "userId": str(edge.get("_from", "")),
        "skillId": str(edge.get("_to", "")),
        "proficiency": edge.get("proficiency"),
        "assessmentMethod": edge.get("assessment_method"),
    }


def target_out(edge: Raw) -> dict[str, Any]:
    return {
        "id": str(edge.get("_key", "")),
        "userId": str(edge.get("_from", "")),
        "careerId": str(edge.get("_to", "")),
        "priority": edge.get("priority"),
    }


def requirement_out(edge: Raw, skill: Raw) -> dict[str, Any]:
    return {
        "id": str(edge.get("_key", "")),
        "careerId": str(edge.get("_from", "")),
        "skillId": str(edge.get("_to", "")),
        "requirementType": edge.get("requirement_type"),
        "requiredLevel": edge.get("required_level"),
        "importance": edge.get("importance"),
        "skill": skill_out(skill),
    }


def prerequisite_out(edge: Raw, skill: Raw, depth: int = 0) -> dict[str, Any]:
    return {
        "id": str(edge.get("_key", "")),
        "fromSkillId": str(edge.get("_from", "")),
        "toSkillId": str(edge.get("_to", "")),
        "strength": edge.get("strength"),
        "relation": edge.get("relation"),
        "depth": depth,
        "skill": skill_out(skill),
    }


def teaches_out(edge: Raw, course: Raw | None = None) -> dict[str, Any]:
    return {
        "id": str(edge.get("_key", "")),
        "courseId": str(edge.get("_from", "")),
        "skillId": str(edge.get("_to", "")),
        "role": edge.get("role"),
        "course": course_out(course) if course else None,
    }


def completed_out(edge: Raw, course: Raw | None = None) -> dict[str, Any]:
    return {
        "id": str(edge.get("_key", "")),
        "userId": str(edge.get("_from", "")),
        "courseId": str(edge.get("_to", "")),
        "progress": edge.get("progress"),
        "score": edge.get("score"),
        "status": edge.get("status"),
        "completedAt": edge.get("completed_at"),
        "course": course_out(course) if course else None,
    }


__all__ = [
    "CareerOut",
    "CompletedOut",
    "CourseOut",
    "HasSkillOut",
    "PrerequisiteOut",
    "ProviderOut",
    "RequirementOut",
    "SkillOut",
    "TargetCareerOut",
    "TeachesOut",
    "UserOut",
    "career_out",
    "completed_out",
    "course_out",
    "has_skill_out",
    "prerequisite_out",
    "provider_out",
    "requirement_out",
    "skill_out",
    "target_out",
    "user_out",
]
