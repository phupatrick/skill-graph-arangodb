"""Nghiệp vụ của hệ thống — TRÁI TIM của đồ án.

Năm chức năng theo đề tài:
    1. CRUD dữ liệu cơ bản        -> user/skill/career/course
    2. Phân tích Skill Gap        -> skill_gap()
    3. Tìm prerequisite nhiều tầng -> prerequisite_closure()
    4. Tìm khóa học phù hợp       -> courses_for_skill() / learning_path()
    5. Tính mức độ phù hợp nghề   -> career_match()
    6. Sinh Learning Path         -> learning_path()

Quy ước quan trọng của đồ án (theo file nghiệp vụ):
    careers --requires_skill--> skills        : nghề yêu cầu kỹ năng
    skills  --prerequisite----> skills        : _from muốn học, _to cần có trước
    courses --teaches---------> skills        : khóa học dạy kỹ năng
    users   --has_skill-------> skills        : kỹ năng + proficiency (0-100)
    users   --completed-------> courses       : đã học khóa nào
    users   --targets_career--> careers       : nghề mục tiêu
"""

from __future__ import annotations

from collections import defaultdict, deque
from typing import Any, Iterable

from ..errors import not_found
from ..schema import EDGE_LABELS
from .storage import Storage

Raw = dict[str, Any]

# Ngưỡng proficiency (0-100) dùng khi career không khai báo required_level.
DEFAULT_REQUIRED_LEVEL = 50


# ==========================================================================
# Tiện ích nhỏ
# ==========================================================================
def _key(doc: Raw) -> str:
    return str(doc.get("_key", ""))


def _ident(collection: str, doc: Raw) -> str:
    return f"{collection}/{_key(doc)}"


def _norm(text: str) -> str:
    return text.strip().lower()


def _matches(text: str | None, needle: str) -> bool:
    if not needle:
        return True
    if not text:
        return False
    return needle.lower() in text.lower()


