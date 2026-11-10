# Skill Graph — Hệ thống đề xuất lộ trình học cá nhân hóa (ArangoDB)

Đồ án nhóm: dùng **ArangoDB** (Document + Graph) để biểu diễn quan hệ giữa
**User – Skill – Career – Course**, từ đó phân tích **Skill Gap**, tìm
**kỹ năng tiên quyết nhiều tầng**, gợi ý **khóa học** và sinh **lộ trình học
cá nhân hóa** cho từng người dùng.

> **Repo này chỉ chứa code + dữ liệu.**
> Báo cáo, slide, tài liệu giải thích và ảnh chụp được **gửi riêng** cho
> thành viên nhóm (file `TAI_LIEU_SKILLGRAPH.zip`), không đặt trong repo.

```
skillgraph/
├── backend/                 API Python (FastAPI) + toàn bộ nghiệp vụ
│   ├── app/                 mã nguồn
│   ├── scripts/             extract_dump.py, smoke_test.py, test_compat.py
│   └── requirements.txt
├── data/                    12 collection dạng JSONL (trích từ dump thật)
├── arangodb-dump/           ★ Dump gốc ArangoDB (43 KB) để arangorestore
├── queries/aql_queries.aql  Bộ truy vấn AQL để dán vào ArangoDB Web UI
├── frontend-bridge/         File cầu nối nối backend với frontend React
├── docker-compose.yml       Dựng ArangoDB bằng Docker (tuỳ chọn)
├── CHAY_NGAY.bat            ★ Bấm đúp để chạy (Windows)
└── CHAY_NGAY.sh             ★ Chạy trên macOS / Linux
```

**Công nghệ:** Python 3.10+ · FastAPI · Pydantic v2 · ArangoDB 3.11+ (AQL) · HTML/SVG thuần

**Giấy phép:** [MIT](LICENSE)

---

## ⚡ Chạy ngay trong 1 bước (dành cho cả nhóm)

Không cần biết gì về lập trình. Chỉ cần **bấm đúp 1 file**.

### Windows

1. Tải repo về: bấm nút xanh **`Code`** → **`Download ZIP`** → giải nén.
2. Vào thư mục vừa giải nén, **bấm đúp vào `CHAY_NGAY.bat`**.
3. Đợi khoảng 10–30 giây (lần đầu lâu hơn vì phải cài thư viện).
4. Trình duyệt **tự mở** giao diện. Xong.

### macOS / Linux

```bash
bash CHAY_NGAY.sh
```

### Script tự làm gì?

| Bước | Việc làm | Nếu thiếu thì sao |
|---|---|---|
| 1 | Tìm Python trên máy | In hướng dẫn cài kèm link tải |
| 2 | Kiểm tra `fastapi`, `uvicorn`, `pydantic` | **Tự cài** (1–2 phút), báo lỗi rõ nếu không có mạng |
| 3 | Kiểm tra 12 file dữ liệu | Báo thiếu file nào, nhắc tải lại đủ bộ |
| 4 | Khởi động server + **tự mở trình duyệt** | — |

Script **không cài gì vào hệ thống ngoài thư viện Python**, không sửa file,
không cần quyền admin.

### Nếu bị lỗi

| Hiện tượng | Cách sửa |
|---|---|
| "KHONG TIM THAY PYTHON" | Cài Python 3.11+ từ <https://www.python.org/downloads/>. **Nhớ tích `Add python.exe to PATH`** khi cài |
| "CAI THU VIEN THAT BAI" | Không có mạng, hoặc mạng công ty chặn `pip`. Thử phát 4G từ điện thoại |
| Cửa sổ đen hiện rồi tắt ngay | Chuột phải `CHAY_NGAY.bat` → **Run as administrator** |
| Trình duyệt không tự mở | Tự mở <http://127.0.0.1:8000/demo> |
| "Port 8000 đang bận" | Đã có chương trình khác dùng cổng 8000. Tắt nó, hoặc xem mục 6 bên dưới |

### Địa chỉ sau khi chạy

| Địa chỉ | Dùng để |
|---|---|
| <http://127.0.0.1:8000/demo> | **Giao diện 4 tab** — dùng để demo trước lớp |
| <http://127.0.0.1:8000/docs> | Tài liệu API, bấm thử trực tiếp được |
| <http://127.0.0.1:8000/api/v1/meta/health> | Kiểm tra hệ thống còn sống |

> **Tắt hệ thống:** đóng cửa sổ đen, hoặc bấm `Ctrl+C` trong đó.

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

### 2.2 Nạp dữ liệu vào ArangoDB

**Dump đã có sẵn trong repo**, không phải xin ai:

```
arangodb-dump/skill_graph_db_dump/     ← 26 file, 43 KB, 1.584 bản ghi
```

Cách chuẩn là `arangorestore` — **đừng** dùng nút *Import JSON* trên ArangoDB
Web Interface, vì nó chỉ tạo document và **mất toàn bộ edge** → đồ thị vô dụng.

```powershell
# 1. Tạo database đích
docker exec -it arangodb arangosh `
  --server.username root --server.password "" `
  --javascript.execute-string "db._createDatabase('skill_graph_db')"

# 2. Chép dump vào container
docker cp .\arangodb-dump\skill_graph_db_dump arangodb:/tmp/dump

# 3. Khôi phục
docker exec arangodb arangorestore `
  --server.endpoint tcp://127.0.0.1:8529 `
  --server.database skill_graph_db `
  --server.username root `
  --server.password "mat_khau_cua_ban" `
  --input-directory /tmp/dump `
  --include-system-collections false `
  --overwrite true
```

