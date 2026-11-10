# Nối Backend Python với Frontend React — Hướng dẫn đầy đủ

> Tài liệu này giải thích **từ đầu** cách nối backend FastAPI của đồ án với
> bộ frontend React có sẵn trong gói bàn giao, và **không sửa một dòng nào**
> trong thư mục frontend gốc.

---

## 1. Vấn đề cần giải (đọc mục này trước)

Có **4 rào cản** khiến việc "chỉ chạy hai thứ cạnh nhau" không đủ. Hiểu 4 rào
cản này là hiểu toàn bộ việc tôi đã làm.

### Rào cản 1 — Frontend không có code gọi API

Trong `src/repositories/catalogRepository.ts` có lớp tên là
`HttpCatalogRepository`, nghe như đã sẵn sàng gọi API. Nhưng **mọi method đều
gọi `this.no()`**, và `no()` chỉ ném lỗi:

```ts
private no(): never { throw new Error('API mode chưa có backend production') }
```

Nghĩa là: đặt biến môi trường `VITE_DATA_SOURCE=api` thì frontend sẽ **văng
lỗi ngay**, vì chưa có một dòng code nào thực sự gọi HTTP. Đây là "client dự
phòng" — khung xương rỗng, chờ người làm backend viết phần thân.

### Rào cản 2 — Hai bên dùng tên trường khác nhau

| Khái niệm | `skill_graph_db` (backend) | `catalog-v355` (frontend) |
|---|---|---|
| Mã nghề | `_key` = `data_analyst` | `_key` = `occ_81ee81619c41c8e73c20e7` |
| Mô tả nghề | `description` | `description` |
| Nhóm nghề | `category` | `career_group` |
| Kỹ năng loại gì | `category` | `skill_type` |
| Khoá học URL | `url` | `canonical_url` |
| Yêu cầu kỹ năng | `importance` (điểm quan trọng) | `requirement_type` (essential/optional) |

Không thể trả document thô. Phải có một lớp **dịch** (adapter).

### Rào cản 3 — Cùng đường dẫn, hai hình dạng khác nhau

Đây là rào cản khó nhất, và cũng là chỗ dễ hỏng nhất:

```
GET /api/v1/careers
```

- **Backend chính** trả về: `{ "items": [...], "total": 29 }`
- **Frontend cần**: `[ {...}, {...} ]` — mảng trần, không bọc

Không thể để cả hai cùng tồn tại trên một đường dẫn: FastAPI chọn **route
khai báo trước** và bỏ qua route sau. Nếu ta đăng ký lớp tương thích sau thì
nó bị che hoàn toàn — đó chính là lỗi tôi gặp đầu tiên (xem mục 6).

Giải pháp: đặt toàn bộ lớp tương thích dưới **tiền tố riêng** `/compat`.

### Rào cản 4 — Interface đồng bộ nhưng HTTP bất đồng bộ

`CatalogRepository` khai báo:

```ts
getCareers(): Career[]        // trả về MẢNG, không phải Promise
```

Nhưng `fetch()` thì bất đồng bộ. Tệ hơn, `App.tsx` gọi ngay ở cấp module:

```ts
const repo = getCatalogRepository()   // chạy trước khi render
```

Nếu để bất đồng bộ, khung hình đầu tiên sẽ thấy mảng rỗng → giao diện trắng
và **không tự vẽ lại**. Đây là lỗi tôi gặp thứ hai.

Giải pháp: nạp dữ liệu bằng `XMLHttpRequest` **đồng bộ** một lần trong
constructor, rồi cache. Đánh đổi: khung hình đầu chậm thêm ~100–300 ms.

---

## 2. Kiến trúc lời giải