# ==========================================================================
# Core
# ==========================================================================
class CatalogCore:
    """Toàn bộ truy vấn nghiệp vụ, chạy trên bất kỳ Storage nào."""

    def __init__(self, storage: Storage, diagnostics: dict[str, Any] | None = None) -> None:
        self.storage = storage
        self.diagnostics = diagnostics or {}

    # ---------------------------------------------------------------------
    # Health / metadata
    # ---------------------------------------------------------------------
    def counts(self) -> dict[str, int]:
        return self.storage.counts()

    def health(self) -> dict[str, Any]:
        counts = self.counts()
        arango = dict(
            self.diagnostics.get(
                "arango",
                {
                    "configured": False,
                    "connected": False,
                    "host": "",
                    "database": "",
                    "server_version": None,
                    "error": None,
                },
            )
        )
        return {
            "status": "ok",
            "dataMode": self.storage.mode,
            "arango": arango,
            "counts": counts,
            "totalRecords": sum(counts.values()),
        }

    # ---------------------------------------------------------------------
    # Đọc document cơ bản
    # ---------------------------------------------------------------------
    def _get(self, collection: str, key: str, kind: str) -> Raw:
        doc = self.storage.vertex(collection, key)
        if doc is None:
            raise not_found(kind, key)
        return doc

    def list_users(self, search: str = "") -> list[Raw]:
        rows = self.storage.vertices("users")
        rows = [r for r in rows if _matches(r.get("full_name"), search) or _matches(r.get("email"), search)]
        return sorted(rows, key=lambda r: str(r.get("full_name", "")))

    def get_user(self, key: str) -> Raw:
        return self._get("users", key, "người dùng")

    def list_skills(self, search: str = "", category: str = "") -> list[Raw]:
        rows = self.storage.vertices("skills")
        rows = [
            r
            for r in rows
            if _matches(r.get("name"), search)
            and (not category or _norm(str(r.get("category", ""))) == _norm(category))
        ]
        return sorted(rows, key=lambda r: str(r.get("name", "")))

    def get_skill(self, key: str) -> Raw:
        return self._get("skills", key, "kỹ năng")

    def list_careers(self, search: str = "", category: str = "") -> list[Raw]:
        rows = self.storage.vertices("careers")
        rows = [
            r
            for r in rows
            if _matches(r.get("name"), search)
            and (not category or _norm(str(r.get("category", ""))) == _norm(category))
        ]
        return sorted(rows, key=lambda r: str(r.get("name", "")))

    def get_career(self, key: str) -> Raw:
        return self._get("careers", key, "nghề nghiệp")

    def list_courses(self, search: str = "", level: str = "") -> list[Raw]:
        rows = self.storage.vertices("courses")
        rows = [
            r
            for r in rows
            if _matches(r.get("title"), search)
            and (not level or _norm(str(r.get("level", ""))) == _norm(level))
        ]
        return sorted(rows, key=lambda r: str(r.get("title", "")))

    def get_course(self, key: str) -> Raw:
        return self._get("courses", key, "khóa học")

    def list_providers(self, search: str = "") -> list[Raw]:
        rows = [r for r in self.storage.vertices("providers") if _matches(r.get("name"), search)]
        return sorted(rows, key=lambda r: str(r.get("name", "")))

    def get_provider(self, key: str) -> Raw:
        return self._get("providers", key, "nhà cung cấp")

    # ---------------------------------------------------------------------
    # Quan hệ của một đỉnh
    # ---------------------------------------------------------------------
    def user_skills(self, user_id: str) -> list[Raw]:
        return sorted(
            self.storage.edges("has_skill", from_id=user_id),
            key=lambda e: "".join(ch for ch in str(e["_to"]) if ch.isdigit()),
        )

    def user_targets(self, user_id: str) -> list[Raw]:
        return sorted(
            self.storage.edges("targets_career", from_id=user_id),
            key=lambda e: int(e.get("priority") or 999),
        )

    def user_completed(self, user_id: str) -> list[Raw]:
        return sorted(
            self.storage.edges("completed", from_id=user_id),
            key=lambda e: str(e.get("completed_at", "")),
            reverse=True,
        )

    def career_requirements(self, career_id: str) -> list[Raw]:
        """Kỹ năng nghề yêu cầu, sắp xếp essential trước, importance giảm dần."""

        def sort_key(edge: Raw) -> tuple[int, int, str]:
            essential = 0 if edge.get("requirement_type") == "essential" else 1
            importance = -(int(edge.get("importance") or 0))
            return (essential, importance, str(edge["_to"]))

        return sorted(self.storage.edges("requires_skill", from_id=career_id), key=sort_key)

    def skill_prerequisites(self, skill_id: str, strength: str | None = None) -> list[Raw]:
        """Trực tiếp: muốn học skill này thì cần những gì (cạnh _from = skill đó)."""
        rows = self.storage.edges("prerequisite", from_id=skill_id)
        if strength:
            rows = [r for r in rows if _norm(str(r.get("strength", ""))) == _norm(strength)]
        return rows

    def skill_unlocks(self, skill_id: str) -> list[Raw]:
        """Có kỹ năng này thì mở khoá được những kỹ năng nào (cạnh _to = skill này)."""
        return self.storage.edges("prerequisite", to_id=skill_id)

    def skill_courses(self, skill_id: str) -> list[Raw]:
        return self.storage.edges("teaches", to_id=skill_id)

    def course_skills(self, course_id: str) -> list[Raw]:
        return self.storage.edges("teaches", from_id=course_id)

    def course_provider(self, course_id: str) -> Raw | None:
        rows = self.storage.edges("offered_by", from_id=course_id)
        if not rows:
            return None
        provider_id = str(rows[0]["_to"])
        return self.storage.vertex("providers", provider_id.split("/", 1)[1])

    def provider_courses(self, provider_id: str) -> list[Raw]:
        return self.storage.edges("offered_by", to_id=provider_id)

    def skill_holders(self, skill_id: str) -> list[Raw]:
        return self.storage.edges("has_skill", to_id=skill_id)

    def course_completions(self, course_id: str) -> list[Raw]:
        return self.storage.edges("completed", to_id=course_id)

    def career_followers(self, career_id: str) -> list[Raw]:
        return self.storage.edges("targets_career", to_id=career_id)

    # ---------------------------------------------------------------------
    # 1. SKILL GAP
    # ---------------------------------------------------------------------
    def skill_gap(self, user_key: str, career_key: str | None = None) -> dict[str, Any]:
        """So sánh yêu cầu của nghề với kỹ năng hiện có của người dùng.

        Career yêu cầu Python level 3, user có level 2 -> gap 1 level.
        Trả về đủ 3 nhóm: missing / below_level / ok để UI hiển thị.
        """
        user = self.get_user(user_key)
        career = self._resolve_target_career(user_key, career_key)

        user_levels: dict[str, int] = {}
        for edge in self.user_skills(_ident("users", user)):
            user_levels[str(edge["_to"])] = int(edge.get("proficiency") or 0)

        items: list[dict[str, Any]] = []
        missing = below = ok = 0
        for edge in self.career_requirements(_ident("careers", career)):
            skill_id = str(edge["_to"])
            skill = self.storage.vertex("skills", skill_id.split("/", 1)[1])
            if skill is None:
                continue
            required = int(edge.get("required_level") or DEFAULT_REQUIRED_LEVEL)
            current = user_levels.get(skill_id)

            if current is None:
                status, gap = "missing", required
                missing += 1
            elif current < required:
                status, gap = "below_level", required - current
                below += 1
            else:
                status, gap = "ok", 0
                ok += 1

            items.append(
                {
                    "skill": skill,
                    "requirementType": edge.get("requirement_type"),
                    "requiredLevel": required,
                    "currentLevel": current,
                    "gapLevel": gap,
                    "importance": edge.get("importance"),
                    "status": status,
                }
            )

        total = len(items)
        return {
            "user": user,
            "career": career,
            "items": items,
            "totalRequired": total,
            "missingCount": missing,
            "belowLevelCount": below,
            "okCount": ok,
            "coveragePct": round((ok / total) * 100, 1) if total else 0.0,
        }

    def _resolve_target_career(self, user_key: str, career_key: str | None) -> Raw:
        """Nếu không truyền careerKey, lấy nghề mục tiêu ưu tiên cao nhất của user."""
        if career_key:
            return self.get_career(career_key)
        targets = self.user_targets(f"users/{user_key}")
        if not targets:
            raise not_found("nghề mục tiêu của người dùng", user_key)
        return self.get_career(str(targets[0]["_to"]).split("/", 1)[1])

    # ---------------------------------------------------------------------
    # 2. PREREQUISITE — TRAVERSAL NHIỀU TẦNG
    # ---------------------------------------------------------------------
    def prerequisite_closure(
        self, skill_key: str, max_depth: int = 5, strength: str | None = None
    ) -> dict[str, Any]:
        """Duyệt ngược cạnh prerequisite để lấy TOÀN BỘ kỹ năng nền.

        Machine Learning -> Statistics -> Mathematics
        Gọi với skill 'machine_learning' sẽ trả về cả 2 tầng trên.

        Dùng BFS + visited để tránh lặp vô hạn nếu dữ liệu có chu trình.
        """
        root = self.get_skill(skill_key)
        root_id = _ident("skills", root)
        nodes: dict[str, Raw] = {}
        edges: list[Raw] = []
        seen_edges: set[str] = set()
        deepest = 0

        queue: deque[tuple[str, int]] = deque([(root_id, 0)])
        visited: set[str] = {root_id}
        while queue:
            current_id, depth = queue.popleft()
            if depth >= max_depth:
                continue
            for edge in self.skill_prerequisites(current_id, strength):
                prereq_id = str(edge["_to"])
                edge_id = str(edge.get("_key", ""))
                if edge_id and edge_id not in seen_edges:
                    seen_edges.add(edge_id)
                    edges.append({**edge, "depth": depth + 1})
                prereq = self.storage.vertex("skills", prereq_id.split("/", 1)[1])
                if prereq is None:
                    continue
                nodes[prereq_id] = prereq
                if prereq_id not in visited:
                    visited.add(prereq_id)
                    deepest = max(deepest, depth + 1)
                    queue.append((prereq_id, depth + 1))

        return {
            "skill": root,
            "nodes": sorted(nodes.values(), key=lambda s: str(s.get("name", ""))),
            "edges": sorted(edges, key=lambda e: int(e.get("depth", 0))),
            "depth": deepest,
        }

    # ---------------------------------------------------------------------
    # 3. KHÓA HỌC PHÙ HỢP
    # ---------------------------------------------------------------------
    def courses_for_skill(self, skill_key: str, limit: int = 10) -> list[Raw]:
        """Khóa học dạy kỹ năng, xếp primary trước."""
        skill = self.get_skill(skill_key)
        edges = self.skill_courses(_ident("skills", skill))
        edges.sort(key=lambda e: (0 if e.get("role") == "primary" else 1, str(e["_from"])))
        out: list[Raw] = []
        for edge in edges[:limit]:
            course = self.storage.vertex("courses", str(edge["_from"]).split("/", 1)[1])
            if course:
                out.append(course)
        return out

    # ---------------------------------------------------------------------
    # 4. CAREER MATCH
    # ---------------------------------------------------------------------
    def career_match(self, user_key: str) -> dict[str, Any]:
        """Điểm phù hợp với từng nghề = tổng importance các kỹ năng đã đạt
        / tổng importance toàn bộ kỹ năng nghề yêu cầu."""
        user = self.get_user(user_key)
        user_levels = {
            str(e["_to"]): int(e.get("proficiency") or 0)
            for e in self.user_skills(_ident("users", user))
        }

        items: list[dict[str, Any]] = []
        for career in self.list_careers():
            career_id = _ident("careers", career)
            requirements = self.career_requirements(career_id)
            total_weight = 0.0
            satisfied_weight = 0.0
            satisfied = 0
            missing_essential = 0
            for edge in requirements:
                weight = float(edge.get("importance") or 10)
                total_weight += weight
                level = user_levels.get(str(edge["_to"]))
                required = int(edge.get("required_level") or DEFAULT_REQUIRED_LEVEL)
                if level is not None and level >= required:
                    satisfied_weight += weight
                    satisfied += 1
                elif edge.get("requirement_type") == "essential":
                    missing_essential += 1
            items.append(
                {
                    "career": career,
                    "matchPct": round((satisfied_weight / total_weight) * 100, 1)
                    if total_weight
                    else 0.0,
                    "requiredTotal": len(requirements),
                    "satisfiedTotal": satisfied,
                    "missingEssential": missing_essential,
                }
            )

        items.sort(key=lambda x: x["matchPct"], reverse=True)
        return {"user": user, "items": items}

    # ---------------------------------------------------------------------
    # 5. LEARNING PATH
    # ---------------------------------------------------------------------
    def learning_path(
        self, user_key: str, career_key: str | None = None, max_steps: int = 20
    ) -> dict[str, Any]:
        """Sinh lộ trình học có thứ tự.

        Thuật toán:
        1. Skill Gap -> tập kỹ năng còn thiếu/chưa đủ trình độ.
        2. Thêm các kỹ năng nền (prerequisite đệ quy) cũng còn thiếu.
        3. Sắp xếp topo: kỹ năng nền trước, kỹ năng phụ thuộc sau.
        4. Ưu tiên essential + importance cao trong cùng một tầng.
        5. Với mỗi bước, đề xuất khóa học dạy kỹ năng đó, BỎ QUA khóa đã học.
        """
        gap = self.skill_gap(user_key, career_key)
        user, career = gap["user"], gap["career"]
        user_id = _ident("users", user)

        completed_courses = {str(e["_to"]) for e in self.user_completed(user_id)}
        user_levels = {
            str(e["_to"]): int(e.get("proficiency") or 0)
            for e in self.user_skills(user_id)
        }

        # --- Bước 1+2: tập kỹ năng cần học, kèm lý do và độ ưu tiên
        needed: dict[str, dict[str, Any]] = {}
        for item in gap["items"]:
            if item["status"] == "ok":
                continue
            skill_id = _ident("skills", item["skill"])
            needed[skill_id] = {
                "skill": item["skill"],
                "reason": "Nghề yêu cầu nhưng bạn chưa có kỹ năng này"
                if item["status"] == "missing"
                else f"Trình độ hiện tại chưa đạt yêu cầu (thiếu {item['gapLevel']})",
                "requiredLevel": item["requiredLevel"],
                "gapLevel": item["gapLevel"],
                "importance": item.get("importance") or 0,
                "is_direct_requirement": True,
                "prerequisite_of": [],
            }

        # Bổ sung kỹ năng nền còn thiếu (đệ quy).
        queue = deque(needed.keys())
        visited_prereq: set[str] = set(needed.keys())
        while queue:
            current_id = queue.popleft()
            for edge in self.skill_prerequisites(current_id):
                prereq_id = str(edge["_to"])
                prereq = self.storage.vertex("skills", prereq_id.split("/", 1)[1])
                if prereq is None:
                    continue
                current_level = user_levels.get(prereq_id, 0)
                required = int(edge.get("required_level") or DEFAULT_REQUIRED_LEVEL)
                if current_level >= required:
                    continue  # đã có đủ -> không cần học lại
                if prereq_id not in needed:
                    needed[prereq_id] = {
                        "skill": prereq,
                        "reason": "Kỹ năng nền bắt buộc cho bước phía sau",
                        "requiredLevel": required,
                        "gapLevel": required - current_level,
                        "importance": 50,
                        "is_direct_requirement": False,
                        "prerequisite_of": [],
                    }
                if current_id in [p for p in needed[prereq_id]["prerequisite_of"]]:
                    pass
                else:
                    needed[prereq_id]["prerequisite_of"].append(
                        str(needed[current_id]["skill"].get("name", current_id))
                    )
                if prereq_id not in visited_prereq:
                    visited_prereq.add(prereq_id)
                    queue.append(prereq_id)

        # --- Bước 3+4: sắp xếp topo (nền trước), ưu tiên essential
        ordered = self._topological_order(needed)

        # --- Bước 5: gắn khóa học còn hiệu lực
        steps: list[dict[str, Any]] = []
        for index, skill_id in enumerate(ordered[:max_steps], start=1):
            info = needed[skill_id]
            courses = [
                course
                for course in self.courses_for_skill(_key(info["skill"]), limit=10)
                if _ident("courses", course) not in completed_courses
            ][:3]
            steps.append(
                {
                    "order": index,
                    "skill": info["skill"],
                    "reason": info["reason"],
                    "gapLevel": info["gapLevel"],
                    "requiredLevel": info["requiredLevel"],
                    "prerequisiteOf": info["prerequisite_of"],
                    "recommendedCourses": courses,
                }
            )

        return {
            "user": user,
            "career": career,
            "steps": steps,
            "skippedCompletedCourses": len(completed_courses),
            "note": (
                "Lộ trình được sinh tự động từ quan hệ requires_skill, prerequisite "
                "và teaches. Thứ tự đảm bảo kỹ năng nền đứng trước kỹ năng phụ thuộc; "
                "khóa học đã hoàn thành không được đề xuất lại."
            ),
        }

    def _topological_order(self, needed: dict[str, dict[str, Any]]) -> list[str]:
        """Kahn's algorithm trên đồ thị con prerequisite.

        Cạnh prerequisite: _from (muốn học) -> _to (cần có trước).
        Vậy _to phải đứng trước _from trong lộ trình.
        """
        indegree: dict[str, int] = {sid: 0 for sid in needed}
        dependents: dict[str, list[str]] = defaultdict(list)
        for skill_id in needed:
            for edge in self.skill_prerequisites(skill_id):
                prereq_id = str(edge["_to"])
                if prereq_id in needed:
                    indegree[skill_id] += 1
                    dependents[prereq_id].append(skill_id)

        def priority(skill_id: str) -> tuple[int, int, str]:
            info = needed[skill_id]
            direct = 0 if info["is_direct_requirement"] else 1
            return (direct, -int(info["importance"] or 0), str(info["skill"].get("name", "")))

        ready = sorted([sid for sid, deg in indegree.items() if deg == 0], key=priority)
        output: list[str] = []
        while ready:
            current = ready.pop(0)
            output.append(current)
            for dependent in dependents.get(current, []):
                indegree[dependent] -= 1
                if indegree[dependent] == 0:
                    ready.append(dependent)
            ready.sort(key=priority)

        # Nếu dữ liệu có chu trình, phần còn lại vẫn được thêm vào cuối.
        if len(output) < len(needed):
            output.extend(sorted((sid for sid in needed if sid not in set(output)), key=priority))
        return output

    # ---------------------------------------------------------------------
    # 6. GRAPH NEIGHBORHOOD (cho trang Skill Graph)
    # ---------------------------------------------------------------------
    _MODE_EDGES: dict[str, tuple[str, ...]] = {
        "user": ("has_skill", "targets_career", "completed"),
        "career": ("requires_skill",),
        "skill": ("prerequisite", "teaches", "requires_skill"),
        "course": ("teaches", "offered_by"),
        "provider": ("offered_by",),
    }

    _MODE_COLLECTION: dict[str, str] = {
        "user": "users",
        "career": "careers",
        "skill": "skills",
        "course": "courses",
        "provider": "providers",
    }

    def graph_neighborhood(
        self,
        focus_key: str,
        mode: str,
        edge_types: list[str] | None = None,
        limit: int = 120,
    ) -> dict[str, Any]:
        """Lấy đồ thị con quanh một đỉnh, giữ nguyên chiều _from -> _to."""
        collection = self._MODE_COLLECTION.get(mode)
        if collection is None:
            raise not_found("chế độ graph", mode)
        focus = self._get(collection, focus_key, mode)
        focus_id = _ident(collection, focus)

        allowed = list(self._MODE_EDGES[mode])
        selected = [e for e in (edge_types or allowed) if e in allowed] or list(allowed)

        nodes: dict[str, dict[str, Any]] = {
            focus_id: self._node(collection, focus)
        }
        edges: list[dict[str, Any]] = []
        for edge_type in selected:
            # Lấy cả hai chiều để đồ thị hiển thị đầy đủ ngữ cảnh.
            found = list(self.storage.edges(edge_type, from_id=focus_id))
            found += list(self.storage.edges(edge_type, to_id=focus_id))
            for edge in found:
                source = str(edge["_from"])
                target = str(edge["_to"])
                for endpoint in (source, target):
                    if endpoint == focus_id or endpoint in nodes:
                        continue
                    endpoint_collection, endpoint_key = endpoint.split("/", 1)
                    doc = self.storage.vertex(endpoint_collection, endpoint_key)
                    if doc is not None:
                        nodes[endpoint] = self._node(endpoint_collection, doc)
                edges.append(
                    {
                        "id": str(edge.get("_key", f"{source}->{target}")),
                        "source": source,
                        "target": target,
                        "type": edge_type,
                        "label": EDGE_LABELS.get(edge_type),
                        "data": {
                            k: v
                            for k, v in edge.items()
                            if k not in {"_id", "_rev", "_key", "_from", "_to"}
                        },
                    }
                )

        truncated = len(nodes) > limit
        kept = list(nodes.items())[:limit]
        kept_ids = {node_id for node_id, _ in kept}
        kept_edges = [
            e for e in edges if e["source"] in kept_ids and e["target"] in kept_ids
        ]

        return {
            "focus": nodes[focus_id],
            "nodes": [node for _, node in kept],
            "edges": kept_edges,
            "mode": mode,
            "truncated": truncated,
            "limit": limit,
            "availableEdgeTypes": selected,
        }

    def _node(self, collection: str, doc: Raw) -> dict[str, Any]:
        labels = {
            "users": doc.get("full_name"),
            "skills": doc.get("name"),
            "careers": doc.get("name"),
            "courses": doc.get("title"),
            "providers": doc.get("name"),
        }
        types = {
            "users": "user",
            "skills": "skill",
            "careers": "career",
            "courses": "course",
            "providers": "provider",
        }
        label = labels.get(collection) or _key(doc) or f"[Thiếu tên] {collection}"
        return {
            "id": _ident(collection, doc),
            "type": types.get(collection, collection),
            "label": str(label),
        }

    # ---------------------------------------------------------------------
    # Tiện ích cho router
    # ---------------------------------------------------------------------
    def vertex_by_id(self, identifier: str) -> Raw | None:
        """'skills/python' -> document. Trả None nếu không phải định dạng hợp lệ."""
        if "/" not in identifier:
            return None
        collection, key = identifier.split("/", 1)
        return self.storage.vertex(collection, key)
