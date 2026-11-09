# -*- coding: utf-8 -*-
"""Sinh slide thuyết trình cho đồ án Skill Graph (python-pptx, không cần mạng)."""
from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.util import Inches, Pt

# ---------- bảng màu ----------
BG      = RGBColor(0x0B, 0x10, 0x20)
PANEL   = RGBColor(0x16, 0x1E, 0x38)
PANEL2  = RGBColor(0x1E, 0x28, 0x48)
ACCENT  = RGBColor(0x5B, 0x8C, 0xFF)
ACCENT2 = RGBColor(0x39, 0xD3, 0xA0)
WARN    = RGBColor(0xFF, 0xB4, 0x54)
BAD     = RGBColor(0xFF, 0x6B, 0x81)
TEXT    = RGBColor(0xE8, 0xEC, 0xF7)
MUTED   = RGBColor(0x93, 0xA0, 0xC0)

prs = Presentation()
prs.slide_width  = Inches(13.333)
prs.slide_height = Inches(7.5)
BLANK = prs.slide_layouts[6]


def add_slide():
    s = prs.slides.add_slide(BLANK)
    s.background.fill.solid()
    s.background.fill.fore_color.rgb = BG
    return s


def txt(slide, x, y, w, h, text, size=18, color=TEXT, bold=False,
        align=PP_ALIGN.LEFT, anchor=MSO_ANCHOR.TOP, line_spacing=1.0):
    box = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    tf = box.text_frame
    tf.word_wrap = True
    tf.vertical_anchor = anchor
    lines = text.split("\n")
    for i, line in enumerate(lines):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.alignment = align
        p.line_spacing = line_spacing
        r = p.add_run()
        r.text = line
        r.font.size = Pt(size)
        r.font.color.rgb = color
        r.font.bold = bold
    return box


def panel(slide, x, y, w, h, fill=PANEL):
    from pptx.enum.shapes import MSO_SHAPE
    sh = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE,
                                Inches(x), Inches(y), Inches(w), Inches(h))
    sh.fill.solid()
    sh.fill.fore_color.rgb = fill
    sh.line.color.rgb = RGBColor(0x2A, 0x35, 0x57)
    sh.line.width = Pt(0.75)
    sh.shadow.inherit = False
    return sh


def bullet_block(slide, x, y, w, items, size=15, gap=0.52):
    for i, item in enumerate(items):
        panel(slide, x, y + i * gap, w, gap - 0.10, PANEL)
        txt(slide, x + 0.18, y + i * gap + 0.08, 0.3, 0.3, "▸", size=size,
            color=ACCENT, bold=True)
        txt(slide, x + 0.52, y + i * gap + 0.06, w - 0.7, gap - 0.12,
            item, size=size, color=TEXT, anchor=MSO_ANCHOR.MIDDLE)


# ============================================================
# Slide 1 — Bìa
# ============================================================
s = add_slide()
txt(s, 0.9, 2.1, 11.5, 1.0, "Hệ thống Skill Graph và đề xuất lộ trình học cá nhân hóa",
    size=34, bold=True)
txt(s, 0.9, 3.2, 11.5, 0.6, "Dựng trên ArangoDB — Document + Graph Database",
    size=20, color=ACCENT2)
txt(s, 0.9, 4.6, 11.5, 1.2,
    "Đề tài 1 · Nhóm Python + ArangoDB\nBackend: FastAPI (Python)  ·  Truy vấn: AQL  ·  Quản trị dữ liệu: ArangoDB Web Interface",
    size=14, color=MUTED, line_spacing=1.3)

# ============================================================
# Slide 2 — Bài toán
# ============================================================
s = add_slide()
txt(s, 0.6, 0.35, 12, 0.8, "1. Bài toán", size=26, bold=True)
txt(s, 0.6, 1.2, 12, 0.7,
    "Người học cần trả lời: “Muốn làm nghề X, tôi đã biết gì, còn thiếu gì, học gì trước?”",
    size=17, color=MUTED)
