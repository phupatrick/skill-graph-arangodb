# -*- coding: utf-8 -*-
"""Sinh báo cáo đồ án Skill Graph (python-docx)."""
from docx import Document
from docx.enum.section import WD_SECTION
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_BREAK
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Pt, RGBColor

OUT = r"C:\Users\phupu\OneDrive\Documents\deepseek-harness\default-workspace\skillgraph\docs\BAO_CAO_DO_AN.docx"

doc = Document()

# ---------- trang & style chung ----------
sec = doc.sections[0]
sec.page_width = Cm(21.0)
sec.page_height = Cm(29.7)
sec.top_margin = Cm(2.2)
sec.bottom_margin = Cm(2.2)
sec.left_margin = Cm(3.0)
sec.right_margin = Cm(2.0)

style = doc.styles["Normal"]
style.font.name = "Times New Roman"
style.font.size = Pt(13)
style.element.rPr.rFonts.set(qn("w:eastAsia"), "Times New Roman")
style.paragraph_format.line_spacing = 1.32
style.paragraph_format.space_after = Pt(6)


def h(text, level=1):
    p = doc.add_heading(text, level=level)
    for r in p.runs:
        r.font.name = "Times New Roman"
        r._element.rPr.rFonts.set(qn("w:eastAsia"), "Times New Roman")
        r.font.color.rgb = RGBColor(0x14, 0x2B, 0x5E)
        r.font.size = Pt(16 if level == 1 else 13.5 if level == 2 else 12.5)
        r.font.bold = True
    p.paragraph_format.space_before = Pt(14 if level == 1 else 10)
    p.paragraph_format.space_after = Pt(6)
    return p


def para(text, bold=False, align=WD_ALIGN_PARAGRAPH.JUSTIFY, size=13, italic=False,
         space_after=6, indent_first=True):
    p = doc.add_paragraph()
    p.alignment = align
    p.paragraph_format.space_after = Pt(space_after)
    if indent_first:
        p.paragraph_format.first_line_indent = Cm(1.0)
    r = p.add_run(text)
    r.font.size = Pt(size)
    r.font.bold = bold
    r.font.italic = italic
    r.font.name = "Times New Roman"
    r._element.rPr.rFonts.set(qn("w:eastAsia"), "Times New Roman")
    return p


def bullet(text, size=12.5):
    p = doc.add_paragraph(style="List Bullet")
    p.paragraph_format.space_after = Pt(3)
    p.paragraph_format.left_indent = Cm(1.2)
    r = p.add_run(text)
    r.font.size = Pt(size)
    r.font.name = "Times New Roman"
    r._element.rPr.rFonts.set(qn("w:eastAsia"), "Times New Roman")
    return p


def code_block(text):
    p = doc.add_paragraph()
    p.paragraph_format.left_indent = Cm(1.0)
    p.paragraph_format.space_before = Pt(4)
    p.paragraph_format.space_after = Pt(8)
    p.paragraph_format.line_spacing = 1.15
    r = p.add_run(text)
    r.font.name = "Consolas"
    r._element.rPr.rFonts.set(qn("w:eastAsia"), "Consolas")
    r.font.size = Pt(10.5)
    shd = OxmlElement("w:shd")
    shd.set(qn("w:val"), "clear")
    shd.set(qn("w:fill"), "F2F4F8")
    p._p.get_or_add_pPr().append(shd)
    return p


def caption(text):
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(2)
    p.paragraph_format.space_after = Pt(10)
    r = p.add_run(text)
    r.font.size = Pt(11)
    r.font.italic = True
    r.font.name = "Times New Roman"


def table(headers, rows, widths=None, font_size=11):
    t = doc.add_table(rows=1, cols=len(headers))
    t.style = "Table Grid"
    t.alignment = WD_TABLE_ALIGNMENT.CENTER
    t.autofit = False
    # ép layout cố định để độ rộng cột được tôn trọng
    tblPr = t._tbl.tblPr
    layout = OxmlElement("w:tblLayout")
    layout.set(qn("w:type"), "fixed")
    tblPr.append(layout)
    hdr = t.rows[0].cells
    for i, name in enumerate(headers):
        hdr[i].text = ""
        p = hdr[i].paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r = p.add_run(name)
        r.font.bold = True
        r.font.size = Pt(font_size)
        r.font.name = "Times New Roman"
        shd = OxmlElement("w:shd")
        shd.set(qn("w:val"), "clear")
        shd.set(qn("w:fill"), "E4EAF5")
        hdr[i]._tc.get_or_add_tcPr().append(shd)
    for row in rows:
        cells = t.add_row().cells
        for i, val in enumerate(row):
            cells[i].text = ""
            p = cells[i].paragraphs[0]
            p.paragraph_format.space_after = Pt(2)
            p.paragraph_format.line_spacing = 1.15
            r = p.add_run(str(val))
            r.font.size = Pt(font_size)
            r.font.name = "Times New Roman"
    # không cho tách một dòng sang trang khác
    for row in t.rows:
        trPr = row._tr.get_or_add_trPr()
        cant = OxmlElement("w:cantSplit")
        trPr.append(cant)
    # lặp lại dòng tiêu đề khi bảng sang trang
    hdrPr = t.rows[0]._tr.get_or_add_trPr()
    tblHeader = OxmlElement("w:tblHeader")
    tblHeader.set(qn("w:val"), "true")
    hdrPr.append(tblHeader)
    if widths:
        grid = t._tbl.tblGrid
        for i, w in enumerate(widths):
            if i < len(grid.gridCol_lst):
                grid.gridCol_lst[i].w = Cm(w)
        for row in t.rows:
            for i, w in enumerate(widths):
                row.cells[i].width = Cm(w)
    doc.add_paragraph().paragraph_format.space_after = Pt(2)
    return t


