"""Lớp tương thích (adapter) phục vụ hợp đồng API mà frontend React mong đợi.

BỐI CẢNH — vì sao cần file này
==============================
Bộ frontend React trong gói bàn giao (`NoSQL_Do_An-main`) gọi API theo một
"hợp đồng" riêng, ghi tại `docs/PROPOSED_API_CONTRACT.md`:

    GET /api/v1/meta/release
    GET /api/v1/careers
    GET /api/v1/careers/{id}
    GET /api/v1/careers/{id}/skills
    GET /api/v1/skills              ?search=
    GET /api/v1/skills/{id}
    GET /api/v1/skills/{id}/resources
    GET /api/v1/resources
    GET /api/v1/resources/{id}
    GET /api/v1/providers
    GET /api/v1/graph/neighborhood  ?focusId=&mode=&nodeTypes=&edgeTypes=&limit=
    GET /api/v1/statistics/coverage

Backend chính của đồ án (`routers/*.py`) dùng tên trường camelCase riêng của
nó (ví dụ `fullName`, `coveragePct`). File này KHÔNG thay thế backend chính —
nó chỉ dịch dữ liệu `skill_graph_db` sang đúng hình dạng mà frontend cần,
để frontend chạy được mà **không phải sửa một dòng TypeScript nào**.

Ánh xạ lược đồ
==============
    skill_graph_db                    ->  catalog-v355 (frontend)
    ---------------------------------     ------------------------------------
    careers._key                      ->  Career.key / id ("careers/<key>")
    careers.name, description         ->  Career.name, description
    (không có)                        ->  Career.careerGroup, iscoGroup, escoUri = null
    skills._key, name, description    ->  Skill.key, name, description
    skills.category                   ->  Skill.skillType  (tạm dùng thay)
    requires_skill (_from career)     ->  Requirement (kèm skill, resourceCount)
    teaches (_to skill)               ->  courses-for-skill + Evidence
    offered_by                        ->  Course.providerName
    (không có prerequisite)           ->  trả mảng rỗng, KHÔNG bịa cạnh

QUAN TRỌNG — điều file này KHÔNG làm
====================================
Bộ dữ liệu `skill_graph_db` có 4 collection rỗng khi xét theo góc nhìn của
frontend: `has_skill` (274 cạnh) là của user, nhưng frontend v355 không có
user nào; `prerequisite`, `targets_career`, `completed` frontend cũng để trống.
Vì vậy các tab Skill Gap / Lộ trình / Nghề phù hợp của frontend sẽ không có
dữ liệu — đó là giới hạn của BỘ DỮ LIỆU, không phải lỗi của adapter.
Adapter tuyệt đối KHÔNG tạo cạnh giả để lấp chỗ trống.
"""

from __future__ import annotations

from typing import Any

from ..data.core import CatalogCore
from ..errors import bad_request

Raw = dict[str, Any]


# ==========================================================================
# Chuyển đổi một document sang hình dạng frontend mong đợi
# ==========================================================================
def _ident(collection: str, key: str) -> str:
    return f"{collection}/{key}"


def _edge_out(edge: Raw) -> dict[str, Any]:
    """Cạnh thô — frontend cần đúng 5 trường này trong interface Edge."""
    return {
        "key": str(edge.get("_key", "")),
        "id": str(edge.get("_key", "")),
        "from": str(edge.get("_from", "")),
        "to": str(edge.get("_to", "")),
        "raw": edge,
    }


def career_row(doc: Raw) -> dict[str, Any]:
    key = str(doc.get("_key", ""))
    return {
        "key": key,
        "id": _ident("careers", key),
        "name": doc.get("name") or "",
        "description": doc.get("description") or "",
        "careerGroup": doc.get("category") or "",
        "iscoGroup": "",
        "escoUri": "",
        "raw": doc,
    }


def skill_row(doc: Raw) -> dict[str, Any]:
    key = str(doc.get("_key", ""))
    return {
        "key": key,
        "id": _ident("skills", key),
        "name": doc.get("name") or "",
        "description": doc.get("description") or "",
        "skillType": doc.get("category") or "",
        "escoUri": "",
        "reuseLevel": doc.get("difficulty"),
        "raw": doc,
    }