```
┌──────────────────────────┐
│  Frontend React (Vite)   │  cổng 5173 / 5174
│  NoSQL_Do_An-main        │  KHÔNG sửa (trừ 1 dòng import)
└───────────┬──────────────┘
            │ HTTP + CORS
            │ GET /compat/api/v1/careers
            ▼
┌──────────────────────────────────────────────┐
│  Backend FastAPI                             │  cổng 8000
│                                              │
│  app/routers/compat.py    ← lớp tương thích  │  /compat/api/v1/*
│  app/data/compat.py       ← dịch lược đồ     │
│         │                                    │
│         ▼                                    │
│  app/data/core.py         ← nghiệp vụ gốc    │
│  app/routers/careers.py   ← API gốc          │  /api/v1/*
│         │                                    │
│         ▼                                    │
│  skill_graph_db (12 collection, 1584 bản ghi)│
└──────────────────────────────────────────────┘
```

Điểm mấu chốt: **lớp tương thích là một lớp mới, nằm ngoài, không sửa
nghiệp vụ cũ.** Toàn bộ 42/42 điểm kiểm thử cũ vẫn chạy nguyên.

---

## 3. Ba file đã tạo

| File | Vai trò | Số dòng |
|---|---|---|
| `backend/app/data/compat.py` | Dịch document thô sang hình dạng frontend cần | ~430 |
| `backend/app/routers/compat.py` | 20 đường dẫn HTTP dưới `/compat/api/v1` | ~230 |
| `frontend-bridge/catalogRepositoryApi.ts` | Cài đặt thật của `CatalogRepository`, gọi API | ~440 |

Ngoài ra sửa **2 chỗ nhỏ** trong file có sẵn:

1. `backend/app/main.py` — thêm 1 dòng import + 1 dòng `include_router`
2. `backend/app/config.py` — thêm cổng 5174 vào danh sách CORS

---

## 4. Danh sách endpoint lớp tương thích

Tất cả nằm dưới `/compat/api/v1`.

| Đường dẫn | Trả về | Ghi chú |
|---|---|---|
| `/meta/release` | object | version, records, số bản ghi từng collection |
| `/careers` | **mảng** Career | 29 phần tử |
| `/careers/{key}` | object Career | 404 nếu không có |
| `/careers/{key}/skills` | `{items, total}` | kèm `resourceCount` |
| `/skills` | **mảng** Skill | hỗ trợ `?search=` |
| `/skills/{key}` | object Skill | |
| `/skills/{key}/resources` | `{items}` | khoá học + `evidence` |
| `/resources` | **mảng** Course | 89 phần tử |
| `/resources/{key}` | object Course | |
| `/resources/{key}/skills` | `{items}` | kỹ năng mà khoá dạy |
| `/providers` | **mảng** Provider | 8 phần tử |
| `/providers/{key}/resources` | `{items}` | |
| `/graph/neighborhood` | `{nodes, edges}` | `focusId`, `mode`, `nodeTypes`, `edgeTypes`, `limit` |
| `/statistics/coverage` | `{items, ...}` | độ phủ học liệu theo nghề |
| `/statistics/gaps` | `{items}` | kỹ năng bắt buộc chưa có khoá dạy |

### Vì sao `/compat` mà không phải `/api/v1`?

Vì đường dẫn `/api/v1/careers` đã bị backend chính chiếm, và hai bên trả
**hai hình dạng khác nhau cho cùng dữ liệu**. Tách tiền tố là cách duy nhất
để cả hai cùng đúng mà không phải phá vỡ bên nào.

Đổi lại, phía frontend phải đặt:

```
VITE_API_BASE_URL=http://127.0.0.1:8000/compat
```

(vì `HttpCatalogClient` tự nối thêm `/api/v1/...` vào sau base URL).

---

## 5. Cách chạy — từng bước

### Bước 1: Chạy backend

```powershell
cd skillgraph\backend
python run.py
```

Phải thấy:

```
[skillgraph] data_mode=jsonl records=1584
Uvicorn running on http://127.0.0.1:8000
```

Kiểm tra nhanh:

```powershell
curl http://127.0.0.1:8000/compat/api/v1/careers
```

### Bước 2: Cài file cầu nối vào frontend

Chép `skillgraph\frontend-bridge\catalogRepositoryApi.ts` vào
`NoSQL_Do_An-main\src\repositories\`.

### Bước 3: Sửa đúng một dòng

Mở `src/repositories/catalogRepository.ts`, dòng cuối. Thêm import và đổi tên
lớp:

```ts
// THÊM dòng này ở đầu file:
import { HttpCatalogRepositoryApi } from './catalogRepositoryApi';