# ============================================================
# TRANG BÌA
# ============================================================
p = doc.add_paragraph()
p.alignment = WD_ALIGN_PARAGRAPH.CENTER
r = p.add_run("TRƯỜNG ĐẠI HỌC …………………\nKHOA CÔNG NGHỆ THÔNG TIN")
r.font.size = Pt(13)
r.font.bold = True
r.font.name = "Times New Roman"

for _ in range(3):
    doc.add_paragraph()

p = doc.add_paragraph()
p.alignment = WD_ALIGN_PARAGRAPH.CENTER
r = p.add_run("BÁO CÁO ĐỒ ÁN NHÓM")
r.font.size = Pt(15)
r.font.bold = True

p = doc.add_paragraph()
p.alignment = WD_ALIGN_PARAGRAPH.CENTER
p.paragraph_format.space_before = Pt(10)
r = p.add_run("HỆ THỐNG SKILL GRAPH VÀ\nĐỀ XUẤT LỘ TRÌNH HỌC CÁ NHÂN HÓA")
r.font.size = Pt(21)
r.font.bold = True
r.font.color.rgb = RGBColor(0x14, 0x2B, 0x5E)

p = doc.add_paragraph()
p.alignment = WD_ALIGN_PARAGRAPH.CENTER
p.paragraph_format.space_before = Pt(8)
r = p.add_run("Dựng trên ArangoDB (Document + Graph Database)")
r.font.size = Pt(14)
r.font.italic = True

for _ in range(4):
    doc.add_paragraph()

info = doc.add_table(rows=4, cols=2)
info.alignment = WD_TABLE_ALIGNMENT.CENTER
data = [("Giảng viên hướng dẫn:", "…………………………………"),
        ("Nhóm thực hiện:", "…………………………………"),
        ("Thành viên:", "…………………………………"),
        ("Thời gian thực hiện:", "Tháng 11 năm 2026")]
for i, (k, v) in enumerate(data):
    for j, txt_ in enumerate((k, v)):
        cell = info.rows[i].cells[j]
        cell.text = ""
        run = cell.paragraphs[0].add_run(txt_)
        run.font.size = Pt(12.5)
        run.font.bold = (j == 0)
        run.font.name = "Times New Roman"

doc.add_paragraph().add_run().add_break(WD_BREAK.PAGE)

# ============================================================
# MỤC LỤC (hướng dẫn)
# ============================================================
h("Mục lục")
para("(Trong Microsoft Word: đặt con trỏ tại đây → References → Table of Contents "
     "để tạo mục lục tự động từ các heading của báo cáo.)", italic=True, indent_first=False)
doc.add_paragraph().add_run().add_break(WD_BREAK.PAGE)

# ============================================================
# MỞ ĐẦU
# ============================================================
h("Mở đầu")
para("Trong những năm gần đây, nhu cầu học lại và chuyển đổi nghề nghiệp tăng nhanh. "
     "Người học thường gặp ba khó khăn: không biết nghề mục tiêu yêu cầu những kỹ năng gì, "
     "không biết mình còn thiếu bao nhiêu, và không biết nên học theo thứ tự nào. "
     "Các hệ thống quản lý học tập truyền thống (LMS) lưu dữ liệu dạng bảng, trong đó quan hệ "
     "giữa các kỹ năng chỉ là một cột khoá ngoại; vì vậy việc trả lời câu hỏi "
     "“học Pandas cần chuẩn bị những gì” đòi hỏi nhiều vòng truy vấn lồng nhau.")