def provider_row(doc: Raw) -> dict[str, Any]:
    key = str(doc.get("_key", ""))
    return {
        "key": key,
        "id": _ident("providers", key),
        "name": doc.get("name") or "",
        "officialWebsite": doc.get("website") or doc.get("url"),
        "raw": doc,
    }


def course_row(doc: Raw) -> dict[str, Any]:
    key = str(doc.get("_key", ""))
    return {
        "key": key,
        "id": _ident("courses", key),
        "title": doc.get("title") or "",
        "canonicalUrl": doc.get("url") or "",
        "providerName": doc.get("provider") or "",
        "resourceType": doc.get("level") or "course",
        "language": doc.get("language") or "en",
        "level": doc.get("level"),
        "certificateAvailable": None,
        "verifiedOutcomeProficiency": None,
        "durationHours": doc.get("duration_hours"),
        "raw": doc,
    }


# ==========================================================================
# Adapter chính
# ==========================================================================
class CatalogCompat:
    """Dịch CatalogCore sang hình dạng hợp đồng API của frontend."""

    def __init__(self, core: CatalogCore) -> None:
        self.core = core

    # -- hỗ trợ ----------------------------------------------------------
    @staticmethod
    def _bare(value: str, collection: str) -> str:
        """Nhận 'abc' hoặc 'careers/abc', luôn trả về key trần."""
        text = str(value or "")
        return text.split("/", 1)[1] if "/" in text else text

    # -- meta ------------------------------------------------------------
    def release_info(self) -> Raw:
        counts = self.core.counts()
        records = sum(counts.values())
        return {
            "version": "skill_graph_db",
            "sprint": 0,
            "records": records,
            "collections": counts,
            "source": self.core.storage.mode,
            "note": (
                "Dữ liệu skill_graph_db (12 collection). "
                "Không phải catalog-v355 của frontend."
            ),
        }

    # -- careers ---------------------------------------------------------
    def careers(self) -> list[Raw]:
        return [career_row(doc) for doc in self.core.list_careers()]

    def career(self, key_or_id: str) -> Raw | None:
        key = self._bare(key_or_id, "careers")
        try:
            return career_row(self.core.get_career(key))
        except Exception:
            return None

    def career_requirements(self, key_or_id: str) -> list[Raw]:
        """Tương đương LocalCatalogRepository.getCareerRequirements()."""
        key = self._bare(key_or_id, "careers")
        career_id = _ident("careers", key)
        rows = []
        for edge in self.core.career_requirements(career_id):
            skill_key = self._bare(str(edge.get("_to", "")), "skills")
            try:
                skill_doc = self.core.get_skill(skill_key)
            except Exception:
                continue
            out = _edge_out(edge)
            out.update(
                {
                    "requirementType": edge.get("requirement_type") or "optional",
                    "requiredLevel": edge.get("required_level"),
                    "importance": edge.get("importance"),
                    "skill": skill_row(skill_doc),
                    "resourceCount": len(self.core.skill_courses(str(edge.get("_to", "")))),
                }
            )
            rows.append(out)
        return rows

    def career_skills(self, key_or_id: str) -> dict[str, Any]:
        """/careers/{id}/skills — frontend gọi endpoint riêng cho tab này."""
        key = self._bare(key_or_id, "careers")
        requirements = self.career_requirements(key)
        return {
            "careerId": _ident("careers", key),
            "items": requirements,
            "total": len(requirements),
        }

    # -- skills ----------------------------------------------------------
    def skills(self, search: str = "") -> list[Raw]:
        return [skill_row(doc) for doc in self.core.list_skills(search)]

    def skill(self, key_or_id: str) -> Raw | None:
        key = self._bare(key_or_id, "skills")
        try:
            return skill_row(self.core.get_skill(key))
        except Exception:
            return None

    def skill_resources(self, key_or_id: str) -> dict[str, Any]:
        """Khóa học dạy kỹ năng này, kèm 'evidence' đúng kiểu frontend."""
        key = self._bare(key_or_id, "skills")
        skill_id = _ident("skills", key)
        items = []
        for edge in self.core.skill_courses(skill_id):
            course_key = self._bare(str(edge.get("_from", "")), "courses")
            try:
                course_doc = self.core.get_course(course_key)
            except Exception:
                continue
            provider = self.core.course_provider(_ident("courses", course_key))
            row = course_row(course_doc)
            if provider and not row["providerName"]:
                row["providerName"] = provider.get("name") or ""
            items.append(
                {
                    "course": row,
                    "evidence": [
                        {
                            "edge": _edge_out(edge),
                            "evidenceScope": "direct_topic",
                            "evidenceLimit": None,
                        }
                    ],
                }
            )
        return {
            "skillId": skill_id,
            "items": items,
            "total": len(items),
            "note": "Mọi cạnh teaches được xem là direct_topic (chưa phân loại chi tiết).",
        }

    # -- courses / resources --------------------------------------------
    def courses(self, search: str = "", level: str = "") -> list[Raw]:
        return [course_row(doc) for doc in self.core.list_courses(search, level)]

    def course(self, key_or_id: str) -> Raw | None:
        key = self._bare(key_or_id, "courses")
        try:
            return course_row(self.core.get_course(key))
        except Exception:
            return None

    def course_skills(self, key_or_id: str) -> dict[str, Any]:
        key = self._bare(key_or_id, "courses")
        course_id = _ident("courses", key)
        items = []
        for edge in self.core.course_skills(course_id):
            skill_key = self._bare(str(edge.get("_to", "")), "skills")
            try:
                skill_doc = self.core.get_skill(skill_key)
            except Exception:
                continue
            items.append(
                {
                    "skill": skill_row(skill_doc),
                    "evidence": [
                        {
                            "edge": _edge_out(edge),
                            "evidenceScope": "direct_topic",
                            "evidenceLimit": None,
                        }
                    ],
                }
            )
        return {"courseId": course_id, "items": items, "total": len(items)}

    # -- providers -------------------------------------------------------
    def providers(self) -> list[Raw]:
        return [provider_row(doc) for doc in self.core.list_providers()]

    def courses_by_provider(self, key_or_id: str) -> dict[str, Any]:
        key = self._bare(key_or_id, "providers")
        provider_id = _ident("providers", key)
        rows = []
        for edge in self.core.provider_courses(provider_id):
            course_key = self._bare(str(edge.get("_from", "")), "courses")
            try:
                rows.append(course_row(self.core.get_course(course_key)))
            except Exception:
                continue
        return {"providerId": provider_id, "items": rows, "total": len(rows)}

    # -- thống kê --------------------------------------------------------
    def coverage(self) -> dict[str, Any]:
        """Độ phủ kỹ năng của từng nghề, tính trên dữ liệu thật.

        Với mỗi nghề: đếm bao nhiêu kỹ năng bắt buộc đã có ít nhất một khóa
        học dạy. Đây là 'độ phủ nội dung học liệu', không phải độ phủ năng
        lực người học.
        """
        rows = []
        buckets = {"full": 0, "high": 0, "medium": 0, "low": 0}
        for career_doc in self.core.list_careers():
            career_id = _ident("careers", str(career_doc.get("_key", "")))
            essential = covered = 0
            for edge in self.core.career_requirements(career_id):
                if edge.get("requirement_type") != "essential":
                    continue
                essential += 1
                if self.core.skill_courses(str(edge.get("_to", ""))):
                    covered += 1
            missing = essential - covered
            pct = round(covered * 100.0 / essential, 1) if essential else 0.0
            if pct >= 90:
                buckets["full"] += 1
            elif pct >= 70:
                buckets["high"] += 1
            elif pct >= 40:
                buckets["medium"] += 1
            else:
                buckets["low"] += 1
            rows.append(
                {
                    "career": str(career_doc.get("name") or ""),
                    "careerKey": str(career_doc.get("_key") or ""),
                    "careerId": career_id,
                    "essential": essential,
                    "covered": covered,
                    "missing": missing,
                    "pct": pct,
                }
            )
        rows.sort(key=lambda r: (-r["pct"], r["career"]))
        total_essential = sum(r["essential"] for r in rows)
        total_covered = sum(r["covered"] for r in rows)
        return {
            "items": rows,
            "total": len(rows),
            "totalEssential": total_essential,
            "totalCovered": total_covered,
            "overallPct": (
                round(total_covered * 100.0 / total_essential, 1) if total_essential else 0.0
            ),
            "buckets": buckets,
            "definition": (
                "Độ phủ = số kỹ năng BẮT BUỘC của nghề có ít nhất một khóa học dạy, "
                "chia tổng số kỹ năng bắt buộc."
            ),
        }

    def remaining_gaps(self) -> dict[str, Any]:
        """Kỹ năng bắt buộc nhưng chưa có khóa học nào dạy."""
        rows = []
        for career_doc in self.core.list_careers():
            career_id = _ident("careers", str(career_doc.get("_key", "")))
            for edge in self.core.career_requirements(career_id):
                if edge.get("requirement_type") != "essential":
                    continue
                skill_id = str(edge.get("_to", ""))
                if self.core.skill_courses(skill_id):
                    continue
                skill_key = self._bare(skill_id, "skills")
                try:
                    skill_doc = self.core.get_skill(skill_key)
                except Exception:
                    continue
                rows.append(
                    {
                        "career": str(career_doc.get("name") or ""),
                        "careerKey": str(career_doc.get("_key") or ""),
                        "skill": str(skill_doc.get("name") or ""),
                        "skillId": skill_id,
                        "status": "no_course_in_catalog",
                        "reason": "Không có cạnh teaches nào trỏ tới kỹ năng này.",
                    }
                )
        return {"items": rows, "total": len(rows)}

    # -- đồ thị ----------------------------------------------------------
    def neighborhood(
        self,
        focus_id: str,
        mode: str = "career",
        edge_types: list[str] | None = None,
        node_types: list[str] | None = None,
        limit: int = 120,
    ) -> Raw:
        """Bọc core.graph_neighborhood và đổi tên trường sang kiểu frontend.

        Chú ý: core.graph_neighborhood() nhận **key trần** (ví dụ 'data_analyst'),
        không nhận '<collection>/<key>'. Phải tách trước khi gọi, nếu không sẽ
        báo "Không tìm thấy career với id 'careers/data_analyst'".
        """
        if "/" not in focus_id:
            raise bad_request(
                "focusId phải có dạng '<collection>/<key>', ví dụ careers/data_analyst."
            )
        collection, focus_key = focus_id.split("/", 1)
        expected_mode = {
            "users": "user",
            "careers": "career",
            "skills": "skill",
            "courses": "course",
            "providers": "provider",
        }.get(collection, mode)
        raw = self.core.graph_neighborhood(
            focus_key, expected_mode, edge_types, limit=limit
        )
        nodes = [
            {
                "id": n.get("id"),
                "type": n.get("type"),
                "label": n.get("label"),
                "raw": n.get("raw"),
            }
            for n in raw.get("nodes", [])
        ]
        edges = [
            {
                "id": e.get("id"),
                "source": e.get("source"),
                "target": e.get("target"),
                "type": e.get("type"),
                "data": e.get("data"),
            }
            for e in raw.get("edges", [])
        ]
        if node_types:
            wanted = {t.lower() for t in node_types}
            keep = {n["id"] for n in nodes if str(n["type"]).lower() in wanted}
            nodes = [n for n in nodes if n["id"] in keep]
            edges = [e for e in edges if e["source"] in keep and e["target"] in keep]
        return {
            "focus": focus_id,
            "mode": mode,
            "nodes": nodes,
            "edges": edges,
            "truncated": raw.get("truncated", False),
            "limit": limit,
            "availableEdgeTypes": raw.get("availableEdgeTypes", []),
        }


__all__ = [
    "CatalogCompat",
    "career_row",
    "course_row",
    "provider_row",
    "skill_row",
]
