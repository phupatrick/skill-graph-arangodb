# Hướng dẫn chi tiết cho người mới — Đồ án Skill Graph

> Tài liệu này giải thích **từng bước, không giả sử bạn biết gì trước**.
> Đọc từ đầu tới cuối là hiểu được: hệ thống làm gì, dữ liệu ntn, code chạy
> thế nào, cách demo trước lớp.

---

## 1. Đề tài yêu cầu gì?

> *"Hệ thống Skill Graph và đề xuất lộ trình học cá nhân hóa"*

Nói đơn giản: một ứng dụng giúp người học trả lời câu hỏi

> *"Tôi muốn trở thành Data Analyst. Tôi đã biết gì, còn thiếu gì,
> nên học gì trước, học khóa nào?"*

Điểm đặc biệt: dữ liệu được lưu trong **ArangoDB** — một loại database
**đa mô hình**, vừa lưu document (như MongoDB) vừa lưu **đồ thị** (như
Neo4j). Đề tài chọn ArangoDB vì quan hệ giữa User–Skill–Career–Course là
**đồ thị**, và truy vấn "tìm toàn bộ kỹ năng nền" bằng **graph traversal**
rất tự nhiên.

### 1.1. Bốn đối tượng chính

| Đối tượng | Nghĩa là gì | Ví dụ |
|---|---|---|
| **User** | Người học | `user_001` — Tran Minh |
| **Skill** | Một kỹ năng | `python`, `sql`, `pandas` |
| **Career** | Một nghề nghiệp | `data_analyst` |
| **Course** | Một khóa học | `course_001` — SQL Fundamentals |

### 1.2. Sáu quan hệ (cạnh) — trái tim của đề tài

```
User ──HAS_SKILL──────> Skill      "Tôi biết Python, trình độ 45/100"
User ──TARGETS_CAREER─> Career     "Tôi muốn làm Data Analyst"
Career ──REQUIRES─────> Skill      "Data Analyst cần SQL, mức 70"
Skill ──PREREQUISITE──> Skill      "Muốn học Pandas phải biết Python trước"
Course ──TEACHES──────> Skill      "Khóa này dạy Python"
User ──COMPLETED──────> Course     "Tôi đã học xong khóa SQL Fundamentals"
```

> **Quy ước chiều cạnh PREREQUISITE (dễ nhầm nhất của đề tài):**
> `_from` = kỹ năng **muốn học**, `_to` = kỹ năng **cần có trước**.
> `skills/pandas → skills/python` nghĩa là *muốn học Pandas thì cần Python*.
> Đọc nhầm chiều là lộ trình học sẽ sai ngược hoàn toàn.

---

## 2. Dữ liệu thật của đề tài

Database `skill_graph_db`, 12 collection, **1.584 bản ghi**:

| Collection | Loại | Số bản ghi | Ý nghĩa |
|---|---|---|---|
| `users` | Vertex | 40 | Người học |
| `skills` | Vertex | 248 | Kỹ năng |
| `careers` | Vertex | 29 | Nghề nghiệp |
| `courses` | Vertex | 89 | Khóa học |
| `providers` | Vertex | 8 | Nhà cung cấp khóa học |
| `has_skill` | Edge | 274 | User → Skill |
| `targets_career` | Edge | 40 | User → Career |
| `requires_skill` | Edge | 312 | Career → Skill |
| `prerequisite` | Edge | 173 | Skill → Skill nền |
| `teaches` | Edge | 172 | Course → Skill |
| `completed` | Edge | 110 | User → Course |
| `offered_by` | Edge | 89 | Course → Provider |

Dữ liệu là **synthetic demo** (`data_origin: synthetic_demo`) — tạo riêng cho
đồ án, không phải dữ liệu người thật.

---

## 3. Backend làm gì? (giải thích từng file)

Backend là **API HTTP** viết bằng Python (FastAPI). Frontend không kết nối
ArangoDB trực tiếp — mọi truy vấn đi qua backend, đúng yêu cầu bảo mật của
đề tài ("không để trình duyệt kết nối trực tiếp vào database").