para("Đồ án xây dựng một hệ thống Skill Graph trên cơ sở dữ liệu đa mô hình ArangoDB, "
     "biểu diễn tường minh bốn loại thực thể (Người dùng, Kỹ năng, Nghề nghiệp, Khoá học) "
     "và sáu loại quan hệ giữa chúng, từ đó cung cấp ba chức năng phân tích: "
     "phân tích khoảng trống kỹ năng (Skill Gap), duyệt kỹ năng tiên quyết nhiều tầng, "
     "và sinh lộ trình học cá nhân hoá.")
para("Báo cáo gồm bốn chương: Chương 1 trình bày cơ sở lý thuyết và lý do lựa chọn ArangoDB; "
     "Chương 2 mô tả thiết kế dữ liệu đa mô hình; Chương 3 trình bày kiến trúc hệ thống và "
     "các thuật toán nghiệp vụ; Chương 4 trình bày kết quả cài đặt, kiểm thử và đánh giá.")

doc.add_paragraph().add_run().add_break(WD_BREAK.PAGE)

# ============================================================
# CHƯƠNG 1
# ============================================================
h("Chương 1. Cơ sở lý thuyết và lựa chọn công nghệ")

h("1.1. Cơ sở dữ liệu đa mô hình", 2)
para("Cơ sở dữ liệu đa mô hình (multi-model database) là hệ quản trị cơ sở dữ liệu hỗ trợ "
     "nhiều mô hình dữ liệu trong cùng một engine và cùng một ngôn ngữ truy vấn. "
     "ArangoDB hỗ trợ đồng thời mô hình tài liệu (document), mô hình đồ thị (graph) và "
     "mô hình khoá – giá trị (key–value). Mỗi bản ghi được lưu dưới dạng JSON, "
     "các bản ghi thuộc cùng một tập hợp được gọi là collection; "
     "collection chứa cạnh gọi là edge collection và bắt buộc có hai trường _from và _to.")
para("Điểm khác biệt so với việc dùng hai hệ thống riêng (ví dụ MongoDB cho tài liệu, "
     "Neo4j cho đồ thị) là dữ liệu không phải đồng bộ giữa hai nơi, và một câu truy vấn "
     "có thể vừa lọc theo thuộc tính tài liệu vừa duyệt theo cạnh đồ thị.")

h("1.2. Ngôn ngữ truy vấn AQL", 2)
para("AQL (ArangoDB Query Language) là ngôn ngữ khai báo có cú pháp gần với đọc hiểu tự nhiên. "
     "Một truy vấn AQL gồm chuỗi thao tác FOR – FILTER – SORT – LIMIT – RETURN. "
     "Với đồ thị, AQL cung cấp toán tử duyệt (traversal) dạng:")
code_block("FOR v, e, p IN 1..5 INBOUND start_vertex edge_collection\n  RETURN v")
para("Trong đó v là đỉnh, e là cạnh và p là đường đi tại mỗi bước; "
     "1..5 là độ sâu tối thiểu và tối đa. Đây chính là cơ chế cho phép tìm toàn bộ "
     "kỹ năng tiên quyết nhiều tầng chỉ bằng một câu truy vấn.")

h("1.3. Vì sao chọn ArangoDB cho bài toán này", 2)
para("Dữ liệu của bài toán có hai đặc điểm: (i) phần lớn thông tin là thuộc tính của thực thể "
     "(tên kỹ năng, mô tả khoá học, trình độ người học) — phù hợp với mô hình tài liệu; "
     "(ii) quan hệ giữa các kỹ năng có tính bắc cầu và nhiều tầng — phù hợp với mô hình đồ thị. "
     "Nếu dùng cơ sở dữ liệu quan hệ, truy vấn “liệt kê mọi kỹ năng nền của Deep Learning” "
     "phải viết CTE đệ quy (recursive common table expression) với nhiều vòng lặp, "
     "khó đọc và khó tối ưu. Trong ArangoDB, cùng truy vấn đó là một câu traversal. "
     "Bảng 1.1 so sánh ba phương án theo các tiêu chí của bài toán.")
table(
    ["Tiêu chí", "Cơ sở dữ liệu quan hệ", "Cơ sở dữ liệu tài liệu", "ArangoDB"],
    [
        ["Duyệt nhiều tầng", "CTE đệ quy, phức tạp", "Không hỗ trợ trực tiếp", "Traversal 1..n"],
        ["Đảm bảo toàn vẹn cạnh", "Khoá ngoại", "Kiểm tra ở tầng ứng dụng", "_from/_to có kiểm tra"],
        ["Một ngôn ngữ cho cả hai mô hình", "Có (SQL)", "Không", "Có (AQL)"],
        ["Trực quan hoá đồ thị", "Phải tự dựng", "Phải tự dựng", "Web Interface có sẵn"],
    ],
    widths=[4.8, 3.9, 3.9, 3.4],
    font_size=10.5,
)
caption("Bảng 1.1. So sánh phương án lưu trữ")