// SỬA dòng cuối, đổi HttpCatalogRepository -> HttpCatalogRepositoryApi:
let repo: CatalogRepository;
export const getCatalogRepository = () =>
  repo || (repo = import.meta.env.VITE_DATA_SOURCE === 'api'
    ? new HttpCatalogRepositoryApi()
    : new LocalCatalogRepository());
```

### Bước 4: Tạo file `.env.local`

Ở thư mục gốc frontend (cùng cấp `package.json`):

```
VITE_DATA_SOURCE=api
VITE_API_BASE_URL=http://127.0.0.1:8000/compat
```

> **Lưu ý BOM:** nếu tạo file bằng PowerShell với `Set-Content -Encoding utf8`,
> file sẽ có BOM (`EF BB BF`) ở đầu và **Vite sẽ không đọc được biến đầu
> tiên**. Dùng `[System.IO.File]::WriteAllText($path, $text, (New-Object
> System.Text.UTF8Encoding $false))` hoặc tạo bằng trình soạn thảo.

### Bước 5: Cài và chạy frontend

```powershell
cd NoSQL_Do_An-main
npm install
npm run dev
```

Mở `http://127.0.0.1:5173`.

### Bước 6: Kiểm tra đã nối đúng

Nhìn 5 ô số liệu ở trang chủ:

| Ô | Nếu nối đúng | Nếu vẫn dùng dữ liệu local |
|---|---|---|
| Nghề nghiệp | **29** | 12 |
| Kỹ năng | **248** | 420 |
| Học liệu | **89** | 504 |
| Nhóm ESCO | **0** | 149 |
| Nhà cung cấp | **8** | 179 |

Thấy 29 / 248 / 89 / 0 / 8 là thành công.

---

## 6. Các lỗi tôi đã gặp và cách sửa (rất đáng đọc khi bảo vệ)

Đây là phần có giá trị nhất khi thầy cô hỏi "em gặp khó khăn gì".

### Lỗi 1 — Route bị route khác che

**Hiện tượng:** đăng ký lớp tương thích ở `/api/v1` thì gọi `/api/v1/careers`
nhận về `{items, total}` chứ không phải mảng. Frontend hiển thị sai.

**Nguyên nhân:** FastAPI duyệt danh sách route **theo thứ tự khai báo** và
dùng route **đầu tiên khớp**. Backend chính khai báo trước nên thắng.

**Cách phát hiện:** in danh sách route ra xem:

```python
for r in app.routes:
    print(getattr(r, 'path', ''), '->', getattr(r, 'name', ''))
```

Thấy `/api/v1/careers` xuất hiện **hai lần** với hai handler khác nhau.

**Cách sửa:** dùng tiền tố riêng `/compat/api/v1`. Không thể "ưu tiên route
sau" một cách sạch sẽ.

### Lỗi 2 — Truyền sai tham số cho hàm đồ thị

**Hiện tượng:** `/compat/api/v1/graph/neighborhood?focusId=careers/data_analyst`
trả 404 "Không tìm thấy career với id 'careers/data_analyst'".

**Nguyên nhân:** `core.graph_neighborhood(focus_key, mode)` nhận **key trần**
(`data_analyst`), không nhận id đầy đủ (`careers/data_analyst`). Tôi đã truyền
nguyên chuỗi `focusId` vào.

**Cách sửa:** tách theo dấu `/` trước khi gọi:

```python
collection, focus_key = focus_id.split("/", 1)
raw = self.core.graph_neighborhood(focus_key, expected_mode, ...)
```

### Lỗi 3 — Gọi sai chữ ký hàm

**Hiện tượng:** gọi nghề không tồn tại trả **500** thay vì **404**.

**Nguyên nhân:** hàm trong `errors.py` là `not_found(kind, identifier)` — hai
tham số. Tôi gọi `not_found(f"Không tìm thấy nghề: {career_id}")` — một tham
số, nên Python ném `TypeError`, và exception handler biến nó thành 500.