```
Trình duyệt (React)
      │  HTTP JSON
      ▼
Backend FastAPI  ──── AQL ────>  ArangoDB (skill_graph_db)
      │
      └── nếu không có ArangoDB: đọc file JSONL (dữ liệu thật đã trích)
```

### 3.1. Cấu trúc thư mục

```
backend/
├── app/
│   ├── main.py          Khởi động FastAPI, đăng ký router, CORS
│   ├── config.py        Đọc biến môi trường (host DB, mật khẩu, chế độ dữ liệu)
│   ├── schema.py        Tên 12 collection, quy ước chiều cạnh, giới hạn limit
│   ├── errors.py        Định dạng lỗi thống nhất { "error": { code, message } }
│   ├── models.py        Model Pydantic — "hợp đồng" JSON trả về cho frontend
│   ├── mappers.py       Chuyển document ArangoDB → JSON camelCase
│   ├── deps.py          Tạo một instance CatalogCore dùng chung
│   ├── data/
│   │   ├── storage.py   Hai cách đọc dữ liệu: JSONL hoặc ArangoDB
│   │   └── core.py      ★ NGHIỆP VỤ: Skill Gap, prerequisite, learning path
│   └── routers/         Định nghĩa URL cho từng nhóm
│       ├── meta.py      /api/v1/meta/health, /release
│       ├── users.py     /api/v1/users/...
│       ├── skills.py    /api/v1/skills/...
│       ├── careers.py   /api/v1/careers/...
│       ├── courses.py   /api/v1/courses/..., /api/v1/providers/...
│       └── analysis.py  /api/v1/users/{u}/skill-gap, /learning-path, ...
├── data/                12 file .jsonl (trích từ dump thật)
├── scripts/
│   ├── extract_dump.py  Trích dump ArangoDB → JSONL
│   └── smoke_test.py    Kiểm tra 42 điểm của toàn bộ API
└── requirements.txt
```

### 3.2. Kiến trúc "repository" — vì sao có hai cách đọc dữ liệu?

`core.py` (nghiệp vụ) **không biết** dữ liệu đến từ đâu. Nó chỉ gọi 4 hàm:

```python
storage.vertices("skills")          # mọi kỹ năng
storage.vertex("skills", "python")  # 1 kỹ năng
storage.edges("teaches", to_id=...) # các cạnh teaches trỏ vào kỹ năng
storage.counts()                    # số bản ghi từng collection
```

Có 2 lớp cài đặt 4 hàm đó:

| Lớp | Đọc từ đâu | Khi nào dùng |
|---|---|---|
| `JsonlStorage` | 12 file `.jsonl` | Demo không cần cài DB, chạy test |
| `ArangoStorage` | ArangoDB qua HTTP + AQL | Khi nhóm đã restore dump |

Lợi ích: **nghiệp vụ viết một lần**, chạy được cả khi có DB lẫn không có DB.
Đây là mẫu thiết kế *Repository Pattern* — tách "lấy dữ liệu" khỏi "xử lý dữ liệu".

### 3.3. Nghiệp vụ chính — `core.py` giải thích từng hàm

#### `skill_gap(user, career)` — Phân tích Skill Gap

```
Bước 1: Lấy danh sách kỹ năng nghề yêu cầu  (cạnh requires_skill)
Bước 2: Lấy trình độ hiện tại của user      (cạnh has_skill)
Bước 3: So từng cặp:
        chưa có kỹ năng        → status = "missing",     gap = required_level
        có nhưng dưới mức      → status = "below_level", gap = required - current
        đủ                     → status = "ok",          gap = 0
Bước 4: Tính coveragePct = số "ok" / tổng yêu cầu × 100
```

Ví dụ thật (user_001, Data Analyst): 11 yêu cầu → 3 đạt, 4 dưới mức,
4 thiếu hẳn → coverage **27.3%**.