# ============================================================
# CHƯƠNG 2
# ============================================================
h("Chương 2. Thiết kế cơ sở dữ liệu đa mô hình")

h("2.1. Các thực thể (vertex)", 2)
para("Hệ thống có năm collection đỉnh. Bảng 2.1 liệt kê số bản ghi thực tế của từng collection "
     "trong cơ sở dữ liệu skill_graph_db.")
table(
    ["Collection", "Vai trò", "Số bản ghi"],
    [
        ["users", "Người học: họ tên, email, trình độ học vấn, chuyên ngành, số năm kinh nghiệm", "40"],
        ["skills", "Kỹ năng: tên, nhóm, mô tả", "248"],
        ["careers", "Nghề nghiệp: tên, nhóm nghề, mô tả", "29"],
        ["courses", "Khoá học: tiêu đề, cấp độ, thời lượng", "89"],
        ["providers", "Nhà cung cấp khoá học", "8"],
    ],
    widths=[3.6, 9.4, 3.0],
)
caption("Bảng 2.1. Các collection đỉnh")

h("2.2. Các quan hệ (edge)", 2)
para("Bảy collection cạnh mã hoá toàn bộ ngữ nghĩa của bài toán. Mỗi cạnh ngoài _from và _to "
     "còn mang thuộc tính riêng, ví dụ trình độ của người dùng trên một kỹ năng, "
     "hay mức độ quan trọng của một kỹ năng đối với nghề.")
table(
    ["Collection", "Từ → Đến", "Thuộc tính", "Số cạnh", "Ý nghĩa"],
    [
        ["has_skill", "users → skills", "proficiency, assessment_method", "274",
         "Người học đã có kỹ năng, ở mức nào"],
        ["targets_career", "users → careers", "priority", "40", "Nghề mục tiêu của người học"],
        ["requires_skill", "careers → skills", "requirement_type, required_level, importance", "312",
         "Nghề yêu cầu kỹ năng ở mức nào"],
        ["prerequisite", "skills → skills", "relation, strength", "173", "Kỹ năng nền cần có trước"],
        ["teaches", "courses → skills", "role", "172", "Khoá học dạy kỹ năng gì"],
        ["completed", "users → courses", "progress, score, status", "110", "Người học đã hoàn thành khoá"],
        ["offered_by", "courses → providers", "—", "89", "Khoá học do ai cung cấp"],
    ],
    widths=[3.0, 3.4, 4.6, 1.8, 4.0],
    font_size=9.5,
)
caption("Bảng 2.2. Các collection cạnh")
para("Tổng số bản ghi của mười hai collection là 1.584.")

h("2.3. Quy ước chiều của quan hệ tiên quyết", 2)
para("Đây là quy ước quan trọng nhất và cũng dễ nhầm nhất trong đồ án. Với cạnh prerequisite, "
     "_from là kỹ năng muốn học, _to là kỹ năng cần có trước. Ví dụ:")
code_block("skills/pandas  --prerequisite-->  skills/python")
para("Nghĩa là: muốn học Pandas thì cần có Python trước. Nếu đọc ngược chiều, thuật toán sinh "
     "lộ trình sẽ cho ra thứ tự sai hoàn toàn (dạy Pandas trước Python). "
     "Vì vậy quy ước này được ghi thành hằng số trong mã nguồn và được kiểm thử tự động.")
para("Khi duyệt ngược từ một kỹ năng để tìm nền tảng, ta dùng hướng INBOUND; "
     "khi muốn biết một kỹ năng mở khoá được những kỹ năng nào, ta dùng hướng OUTBOUND.")

h("2.4. Thang đo trình độ", 2)
para("Trường proficiency của cạnh has_skill và trường required_level của cạnh requires_skill "
     "đều dùng thang 0–100. Khi một yêu cầu không khai báo required_level, hệ thống áp dụng "
     "giá trị mặc định 50 và ghi rõ trong phản hồi API, không tự suy diễn là đã đạt.")

h("2.5. Đồ thị có tên (named graph)", 2)
para("Ngoài mười hai collection, cơ sở dữ liệu còn đăng ký một named graph tên skill_graph, "
     "gom năm collection đỉnh và bảy collection cạnh. Named graph cho phép dùng truy vấn "
     "GRAPH thay vì liệt kê từng collection, và cho phép duyệt hỗn hợp nhiều loại cạnh "
     "trong cùng một câu lệnh.")

# ============================================================
# CHƯƠNG 3
# ============================================================
h("Chương 3. Kiến trúc hệ thống và thuật toán nghiệp vụ")