Nếu **không** dùng Docker, đổi `docker exec arangodb` thành gọi trực tiếp
`arangorestore` nếu máy đã cài ArangoDB.

Kiểm tra khôi phục thành công — phải ra **1.584**:

```powershell
docker exec arangodb arangosh `
  --server.username root --server.password "mat_khau_cua_ban" `
  --server.database skill_graph_db `
  --javascript.execute-string "print(db._collections().length, db.skills.count())"
# mong đợi: 12 248
```

**Số bản ghi từng collection** (đã đối chiếu khớp với `data/*.jsonl`):

| Collection | Bản ghi | | Collection | Bản ghi |
|---|---|---|---|---|
| `users` | 40 | | `has_skill` | 274 |
| `skills` | 248 | | `targets_career` | 40 |
| `careers` | 29 | | `requires_skill` | 312 |
| `courses` | 89 | | `prerequisite` | 173 |
| `providers` | 8 | | `teaches` | 172 |
| | | | `completed` | 110 |
| | | | `offered_by` | 89 |

> Dump không chứa mật khẩu hay dữ liệu nhạy cảm (`ENCRYPTION` ghi `none`).

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

## 8. Nối với Frontend React (gói bàn giao)

Backend có sẵn một **lớp tương thích** phục vụ đúng hợp đồng API mà frontend
React trong `NoSQL_Do_An-main` mong đợi — **không phải sửa frontend gốc**.

| Thành phần | Vị trí | Vai trò |
|---|---|---|
| Lớp dịch lược đồ | `backend/app/data/compat.py` | Chuyển document thô sang hình dạng frontend cần |
| Router tương thích | `backend/app/routers/compat.py` | 20 endpoint dưới `/compat/api/v1` |
| Cầu nối TypeScript | `frontend-bridge/catalogRepositoryApi.ts` | Cài đặt thật của `CatalogRepository`, gọi HTTP |
| Kiểm thử | `backend/scripts/test_compat.py` | 21 điểm kiểm thử (chạy khi backend đã bật) |

### Chạy thử

```powershell
# Cửa sổ 1 — backend
cd backend
python run.py

# Cửa sổ 2 — kiểm tra lớp tương thích
python scripts\test_compat.py     # mong đợi: 21 đạt / 0 hỏng
```

### Nối frontend (chỉ sửa 1 dòng)

1. Chép `frontend-bridge/catalogRepositoryApi.ts` vào
   `NoSQL_Do_An-main/src/repositories/`
2. Trong `src/repositories/catalogRepository.ts`, thêm import và đổi
   `new HttpCatalogRepository()` thành `new HttpCatalogRepositoryApi()`
3. Tạo `.env.local` ở thư mục gốc frontend (**không BOM**):

   ```
   VITE_DATA_SOURCE=api
   VITE_API_BASE_URL=http://127.0.0.1:8000/compat
   ```

4. `npm install` rồi `npm run dev`

**Cách nhận biết đã nối đúng:** 5 ô số liệu ở trang chủ hiện
**29 nghề / 248 kỹ năng / 89 học liệu / 0 nhóm ESCO / 8 nhà cung cấp**.
Nếu thấy 12 / 420 / 504 / 149 / 179 thì vẫn đang dùng dữ liệu local.

> Chi tiết đầy đủ (kể cả 7 lỗi đã gặp và cách sửa) nằm trong tài liệu
> `NOI_FRONTEND_VOI_BACKEND.md`, gửi riêng cho thành viên nhóm.

### Vì sao `/compat` mà không phải `/api/v1`

Vì cùng đường dẫn `/api/v1/careers` nhưng hai bên cần **hai hình dạng khác
nhau**: backend chính trả `{items, total}`, frontend cần mảng trần `Career[]`.
Tách tiền tố để cả hai cùng đúng mà không phá vỡ bên nào.

### Giới hạn phải nói thật

`skill_graph_db` **không có** `skill_groups` và 4 collection `esco_*`, nên
phần "Nhóm ESCO" và tab "ESCO Taxonomy" hiển thị rỗng. Đó là phản ánh trung
thực của bộ dữ liệu, **không phải lỗi**. Lớp tương thích trả mảng rỗng chứ
không bịa dữ liệu.

Ngoài ra `StatisticsDashboard.tsx` còn hardcode "5.718 tổng bản ghi" — sót lại
của bản v3.55, số đúng là **1.584**. Đây là chuỗi tĩnh trong frontend gốc,
không phải dữ liệu lấy từ backend.

---

## 9. Ghi chú trung thực

- Mật khẩu ArangoDB **không** nằm trong code; phải truyền qua biến môi trường.
- Backend hiện **chỉ đọc** dữ liệu. Phần CRUD được thực hiện bằng AQL
  (A8–A10) hoặc trên ArangoDB Web Interface, đúng yêu cầu "quản trị dữ liệu
  trên ArangoDB Web Interface" của đề tài.
- Dữ liệu là **synthetic demo** (`data_origin: synthetic_demo`) phục vụ đồ án,
  không phải dữ liệu người thật.
- `direct_topic`/`importance` chỉ thể hiện mức liên quan của kỹ năng với nghề,
  **không** hàm ý đã đáp ứng hay được duyệt.