#### `prerequisite_closure(skill)` — Duyệt kỹ năng nền nhiều tầng

```
BFS từ kỹ năng gốc, đi ngược cạnh prerequisite:
  deep_learning → tầng 1: machine_learning, linear_algebra, probability
                → tầng 2: statistics, python (nền của machine_learning)
Dùng tập "visited" để tránh lặp vô hạn nếu dữ liệu có chu trình.
```

Đây chính là **Graph Traversal** mà đề tài yêu cầu — một câu AQL
(`FOR v, e, p IN 1..5 INBOUND s prerequisite`) thay cho N vòng lặp SQL.

#### `career_match(user)` — Điểm phù hợp từng nghề

```
Với mỗi nghề:
  điểm = Σ importance của kỹ năng user ĐẠT / Σ importance toàn bộ yêu cầu × 100
Sắp xếp giảm dần → "nghề nào bạn gần nhất".
```

#### `learning_path(user, career)` — Sinh lộ trình học

```
Bước 1: Chạy skill_gap → lấy các kỹ năng còn thiếu / dưới mức
Bước 2: Với mỗi kỹ năng, leo ngược prerequisite để tìm kỹ năng nền
        cũng còn thiếu → thêm vào danh sách
Bước 3: Sắp xếp TOPOLOGICAL (thuật toán Kahn):
        kỹ năng nền đứng trước kỹ năng phụ thuộc nó
        hoà nhau thì ưu tiên essential + importance cao
Bước 4: Với mỗi bước, tìm khóa học dạy kỹ năng đó (cạnh teaches),
        LOẠI khóa user đã hoàn thành (cạnh completed)
```

Kết quả thật cho user_001 → Data Analyst:

```
1. SQL                          (thiếu hẳn)
2. Python                       (thiếu hẳn)
3. Pandas                       (thiếu hẳn — cần Python trước ✓)
4. Exploratory Data Analysis    (35 → cần 70)
5. Data Visualization           (thiếu hẳn)
6. Power BI                     (45 → cần 70)
7. Tableau                      (45 → cần 55)
8. Data Cleaning                (45 → cần 55)
```

Pandas đứng **sau** Python vì Pandas phụ thuộc Python — đúng logic học.

---

## 4. Chạy hệ thống từng bước

### 4.1. Cài Python package

```powershell
cd skillgraph\backend
pip install -r requirements.txt
```

### 4.2. Chạy backend (không cần ArangoDB)

```powershell
python run.py
```

Mở <http://127.0.0.1:8000/docs> — đây là **Swagger UI** tự sinh từ code,
bấm thử được từng API ngay trong trình duyệt.

### 4.3. Kiểm tra 42 điểm tự động

```powershell
python scripts\smoke_test.py
```

Kỳ vọng: `PASSED: 42  FAILED: 0`.

### 4.4. Chạy với ArangoDB thật (khi máy có Docker)

```powershell
cd skillgraph
docker compose up -d arangodb          # dựng ArangoDB 3.12
# restore dump (xem README mục 2.2)
cd backend
$env:ARANGO_PASSWORD = "matkhau_doi_di"
$env:SKILLGRAPH_DATA_MODE = "arango"
python run.py
```

Kiểm tra `dataMode` đã chuyển sang `arango`:

```
http://127.0.0.1:8000/api/v1/meta/health
→ {"status":"ok","dataMode":"arango","arango":{"connected":true,...}}
```

---

## 5. Demo trước lớp — kịch bản 10 phút

1. **Mở ArangoDB Web Interface** → database `skill_graph_db` → tab *Collections*
   → chỉ 12 collection + graph `skill_graph`. Chụp ảnh.
2. **Chạy AQL B13** (thống kê) → 1.584 bản ghi. Chụp ảnh.
3. **Chạy AQL B3** (prerequisite deep_learning) → cho thấy traversal nhiều tầng.
4. **Mở Swagger** <http://127.0.0.1:8000/docs> → chạy
   `GET /api/v1/users/user_001/skill-gap` → giải thích 3 trạng thái
   missing / below_level / ok.