h("3.1. Kiến trúc tổng thể", 2)
para("Hệ thống gồm ba tầng. Tầng trình bày là ứng dụng web chạy trong trình duyệt. "
     "Tầng ứng dụng là máy chủ FastAPI viết bằng Python, chịu trách nhiệm xác thực đầu vào, "
     "thực thi nghiệp vụ và định dạng phản hồi. Tầng dữ liệu là ArangoDB.")
para("Nguyên tắc quan trọng: trình duyệt không kết nối trực tiếp tới ArangoDB. "
     "Nếu để trình duyệt kết nối thẳng, thông tin đăng nhập cơ sở dữ liệu sẽ lộ trong mã nguồn "
     "phía client, và bất kỳ ai cũng có thể gửi truy vấn tuỳ ý. Máy chủ ứng dụng đóng vai trò "
     "lớp kiểm soát: chỉ những truy vấn đã được định nghĩa trước mới được thực thi.")

h("3.2. Mẫu thiết kế Repository", 2)
para("Mã nghiệp vụ không được phép biết dữ liệu đến từ đâu. Vì vậy toàn bộ thao tác đọc dữ liệu "
     "được trừu tượng hoá thành bốn hàm: lấy danh sách đỉnh theo collection, lấy một đỉnh theo "
     "khoá, lấy danh sách cạnh theo chiều, và đếm số bản ghi. Có hai lớp cài đặt cùng tuân theo "
     "giao diện này: một lớp đọc từ tệp JSONL trích sẵn, một lớp gửi truy vấn AQL tới ArangoDB.")
table(
    ["Lớp cài đặt", "Nguồn dữ liệu", "Mục đích sử dụng"],
    [
        ["JsonlStorage", "12 tệp JSONL trong thư mục data", "Kiểm thử tự động, chạy demo khi chưa có ArangoDB"],
        ["ArangoStorage", "ArangoDB qua HTTP + AQL", "Chạy thật với cơ sở dữ liệu đã phục hồi từ dump"],
    ],
    widths=[3.6, 6.2, 6.2],
)
caption("Bảng 3.1. Hai lớp cài đặt lưu trữ")
para("Nhờ cách tách này, cùng một đoạn mã nghiệp vụ chạy được ở cả hai môi trường, "
     "và kết quả kiểm thử ở môi trường JSONL có giá trị tham chiếu cho môi trường ArangoDB.")

h("3.3. Thuật toán phân tích Skill Gap", 2)
para("Đầu vào là một người dùng và một nghề nghiệp. Thuật toán gồm bốn bước: "
     "lấy danh sách kỹ năng nghề yêu cầu cùng mức yêu cầu; lấy trình độ hiện tại của người dùng; "
     "so sánh từng cặp theo ba trạng thái; tính tỉ lệ đáp ứng.")
table(
    ["Trạng thái", "Điều kiện", "Ý nghĩa"],
    [
        ["missing", "Người dùng chưa khai báo kỹ năng", "Phải học từ đầu"],
        ["below_level", "Có kỹ năng nhưng proficiency < required_level", "Cần nâng lên mức yêu cầu"],
        ["ok", "proficiency ≥ required_level", "Đã đáp ứng"],
    ],
    widths=[3.4, 7.2, 5.4],
)
caption("Bảng 3.2. Ba trạng thái của phân tích Skill Gap")
para("Tỉ lệ đáp ứng được tính bằng số yêu cầu ở trạng thái ok chia cho tổng số yêu cầu. "
     "Hệ thống không suy diễn kỹ năng chưa khai báo là đã có, và không tự động đánh giá "
     "một kỹ năng là đạt khi thiếu dữ liệu.")

h("3.4. Thuật toán duyệt kỹ năng tiên quyết nhiều tầng", 2)
para("Bài toán: cho một kỹ năng, liệt kê toàn bộ kỹ năng nền cần có, kèm độ sâu. "
     "Thuật toán dùng duyệt theo chiều rộng (BFS) trên đồ thị có hướng, đi ngược cạnh "
     "prerequisite, với một tập đã thăm để tránh lặp vô hạn nếu dữ liệu có chu trình.")
code_block(
    "hàng đợi = [(kỹ_năng_gốc, 0)]\n"
    "đã_thăm = {kỹ_năng_gốc}\n"
    "trong khi hàng đợi còn phần tử:\n"
    "    (hiện_tại, độ_sâu) = lấy_ra_đầu_hàng_đợi\n"
    "    nếu độ_sâu = giới_hạn: tiếp tục\n"
    "    với mỗi cạnh prerequisite trỏ vào hiện_tại:\n"
    "        ghi_nhận(đỉnh_nguồn, độ_sâu + 1)\n"
    "        nếu đỉnh_nguồn chưa thăm: thêm vào hàng đợi"
)
para("Kết quả thực tế với kỹ năng Deep Learning: tầng 1 gồm Machine Learning, Linear Algebra "
     "và Probability; tầng 2 gồm Statistics và Python (là nền của Machine Learning). "
     "Tổng cộng năm kỹ năng nền, độ sâu tối đa là hai.")