**Cách sửa:** `raise not_found("nghề", career_id)`.

**Bài học:** 500 là "lỗi lập trình", 404 là "không tìm thấy dữ liệu". Khi
thấy 500 ở một endpoint lẽ ra phải 404, gần như chắc chắn là gọi sai hàm.

### Lỗi 4 — File `.env.local` có BOM

**Hiện tượng:** đã tạo `.env.local` đúng nội dung mà frontend vẫn dùng dữ
liệu local (12 nghề).

**Nguyên nhân:** PowerShell `Set-Content -Encoding utf8` ghi thêm 3 byte BOM
`EF BB BF` ở đầu file. Vite đọc dòng đầu thành `\uFEFFVITE_DATA_SOURCE` —
tên biến sai nên không nhận.

**Cách phát hiện:**

```powershell
$bytes = [System.IO.File]::ReadAllBytes("$PWD\.env.local")
($bytes[0..5] | ForEach-Object { '{0:X2}' -f $_ }) -join ' '
# EF BB BF 56 49 54  =>  có BOM
```

**Cách sửa:** ghi không BOM:

```powershell
[System.IO.File]::WriteAllText($path, $text,
  (New-Object System.Text.UTF8Encoding $false))
```

### Lỗi 5 — CORS chặn cổng 5174

**Hiện tượng:** trang chủ hiện toàn số **0**, console báo:

```
Access to XMLHttpRequest at 'http://127.0.0.1:8000/compat/api/v1/meta/release'
from origin 'http://127.0.0.1:5174' has been blocked by CORS policy
```

**Nguyên nhân:** danh sách CORS của backend mặc định chỉ có 5173. Khi chạy
Vite ở cổng 5174 (vì 5173 đang bận), trình duyệt coi đó là **origin khác** và
chặn.

**Cách sửa:** thêm `http://127.0.0.1:5174` và `http://localhost:5174` vào
`SKILLGRAPH_CORS_ORIGINS` (tôi đã sửa sẵn trong `config.py`).

**Bài học:** CORS so sánh **cả cổng**, không chỉ host. `localhost:5173` và
`127.0.0.1:5173` cũng là hai origin khác nhau.

### Lỗi 6 — Trang Thống kê trắng vì `undefined.length`

**Hiện tượng:** `/statistics` trắng hoàn toàn. Console:

```
Uncaught TypeError: Cannot read properties of undefined (reading 'length')
at StatisticsDashboard.tsx:28
```

**Nguyên nhân:** trang này đọc thẳng 7 collection ESCO:

```ts
relations = ["requires_skill", "teaches", ..., "esco_skill_knowledge"]
  .map(name => ({ name, value: p.collections[name].length }))
```

`skill_graph_db` chỉ có 4 trong 7 collection đó. `getRaw()` của tôi trả
`undefined` cho 3 cái còn lại → `.length` ném lỗi → cả trang sập.

**Cách sửa:** luôn trả **đủ key**, collection không có thì trả mảng rỗng:

```ts
esco_skill_group: [] as any,
esco_skill_broader: [] as any,
esco_group_broader: [] as any,
esco_skill_knowledge: [] as any,
skill_groups: [] as any,
```

**Bài học:** đây là chỗ dễ "làm cho qua" bằng cách bịa số. Tôi chọn trả mảng
rỗng vì **đúng với sự thật dữ liệu** — `skill_graph_db` thật sự không có phân
loại ESCO. Giao diện hiện 0 là phản ánh trung thực.

### Lỗi 7 — Interface đồng bộ, HTTP bất đồng bộ

**Hiện tượng:** dùng `fetch()` (bất đồng bộ) thì trang chủ hiện toàn 0, dù
API trả đúng.

**Nguyên nhân:** `App.tsx` gọi `const repo = getCatalogRepository()` ở cấp
module, **trước** khi `fetch` kịp trả về. Repo trả mảng rỗng, và không có cơ
chế nào khiến React vẽ lại sau khi dữ liệu về.

