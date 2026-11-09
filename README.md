# Skill Graph — Hệ thống đề xuất lộ trình học cá nhân hóa (ArangoDB)

Đồ án nhóm: dùng **ArangoDB** (Document + Graph) để biểu diễn quan hệ giữa
**User – Skill – Career – Course**, từ đó phân tích **Skill Gap**, tìm
**kỹ năng tiên quyết nhiều tầng**, gợi ý **khóa học** và sinh **lộ trình học
cá nhân hóa** cho từng người dùng.

```
skillgraph/
├── backend/                 API Python (FastAPI) + toàn bộ nghiệp vụ
│   ├── app/                 mã nguồn
│   ├── data/                12 collection dạng JSONL (trích từ dump thật)
│   ├── scripts/             extract_dump.py, smoke_test.py
│   └── requirements.txt
├── queries/aql_queries.aql  Bộ truy vấn AQL để dán vào ArangoDB Web UI
├── docker-compose.yml       Dựng ArangoDB bằng Docker (tuỳ chọn)
└── docs/                    Báo cáo + slide + tài liệu học tập
    ├── BAO_CAO_DO_AN.docx        Báo cáo đồ án (4 chương, 13 trang)
    ├── BAO_CAO_SLIDE.pptx        Slide thuyết trình (10 slide)
    ├── GIAI_THICH_CHI_TIET.docx  ★ Tài liệu học tập & thuyết trình (41 trang)
    └── HUONG_DAN_CHI_TIET.md     Bản markdown của hướng dẫn chi tiết
```

> **Mới tham gia nhóm?** Đọc `docs/GIAI_THICH_CHI_TIET.docx` trước — giải thích từ
> số 0, có kịch bản nói từng slide và 25 câu hỏi bảo vệ kèm câu trả lời mẫu.

---

## 1. Chạy nhanh nhất (không cần cài ArangoDB)

Backend đọc trực tiếp 12 file JSONL trong `backend/data/`, dữ liệu **thật**
trích từ dump `skill_graph_db`.

```powershell
cd skillgraph/backend
pip install -r requirements.txt
python run.py
```

Mở:
- Giao diện demo 4 tab: <http://127.0.0.1:8000/demo>
- Dữ liệu của đồ án: 12 collection, 1.584 bản ghi
- API: <http://127.0.0.1:8000/api/v1/meta/health>
- Tài liệu tự sinh (bấm thử được): <http://127.0.0.1:8000/docs>

Kiểm tra toàn bộ 42 điểm:

```powershell
python scripts/smoke_test.py
```

---

## 2. Chạy với ArangoDB thật

### 2.1 Dựng database bằng Docker

```powershell
cd skillgraph
docker compose up -d arangodb
```

ArangoDB chạy tại <http://127.0.0.1:8529> (user `root`).

### 2.2 Nạp dữ liệu thật vào ArangoDB

Nếu đã nhận file dump `skill_graph_db` từ nhóm, cách chuẩn là `arangorestore`:

```powershell
docker cp .\skill_graph_db_dump arangodb:/tmp/dump
docker exec arangodb arangorestore `
  --server.endpoint tcp://127.0.0.1:8529 `
  --server.database skill_graph_db `
  --server.username root `
  --server.password "mat_khau_cua_ban" `
  --input-directory /tmp/dump
```

> ⚠️ **Đừng** dùng nút *Import JSON* trên ArangoDB Web Interface cho dump này:
> nó chỉ tạo document, **mất toàn bộ edge** → đồ thị vô dụng.

Một cách khác nếu không có dump: import lại từ JSONL đã trích sẵn.

```powershell
docker exec -it arangodb arangosh --server.password "" --javascript.execute-string `
  "db._createDatabase('skill_graph_db')"