h("3.5. Thuật toán tính điểm phù hợp nghề nghiệp", 2)
para("Mỗi yêu cầu kỹ năng của nghề có trường importance biểu thị mức quan trọng. "
     "Điểm phù hợp của một người với một nghề được định nghĩa là tổng importance của các "
     "yêu cầu đã đạt chia cho tổng importance của toàn bộ yêu cầu, nhân một trăm.")
code_block("điểm = 100 × (Σ importance của yêu cầu đã đạt) / (Σ importance của toàn bộ yêu cầu)")
para("Cách tính này phản ánh đúng thực tế: đạt một kỹ năng quan trọng đem lại nhiều điểm hơn "
     "đạt nhiều kỹ năng ít quan trọng. Kết quả được sắp xếp giảm dần để trả về danh sách "
     "nghề phù hợp nhất.")

h("3.6. Thuật toán sinh lộ trình học", 2)
para("Đây là chức năng trung tâm của đồ án, gồm bốn bước.")
para("Bước 1. Chạy phân tích Skill Gap để lấy danh sách kỹ năng ở trạng thái missing hoặc "
     "below_level.", indent_first=False)
para("Bước 2. Với mỗi kỹ năng trong danh sách, duyệt ngược cạnh prerequisite để bổ sung "
     "các kỹ năng nền cũng còn thiếu. Bước này đảm bảo lộ trình không bỏ sót nền tảng.", indent_first=False)
para("Bước 3. Sắp xếp danh sách bằng sắp xếp topo (thuật toán Kahn) trên đồ thị con chỉ gồm "
     "các kỹ năng cần học: kỹ năng nền luôn đứng trước kỹ năng phụ thuộc nó. "
     "Khi nhiều kỹ năng cùng bậc, ưu tiên kỹ năng bắt buộc và có importance cao hơn.", indent_first=False)
para("Bước 4. Với mỗi bước trong lộ trình, tìm các khoá học dạy kỹ năng đó và loại bỏ những "
     "khoá người dùng đã hoàn thành, tránh gợi ý trùng lặp.", indent_first=False)
para("Trường hợp dữ liệu có chu trình (A cần B và B cần A), thuật toán Kahn không thể xếp hết; "
     "khi đó các kỹ năng còn lại được đưa xuống cuối lộ trình và hệ thống ghi chú rõ, "
     "không tự ý phá vỡ ràng buộc.")

# ============================================================
# CHƯƠNG 4
# ============================================================
h("Chương 4. Kết quả cài đặt và kiểm thử")

h("4.1. Môi trường và công nghệ", 2)
table(
    ["Thành phần", "Công nghệ", "Ghi chú"],
    [
        ["Cơ sở dữ liệu", "ArangoDB 3.12", "Document + Graph, quản trị qua Web Interface"],
        ["Máy chủ ứng dụng", "Python 3.11+, FastAPI", "Sinh tài liệu API tự động (OpenAPI)"],
        ["Kiểm tra kiểu dữ liệu", "Pydantic v2", "Đặt tên trường theo camelCase cho phía client"],
        ["Truy vấn", "AQL", "30 truy vấn, chia hai nhóm cơ bản và nâng cao"],
        ["Kiểm thử", "pytest + httpx", "42 điểm kiểm tra tự động"],
    ],
    widths=[3.6, 4.6, 7.8],
)
caption("Bảng 4.1. Môi trường cài đặt")

h("4.2. Danh sách API", 2)
table(
    ["Phương thức", "Đường dẫn", "Chức năng"],
    [
        ["GET", "/api/v1/meta/health", "Trạng thái hệ thống và kết nối cơ sở dữ liệu"],
        ["GET", "/api/v1/meta/release", "Số bản ghi từng collection"],
        ["GET", "/api/v1/users", "Danh sách người học"],
        ["GET", "/api/v1/users/{key}", "Chi tiết người học kèm kỹ năng, mục tiêu"],
        ["GET", "/api/v1/users/{key}/skill-gap", "Phân tích khoảng trống kỹ năng"],
        ["GET", "/api/v1/users/{key}/career-match", "Xếp hạng nghề phù hợp"],
        ["GET", "/api/v1/users/{key}/learning-path", "Sinh lộ trình học"],
        ["GET", "/api/v1/skills/{key}/prerequisites", "Duyệt kỹ năng tiên quyết nhiều tầng"],
        ["GET", "/api/v1/skills/{key}/courses", "Khoá học dạy kỹ năng"],
        ["GET", "/api/v1/careers/{key}", "Nghề nghiệp kèm yêu cầu"],
        ["GET", "/api/v1/courses/{key}", "Chi tiết khoá học"],
        ["GET", "/api/v1/graph/neighborhood", "Đồ thị con phục vụ trực quan hoá"],
    ],
    widths=[2.6, 7.4, 6.0],
    font_size=10,
)
caption("Bảng 4.2. Danh sách API chính")