**Cách sửa:** dùng `XMLHttpRequest` với `open(..., false)` (đồng bộ) trong
constructor, cache lại. Đánh đổi: khung hình đầu chậm ~100–300 ms.

**Cách sạch hơn (nếu được sửa `main.tsx`):**

```ts
await (repo as any).ready?.();
createRoot(document.getElementById('root')!).render(<App />);
```

---

## 7. Giới hạn — điều phải nói thật khi bảo vệ

Khi nối frontend vào `skill_graph_db`, **5 chỗ hiển thị 0 hoặc rỗng** và đó
là **đúng**. Phải nói rõ với thầy cô, đừng để bị hỏi mới trả lời.

| Chỗ hiển thị | Vì sao rỗng | Có nên lo? |
|---|---|---|
| Nhóm ESCO (trang chủ) | `skill_graph_db` không có collection `skill_groups` | Không — dữ liệu thật sự không có |
| Tab "ESCO Taxonomy" | Không có 4 collection `esco_*` | Không |
| Tổng bản ghi "5.718" | Con số **hardcode** trong `StatisticsDashboard.tsx:56` | Có — nên sửa thành 1.584 |
| Chân trang "Local v3.55 Adapter" | Chuỗi tĩnh trong `App.tsx` | Nhỏ |

Con số 5.718 là **sót lại của bản v3.55**, không phải dữ liệu backend. Hai
con số cạnh nó (152/189 và 37) thì **đã đúng** vì đọc từ `manifest` do
backend tính.

### Vì sao không dùng dữ liệu v3.55 cho tất cả?

Vì `catalog-v355` có:

- `prerequisite`: **0 cạnh** → không demo được prerequisite nhiều tầng
- `has_skill`: **0 cạnh** → không demo được Skill Gap
- `completed`: **0 cạnh** → không demo được lộ trình cá nhân hóa
- `targets_career`: **0 cạnh** → không demo được nghề mục tiêu

Còn `skill_graph_db` có 173 cạnh prerequisite, 274 cạnh has_skill, 110 cạnh
completed — **đủ cả 4 chức năng cốt lõi của đề tài**.

Đây là lý do chọn `skill_graph_db`, và là điều nên nói khi bảo vệ: *"em chọn
bộ dữ liệu có đủ cạnh đồ thị để chứng minh thuật toán, thay vì bộ có nhiều
bản ghi nhưng 0 cạnh."*

---

## 8. Vì sao không sửa frontend gốc

Anh yêu cầu rõ: *"Đảm bảo front end chưa sửa gì ở phần tôi gửi."*

Tôi đã xác minh bằng hai cách độc lập:

1. **Mốc thời gian:** cả 76 file đều giữ `2026-10-22 19:58:50`, **0 file** bị
   đổi.
2. **SHA-256:** lưu baseline từng file vào `docs/FRONTEND_GOC_SHA256.txt`.

Bản chạy thử nằm ở thư mục **riêng** `frontend-connected/` (bản sao), nên nếu
có hỏng cũng không ảnh hưởng bản gốc.

Câu trả lời khi bảo vệ: *"bản gốc em giữ nguyên làm mốc đối chiếu, bản nối
API là bản sao có thêm 1 file và sửa 1 dòng — để chứng minh thay đổi là tối
thiểu và có thể kiểm chứng."*

---

## 9. Kiểm thử tự động

Chạy 20 điểm kiểm thử lớp tương thích:

```powershell
cd skillgraph\backend
python scripts\test_compat.py
```

Kết quả mong đợi:

```
OK=20 BAD=0
```

Chạy 42 điểm kiểm thử nghiệp vụ gốc (phải vẫn xanh):

```powershell
python scripts\smoke_test.py
```

Kết quả mong đợi:

```
42/42 PASS
```

---

## 10. Tóm tắt một câu

> Backend thêm một **lớp tương thích** dưới tiền tố `/compat` để dịch
> `skill_graph_db` sang đúng hình dạng mà frontend React mong đợi; frontend
> chỉ cần **một file mới và một dòng sửa** là chạy được với dữ liệu thật,
> trong khi bản gốc và toàn bộ nghiệp vụ cũ giữ nguyên không đổi.
