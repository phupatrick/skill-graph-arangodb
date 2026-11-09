"""Schema của database skill_graph_db: 5 vertex + 7 edge collection.

Đây là "hợp đồng" giữa dữ liệu và code. Mọi nơi khác trong backend đều
import từ file này, không hard-code tên collection rải rác.
"""

from __future__ import annotations

DATABASE_NAME = "skill_graph_db"
GRAPH_NAME = "skill_graph"

VERTEX_COLLECTIONS: tuple[str, ...] = ("users", "skills", "careers", "courses", "providers")

EDGE_COLLECTIONS: dict[str, tuple[tuple[str, ...], tuple[str, ...]]] = {
    "has_skill": (("users",), ("skills",)),
    "targets_career": (("users",), ("careers",)),
    "requires_skill": (("careers",), ("skills",)),
    "prerequisite": (("skills",), ("skills",)),
    "teaches": (("courses",), ("skills",)),
    "completed": (("users",), ("courses",)),
    "offered_by": (("courses",), ("providers",)),
}

ALL_COLLECTIONS: tuple[str, ...] = VERTEX_COLLECTIONS + tuple(EDGE_COLLECTIONS)

# Nhãn tiếng Việt cho từng loại cạnh, dùng trong UI và tài liệu.
EDGE_LABELS: dict[str, str] = {
    "has_skill": "Người dùng có kỹ năng",
    "targets_career": "Người dùng hướng tới nghề",
    "requires_skill": "Nghề yêu cầu kỹ năng",
    "prerequisite": "Kỹ năng cần kỹ năng nền",
    "teaches": "Khóa học dạy kỹ năng",
    "completed": "Người dùng đã hoàn thành khóa học",
    "offered_by": "Khóa học do nhà cung cấp phát hành",
}

# Khoảng giới hạn an toàn cho tham số limit của endpoint graph.
MIN_GRAPH_LIMIT = 5
MAX_GRAPH_LIMIT = 500
DEFAULT_GRAPH_LIMIT = 120


def collection_of(identifier: str) -> str:
    """Tách 'skills/python' -> 'skills'. Trả '' nếu đầu vào không có dấu '/'."""
    return identifier.split("/", 1)[0] if "/" in identifier else ""


def key_of(identifier: str) -> str:
    """Tách 'skills/python' -> 'python'."""
    return identifier.split("/", 1)[1] if "/" in identifier else identifier