h("4.3. Kết quả kiểm thử", 2)
para("Bộ kiểm thử tự động gồm 42 điểm, bao phủ toàn bộ endpoint và các bất biến nghiệp vụ "
     "quan trọng. Kết quả chạy trên dữ liệu thật: 42 đạt, 0 lỗi.")
table(
    ["Nhóm kiểm thử", "Nội dung", "Kết quả"],
    [
        ["Metadata", "Đếm đủ 12 collection, tổng 1.584 bản ghi", "Đạt"],
        ["Danh sách thực thể", "Số lượng đúng theo từng collection", "Đạt"],
        ["Chi tiết thực thể", "Trả về kèm quan hệ liên quan", "Đạt"],
        ["Skill Gap", "missing + below_level + ok = tổng yêu cầu", "Đạt"],
        ["Career Match", "29 nghề, điểm trong khoảng 0–100, sắp giảm dần", "Đạt"],
        ["Prerequisite", "Duyệt đúng nhiều tầng, không lặp đỉnh", "Đạt"],
        ["Learning Path", "Thứ tự 1..n liên tục, mọi bước có gap dương, không lặp khoá đã học", "Đạt"],
        ["Đồ thị", "Mọi cạnh trỏ tới đỉnh tồn tại trong phản hồi", "Đạt"],
        ["Xử lý lỗi", "Trả về đúng cấu trúc lỗi thống nhất", "Đạt"],
    ],
    widths=[4.0, 9.2, 2.8],
)
caption("Bảng 4.3. Kết quả kiểm thử tự động")

h("4.4. Kết quả nghiệp vụ trên dữ liệu thật", 2)
para("Với người dùng user_001 hướng tới nghề Data Analyst, hệ thống trả về các kết quả sau.")
para("Phân tích Skill Gap: nghề yêu cầu 11 kỹ năng, trong đó 3 đạt, 4 chưa đủ mức và 4 thiếu hẳn; "
     "tỉ lệ đáp ứng là 27,3%.", indent_first=False)
table(
    ["Kỹ năng", "Yêu cầu", "Hiện có", "Trạng thái"],
    [
        ["SQL", "70", "—", "missing"],
        ["Python", "70", "—", "missing"],
        ["Pandas", "70", "—", "missing"],
        ["Data Visualization", "70", "—", "missing"],
        ["Exploratory Data Analysis", "70", "35", "below_level"],
        ["Power BI", "70", "45", "below_level"],
        ["Tableau", "55", "45", "below_level"],
        ["Data Cleaning", "55", "45", "below_level"],
        ["Statistics", "70", "75", "ok"],
        ["A/B Testing", "55", "75", "ok"],
        ["Communication", "55", "60", "ok"],
    ],
    widths=[6.4, 3.2, 3.0, 3.4],
)
caption("Bảng 4.4. Kết quả Skill Gap của user_001 với nghề Data Analyst")
para("Lộ trình học sinh ra gồm tám bước, sắp xếp đúng thứ tự phụ thuộc. Đáng chú ý, Pandas đứng "
     "sau Python vì Pandas có kỹ năng tiên quyết là Python; bốn khoá học người dùng đã hoàn thành "
     "không xuất hiện trong danh sách gợi ý.")
table(
    ["Bước", "Kỹ năng"],
    [
        ["1", "SQL"], ["2", "Python"], ["3", "Pandas"],
        ["4", "Exploratory Data Analysis"], ["5", "Data Visualization"],
        ["6", "Power BI"], ["7", "Tableau"], ["8", "Data Cleaning"],
    ],
    widths=[2.4, 12.6],
)
caption("Bảng 4.5. Lộ trình học đề xuất cho user_001")
para("Xếp hạng nghề phù hợp: Data Analyst đứng đầu với 24,9%, tiếp theo là Data Scientist 13,2%. "
     "Kết quả này nhất quán với nghề mục tiêu mà người dùng đã khai báo.")

h("4.5. Bộ truy vấn AQL", 2)
para("Đồ án cung cấp 30 truy vấn AQL chạy trực tiếp trên ArangoDB Web Interface, chia hai nhóm. "
     "Nhóm cơ bản gồm đếm bản ghi, liệt kê, tìm kiếm, lọc, xem quan hệ của một người dùng và "
     "các thao tác thêm/sửa/xoá. Nhóm nâng cao gồm mười ba truy vấn sử dụng graph traversal:")