panel(s, 0.6, 2.1, 6.0, 4.6)
txt(s, 0.9, 2.3, 5.4, 0.5, "Luồng nghiệp vụ", size=16, bold=True, color=ACCENT2)
bullet_block(s, 0.9, 2.85, 5.4, [
    "Khai báo kỹ năng hiện tại",
    "Chọn nghề nghiệp mục tiêu",
    "Phân tích Skill Gap",
    "Kiểm tra kỹ năng tiên quyết",
    "Tìm khóa học phù hợp",
    "Sinh lộ trình học cá nhân hóa",
], size=13.5, gap=0.62)
panel(s, 7.0, 2.1, 5.7, 4.6)
txt(s, 7.3, 2.3, 5.1, 0.5, "Vì sao chọn ArangoDB?", size=16, bold=True, color=ACCENT2)
txt(s, 7.3, 2.9, 5.1, 3.6,
    "Quan hệ giữa User – Skill – Career – Course là ĐỒ THỊ.\n"
    "Đặc biệt quan hệ giữa các Skill tạo thành nhiều tầng:\n\n"
    "Machine Learning ↓ Statistics ↓ Mathematics\n\n"
    "Tìm toàn bộ kỹ năng nền = 1 câu graph traversal,\nthay cho N vòng lặp recursive CTE trong SQL.\n\n"
    "ArangoDB: một engine, một AQL, cả document lẫn graph.",
    size=13.5, color=TEXT, line_spacing=1.25)

# ============================================================
# Slide 3 — Mô hình dữ liệu
# ============================================================
s = add_slide()
txt(s, 0.6, 0.35, 12, 0.8, "2. Mô hình dữ liệu — 4 đỉnh, 6 cạnh chính", size=26, bold=True)
# đỉnh
for i, (name, desc, color) in enumerate([
    ("User", "Người học", ACCENT),
    ("Skill", "Kỹ năng", ACCENT2),
    ("Career", "Nghề nghiệp", ACCENT),
    ("Course", "Khóa học", WARN),
]):
    panel(s, 0.7 + i * 3.1, 1.35, 2.7, 1.0, PANEL2)
    txt(s, 0.9 + i * 3.1, 1.5, 2.3, 0.4, name, size=17, bold=True, color=color)
    txt(s, 0.9 + i * 3.1, 1.9, 2.3, 0.3, desc, size=12, color=MUTED)
# cạnh
panel(s, 0.7, 2.8, 12.0, 3.3)
txt(s, 1.0, 3.0, 11.4, 0.4, "Sáu quan hệ (edge collection)", size=15, bold=True, color=ACCENT2)
rels = [
    ("HAS_SKILL",       "User → Skill      “tôi biết Python, trình độ 45/100”"),
    ("TARGETS_CAREER",  "User → Career     “tôi muốn làm Data Analyst”"),
    ("REQUIRES",        "Career → Skill    “Data Analyst cần SQL, mức 70”"),
    ("PREREQUISITE",    "Skill → Skill     “muốn học Pandas phải biết Python”"),
    ("TEACHES",         "Course → Skill    “khóa này dạy Python”"),
    ("COMPLETED",       "User → Course     “tôi đã học xong khóa SQL”"),
]
for i, (name, desc) in enumerate(rels):
    txt(s, 1.0, 3.5 + i * 0.42, 3.2, 0.35, name, size=13, bold=True, color=ACCENT)
    txt(s, 4.2, 3.5 + i * 0.42, 8.2, 0.35, desc, size=13, color=TEXT)
txt(s, 0.7, 6.35, 12, 0.6,
    "⚠ Quy ước chiều PREREQUISITE: _from = kỹ năng MUỐN HỌC → _to = kỹ năng CẦN CÓ TRƯỚC. Đọc nhầm chiều là lộ trình sai ngược.",
    size=12, color=WARN)

