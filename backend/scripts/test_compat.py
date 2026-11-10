"""Kiểm thử lớp tương thích frontend (/compat/api/v1).

Chạy khi backend ĐÃ BẬT:
    cd skillgraph/backend
    python run.py            # cửa sổ 1
    python scripts/test_compat.py   # cửa sổ 2

Vì sao phải có file này: lớp tương thích trả về hình dạng dữ liệu KHÁC backend
chính (mảng trần thay vì {items,total}). Nếu ai sửa backend chính mà vô tình
đổi hình dạng, frontend React sẽ trắng trang mà không có cảnh báo. Bộ test này
canh đúng những chỗ dễ vỡ đó.
"""

from __future__ import annotations

import json
import sys
import urllib.error
import urllib.request

BASE = "http://127.0.0.1:8000"
PREFIX = "/compat/api/v1"

# (đường_dẫn, mã_mong_đợi, mô_tả)
CASES: list[tuple[str, int, str]] = [
    ("/meta/release", 200, "thông tin phát hành"),
    ("/careers", 200, "danh sách nghề (phải là MẢNG)"),
    ("/careers/data_analyst", 200, "chi tiết một nghề"),
    ("/careers/data_analyst/skills", 200, "kỹ năng nghề yêu cầu"),
    ("/skills", 200, "danh sách kỹ năng (phải là MẢNG)"),
    ("/skills?search=python", 200, "tìm kiếm kỹ năng"),
    ("/skills/python", 200, "chi tiết kỹ năng"),
    ("/skills/python/resources", 200, "học liệu của kỹ năng"),
    ("/resources", 200, "danh sách học liệu (phải là MẢNG)"),
    ("/resources/course_001", 200, "chi tiết học liệu"),
    ("/resources/course_001/skills", 200, "kỹ năng của học liệu"),
    ("/providers", 200, "danh sách nhà cung cấp (phải là MẢNG)"),
    ("/providers/coursera/resources", 200, "học liệu theo nhà cung cấp"),
    (
        "/graph/neighborhood?focusId=careers/data_analyst&mode=career&limit=60",
        200,
        "đồ thị quanh một nghề",
    ),
    (
        "/graph/neighborhood?focusId=skills/python&mode=skill&limit=60",
        200,
        "đồ thị quanh một kỹ năng",
    ),
    ("/statistics/coverage", 200, "độ phủ học liệu"),
    ("/statistics/gaps", 200, "kỹ năng chưa có khoá dạy"),
    # --- các trường hợp phải báo lỗi đúng mã ---
    ("/careers/khong_ton_tai", 404, "nghề không tồn tại -> 404"),
    ("/skills/khong_ton_tai", 404, "kỹ năng không tồn tại -> 404"),
    ("/resources/khong_ton_tai", 404, "học liệu không tồn tại -> 404"),
    ("/graph/neighborhood?focusId=sai_dinh_dang", 400, "focusId sai định dạng -> 400"),
]

# Những đường dẫn BẮT BUỘC trả về mảng trần. Nếu trả {items,total} là hỏng
# (frontend sẽ .map() trên object -> lỗi).
MUST_BE_ARRAY = {
    "/careers",
    "/skills",
    "/skills?search=python",
    "/resources",
    "/providers",
}


def fetch(path: str) -> tuple[int, object]:
    url = BASE + PREFIX + path
    try:
        with urllib.request.urlopen(url, timeout=30) as res:
            return res.status, json.loads(res.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        try:
            return exc.code, json.loads(exc.read().decode("utf-8"))
        except Exception:
            return exc.code, None
    except Exception as exc:  # noqa: BLE001
        return 0, str(exc)


def main() -> int:
    passed = failed = 0

    for path, want_status, note in CASES:
        status, body = fetch(path)

        problems: list[str] = []
        if status != want_status:
            problems.append(f"mã {status} != {want_status}")

        # Hình dạng dữ liệu
        if want_status == 200:
            if path in MUST_BE_ARRAY:
                if not isinstance(body, list):
                    kind = type(body).__name__
                    problems.append(f"phải là MẢNG, nhận {kind}")
                elif not body:
                    problems.append("mảng rỗng (đáng lẽ phải có dữ liệu)")
            elif path.startswith("/graph/"):
                if not isinstance(body, dict) or "nodes" not in body:
                    problems.append("thiếu 'nodes'")
                elif not body.get("nodes"):
                    problems.append("đồ thị không có node nào")
            elif path.startswith("/statistics/"):
                if not isinstance(body, dict) or "items" not in body:
                    problems.append("thiếu 'items'")
                elif not body.get("items"):
                    problems.append("'items' rỗng")
            elif isinstance(body, dict) and "error" in body:
                problems.append("trả về lỗi thay vì dữ liệu")

        # Lỗi phải đúng phong bì {error:{code,message}}
        if want_status >= 400:
            if not isinstance(body, dict) or "error" not in body:
                problems.append("thiếu phong bì {error:{...}}")
            elif not body["error"].get("code"):
                problems.append("thiếu error.code")

        if problems:
            failed += 1
            print(f"[FAIL] {path}")
            print(f"        {note}")
            for p in problems:
                print(f"        -> {p}")
        else:
            passed += 1
            if isinstance(body, list):
                detail = f"mảng[{len(body)}]"
            elif isinstance(body, dict) and "nodes" in body:
                detail = f"nodes[{len(body['nodes'])}] edges[{len(body['edges'])}]"
            elif isinstance(body, dict) and "items" in body:
                detail = f"items[{len(body['items'])}]"
            elif isinstance(body, dict) and "error" in body:
                detail = f"error={body['error'].get('code')}"
            else:
                detail = "ok"
            print(f"[ OK ] {want_status} {path:<62} {detail}")

    print()
    print(f"KẾT QUẢ: {passed} đạt / {failed} hỏng (tổng {passed + failed})")
    if failed:
        print()
        print("Gợi ý: backend đã chạy chưa? Thử:")
        print("  curl http://127.0.0.1:8000/compat/api/v1/careers")
        print("Nếu endpoint /compat/* trả 404, kiểm tra app/main.py đã")
        print("include_router(compat.router) chưa.")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