bullet("Duyệt yêu cầu kỹ năng của một nghề")
bullet("Phân tích Skill Gap bằng cách kết hợp yêu cầu và trình độ hiện có")
bullet("Duyệt kỹ năng tiên quyết nhiều tầng và in ra đường đi đầy đủ")
bullet("Tìm khoá học dạy một kỹ năng kèm nhà cung cấp")
bullet("Tính điểm phù hợp của một người với mọi nghề")
bullet("Sinh lộ trình học có thứ tự")
bullet("Tìm đường đi ngắn nhất giữa hai kỹ năng")
bullet("Phát hiện kỹ năng không có khoá học nào dạy")
para("Mỗi truy vấn đã được mô phỏng lại trên dữ liệu thật bằng một chương trình Python độc lập "
     "và đối chiếu với kết quả của máy chủ ứng dụng; các giá trị then chốt trùng khớp, "
     "bao gồm tỉ lệ đáp ứng 27,3%, thứ hạng nghề và tập tám kỹ năng cần học.")

h("4.6. Hạn chế", 2)
bullet("Máy phát triển chưa cài Docker nên chưa chạy được bước phục hồi dump vào ArangoDB thật; "
       "toàn bộ kiểm thử hiện thực hiện trên dữ liệu JSONL trích từ chính dump đó.")
bullet("Máy chủ ứng dụng hiện chỉ đọc dữ liệu; các thao tác thêm/sửa/xoá được thực hiện bằng AQL "
       "hoặc trên ArangoDB Web Interface, đúng với yêu cầu quản trị dữ liệu của đề tài.")
bullet("Dữ liệu mang nhãn synthetic_demo, là dữ liệu mẫu phục vụ đồ án, không phải dữ liệu người thật.")
bullet("Trường importance và required_level chỉ biểu thị mức liên quan giữa kỹ năng và nghề, "
       "không hàm ý người học đã được công nhận năng lực.")

doc.add_paragraph().add_run().add_break(WD_BREAK.PAGE)

# ============================================================
# KẾT LUẬN
# ============================================================
h("Kết luận")
para("Đồ án đã xây dựng được một hệ thống Skill Graph hoàn chỉnh trên ArangoDB, đáp ứng ba "
     "chức năng cốt lõi của đề tài: phân tích khoảng trống kỹ năng, duyệt kỹ năng tiên quyết "
     "nhiều tầng, và sinh lộ trình học cá nhân hoá. Máy chủ ứng dụng cung cấp mười hai nhóm "
     "API, vượt qua 42 điểm kiểm thử tự động, và cho ra kết quả nghiệp vụ hợp lý trên dữ liệu thật.")
para("Giá trị lớn nhất của việc chọn cơ sở dữ liệu đồ thị thể hiện ở chức năng duyệt tiên quyết: "
     "một câu truy vấn AQL thay thế được nhiều vòng CTE đệ quy, đồng thời diễn đạt đúng bản chất "
     "của bài toán là quan hệ bắc cầu giữa các kỹ năng.")
para("Hướng phát triển tiếp theo gồm: phục hồi dump vào ArangoDB thật trên máy có Docker để "
     "kiểm thử đầu cuối; bổ sung các endpoint ghi dữ liệu để người dùng tự cập nhật kỹ năng; "
     "và mở rộng thuật toán lộ trình bằng cách tính đến thời lượng và chi phí khoá học.")

# ============================================================
# TÀI LIỆU THAM KHẢO
# ============================================================
h("Tài liệu tham khảo")
refs = [
    "ArangoDB GmbH. ArangoDB Documentation 3.12 — AQL, Graph Traversal, Named Graphs.",
    "ArangoDB GmbH. ArangoDB Web Interface User Guide.",
    "FastAPI. FastAPI Documentation — Path Operations, Dependencies, Response Models.",
    "Pydantic. Pydantic v2 Documentation — Field Aliases and Validation.",
    "Kahn, A. B. (1962). Topological sorting of large networks. Communications of the ACM, 5(11).",
    "Tài liệu nghiệp vụ và cơ sở dữ liệu đề tài 1 do nhóm cung cấp.",
]
for i, ref in enumerate(refs, 1):
    p = doc.add_paragraph()
    p.paragraph_format.space_after = Pt(4)
    p.paragraph_format.left_indent = Cm(0.8)
    p.paragraph_format.first_line_indent = Cm(-0.8)
    r = p.add_run(f"[{i}] {ref}")
    r.font.size = Pt(12)
    r.font.name = "Times New Roman"

doc.save(OUT)
print("saved:", OUT)
