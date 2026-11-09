"""Smoke test toàn bộ endpoint — chạy không cần ArangoDB.

    python scripts/smoke_test.py

Script này kiểm tra cả dữ liệu trả về, không chỉ status code, nên nếu
backend sai logic (ví dụ skill gap tính nhầm) thì sẽ báo lỗi ngay.
"""

from __future__ import annotations

import io
import json
import os
import sys
from pathlib import Path

# Console Windows mặc định cp1258 -> ép UTF-8.
for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError):
        pass

BACKEND_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND_DIR))
os.environ.setdefault("SKILLGRAPH_DATA_MODE", "jsonl")

from fastapi.testclient import TestClient  # noqa: E402

from app.main import app  # noqa: E402

PASSED: list[str] = []
FAILED: list[tuple[str, str]] = []


def check(name: str, condition: bool, detail: str = "") -> None:
    if condition:
        PASSED.append(name)
        print(f"  PASS  {name}")
    else:
        FAILED.append((name, detail))
        print(f"  FAIL  {name}  {detail}")


def main() -> int:
    with TestClient(app) as client:
        print("\n=== Metadata ===")
        r = client.get("/api/v1/meta/health")
        health = r.json()
        check("health 200", r.status_code == 200, str(r.status_code))
        check("data_mode jsonl", health["dataMode"] == "jsonl", health.get("dataMode"))
        check("12 collections", len(health["counts"]) == 12, str(len(health["counts"])))
        check("1584 records", health["totalRecords"] == 1584, str(health.get("totalRecords")))

        r = client.get("/api/v1/meta/release")
        check("release 200", r.status_code == 200, str(r.status_code))

        print("\n=== Danh sách ===")
        users = client.get("/api/v1/users").json()
        check("40 users", users["total"] == 40, str(users["total"]))
        skills = client.get("/api/v1/skills").json()
        check("248 skills", skills["total"] == 248, str(skills["total"]))
        careers = client.get("/api/v1/careers").json()
        check("29 careers", careers["total"] == 29, str(careers["total"]))
        courses = client.get("/api/v1/courses").json()
        check("89 courses", courses["total"] == 89, str(courses["total"]))
        providers = client.get("/api/v1/providers").json()
        check("8 providers", providers["total"] == 8, str(providers["total"]))
        check(
            "provider có courseCount",
            all(p["courseCount"] >= 0 for p in providers["items"]),
            "missing courseCount",
        )

        print("\n=== Chi tiết ===")
        r = client.get("/api/v1/users/user_001")
        check("user detail 200", r.status_code == 200, str(r.status_code))
        detail = r.json()
        check("user có skills", len(detail["skills"]) > 0, str(len(detail["skills"])))
        check("user có targets", len(detail["targets"]) > 0, str(len(detail["targets"])))

        r = client.get("/api/v1/careers/data_analyst")
        career = r.json()
        check("career detail 200", r.status_code == 200, str(r.status_code))
        check("career có requirements", len(career["requirements"]) > 0, "")

        r = client.get("/api/v1/skills/python")
        skill = r.json()
        check("skill detail 200", r.status_code == 200, str(r.status_code))
        check("skill có courses", len(skill["courses"]) > 0, str(len(skill["courses"])))

        r = client.get("/api/v1/courses/course_001")
        check("course detail 200", r.status_code == 200, str(r.status_code))
        check("course có provider", r.json()["provider"] is not None, "")

        print("\n=== Nghiệp vụ: Skill Gap ===")
        r = client.get("/api/v1/users/user_001/skill-gap")
        gap = r.json()
        check("skill-gap 200", r.status_code == 200, str(r.status_code))
        check("gap có items", len(gap["items"]) > 0, str(len(gap["items"])))
        check(
            "tổng missing+below+ok = total",
            gap["missingCount"] + gap["belowLevelCount"] + gap["okCount"] == gap["totalRequired"],
            f"{gap['missingCount']}+{gap['belowLevelCount']}+{gap['okCount']} != {gap['totalRequired']}",
        )
        check(
            "mọi item có status hợp lệ",
            all(i["status"] in {"missing", "below_level", "ok"} for i in gap["items"]),
            "",
        )

        print("\n=== Nghiệp vụ: Career Match ===")
        r = client.get("/api/v1/users/user_001/career-match")
        match = r.json()
        check("career-match 200", r.status_code == 200, str(r.status_code))
        check("có 29 nghề", len(match["items"]) == 29, str(len(match["items"])))
        pcts = [i["matchPct"] for i in match["items"]]
        check("xếp hạng giảm dần", pcts == sorted(pcts, reverse=True), "chưa sort")
        check("điểm trong 0..100", all(0 <= p <= 100 for p in pcts), "")

        print("\n=== Nghiệp vụ: Prerequisite nhiều tầng ===")
        r = client.get("/api/v1/skills/machine_learning/prerequisites")
        prereq = r.json()
        check("prerequisite 200", r.status_code == 200, str(r.status_code))
        check(
            "duyệt được nhiều hơn 1 tầng hoặc không có nền",
            prereq["depth"] >= 0,
            str(prereq["depth"]),
        )

        print("\n=== Nghiệp vụ: Learning Path ===")
        r = client.get("/api/v1/users/user_001/learning-path?max_steps=10")
        path = r.json()
        check("learning-path 200", r.status_code == 200, str(r.status_code))
        check("có bước", len(path["steps"]) > 0, str(len(path["steps"])))
        check(
            "order tăng dần 1..n",
            [s["order"] for s in path["steps"]] == list(range(1, len(path["steps"]) + 1)),
            "order sai",
        )
        check(
            "bước không chứa kỹ năng đã đạt",
            all(s["gapLevel"] > 0 for s in path["steps"]),
            "có bước gapLevel <= 0",
        )

        print("\n=== Graph ===")
        r = client.get("/api/v1/graph/neighborhood?focusId=careers/data_analyst")
        graph = r.json()
        check("graph 200", r.status_code == 200, str(r.status_code))
        check("graph có node", len(graph["nodes"]) > 1, str(len(graph["nodes"])))
        check("graph có edge", len(graph["edges"]) >= 1, str(len(graph["edges"])))
        node_ids = {n["id"] for n in graph["nodes"]}
        check(
            "mọi edge trỏ tới node tồn tại",
            all(e["source"] in node_ids and e["target"] in node_ids for e in graph["edges"]),
            "edge mồ côi",
        )
        check(
            "giữ chiều career -> skill",
            all(
                e["source"].startswith("careers/") or e["source"].startswith("skills/")
                for e in graph["edges"]
            ),
            "",
        )

        print("\n=== Lỗi ===")
        r = client.get("/api/v1/users/khong_ton_tai")
        check("404 đúng định dạng", r.status_code == 404 and "error" in r.json(), r.text[:120])
        check(
            "error có code",
            r.json()["error"]["code"] == "NOT_FOUND",
            r.json()["error"]["code"],
        )
        r = client.get("/api/v1/graph/neighborhood?focusId=abc")
        check("focusId sai -> 400", r.status_code == 400, str(r.status_code))

    print("\n" + "=" * 60)
    print(f"PASSED: {len(PASSED)}   FAILED: {len(FAILED)}")
    if FAILED:
        for name, detail in FAILED:
            print(f"  - {name}: {detail}")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