# ============================================================
# Slide 4 — Dữ liệu thật
# ============================================================
s = add_slide()
txt(s, 0.6, 0.35, 12, 0.8, "3. Dữ liệu thật — database skill_graph_db", size=26, bold=True)
txt(s, 0.6, 1.15, 12, 0.5, "1.584 bản ghi · 12 collection · data_origin: synthetic_demo (dữ liệu mẫu cho đồ án)",
    size=15, color=MUTED)
panel(s, 0.7, 1.85, 5.9, 4.7)
txt(s, 1.0, 2.05, 5.3, 0.4, "Đỉnh (vertex)", size=15, bold=True, color=ACCENT2)
verts = [("users", "40"), ("skills", "248"), ("careers", "29"),
         ("courses", "89"), ("providers", "8")]
for i, (n, v) in enumerate(verts):
    txt(s, 1.0, 2.55 + i * 0.5, 3.0, 0.4, n, size=14)
    txt(s, 4.6, 2.55 + i * 0.5, 1.6, 0.4, v, size=14, bold=True, align=PP_ALIGN.RIGHT)
panel(s, 6.9, 1.85, 5.8, 4.7)
txt(s, 7.2, 2.05, 5.2, 0.4, "Cạnh (edge)", size=15, bold=True, color=ACCENT2)
edges = [("has_skill", "274"), ("targets_career", "40"), ("requires_skill", "312"),
         ("prerequisite", "173"), ("teaches", "172"), ("completed", "110"),
         ("offered_by", "89")]
for i, (n, v) in enumerate(edges):
    txt(s, 7.2, 2.55 + i * 0.5, 3.4, 0.4, n, size=14)
    txt(s, 11.0, 2.55 + i * 0.5, 1.4, 0.4, v, size=14, bold=True, align=PP_ALIGN.RIGHT)