5. **Chạy `GET /api/v1/users/user_001/learning-path`** → nhấn mạnh:
   - Pandas đứng sau Python (prerequisite),
   - khóa đã học không bị đề xuất lại,
   - mỗi bước có khóa học gợi ý.
6. **Chạy `GET /api/v1/users/user_001/career-match`** → Data Analyst 24.9% đứng đầu.
7. **Mở `/api/v1/graph/neighborhood?focusId=careers/data_analyst`** → dữ liệu
   cho trang Skill Graph (nodes + edges, giữ nguyên chiều `_from → _to`).

---

## 6. Câu hỏi thường gặp khi bảo vệ

**Q: Vì sao chọn ArangoDB mà không dùng MySQL?**
A: Quan hệ giữa Skill–Skill (prerequisite) là **đồ thị nhiều tầng**. Trong SQL,
tìm "toàn bộ kỹ năng nền của Deep Learning" cần recursive CTE lồng nhau; trong
ArangoDB là **một câu traversal** `1..5 INBOUND`, đọc được ngay ý nghĩa.
Ngoài ra ArangoDB vừa làm document vừa làm graph trong **một engine, một AQL**.

**Q: Skill Gap tính thế nào?**
A: So từng cặp (requires_skill ↔ has_skill) theo `required_level` và
`proficiency` trên cùng thang 0–100. Thiếu hẳn = `missing`, có nhưng dưới mức
= `below_level`. Không tự suy diễn "đã đủ" khi thiếu dữ liệu.

**Q: Lộ trình học đảm bảo đúng thứ tự thế nào?**
A: Thuật toán **topological sort (Kahn)** trên đồ thị con prerequisite:
kỹ năng nền luôn đứng trước kỹ năng phụ thuộc. Nếu dữ liệu có chu trình
(A cần B, B cần A), phần còn lại vẫn được xuất ra cuối và ghi chú rõ.

**Q: Sao không cho frontend nối thẳng ArangoDB?**
A: Ba lý do: (1) lộ mật khẩu DB ra trình duyệt; (2) không kiểm soát được
truy vấn ai đó gửi; (3) không test được logic nghiệp vụ. Backend là lớp
**kiểm soát truy cập + nghiệp vụ**.

**Q: Dữ liệu thật hay giả?**
A: `data_origin: synthetic_demo` — dữ liệu mẫu tạo cho đồ án, đủ lớn để demo
(1.584 bản ghi, 173 cạnh prerequisite, 40 người dùng) nhưng không phải người thật.

**Q: `direct_topic` / `importance` nghĩa là gì?**
A: Chỉ là **mức liên quan chủ đề** giữa kỹ năng và nghề. KHÔNG hàm ý người học
đã đáp ứng, đã được duyệt, hay khóa học miễn phí. Hệ thống không tự động
"phê duyệt" anything — chỉ đề xuất dựa trên dữ liệu.

---

## 7. Việc còn tồn đọng (nói thật với nhóm)

- [ ] **Restore dump vào ArangoDB thật** — cần máy có Docker. Backend đã sẵn
      chế độ `arango`, chỉ cần đặt `ARANGO_PASSWORD` và chạy.
- [ ] **Frontend gọi API** — hiện frontend dùng mock v3.49; cần chuyển sang
      `VITE_DATA_SOURCE=api` + `VITE_API_BASE_URL=http://127.0.0.1:8000`.
- [ ] **CRUD ghi dữ liệu** — hiện backend chỉ đọc; CRUD thực hiện bằng AQL
      (A8–A10) hoặc trên Web Interface, đúng yêu cầu "quản trị dữ liệu trên
      ArangoDB Web Interface".
- [ ] **Sửa lỗi hiển thị tiếng Việt (mojibake)** trong một số file frontend
      (`App.tsx`, `teaches.jsonl`) — ký tự bị mã hóa kép, cần script sửa.
- [ ] **Báo cáo + slide** — chưa viết.