# rồi import từng collection bằng arangoimport (xem docs/HUONG_DAN_CHI_TIET.md)
```

### 2.3 Trỏ backend vào ArangoDB

```powershell
$env:SKILLGRAPH_DATA_MODE = "arango"
$env:ARANGO_PASSWORD     = "mat_khau_cua_ban"
python run.py
```

Kiểm tra đã nối được chưa:

```powershell
curl http://127.0.0.1:8000/api/v1/meta/health
# {"status":"ok","dataMode":"arango","arango":{"connected":true,...}}
```

---

## 3. Bộ truy vấn AQL (phần chấm điểm của đề tài)

Mở ArangoDB Web Interface → chọn database `skill_graph_db` → tab **QUERIES**
→ dán từng truy vấn trong `queries/aql_queries.aql` → **Run**.

| Nhóm | Truy vấn | Nội dung |
|---|---|---|
| Cơ bản | A1–A4 | Đếm, liệt kê, tìm kiếm, lọc |
| Cơ bản | A5–A7 | Quan hệ của một user (kỹ năng, mục tiêu, đã học) |
| CRUD | A8–A10 | Thêm / cập nhật / xoá |
| Nâng cao | **B2** | **Skill Gap** (so sánh requires ↔ has_skill) |
| Nâng cao | **B3, B4** | **Prerequisite nhiều tầng** + đường đi đầy đủ |
| Nâng cao | B5, B7 | Khóa học phù hợp (chưa học) |
| Nâng cao | **B6** | **Career fit** — điểm phù hợp từng nghề |
| Nâng cao | **B8** | **Sinh Learning Path có thứ tự** |
| Nâng cao | B11 | `SHORTEST_PATH` giữa hai kỹ năng |
| Nâng cao | B12, B13 | Khoảng trống dữ liệu + thống kê |

---

## 4. Các API chính

| Method | Đường dẫn | Ý nghĩa |
|---|---|---|
| GET | `/api/v1/meta/health` | Trạng thái backend + kết nối ArangoDB |
| GET | `/api/v1/meta/release` | Số bản ghi từng collection |
| GET | `/api/v1/users` | Danh sách người dùng |
| GET | `/api/v1/users/{key}` | Chi tiết user + kỹ năng + mục tiêu |
| GET | **`/api/v1/users/{key}/skill-gap`** | **Phân tích kỹ năng còn thiếu** |
| GET | **`/api/v1/users/{key}/learning-path`** | **Lộ trình học đề xuất** |
| GET | **`/api/v1/users/{key}/career-match`** | **Xếp hạng nghề phù hợp** |
| GET | `/api/v1/skills` | Danh sách kỹ năng |
| GET | **`/api/v1/skills/{key}/prerequisites`** | **Duyệt kỹ năng nền nhiều tầng** |
| GET | `/api/v1/careers/{key}` | Nghề + yêu cầu kỹ năng |
| GET | `/api/v1/courses/{key}` | Khóa học + kỹ năng + nhà cung cấp |
| GET | `/api/v1/graph/neighborhood` | Đồ thị con cho trang Skill Graph |

---

## 5. Dữ liệu

`skill_graph_db` — 12 collection, **1.584 bản ghi**:

| Collection | Loại | Số bản ghi | Ý nghĩa |
|---|---|---|---|
| `users` | Vertex | 40 | Người dùng |
| `skills` | Vertex | 248 | Kỹ năng |
| `careers` | Vertex | 29 | Nghề nghiệp |
| `courses` | Vertex | 89 | Khóa học |
| `providers` | Vertex | 8 | Nhà cung cấp |
| `has_skill` | Edge | 274 | User → Skill |
| `targets_career` | Edge | 40 | User → Career |
| `requires_skill` | Edge | 312 | Career → Skill |
| `prerequisite` | Edge | 173 | Skill → Skill nền |
| `teaches` | Edge | 172 | Course → Skill |
| `completed` | Edge | 110 | User → Course |
| `offered_by` | Edge | 89 | Course → Provider |

**Quy ước chiều cạnh quan trọng nhất:**

```
prerequisite:  _from = kỹ năng MUỐN HỌC   →  _to = kỹ năng CẦN CÓ TRƯỚC
               skills/pandas → skills/python
               (muốn học Pandas thì phải có Python)
```

Đọc nhầm chiều là sai toàn bộ lộ trình học. Đây là lỗi phổ biến nhất khi
làm đề tài này.

---

## 6. Ba chế độ dữ liệu

| `SKILLGRAPH_DATA_MODE` | Hành vi |
|---|---|
| `jsonl` (mặc định khi test) | Chỉ đọc file, không cần DB |
| `auto` (mặc định) | Thử ArangoDB trước, lỗi thì tự rơi về JSONL |
| `arango` | Bắt buộc ArangoDB, không kết nối được là báo lỗi ngay |

---

## 7. Biến môi trường

| Biến | Mặc định | Ý nghĩa |
|---|---|---|
| `SKILLGRAPH_DATA_MODE` | `auto` | `auto` / `jsonl` / `arango` |
| `SKILLGRAPH_DATA_DIR` | `../data` | Thư mục chứa JSONL |
| `ARANGO_HOST` | `http://127.0.0.1:8529` | Địa chỉ ArangoDB |
| `ARANGO_USER` | `root` | Tài khoản |
| `ARANGO_PASSWORD` | *(rỗng)* | Mật khẩu — **không commit vào git** |
| `ARANGO_DATABASE` | `skill_graph_db` | Tên database |
| `SKILLGRAPH_CORS_ORIGINS` | `localhost:5173,...` | Nguồn frontend được phép |

---

## 8. Ghi chú trung thực

- Mật khẩu ArangoDB **không** nằm trong code; phải truyền qua biến môi trường.
- Backend hiện **chỉ đọc** dữ liệu. Phần CRUD được thực hiện bằng AQL
  (A8–A10) hoặc trên ArangoDB Web Interface, đúng yêu cầu "quản trị dữ liệu
  trên ArangoDB Web Interface" của đề tài.
- Dữ liệu là **synthetic demo** (`data_origin: synthetic_demo`) phục vụ đồ án,
  không phải dữ liệu người thật.
- `direct_topic`/`importance` chỉ thể hiện mức liên quan của kỹ năng với nghề,
  **không** hàm ý đã đáp ứng hay được duyệt.