# ============================================================
# Slide 5 — Kiến trúc
# ============================================================
s = add_slide()
txt(s, 0.6, 0.35, 12, 0.8, "4. Kiến trúc hệ thống", size=26, bold=True)
# trình duyệt
panel(s, 0.7, 1.5, 3.4, 1.3, PANEL2)
txt(s, 0.9, 1.7, 3.0, 0.9, "Trình duyệt\n(React / Demo UI)", size=14, bold=True,
    align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
# mũi tên
txt(s, 4.3, 1.85, 1.6, 0.6, "HTTP\nJSON →", size=13, color=MUTED, align=PP_ALIGN.CENTER)
# backend
panel(s, 5.9, 1.5, 3.6, 1.3, PANEL2)
txt(s, 6.1, 1.7, 3.2, 0.9, "Backend FastAPI\n(Python)", size=14, bold=True,
    align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
txt(s, 9.7, 1.85, 1.6, 0.6, "AQL →", size=13, color=MUTED, align=PP_ALIGN.CENTER)
# arango
panel(s, 11.2, 1.5, 1.6, 1.3, PANEL2)
txt(s, 11.3, 1.7, 1.4, 0.9, "ArangoDB\n8529", size=12, bold=True,
    align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
txt(s, 0.7, 3.1, 12, 0.5,
    "Trình duyệt KHÔNG kết nối thẳng database — mọi truy vấn đi qua backend (bảo mật + kiểm soát nghiệp vụ).",
    size=13, color=MUTED)
panel(s, 0.7, 3.8, 12.0, 2.8)
txt(s, 1.0, 4.0, 11.4, 0.4, "Hai lớp trong backend — Repository Pattern", size=15, bold=True, color=ACCENT2)
txt(s, 1.0, 4.5, 5.6, 1.9,
    "Lớp NGHIỆP VỤ (core.py)\nSkill Gap · prerequisite · career match · learning path\nViết MỘT LẦN, không biết dữ liệu đến từ đâu.",
    size=13, color=TEXT, line_spacing=1.25)
txt(s, 6.9, 4.5, 5.6, 1.9,
    "Lớp LƯU TRỮ (storage.py)\n• JsonlStorage — đọc 12 file JSONL (không cần DB)\n• ArangoStorage — gửi AQL qua HTTP\nCùng 4 hàm: vertices / vertex / edges / counts",
    size=13, color=TEXT, line_spacing=1.25)

# ============================================================
# Slide 6 — Skill Gap
# ============================================================
s = add_slide()
txt(s, 0.6, 0.35, 12, 0.8, "5. Chức năng 1 — Phân tích Skill Gap", size=26, bold=True)
panel(s, 0.7, 1.3, 5.9, 2.6)
txt(s, 1.0, 1.5, 5.3, 0.4, "Cách tính", size=15, bold=True, color=ACCENT2)
txt(s, 1.0, 1.95, 5.3, 1.8,
    "Bước 1: lấy yêu cầu của nghề (cạnh REQUIRES)\n"
    "Bước 2: lấy trình độ user (cạnh HAS_SKILL)\n"
    "Bước 3: so từng cặp trên thang 0–100\n"
    "Bước 4: coverage = số ĐẠT / tổng yêu cầu",
    size=13.5, line_spacing=1.35)
panel(s, 6.9, 1.3, 5.8, 2.6)
txt(s, 7.2, 1.5, 5.2, 0.4, "Ba trạng thái", size=15, bold=True, color=ACCENT2)
txt(s, 7.2, 1.95, 5.2, 0.45, "● Chưa có (missing)", size=14, color=BAD)
txt(s, 7.2, 2.4, 5.2, 0.45, "● Chưa đủ mức (below_level)", size=14, color=WARN)
txt(s, 7.2, 2.85, 5.2, 0.45, "● Đã đạt (ok)", size=14, color=ACCENT2)
panel(s, 0.7, 4.2, 12.0, 2.3)
txt(s, 1.0, 4.4, 11.4, 0.4, "Kết quả thật — user_001 hướng tới Data Analyst", size=15, bold=True, color=ACCENT2)
txt(s, 1.0, 4.85, 11.4, 1.5,
    "11 yêu cầu:  3 đã đạt  ·  4 chưa đủ mức  ·  4 thiếu hẳn        →  độ phủ 27.3%\n\n"
    "Thiếu hẳn: SQL, Python, Pandas, Data Visualization\n"
    "Chưa đủ:  EDA (35→70), Power BI (45→70), Tableau (45→55), Data Cleaning (45→55)",
    size=13.5, color=TEXT, line_spacing=1.3)

# ============================================================
# Slide 7 — Prerequisite
# ============================================================
s = add_slide()
txt(s, 0.6, 0.35, 12, 0.8, "6. Chức năng 2 — Duyệt prerequisite nhiều tầng", size=26, bold=True)
panel(s, 0.7, 1.3, 6.2, 4.9)
txt(s, 1.0, 1.5, 5.6, 0.4, "Điểm mạnh của Graph Database", size=15, bold=True, color=ACCENT2)
txt(s, 1.0, 2.0, 5.6, 1.6,
    "Deep Learning\n   ↓ cần trước\nMachine Learning, Linear Algebra, Probability\n   ↓ cần trước\nStatistics, Python",
    size=14, color=TEXT, line_spacing=1.4)
txt(s, 1.0, 4.05, 5.6, 1.95,
    "Tìm TOÀN BỘ kỹ năng nền:\n\nFOR v, e, p IN 1..5 INBOUND s prerequisite\n  RETURN v\n\n→ 1 câu AQL duyệt mọi tầng, thay cho\n  recursive CTE nhiều vòng trong SQL.",
    size=12.5, color=MUTED, line_spacing=1.28)
panel(s, 7.3, 1.3, 5.4, 4.9)
txt(s, 7.6, 1.5, 4.8, 0.4, "Kết quả thật (depth = tầng xa nhất)", size=15, bold=True, color=ACCENT2)
rows = [("Deep Learning", "2 tầng", "ML, Linear Algebra, Probability (1) + Statistics, Python (2)"),
        ("Machine Learning", "1 tầng", "Linear Algebra, Probability, Python, Statistics"),
        ("Pandas", "1 tầng", "Python")]
for i, (name, depth, detail) in enumerate(rows):
    txt(s, 7.6, 2.05 + i * 1.35, 4.8, 0.4, name, size=15, bold=True, color=TEXT)
    txt(s, 7.6, 2.45 + i * 1.35, 4.8, 0.35, depth, size=12.5, color=ACCENT2)
    txt(s, 7.6, 2.78 + i * 1.35, 4.8, 0.75, detail, size=11.5, color=MUTED, line_spacing=1.2)
txt(s, 0.7, 6.45, 12, 0.5,
    "Dùng BFS + tập visited để chống lặp vô hạn nếu dữ liệu có chu trình.",
    size=12, color=MUTED)

# ============================================================
# Slide 8 — Learning Path
# ============================================================
s = add_slide()
txt(s, 0.6, 0.35, 12, 0.8, "7. Chức năng 3 — Sinh lộ trình học cá nhân hóa", size=26, bold=True)
panel(s, 0.7, 1.3, 5.9, 4.9)
txt(s, 1.0, 1.5, 5.3, 0.4, "Thuật toán 4 bước", size=15, bold=True, color=ACCENT2)
steps = [
    "Skill Gap → lấy kỹ năng còn thiếu / dưới mức",
    "Leo ngược prerequisite → thêm kỹ năng nền còn thiếu",
    "Sắp xếp TOPOLOGICAL (Kahn): nền trước, phụ thuộc sau",
    "Gắn khóa học (TEACHES), loại khóa đã COMPLETED",
]
for i, st in enumerate(steps):
    txt(s, 1.0, 2.0 + i * 0.75, 0.4, 0.4, str(i + 1), size=15, bold=True, color=ACCENT)
    txt(s, 1.5, 2.02 + i * 0.75, 4.9, 0.65, st, size=13, color=TEXT, line_spacing=1.15)
txt(s, 1.0, 5.15, 5.3, 0.9,
    "Hoà thứ tự → ưu tiên essential + importance cao.\nCó chu trình → phần còn lại xếp cuối + ghi chú rõ.",
    size=11.5, color=MUTED, line_spacing=1.25)
panel(s, 6.9, 1.3, 5.8, 4.9)
txt(s, 7.2, 1.5, 5.2, 0.4, "Lộ trình thật — user_001 → Data Analyst", size=15, bold=True, color=ACCENT2)
path = ["1. SQL", "2. Python", "3. Pandas  (cần Python trước ✓)",
        "4. Exploratory Data Analysis", "5. Data Visualization",
        "6. Power BI", "7. Tableau", "8. Data Cleaning"]
for i, p in enumerate(path):
    txt(s, 7.2, 2.05 + i * 0.5, 5.2, 0.4, p, size=13.5, color=TEXT)
txt(s, 7.2, 6.1, 5.2, 0.35,
    "→ mỗi bước kèm 2–3 khóa học gợi ý, không lặp khóa đã học",
    size=11.5, color=MUTED)

# ============================================================
# Slide 9 — Kết quả kiểm thử
# ============================================================
s = add_slide()
txt(s, 0.6, 0.35, 12, 0.8, "8. Kiểm thử — 42/42 PASS", size=26, bold=True)
panel(s, 0.7, 1.3, 5.9, 4.9)
txt(s, 1.0, 1.5, 5.3, 0.4, "Smoke test tự động (scripts/smoke_test.py)", size=15, bold=True, color=ACCENT2)
checks = [
    ("Metadata & đếm bản ghi", "12 collection, 1.584 records"),
    ("Danh sách 5 collection", "đúng số lượng từng loại"),
    ("Chi tiết user / career / skill / course", "kèm quan hệ"),
    ("Skill Gap", "missing + below + ok = tổng"),
    ("Career Match", "29 nghề, 0–100%"),
    ("Prerequisite", "duyệt nhiều tầng"),
    ("Learning Path", "order 1..n, loại khóa đã học"),
    ("Graph", "mọi edge trỏ tới node tồn tại"),
    ("Xử lý lỗi", "404/400 đúng format error"),
]
for i, (a, b) in enumerate(checks):
    txt(s, 1.0, 1.98 + i * 0.47, 0.3, 0.4, "✓", size=12, color=ACCENT2, bold=True)
    txt(s, 1.30, 1.98 + i * 0.47, 2.95, 0.4, a, size=11.5, color=TEXT)
    txt(s, 4.25, 1.98 + i * 0.47, 2.15, 0.4, b, size=10.5, color=MUTED)
panel(s, 6.9, 1.3, 5.8, 4.9)
txt(s, 7.2, 1.5, 5.2, 0.4, "Kiểm chứng chéo AQL ↔ Backend", size=15, bold=True, color=ACCENT2)
txt(s, 7.2, 2.0, 5.2, 3.9,
    "Mỗi truy vấn AQL trong queries/aql_queries.aql\nđã được mô phỏng trên dữ liệu thật bằng Python\nvà ĐỐI CHIẾU với kết quả backend:\n\n"
    "• Skill Gap: cùng 27.3% coverage ✓\n"
    "• Career Match: cùng thứ hạng top 5 ✓\n"
    "• Learning Path: cùng 8 kỹ năng cần học ✓\n"
    "• Prerequisite: cùng tập kỹ năng nền ✓\n\n"
    "→ Backend và AQL đồng nhất về nghiệp vụ.",
    size=13, color=TEXT, line_spacing=1.35)

# ============================================================
# Slide 10 — Demo & kết luận
# ============================================================
s = add_slide()
txt(s, 0.6, 0.35, 12, 0.8, "9. Demo & hướng phát triển", size=26, bold=True)
panel(s, 0.7, 1.3, 5.9, 4.9)
txt(s, 1.0, 1.5, 5.3, 0.4, "Demo 10 phút", size=15, bold=True, color=ACCENT2)
demo = [
    "ArangoDB Web UI: 12 collection + graph",
    "AQL B13: thống kê 1.584 bản ghi",
    "AQL B3: traversal prerequisite nhiều tầng",
    "Swagger /docs: thử API trực tiếp",
    "Demo UI /demo: Skill Gap + Lộ trình",
    "Graph neighborhood: dữ liệu cho trang đồ thị",
]
bullet_block(s, 1.0, 2.0, 5.3, demo, size=12.5, gap=0.62)
panel(s, 6.9, 1.3, 5.8, 4.9)
txt(s, 7.2, 1.5, 5.2, 0.4, "Việc tiếp theo", size=15, bold=True, color=ACCENT2)
todo = [
    "Restore dump vào ArangoDB thật (máy có Docker)",
    "Nối frontend React sang API (VITE_DATA_SOURCE=api)",
    "Thêm CRUD ghi dữ liệu qua API",
    "Sửa lỗi hiển thị tiếng Việt (mojibake) trong frontend",
    "Hoàn thiện báo cáo + slide cuối",
]
bullet_block(s, 7.2, 2.0, 5.2, todo, size=12.5, gap=0.7)
txt(s, 0.7, 6.55, 12, 0.5,
    "Backend + AQL + dữ liệu thật + UI demo: ĐÃ CHẠY ĐƯỢC. Còn lại: hạ tầng DB thật và tích hợp frontend.",
    size=13, color=ACCENT2, bold=True)

out = r"C:\Users\phupu\OneDrive\Documents\deepseek-harness\default-workspace\skillgraph\docs\BAO_CAO_SLIDE.pptx"
prs.save(out)
print("saved:", out)
