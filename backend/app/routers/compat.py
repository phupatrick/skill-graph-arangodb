"""Router tương thích cho frontend React trong gói bàn giao.

Cung cấp ĐÚNG 12 đường dẫn mà `src/repositories/HttpCatalogClient.ts` gọi,
với tên trường đúng như interface trong `src/types/catalog.ts`.

Không sửa gì phía frontend — chỉ cần đặt:
    VITE_DATA_SOURCE=api
    VITE_API_BASE_URL=http://127.0.0.1:8000
rồi chạy `npm run dev`.

Lưu ý về phạm vi: `/statistics/coverage` ở đây tính "độ phủ học liệu"
(mỗi kỹ năng bắt buộc có khóa học nào dạy chưa), khác với "độ phủ năng lực
người học" của backend chính — vì frontend v355 không có user nào.
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, Query

from ..data.compat import CatalogCompat
from ..deps import core_from_request
from ..data.core import CatalogCore
from ..errors import bad_request, not_found
from ..schema import DEFAULT_GRAPH_LIMIT, MAX_GRAPH_LIMIT, MIN_GRAPH_LIMIT

router = APIRouter(prefix="/compat/api/v1", tags=["compat (frontend React)"])


# Vì sao có tiền tố "/compat"?
# ----------------------------
# Frontend cần `GET /careers` trả về MẢNG Career[], còn backend chính trả về
# `{items, total}`. Hai hình dạng mâu thuẫn nhau trên cùng một đường dẫn.
# Nếu đăng ký trùng đường dẫn thì chỉ một bên thắng, bên kia hỏng.
# Vì vậy toàn bộ lớp tương thích nằm dưới tiền tố riêng:
#
#     http://127.0.0.1:8000/compat/api/v1/careers      -> mảng Career[]
#     http://127.0.0.1:8000/api/v1/careers             -> {items, total}
#
# Phía frontend chỉ cần đặt VITE_API_BASE_URL=http://127.0.0.1:8000/compat
# (vì HttpCatalogClient tự nối thêm '/api/v1/...' vào sau base URL).
# Nhờ vậy KHÔNG phải sửa một dòng nào trong backend chính, và 42 điểm kiểm
# thử cũ vẫn chạy nguyên.


def _compat(core: CatalogCore = Depends(core_from_request)) -> CatalogCompat:
    return CatalogCompat(core)


# ----------------------------------------------------------------------
# meta
# ----------------------------------------------------------------------
@router.get(
    "/meta/release",
    summary="[compat] Thông tin phát hành dữ liệu cho frontend",
)
def release(compat: CatalogCompat = Depends(_compat)) -> dict:
    return compat.release_info()


# ----------------------------------------------------------------------
# careers
# ----------------------------------------------------------------------
@router.get("/careers", summary="[compat] Danh sách nghề (kiểu frontend)")
def list_careers_compat(compat: CatalogCompat = Depends(_compat)) -> list:
    return compat.careers()


@router.get("/careers/{career_id}", summary="[compat] Chi tiết một nghề")
def get_career_compat(career_id: str, compat: CatalogCompat = Depends(_compat)) -> dict:
    if "/" in career_id:
        raise bad_request(
            "Tham số phải là key trần, ví dụ 'data_analyst' — không phải 'careers/data_analyst'."
        )
    row = compat.career(career_id)
    if row is None:
        raise not_found("nghề", career_id)
    return row


@router.get(
    "/careers/{career_id}/skills",
    summary="[compat] Kỹ năng nghề yêu cầu (kèm resourceCount)",
)
def get_career_skills_compat(career_id: str, compat: CatalogCompat = Depends(_compat)) -> dict:
    if compat.career(career_id) is None:
        raise not_found("nghề", career_id)
    return compat.career_skills(career_id)


# ----------------------------------------------------------------------
# skills
# ----------------------------------------------------------------------
@router.get("/skills", summary="[compat] Danh sách / tìm kiếm kỹ năng")
def list_skills_compat(
    search: str = Query("", description="Từ khoá tìm theo tên"),
    compat: CatalogCompat = Depends(_compat),
) -> list:
    return compat.skills(search)


@router.get("/skills/{skill_id}", summary="[compat] Chi tiết một kỹ năng")
def get_skill_compat(skill_id: str, compat: CatalogCompat = Depends(_compat)) -> dict:
    row = compat.skill(skill_id)
    if row is None:
        raise not_found("kỹ năng", skill_id)
    return row


@router.get(
    "/skills/{skill_id}/resources",
    summary="[compat] Khoá học dạy kỹ năng (kèm evidence)",
)
def get_skill_resources_compat(skill_id: str, compat: CatalogCompat = Depends(_compat)) -> dict:
    if compat.skill(skill_id) is None:
        raise not_found("kỹ năng", skill_id)
    return compat.skill_resources(skill_id)


# ----------------------------------------------------------------------
# resources (frontend gọi "resource", dữ liệu của ta là "courses")
# ----------------------------------------------------------------------
@router.get("/resources", summary="[compat] Danh sách học liệu (khóa học)")
def list_resources_compat(
    search: str = Query("", description="Từ khoá tìm theo tên khoá học"),
    level: str = Query("", description="Lọc theo trình độ"),
    compat: CatalogCompat = Depends(_compat),
) -> list:
    return compat.courses(search, level)


@router.get("/resources/{resource_id}", summary="[compat] Chi tiết một học liệu")
def get_resource_compat(resource_id: str, compat: CatalogCompat = Depends(_compat)) -> dict:
    row = compat.course(resource_id)
    if row is None:
        raise not_found("học liệu", resource_id)
    return row


@router.get(
    "/resources/{resource_id}/skills",
    summary="[compat] Kỹ năng mà học liệu này dạy",
)
def get_resource_skills_compat(resource_id: str, compat: CatalogCompat = Depends(_compat)) -> dict:
    if compat.course(resource_id) is None:
        raise not_found("học liệu", resource_id)
    return compat.course_skills(resource_id)


# ----------------------------------------------------------------------
# providers
# ----------------------------------------------------------------------
@router.get("/providers", summary="[compat] Danh sách nhà cung cấp")
def list_providers_compat(compat: CatalogCompat = Depends(_compat)) -> list:
    return compat.providers()


@router.get(
    "/providers/{provider_id}/resources",
    summary="[compat] Học liệu của một nhà cung cấp",
)
def list_provider_resources_compat(
    provider_id: str, compat: CatalogCompat = Depends(_compat)
) -> dict:
    return compat.courses_by_provider(provider_id)


# ----------------------------------------------------------------------
# graph
# ----------------------------------------------------------------------
@router.get(
    "/graph/neighborhood",
    summary="[compat] Đồ thị con (tham số giống frontend: focusId/mode/nodeTypes/edgeTypes/limit)",
)
def neighborhood_compat(
    focus_id: str = Query(..., alias="focusId", description="Ví dụ: careers/data_analyst"),
    mode: str = Query("career", description="user | career | skill | course | provider"),
    node_types: str = Query("", alias="nodeTypes", description="Phân tách bằng dấu phẩy"),
    edge_types: str = Query("", alias="edgeTypes", description="Phân tách bằng dấu phẩy"),
    limit: int = Query(DEFAULT_GRAPH_LIMIT, ge=MIN_GRAPH_LIMIT, le=MAX_GRAPH_LIMIT),
    compat: CatalogCompat = Depends(_compat),
) -> dict:
    if "/" not in focus_id:
        raise bad_request(
            "focusId phải có dạng '<collection>/<key>', ví dụ careers/data_analyst."
        )
    return compat.neighborhood(
        focus_id=focus_id,
        mode=mode,
        edge_types=[e.strip() for e in edge_types.split(",") if e.strip()] or None,
        node_types=[n.strip() for n in node_types.split(",") if n.strip()] or None,
        limit=limit,
    )


# ----------------------------------------------------------------------
# statistics
# ----------------------------------------------------------------------
@router.get(
    "/statistics/coverage",
    summary="[compat] Độ phủ học liệu theo nghề",
)
def coverage_compat(compat: CatalogCompat = Depends(_compat)) -> dict:
    return compat.coverage()


@router.get(
    "/statistics/gaps",
    summary="[compat] Kỹ năng bắt buộc chưa có khoá học nào dạy",
)
def gaps_compat(compat: CatalogCompat = Depends(_compat)) -> dict:
    return compat.remaining_gaps()
