# SkillGraph — Career & Learning Explorer

Frontend React 19 + TypeScript cho dữ liệu **Skill Graph v3.55 / Sprint 92 (TEAM PREVIEW)**.

## Chạy local

```bash
npm install
npm run data:generate
npm run dev
```

Build và kiểm thử:

```bash
npm run data:validate
npm test
npm run build
```

## Nguồn dữ liệu

`scripts/generate-catalog.mjs` đọc 24 JSONL trong `data-source-v355/SkillGraph_Team_Python_ArangoDB_Import_v355/release`, tạo projection UI tại `src/data/generated/catalog-v355.json` và metadata audit đầy đủ tại `public/data/catalog-audit-v355.json`. Script không sửa JSONL nguồn; `_key`, `_from`, `_to`, null và metadata gốc vẫn được bảo toàn trong đầu ra tương ứng.

Mặc định `VITE_DATA_SOURCE=local`. Chế độ `api` được dành cho Python REST API tương lai; ZIP không chứa API production và frontend không kết nối trực tiếp ArangoDB.

## Phân biệt dữ liệu

- Catalog, taxonomy, graph, coverage và data quality dùng dữ liệu v3.55.
- Career Goal, My Skills, Skill Gap, Learning Path và My Learning là **MÔ PHỎNG**, lưu localStorage.
- `direct_topic` chỉ là liên quan chủ đề; không chứng minh thành thạo hay khuyến nghị được phê duyệt.
- Không có prerequisite edge và không có thuật toán cá nhân hóa chính thức.
- Validation là offline; database live chưa được xác minh trong frontend.

Xem thêm [Data version](docs/DATA_VERSION.md) và [API contract đề xuất](docs/PROPOSED_API_CONTRACT.md).
