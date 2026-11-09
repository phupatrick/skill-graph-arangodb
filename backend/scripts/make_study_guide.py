# -*- coding: utf-8 -*-
"""Sinh tài liệu học tập & thuyết trình: GIAI_THICH_CHI_TIET.docx"""
from docx import Document
from docx.enum.section import WD_ORIENT
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_BREAK
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Pt, RGBColor

OUT = (r"C:\Users\phupu\OneDrive\Documents\deepseek-harness\default-workspace"
       r"\skillgraph\docs\GIAI_THICH_CHI_TIET.docx")

NAVY   = RGBColor(0x14, 0x2B, 0x5E)
BLUE   = RGBColor(0x1F, 0x4E, 0xA8)
GREEN  = RGBColor(0x0E, 0x6B, 0x4E)
RED    = RGBColor(0xA8, 0x1F, 0x2E)
GREY   = RGBColor(0x55, 0x5B, 0x6B)
ORANGE = RGBColor(0xA0, 0x5A, 0x00)

doc = Document()

sec = doc.sections[0]
sec.page_width, sec.page_height = Cm(21.0), Cm(29.7)
sec.top_margin = sec.bottom_margin = Cm(2.0)
sec.left_margin, sec.right_margin = Cm(2.8), Cm(1.8)

st = doc.styles["Normal"]
st.font.name = "Times New Roman"
st.font.size = Pt(12.5)
st.element.rPr.rFonts.set(qn("w:eastAsia"), "Times New Roman")
st.paragraph_format.line_spacing = 1.3
st.paragraph_format.space_after = Pt(5)


# ---------------------------------------------------------------- helpers
def _vi(run, name="Times New Roman"):
    run.font.name = name
    run._element.rPr.rFonts.set(qn("w:eastAsia"), name)


def h1(text, page_break=True):
    if page_break:
        doc.add_paragraph().add_run().add_break(WD_BREAK.PAGE)
    p = doc.add_heading(text, level=1)
    for r in p.runs:
        _vi(r)
        r.font.color.rgb = NAVY
        r.font.size = Pt(17)
        r.font.bold = True
    p.paragraph_format.space_before = Pt(2)
    p.paragraph_format.space_after = Pt(10)
    return p


def h2(text):
    p = doc.add_heading(text, level=2)
    for r in p.runs:
        _vi(r)
        r.font.color.rgb = BLUE
        r.font.size = Pt(13.5)
        r.font.bold = True
    p.paragraph_format.space_before = Pt(11)
    p.paragraph_format.space_after = Pt(4)
    return p


def h3(text):
    p = doc.add_heading(text, level=3)
    for r in p.runs:
        _vi(r)
        r.font.color.rgb = GREEN
        r.font.size = Pt(12.5)
        r.font.bold = True
    p.paragraph_format.space_before = Pt(8)
    p.paragraph_format.space_after = Pt(3)
    return p


def para(text, bold=False, italic=False, size=12.5, color=None,
         align=WD_ALIGN_PARAGRAPH.JUSTIFY, indent=True, space_after=5):
    p = doc.add_paragraph()
    p.alignment = align
    p.paragraph_format.space_after = Pt(space_after)
    if indent:
        p.paragraph_format.first_line_indent = Cm(0.9)
    r = p.add_run(text)
    _vi(r)
    r.font.size = Pt(size)
    r.font.bold = bold
    r.font.italic = italic
    if color is not None:
        r.font.color.rgb = color
    return p


def rich(parts, indent=True, size=12.5, align=WD_ALIGN_PARAGRAPH.JUSTIFY):
    """parts: list of (text, bold, italic, color_or_None)"""
    p = doc.add_paragraph()
    p.alignment = align
    p.paragraph_format.space_after = Pt(5)
    if indent:
        p.paragraph_format.first_line_indent = Cm(0.9)
    for text, b, i, c in parts:
        r = p.add_run(text)
        _vi(r)
        r.font.size = Pt(size)
        r.font.bold = b
        r.font.italic = i
        if c is not None:
            r.font.color.rgb = c
    return p


def bullet(text, size=12, level=0):
    p = doc.add_paragraph(style="List Bullet")
    p.paragraph_format.space_after = Pt(2)
    p.paragraph_format.left_indent = Cm(1.0 + 0.6 * level)
    p.paragraph_format.first_line_indent = Cm(-0.4)
    r = p.add_run(text)
    _vi(r)
    r.font.size = Pt(size)
    return p


_num_counter = {"n": 0}


def reset_num():
    """Goi truoc moi khoi danh sach de bat dau lai tu 1."""
    _num_counter["n"] = 0


def num(text, size=12, restart=False):
    """Danh sach danh so tu viet so (tranh loi Word tiep tuc dem xuyen muc)."""
    if restart:
        _num_counter["n"] = 0
    _num_counter["n"] += 1
    p = doc.add_paragraph()
    p.paragraph_format.space_after = Pt(2)
    p.paragraph_format.left_indent = Cm(1.4)
    p.paragraph_format.first_line_indent = Cm(-0.7)
    r = p.add_run(f"{_num_counter['n']}. ")
    _vi(r)
    r.font.size = Pt(size)
    r.font.bold = True
    r2 = p.add_run(text)
    _vi(r2)
    r2.font.size = Pt(size)
    return p


def code(text, size=10):
    p = doc.add_paragraph()
    p.paragraph_format.left_indent = Cm(0.8)
    p.paragraph_format.space_before = Pt(3)
    p.paragraph_format.space_after = Pt(7)
    p.paragraph_format.line_spacing = 1.1
    r = p.add_run(text)
    _vi(r, "Consolas")
    r.font.size = Pt(size)
    shd = OxmlElement("w:shd")
    shd.set(qn("w:val"), "clear")
    shd.set(qn("w:fill"), "F1F3F7")
    p._p.get_or_add_pPr().append(shd)
    return p


def box(title, lines, fill="FFF4E5", title_color=ORANGE):
    """Khung ghi chú có tiêu đề."""
    t = doc.add_table(rows=1, cols=1)
    t.alignment = WD_TABLE_ALIGNMENT.CENTER
    cell = t.rows[0].cells[0]
    cell.width = Cm(16.4)
    shd = OxmlElement("w:shd")
    shd.set(qn("w:val"), "clear")
    shd.set(qn("w:fill"), fill)
    cell._tc.get_or_add_tcPr().append(shd)
    cell.text = ""
    p0 = cell.paragraphs[0]
    p0.paragraph_format.space_after = Pt(3)
    p0.paragraph_format.keep_with_next = True
    r0 = p0.add_run(title)
    _vi(r0)
    r0.font.size = Pt(12)
    r0.font.bold = True
    r0.font.color.rgb = title_color
    for line in lines:
        p = cell.add_paragraph()
        p.paragraph_format.space_after = Pt(2)
        p.paragraph_format.line_spacing = 1.2
        rr = p.add_run(line)
        _vi(rr)
        rr.font.size = Pt(11.5)


def table(headers, rows, widths=None, size=10.5, head_fill="E4EAF5"):
    t = doc.add_table(rows=1, cols=len(headers))
    t.style = "Table Grid"
    t.alignment = WD_TABLE_ALIGNMENT.CENTER
    t.autofit = False
    layout = OxmlElement("w:tblLayout")
    layout.set(qn("w:type"), "fixed")
    t._tbl.tblPr.append(layout)

    for i, name in enumerate(headers):
        c = t.rows[0].cells[i]
        c.text = ""
        p = c.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.space_after = Pt(2)
        r = p.add_run(name)
        _vi(r)
        r.font.bold = True
        r.font.size = Pt(size)
        shd = OxmlElement("w:shd")
        shd.set(qn("w:val"), "clear")
        shd.set(qn("w:fill"), head_fill)
        c._tc.get_or_add_tcPr().append(shd)

    for row in rows:
        cells = t.add_row().cells
        for i, val in enumerate(row):
            cells[i].text = ""
            p = cells[i].paragraphs[0]
            p.paragraph_format.space_after = Pt(2)
            p.paragraph_format.line_spacing = 1.12
            r = p.add_run(str(val))
            _vi(r)
            r.font.size = Pt(size)

    for row in t.rows:
        trPr = row._tr.get_or_add_trPr()
        trPr.append(OxmlElement("w:cantSplit"))
    hdrPr = t.rows[0]._tr.get_or_add_trPr()
    th = OxmlElement("w:tblHeader")
    th.set(qn("w:val"), "true")
    hdrPr.append(th)

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


def caption(text):
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.space_after = Pt(9)
    r = p.add_run(text)
    _vi(r)
    r.font.size = Pt(10.5)
    r.font.italic = True


def page_break():
    doc.add_paragraph().add_run().add_break(WD_BREAK.PAGE)


# footer: số trang
footer_p = sec.footer.paragraphs[0]
footer_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
run = footer_p.add_run()
_vi(run)
run.font.size = Pt(10)
fld = OxmlElement("w:fldSimple")
fld.set(qn("w:instr"), "PAGE")
run._element.addnext(fld)


# ================================================================
# TRANG BÌA
# ================================================================
p = doc.add_paragraph()
p.alignment = WD_ALIGN_PARAGRAPH.CENTER
r = p.add_run("TÀI LIỆU HỌC TẬP VÀ THUYẾT TRÌNH")
r.font.size = Pt(14); r.font.bold = True; _vi(r)
r.font.color.rgb = GREY

p = doc.add_paragraph()
p.alignment = WD_ALIGN_PARAGRAPH.CENTER
p.paragraph_format.space_before = Pt(18)
r = p.add_run("ĐỒ ÁN SKILL GRAPH\nGIẢI THÍCH CHI TIẾT TỪNG PHẦN ĐÃ LÀM")
r.font.size = Pt(26); r.font.bold = True; _vi(r)
r.font.color.rgb = NAVY

p = doc.add_paragraph()
p.alignment = WD_ALIGN_PARAGRAPH.CENTER
p.paragraph_format.space_before = Pt(10)
r = p.add_run("Dành cho người chưa biết gì về đề tài — đọc xong hiểu và trình bày được")
r.font.size = Pt(13); r.font.italic = True; _vi(r)
r.font.color.rgb = BLUE

doc.add_paragraph()
doc.add_paragraph()

box("TÀI LIỆU NÀY DÙNG ĐỂ LÀM GÌ?", [
    "• Học: giải thích mọi khái niệm từ số 0 — ArangoDB là gì, AQL là gì, đồ thị là gì.",
    "• Hiểu code: từng file, từng hàm làm gì, tại sao phải viết như vậy.",
    "• Thuyết trình: kịch bản nói từng slide, câu chữ cụ thể, phần nào nói gì.",
    "• Bảo vệ: 25 câu hỏi thầy cô hay hỏi kèm câu trả lời mẫu.",
    "• Kiểm tra: các con số thật của hệ thống để không nói sai trước lớp.",
], fill="EAF1FB", title_color=NAVY)

doc.add_paragraph()

table(
    ["Mục", "Nội dung", "Trang"],
    [
        ["1", "Hiểu đề tài trong 5 phút (không cần biết lập trình)", "2"],
        ["2", "Kiến thức nền: database, đồ thị, ArangoDB, AQL", "4"],
        ["3", "Dữ liệu của đồ án: 12 collection, 1.584 bản ghi", "7"],
        ["4", "Bức tranh toàn cảnh: hệ thống chạy thế nào", "9"],
        ["5", "Giải thích từng file code (backend)", "12"],
        ["6", "Bốn thuật toán nghiệp vụ — giải thích bằng ví dụ số", "17"],
        ["7", "30 truy vấn AQL — dùng để làm gì, đọc thế nào", "23"],
        ["8", "Cách chạy hệ thống và demo", "26"],
        ["9", "Kịch bản thuyết trình từng slide (nói gì, nói sao)", "28"],
        ["10", "25 câu hỏi bảo vệ + câu trả lời mẫu", "33"],
        ["11", "Hạn chế và việc còn lại — nói thật với nhóm", "38"],
        ["12", "Bảng tra nhanh tất cả con số", "40"],
    ],
    widths=[1.4, 11.6, 2.0], size=11,
)
caption("Bảng 0.1. Cấu trúc tài liệu — nếu gấp, đọc mục 1, 4, 9, 10")

page_break()

# ================================================================
# 1. HIỂU ĐỀ TÀI TRONG 5 PHÚT
# ================================================================
h1("1. Hiểu đề tài trong 5 phút", page_break=False)

h2("1.1. Vấn đề thật sự cần giải quyết")

para("Hãy tưởng tượng bạn muốn trở thành chuyên viên phân tích dữ liệu "
     "(Data Analyst). Bạn mở mạng lên và thấy hàng trăm bài viết: người bảo phải học "
     "SQL trước, người bảo học Python trước, người bảo phải có Excel, người bảo "
     "phải học thống kê. Bạn không biết ba điều:")

num("Nghề đó yêu cầu chính xác những kỹ năng nào, ở mức độ nào?", restart=True)
num("Mình đang có gì, còn thiếu gì?")
num("Nên học cái nào trước, cái nào sau, học khóa nào?")

para("Đồ án này xây dựng một hệ thống trả lời ba câu hỏi đó một cách tự động. "
     "Đó chính là ý nghĩa của cụm từ “lộ trình học cá nhân hóa”: lộ trình khác nhau "
     "cho từng người, vì mỗi người đã biết những thứ khác nhau.")

h2("1.2. Ví dụ cụ thể để hình dung")

box("VÍ DỤ THẬT TỪ HỆ THỐNG (dùng được khi thuyết trình)", [
    "Người học: Trần Minh (mã user_001).",
    "Nghề mục tiêu: Data Analyst.",
    "Hệ thống trả lời: “Anh cần 11 kỹ năng. Anh đã đạt 3, còn 4 kỹ năng chưa đủ mức "
    "và 4 kỹ năng chưa có. Độ phủ hiện tại là 27,3%.”",
    "Sau đó hệ thống xếp ra thứ tự học: SQL → Python → Pandas → Phân tích dữ liệu khám phá "
    "→ Trực quan hóa dữ liệu → Power BI → Tableau → Làm sạch dữ liệu.",
    "Điểm quan trọng: Pandas được xếp SAU Python, vì muốn học Pandas thì phải biết Python trước. "
    "Hệ thống tự tìm ra quan hệ này, không phải ai đó gõ tay thứ tự.",
], fill="E8F6F0", title_color=GREEN)

h2("1.3. Điểm làm nên đồ án — chữ “Graph”")

para("Nếu chỉ lưu dữ liệu như bảng tính thông thường, hệ thống vẫn làm được câu hỏi số 1 và số 2. "
     "Nhưng câu hỏi số 3 — học cái gì trước — mới là phần khó, vì kỹ năng có quan hệ nhiều tầng với nhau.")

para("Ví dụ: muốn học Deep Learning thì cần Machine Learning. "
     "Nhưng muốn học Machine Learning thì lại cần Statistics, Linear Algebra, Probability và Python. "
     "Và muốn học Statistics thì có thể lại cần Math. Đây là một chuỗi phụ thuộc sâu nhiều tầng.")

rich([("Đó chính là hình dạng của một ", False, False, None),
      ("đồ thị", True, False, RED),
      (" (graph): các điểm nối với nhau bằng các đường. Kỹ năng là điểm, "
       "quan hệ “cần học trước” là đường. Vì vậy đồ án dùng ", False, False, None),
      ("ArangoDB", True, False, RED),
      (" — loại cơ sở dữ liệu lưu được đồ thị một cách tự nhiên — thay vì bảng tính.", False, False, None)])

h2("1.4. Đồ án đã làm ra cái gì (nói ngắn gọn)")

table(
    ["Thành phần", "Là gì", "Trạng thái"],
    [
        ["Cơ sở dữ liệu", "Database ArangoDB tên skill_graph_db, 12 tập dữ liệu, 1.584 bản ghi",
         "Có dữ liệu thật, đã trích sẵn"],
        ["Bộ 30 truy vấn AQL", "30 câu lệnh truy vấn chạy trực tiếp trong ArangoDB Web Interface",
         "Đã viết, đã kiểm tra logic"],
        ["Máy chủ API", "Backend Python (FastAPI) cung cấp 12 nhóm đường dẫn để lấy dữ liệu và tính toán",
         "Chạy được, 42/42 kiểm thử đạt"],
        ["Thuật toán", "Skill Gap, duyệt tiên quyết nhiều tầng, điểm phù hợp nghề, sinh lộ trình",
         "Đã cài đặt, có kết quả thật"],
        ["Giao diện demo", "Trang web hiển thị 4 tab: Skill Gap, Lộ trình, Nghề phù hợp, Đồ thị",
         "Chạy được ở địa chỉ /demo"],
        ["Báo cáo + slide", "File Word 4 chương và slide 10 trang để nộp",
         "Đã xong"],
    ],
    widths=[3.2, 8.6, 3.2], size=10.5,
)
caption("Bảng 1.1. Sản phẩm của đồ án")

box("NÓI THẬT NGAY TỪ ĐẦU", [
    "Máy dùng để phát triển đồ án không cài được Docker nên chưa chạy được ArangoDB thật. "
    "Vì vậy toàn bộ kiểm thử chạy trên dữ liệu đã trích ra từ chính file dump của đề tài "
    "(12 file JSONL, đúng 1.584 bản ghi).",
    "Nghĩa là: logic nghiệp vụ và dữ liệu là thật, chỉ khâu kết nối tới ArangoDB là chưa được "
    "bật thử. Trong code đã có sẵn chế độ “arango”; máy có Docker chỉ cần phục hồi dump rồi đổi "
    "một biến môi trường là chạy.",
    "Khi thuyết trình nên nói rõ điều này — thầy cô đánh giá cao sự trung thực hơn là bị hỏi vặn "
    "rồi mới nhận.",
], fill="FDECEE", title_color=RED)

# ================================================================
# 2. KIẾN THỨC NỀN
# ================================================================
h1("2. Kiến thức nền — giải thích từ số 0")

box("MỤC TIÊU CỦA CHƯƠNG NÀY", [
    "Đọc xong chương này bạn hiểu được các từ khoá mà thầy cô và slide sẽ dùng: "
    "cơ sở dữ liệu, document, graph, vertex, edge, collection, traversal, AQL, "
    "index, REST API, JSON. Không cần học thuộc — chỉ cần hiểu để không bị hỏi vặn.",
], fill="EAF1FB", title_color=NAVY)

h2("2.1. Cơ sở dữ liệu là gì, nhắc lại thật nhanh")

para("Cơ sở dữ liệu (database) là phần mềm giúp lưu dữ liệu xuống ổ cứng và tìm lại nhanh. "
     "Bạn không dùng file Excel vì Excel không chịu được nhiều người truy cập cùng lúc, "
     "không đảm bảo dữ liệu không bị hỏng, và tìm kiếm trên triệu dòng thì rất chậm.")

para("Có bốn kiểu cơ sở dữ liệu phổ biến, chia theo cách tổ chức dữ liệu:")

table(
    ["Kiểu", "Tổ chức dữ liệu", "Ví dụ phần mềm", "Dùng khi nào"],
    [
        ["Quan hệ (relational)", "Bảng có cột cố định, các bảng nối bằng khoá ngoại",
         "MySQL, PostgreSQL, SQL Server", "Dữ liệu có cấu trúc chặt, cần ràng buộc mạnh"],
        ["Tài liệu (document)", "Lưu cả khối JSON, mỗi bản ghi có cấu trúc riêng",
         "MongoDB, CouchDB", "Dữ liệu đa dạng, mỗi bản ghi khác nhau"],
        ["Đồ thị (graph)", "Điểm (đỉnh) và đường nối (cạnh)",
         "Neo4j, ArangoDB", "Quan hệ quan trọng hơn thuộc tính, cần duyệt nhiều tầng"],
        ["Khoá – giá trị", "Tra cứu theo khoá", "Redis", "Bộ nhớ đệm, tốc độ cực nhanh"],
    ],
    widths=[3.4, 4.8, 3.6, 4.0], size=10,
)
caption("Bảng 2.1. Bốn kiểu cơ sở dữ liệu")

para("ArangoDB là loại thứ năm: đa mô hình (multi-model) — làm được cả tài liệu, cả đồ thị, "
     "cả khoá–giá trị trong cùng một phần mềm, dùng chung một ngôn ngữ truy vấn. "
     "Đây là lý do đề tài chọn nó.")

h2("2.2. Đồ thị: đỉnh và cạnh")

para("Đừng nghĩ đồ thị là biểu đồ cột hay đường. Trong khoa học máy tính, "
     "đồ thị (graph) chỉ đơn giản là: một tập các điểm, và một tập các đường nối giữa các điểm.")

table(
    ["Thuật ngữ", "Tên khác", "Nghĩa", "Trong đồ án này"],
    [
        ["Đỉnh", "Vertex, Node", "Một điểm trong đồ thị", "Một người dùng, một kỹ năng, một nghề, một khóa học"],
        ["Cạnh", "Edge, Relation", "Một đường nối hai đỉnh", "“user_001 biết Python, trình độ 45”"],
        ["Hướng", "Direction", "Cạnh có mũi tên hay không",
         "Có hướng: A → B khác B → A"],
        ["Bậc", "Degree", "Số cạnh nối vào một đỉnh", "Python có nhiều cạnh prerequisite trỏ vào"],
        ["Đường đi", "Path", "Chuỗi đỉnh nối tiếp nhau", "Deep Learning → ML → Python"],
        ["Chu trình", "Cycle", "Đường đi quay về đỉnh xuất phát", "A cần B, B cần A — dữ liệu lỗi"],
    ],
    widths=[2.6, 3.0, 4.6, 5.6], size=10,
)
caption("Bảng 2.2. Từ vựng đồ thị — nhớ 6 từ này là đủ")

para("Mỗi cạnh trong ArangoDB bắt buộc có hai trường: _from (đỉnh xuất phát) và _to (đỉnh đích). "
     "Ví dụ một cạnh prerequisite trong dữ liệu thật:")

code('{\n'
     '  "_id": "prerequisite/12345",\n'
     '  "_from": "skills/pandas",        ← kỹ năng MUỐN học\n'
     '  "_to":   "skills/python",        ← kỹ năng CẦN có trước\n'
     '  "relation": "prerequisite",\n'
     '  "strength": "recommended"\n'
     '}')

box("QUY ƯỚC DỄ SAI NHẤT CỦA CẢ ĐỒ ÁN", [
    "Cạnh prerequisite: _from là kỹ năng MUỐN HỌC, _to là kỹ năng CẦN CÓ TRƯỚC.",
    "Đọc xuôi “pandas → python” phải hiểu là “muốn Pandas thì cần Python”, KHÔNG phải "
    "“học Pandas xong thì biết Python”.",
    "Nếu đọc ngược chiều này, thuật toán sinh lộ trình sẽ cho ra thứ tự sai hoàn toàn: "
    "dạy Pandas trước Python. Đây là lỗi phổ biến nhất khi làm đề tài dạng này, và cũng là "
    "câu hỏi thầy cô rất hay dùng để kiểm tra.",
    "Cách nhớ: giống dấu “⊃” — cái to cần cái nhỏ bên trong.",
], fill="FDECEE", title_color=RED)

h2("2.3. Collection, document, và cấu trúc lưu trữ của ArangoDB")

para("Trong ArangoDB, dữ liệu được chia vào các thùng gọi là collection. "
     "Có hai loại collection:")

bullet("Collection đỉnh (vertex collection): chứa các bản ghi bình thường, mỗi bản ghi là một khối JSON.")
bullet("Collection cạnh (edge collection): chứa các cạnh, mỗi bản ghi buộc phải có _from và _to.")

para("Mỗi bản ghi có một khoá _key (ví dụ python) và một định danh đầy đủ _id "
     "gồm tên collection + dấu gạch chéo + khoá (ví dụ skills/python). "
     "Trong đồ án này, khoá được đặt là chữ có nghĩa thay vì số ngẫu nhiên, "
     "để khi demo đọc lên là hiểu ngay: skills/python, skills/pandas, careers/data_analyst.")

para("Ngoài ra còn có khái niệm named graph — một đăng ký gom nhiều collection lại thành "
     "một đồ thị có tên. Đồ án đăng ký một graph tên skill_graph gồm 5 collection đỉnh "
     "và 7 collection cạnh. Lợi ích: câu truy vấn không phải liệt kê từng collection, "
     "và giao diện ArangoDB vẽ được đồ thị trực quan.")

h2("2.4. AQL là gì và đọc một câu AQL thế nào")

para("AQL là viết tắt của ArangoDB Query Language — ngôn ngữ để hỏi cơ sở dữ liệu. "
     "Nó có dạng giống câu tiếng Anh: FOR mỗi phần tử, FILTER lọc, SORT sắp xếp, "
     "LIMIT giới hạn, RETURN trả về. Đọc từ trên xuống là hiểu.")

code('FOR s IN skills                    // với mỗi s trong danh sách skills\n'
     '  FILTER s.category == "Programming"   // chỉ lấy kỹ năng nhóm lập trình\n'
     '  SORT s.name                          // sắp theo tên\n'
     '  LIMIT 5                              // lấy 5 cái đầu\n'
     '  RETURN s.name                        // trả về tên')

para("Phần thú vị nhất là traversal — toán tử duyệt đồ thị. Đây là thứ mà SQL không có:")

code('FOR v, e, p IN 1..5 INBOUND s prerequisite\n'
     '  RETURN v')

table(
    ["Thành phần", "Nghĩa"],
    [
        ["FOR v, e, p", "v = đỉnh tìm được, e = cạnh vừa đi qua, p = cả đường đi"],
        ["IN 1..5", "đi sâu từ 1 tới 5 tầng"],
        ["INBOUND", "đi NGƯỢC chiều mũi tên (tìm cái cần có trước)"],
        ["s prerequisite", "từ đỉnh s, đi theo collection cạnh prerequisite"],
        ["RETURN v", "trả về các đỉnh tìm được"],
    ],
    widths=[3.6, 12.8], size=10.5,
)
caption("Bảng 2.3. Đọc một câu traversal")

rich([("Một câu lệnh như trên thay thế cho nhiều vòng lặp lồng nhau trong SQL. "
       "Đây là câu trả lời chuẩn khi bị hỏi “vì sao chọn graph database”.", False, False, None)])

h2("2.5. REST API, JSON, và vì sao cần backend")

para("API là cách hai chương trình nói chuyện với nhau. REST API là kiểu phổ biến nhất: "
     "bên gọi gửi một yêu cầu HTTP tới một đường dẫn (URL), bên nhận trả về dữ liệu, "
     "thường ở dạng JSON (một khối text có ngoặc nhọn, giống object trong lập trình).")

para("Một điểm cần hiểu rõ để trả lời khi bảo vệ: trình duyệt không được nối thẳng vào "
     "ArangoDB. Có ba lý do:")

num("Bảo mật: muốn nối thẳng phải nhúng mật khẩu database vào mã JavaScript — ai mở "
    "trang web cũng đọc được, và có thể xoá sạch dữ liệu.", restart=True)
num("Kiểm soát: nếu cho nối thẳng, người dùng có thể gửi bất kỳ câu truy vấn nào, "
    "kể cả truy vấn xoá toàn bộ dữ liệu.", restart=True)
num("Nghiệp vụ: các phép tính như Skill Gap, lộ trình học phải chạy ở đâu đó. "
    "Đặt ở backend thì viết một lần bằng Python, dễ kiểm thử; đặt ở trình duyệt thì "
    "mỗi loại trình duyệt một kiểu, và lộ logic ra ngoài.", restart=True)

para("Vì vậy kiến trúc là: Trình duyệt → gọi API → Backend Python → gửi AQL → ArangoDB. "
     "Backend đóng vai trò người gác cửa và người tính toán.")

box("CÂU HỎI TỰ KIỂM TRA CHƯƠNG 2", [
    "1. Đỉnh và cạnh khác nhau thế nào? Cho ví dụ trong đồ án.",
    "2. Cạnh prerequisite pandas → python nghĩa là gì? (Trả lời: muốn học Pandas thì cần Python.)",
    "3. INBOUND khác OUTBOUND thế nào? (INBOUND đi ngược mũi tên — tìm cái cần có trước.)",
    "4. Vì sao không cho trình duyệt nối thẳng database? (Ba lý do: bảo mật, kiểm soát, nghiệp vụ.)",
], fill="EAF1FB", title_color=NAVY)

# ================================================================
# 3. DỮ LIỆU
# ================================================================
h1("3. Dữ liệu của đồ án — đọc hiểu từng con số")

para("Chương này quan trọng vì khi thuyết trình bạn sẽ phải nói về dữ liệu. "
     "Nói đúng số liệu tạo cảm giác mình thực sự làm, không phải chép.")

h2("3.1. Mười hai collection và số bản ghi thật")

table(
    ["Collection", "Loại", "Số bản ghi", "Nghĩa", "Ví dụ một bản ghi"],
    [
        ["users", "Đỉnh", "40", "Người học", "user_001 — Tran Minh"],
        ["skills", "Đỉnh", "248", "Kỹ năng", "skills/python — Python"],
        ["careers", "Đỉnh", "29", "Nghề nghiệp", "careers/data_analyst"],
        ["courses", "Đỉnh", "89", "Khóa học", "course_001 — SQL Fundamentals"],
        ["providers", "Đỉnh", "8", "Nhà cung cấp khóa học", "Coursera, edX, Kaggle Learn…"],
        ["has_skill", "Cạnh", "274", "User biết Skill", "user_001 → python, 45/100"],
        ["targets_career", "Cạnh", "40", "User nhắm Career", "user_001 → data_analyst"],
        ["requires_skill", "Cạnh", "312", "Career yêu cầu Skill", "data_analyst → sql, mức 70"],
        ["prerequisite", "Cạnh", "173", "Skill cần Skill trước", "pandas → python"],
        ["teaches", "Cạnh", "172", "Course dạy Skill", "course_001 → sql"],
        ["completed", "Cạnh", "110", "User hoàn thành Course", "user_001 → course_012"],
        ["offered_by", "Cạnh", "89", "Course do Provider cấp", "course_001 → Coursera"],
    ],
    widths=[2.7, 1.4, 1.9, 3.4, 7.0], size=9.5,
)
caption("Bảng 3.1. Mười hai collection — tổng 1.584 bản ghi")

rich([("Con số cần nhớ: ", False, False, None),
      ("5 collection đỉnh + 7 collection cạnh = 12 collection, tổng 1.584 bản ghi", True, False, NAVY),
      (". Đây là con số khớp với tài liệu nghiệp vụ của đề tài.", False, False, None)])

h2("3.2. Vài thống kê dùng được khi nói về dữ liệu")

table(
    ["Thông tin", "Giá trị", "Ý nghĩa khi thuyết trình"],
    [
        ["Số kỹ năng", "248", "Chia thành nhiều nhóm: Data Science & AI (38), Cloud & DevOps (31), "
                              "Database & Data (30), Software Engineering & QA (28), Web (25)…"],
        ["Số cạnh prerequisite", "173", "Đủ dày để thuật toán duyệt nhiều tầng có ý nghĩa"],
        ["Số khóa học", "89", "Trình độ: Trung cấp 51, Cơ bản 26, Nâng cao 12"],
        ["Số nhà cung cấp", "8", "Coursera, edX, MIT OpenCourseWare, freeCodeCamp, "
                                 "Microsoft Learn, Google Cloud Skills Boost, "
                                 "Cisco Networking Academy, Kaggle Learn"],
        ["Kỹ năng KHÔNG có khóa học nào dạy", "145 / 248", "Đây là phát hiện đáng nói: dữ liệu "
                                                          "không phủ hết, hệ thống vẫn xử lý được (ghi rõ “chưa có khóa học”)"],
        ["Lượt khai báo kỹ năng dưới mức 50", "51 / 274", "Cho thấy nhiều người đang ở mức nhập môn"],
        ["Trạng thái các khóa đã học", "110 đều là completed", "Không có khóa đang học dở trong dữ liệu mẫu"],
    ],
    widths=[4.4, 2.6, 9.4], size=10,
)
caption("Bảng 3.2. Thống kê dữ liệu — dùng để trả lời “dữ liệu có đủ lớn không?”")

h2("3.3. Dữ liệu này từ đâu ra — trả lời trung thực")

para("Trường data_origin của dữ liệu ghi là synthetic_demo. Nghĩa là dữ liệu mẫu "
     "được tạo cho mục đích đồ án, không phải dữ liệu người thật, cũng không phải "
     "trích trực tiếp từ hệ thống của trường. Tuy vậy nó không phải dữ liệu rác:")

bullet("Tên kỹ năng, tên nghề tham chiếu theo khung năng lực quốc tế ESCO và O*NET "
       "(hai bộ khung phân loại kỹ năng nghề nghiệp phổ biến), nên tên gọi có nghĩa thật.")
bullet("Có đủ cấu trúc để kiểm thử: 40 người, 29 nghề, 173 cạnh tiên quyết — tức là "
       "thuật toán duyệt nhiều tầng thực sự có việc để làm.")
bullet("Trường importance và required_level chỉ là mức liên quan giữa kỹ năng và nghề, "
       "không hàm ý một người cụ thể đã được công nhận năng lực.")

box("NẾU BỊ HỎI “DỮ LIỆU THẬT KHÔNG?”", [
    "Trả lời: “Dữ liệu là dữ liệu mẫu của đề tài, gắn nhãn synthetic_demo. "
    "Nhóm không nói đây là dữ liệu người thật. Tuy vậy cấu trúc và quy mô đúng theo tài liệu "
    "nghiệp vụ: 12 collection, 1.584 bản ghi, 173 quan hệ tiên quyết — đủ để chứng minh "
    "thuật toán chạy đúng. Nếu có dữ liệu thật, nhóm chỉ cần thay nguồn dữ liệu, phần code "
    "không phải sửa vì đã tách lớp lưu trữ.”",
], fill="FFF4E5", title_color=ORANGE)

h2("3.4. Ba thang đo cần phân biệt")

table(
    ["Tên trường", "Nằm ở cạnh nào", "Thang", "Nghĩa"],
    [
        ["proficiency", "has_skill", "0 – 100", "Người học tự khai mình đang ở mức nào"],
        ["required_level", "requires_skill", "0 – 100", "Nghề yêu cầu mức tối thiểu bao nhiêu"],
        ["importance", "requires_skill", "0 – 100", "Kỹ năng này quan trọng đến mức nào với nghề"],
        ["requirement_type", "requires_skill", "essential / optional", "Bắt buộc hay chỉ là lợi thế"],
        ["strength", "prerequisite", "recommended", "Mức khuyến nghị của quan hệ tiên quyết"],
    ],
    widths=[3.4, 3.2, 3.6, 6.2], size=10,
)
caption("Bảng 3.3. Ba thang đo — đừng lẫn proficiency với required_level")

box("NÓI ĐÚNG KHI THUYẾT TRÌNH", [
    "Nói: “proficiency là trình độ hiện có của người học, required_level là mức nghề yêu cầu. "
    "Hai con số cùng thang 0–100 nên so sánh được trực tiếp.”",
    "Đừng nói: “điểm 70 nghĩa là giỏi” — 70 chỉ có nghĩa khi so với một mức yêu cầu cụ thể.",
    "Khi một yêu cầu không ghi required_level, hệ thống dùng mặc định 50 và ghi rõ trong phản hồi, "
    "không tự cho là đã đạt.",
], fill="E8F6F0", title_color=GREEN)

# ================================================================
# 4. BỨC TRANH TOÀN CẢNH
# ================================================================
h1("4. Bức tranh toàn cảnh — hệ thống chạy thế nào")

h2("4.1. Sơ đồ ba tầng")

code('┌──────────────────────────────────────────────────────────┐\n'
     '│  TẦNG 1 — TRÌNH DUYỆT (người dùng nhìn thấy)             │\n'
     '│  Trang /demo — 4 tab: Skill Gap | Lộ trình | Nghề | Đồ thị│\n'
     '└───────────────────────┬──────────────────────────────────┘\n'
     '                        │  HTTP + JSON\n'
     '┌───────────────────────▼──────────────────────────────────┐\n'
     '│  TẦNG 2 — BACKEND FastAPI (Python)                       │\n'
     '│  12 nhóm đường dẫn API  +  4 thuật toán nghiệp vụ        │\n'
     '│  ★ đây là nơi mọi phép tính xảy ra                       │\n'
     '└───────────────────────┬──────────────────────────────────┘\n'
     '                        │  AQL qua HTTP\n'
     '┌───────────────────────▼──────────────────────────────────┐\n'
     '│  TẦNG 3 — ArangoDB  (database skill_graph_db)            │\n'
     '│  12 collection, 1.584 bản ghi, graph tên skill_graph     │\n'
     '└──────────────────────────────────────────────────────────┘')

para("Khi demo, bạn chỉ cần nói: “Trình duyệt gọi API, backend tính toán rồi hỏi database bằng AQL. "
     "Ba tầng tách nhau nên thay tầng nào cũng được mà không phá tầng khác.”")

h2("4.2. Một đường đi cụ thể — từ cú click tới kết quả")

para("Đây là phần rất đáng nói khi thuyết trình, vì nó chứng minh bạn hiểu hệ thống chứ không "
     "chỉ chạy được. Hãy kể theo trình tự sau khi bấm tab “Lộ trình học”:")

num("Trình duyệt gửi: GET /api/v1/users/user_001/learning-path?career=data_analyst", restart=True)
num("FastAPI nhận yêu cầu, tìm hàm xử lý tương ứng trong routers/analysis.py. "
    "Pydantic kiểm tra tham số: max_steps phải từ 1 đến 50.")
num("Hàm gọi core.learning_path(\"user_001\", \"data_analyst\").")
num("Bên trong core, bước 1: gọi skill_gap() — lấy 11 yêu cầu của nghề và so với trình độ user.")
num("Bước 2: với mỗi kỹ năng còn thiếu, gọi prerequisite_closure() để leo ngược tìm kỹ năng nền.")
num("Bước 3: sắp xếp topo để kỹ năng nền đứng trước.")
num("Bước 4: với mỗi bước, tìm khóa học qua cạnh teaches, trừ các khóa đã có cạnh completed.")
num("Kết quả được chuyển qua mappers.py để đổi tên trường từ snake_case sang camelCase "
    "(ví dụ required_level → requiredLevel) cho phía giao diện dễ dùng.")
num("FastAPI đóng gói thành JSON và trả về. Trình duyệt vẽ ra 8 bước.")

box("ĐIỂM ĂN TIỀN KHI KỂ ĐOẠN NÀY", [
    "“Thầy cô thấy ở bước 4, hệ thống không đề xuất lại khóa đã học — vì có một phép trừ dựa trên "
    "cạnh completed. Và ở bước 3, thứ tự không phải theo bảng chữ cái mà theo quan hệ phụ thuộc thật.”",
], fill="EAF1FB", title_color=NAVY)

h2("4.3. Vì sao code chia hai lớp: nghiệp vụ và lưu trữ")

para("Đây là quyết định thiết kế quan trọng nhất trong code, nên phải hiểu để trả lời khi bị hỏi.")

para("Tưởng tượng bạn viết hàm tính Skill Gap. Hàm đó cần lấy dữ liệu. Nếu bên trong hàm gọi "
     "thẳng ArangoDB thì mỗi lần muốn kiểm thử phải có ArangoDB đang chạy. "
     "Cách làm tốt hơn: định nghĩa bốn hàm lấy dữ liệu, rồi viết hai phiên bản.")


# mini architecture table
t = table(
    ["Lớp", "File", "Nhiệm vụ", "Biết gì về database?"],
    [
        ["Nghiệp vụ", "app/data/core.py", "Skill Gap, duyệt tiên quyết, điểm phù hợp, lộ trình học",
         "KHÔNG biết gì — chỉ gọi 4 hàm trừu tượng"],
        ["Lưu trữ", "app/data/storage.py", "Đọc dữ liệu từ JSONL hoặc từ ArangoDB",
         "Biết hết"],
    ],
    widths=[2.6, 4.4, 6.2, 4.0], size=10,
)
caption("Bảng 4.1. Hai lớp — nghiệp vụ không biết dữ liệu từ đâu")

para("Bốn hàm đó là: vertices(tên collection) lấy danh sách đỉnh; vertex(collection, khoá) lấy một đỉnh; "
     "edges(collection, đầu này, đầu kia) lấy danh sách cạnh; counts() đếm số bản ghi mỗi collection.")

table(
    ["Lớp cài đặt", "Đọc từ", "Dùng khi nào", "Tốc độ"],
    [
        ["JsonlStorage", "12 file .jsonl trong thư mục data/", "Kiểm thử tự động, demo khi chưa cài ArangoDB",
         "Tải hết vào RAM, tra cứu tức thì"],
        ["ArangoStorage", "ArangoDB qua HTTP + AQL", "Khi đã phục hồi dump, chạy thật", "Phụ thuộc mạng, "
                                                                                          "chỉ lấy đúng phần cần"],
    ],
    widths=[3.0, 5.0, 5.4, 4.0], size=10,
)
caption("Bảng 4.2. Hai cách đọc dữ liệu, cùng một giao diện")

para("Cách làm này có tên trong sách giáo khoa: Repository Pattern. Lợi ích thực tế với đồ án: "
     "nhóm viết nghiệp vụ một lần, kiểm thử 42 điểm chạy được ngay trên máy không có Docker, "
     "và khi có ArangoDB chỉ cần đổi biến môi trường SKILLGRAPH_DATA_MODE=arango.")

h2("4.4. Bốn chế độ dữ liệu")

table(
    ["Giá trị biến môi trường", "Hành vi", "Dùng khi nào"],
    [
        ["auto (mặc định)", "Thử kết nối ArangoDB trước; không được thì đọc JSONL", "Chạy trên máy bất kỳ"],
        ["jsonl", "Chỉ đọc file JSONL", "Kiểm thử, demo offline"],
        ["arango", "Chỉ dùng ArangoDB, kết nối lỗi thì báo lỗi ngay", "Khi đã phục hồi dump, muốn chắc "
                                                                    "chắn dữ liệu từ DB"],
    ],
    widths=[4.4, 7.0, 6.0], size=10,
)
caption("Bảng 4.3. Ba chế độ — auto là mặc định an toàn")

box("VÌ SAO CẦN CHẾ ĐỘ arango BÁO LỖI NGAY?", [
    "Nếu để auto mà ArangoDB chết, hệ thống lặng lẽ đọc file JSONL và vẫn trả kết quả — "
    "bạn sẽ tưởng mình đang demo trên database thật trong khi không phải. "
    "Chế độ arango cố tình làm khó: không kết nối được là dừng, báo lỗi rõ. "
    "Đây là chi tiết nhỏ nhưng thể hiện sự cẩn thận khi làm việc với dữ liệu.",
], fill="FFF4E5", title_color=ORANGE)

# ================================================================
# 5. GIẢI THÍCH TỪNG FILE CODE
# ================================================================
h1("5. Giải thích từng file code — backend")

para("Chương này đi qua từng file theo đúng thứ tự bạn nên đọc. "
     "Với mỗi file: nó làm gì, tại sao cần nó, và câu then chốt để trả lời nếu bị hỏi.")

h2("5.1. Cây thư mục")

code('skillgraph/\n'
     '├── backend/\n'
     '│   ├── app/\n'
     '│   │   ├── main.py         ★ khởi động ứng dụng, đăng ký mọi thứ\n'
     '│   │   ├── config.py         đọc biến môi trường\n'
     '│   │   ├── schema.py         hằng số: tên collection, giới hạn\n'
     '│   │   ├── errors.py         định dạng lỗi thống nhất\n'
     '│   │   ├── models.py         khuôn dữ liệu trả về (Pydantic)\n'
     '│   │   ├── mappers.py        đổi tên trường snake_case → camelCase\n'
     '│   │   ├── deps.py           tạo một core dùng chung\n'
     '│   │   ├── data/\n'
     '│   │   │   ├── storage.py    hai cách đọc dữ liệu\n'
     '│   │   │   └── core.py     ★★ TOÀN BỘ NGHIỆP VỤ Ở ĐÂY\n'
     '│   │   ├── routers/          đường dẫn API chia theo chủ đề\n'
     '│   │   └── static/index.html  giao diện demo (1 file, không build)\n'
     '│   ├── scripts/\n'
     '│   │   ├── extract_dump.py   trích dump ArangoDB ra JSONL\n'
     '│   │   ├── smoke_test.py    42 điểm kiểm thử\n'
     '│   │   ├── make_report.py   sinh báo cáo Word\n'
     '│   │   └── make_slides.py   sinh slide\n'
     '│   ├── run.py              chạy server (1 dòng)\n'
     '│   └── requirements.txt\n'
     '├── data/                   12 file .jsonl + manifest.json\n'
     '├── queries/aql_queries.aql  30 truy vấn AQL\n'
     '├── docs/                   báo cáo, slide, tài liệu này\n'
     '├── docker-compose.yml      dựng ArangoDB bằng 1 lệnh\n'
     '└── README.md              hướng dẫn chạy\n')

h2("5.2. config.py — cấu hình")

para("Đọc các biến môi trường để biết: chế độ dữ liệu nào, thư mục dữ liệu ở đâu, "
     "ArangoDB nằm ở địa chỉ nào, tài khoản gì, thời gian chờ bao lâu, và những trang web nào "
     "được phép gọi API (CORS).")

rich([("Câu then chốt: ", False, False, None),
      ("“Mọi thứ cấu hình đưa ra biến môi trường, không viết cứng trong code — "
       "nhờ vậy cùng một bộ code chạy được trên máy cá nhân và trên server mà không phải sửa file.”",
       True, False, NAVY)])

para("CORS là danh sách những địa chỉ web được phép gọi API. Nếu không khai báo, "
     "trình duyệt sẽ chặn vì lý do an toàn. Đây là khái niệm hay bị hỏi.")

h2("5.3. schema.py — một chỗ duy nhất khai báo sự thật về dữ liệu")

para("File rất ngắn nhưng quan trọng: nó gom mọi hằng số về cấu trúc dữ liệu vào một chỗ.")

table(
    ["Hằng số", "Giá trị", "Ý nghĩa"],
    [
        ["DATABASE_NAME", "skill_graph_db", "Tên database — khớp với dump của đề tài"],
        ["GRAPH_NAME", "skill_graph", "Tên named graph đã đăng ký"],
        ["VERTEX_COLLECTIONS", "5 tên", "users, skills, careers, courses, providers"],
        ["EDGE_COLLECTIONS", "7 tên", "has_skill, targets_career, requires_skill, prerequisite, "
                                      "teaches, completed, offered_by"],
        ["MIN/MAX/DEFAULT_GRAPH_LIMIT", "5 / 500 / 120", "Giới hạn số đỉnh trả về ở API đồ thị — "
                                                         "chống treo trình duyệt nếu đồ thị quá lớn"],
    ],
    widths=[4.6, 2.8, 9.0], size=10,
)
caption("Bảng 5.1. Những gì khai báo trong schema.py")

para("Lợi ích: nếu đề tài đổi tên collection, chỉ sửa một dòng. Không có chỗ nào trong code "
     "viết cứng chuỗi \"has_skill\" rải rác — đó là cách tránh lỗi gõ sai tên.")

h2("5.4. errors.py — định dạng lỗi thống nhất")

para("Khi có lỗi, hệ thống luôn trả về cùng một khuôn:")

code('{\n'
     '  "error": {\n'
     '    "code": "not_found",\n'
     '    "message": "Không tìm thấy người dùng: user_999"\n'
     '  }\n'
     '}')

para("Vì sao cần: nếu mỗi chỗ trả lỗi một kiểu, giao diện phải viết nhiều đoạn xử lý khác nhau. "
     "Có khuôn chung thì giao diện chỉ cần đọc error.message là hiển thị được. "
     "Đây là yêu cầu của bản hợp đồng API mà đề tài đưa ra.")

para("File này cũng đăng ký các hàm xử lý lỗi toàn cục: lỗi do mình chủ động ném ra "
     "(ApiError), lỗi kiểm tra tham số của FastAPI (422), và lỗi không lường trước (500). "
     "Tất cả được đưa về cùng một khuôn.")

h2("5.5. models.py — khuôn dữ liệu trả về")

para("Đây là file khai báo các lớp Pydantic. Hiểu đơn giản: mỗi lớp là một bản thiết kế mô tả "
     "JSON sẽ trả về có trường gì, kiểu gì, có bắt buộc không.")

para("Ví dụ lớp mô tả một bước trong lộ trình học có các trường: order (thứ tự), skill (kỹ năng), "
     "requiredLevel (mức nghề yêu cầu), currentLevel (mức hiện có), gapLevel (còn thiếu bao nhiêu), "
     "reason (vì sao bước này có mặt), prerequisiteOf (kỹ năng nào cần kỹ năng này trước), "
     "recommendedCourses (khóa học gợi ý).")

rich([("Vì sao viết hoa chữ giữa (camelCase) mà không phải snake_case? Vì JavaScript — ngôn ngữ của "
       "trình duyệt — theo quy ước camelCase, còn Python theo snake_case. File ", False, False, None),
      ("mappers.py", True, False, None),
      (" lo phần đổi tên, nên database giữ snake_case còn API trả ra camelCase. "
       "Đây là chi tiết nhỏ nhưng thể hiện hiểu biết về hợp đồng API.", False, False, None)])

para("Lợi ích của Pydantic: FastAPI tự kiểm tra kiểu. Nếu code trả về thiếu trường bắt buộc, "
     "hệ thống báo lỗi ngay khi phát triển, chứ không để giao diện nhận dữ liệu hỏng. "
     "Ngoài ra FastAPI tự sinh tài liệu Swagger từ các lớp này — đó là lý do mở /docs là thấy "
     "đầy đủ mọi API kèm ví dụ.")

h2("5.6. storage.py — hai cách đọc dữ liệu")

para("File dài thứ hai trong dự án. Cấu trúc gồm:")

bullet("Một giao diện (Protocol) tên Storage khai báo bốn hàm bắt buộc. "
       "Đây là “hợp đồng” mà mọi lớp lưu trữ phải theo.")
bullet("Lớp JsonlStorage: khi khởi tạo thì đọc 12 file .jsonl vào bộ nhớ, "
       "xây ba bảng tra cứu: theo _id, theo đầu _from, theo cuối _to. "
       "Nhờ vậy tìm một đỉnh hay các cạnh của một đỉnh là tra bảng, tức thì.")
bullet("Lớp ArangoStorage: gửi câu AQL qua HTTP tới ArangoDB, đọc kết quả theo từng lô "
       "(cursor) để không tải hết một lần nếu dữ liệu lớn. Có hàm ping() để kiểm tra kết nối.")
bullet("Hàm build_storage(settings) quyết định dùng lớp nào dựa vào biến môi trường, "
       "và trả kèm thông tin chẩn đoán để API /health hiển thị.")

box("CHI TIẾT ĐÁNG NÓI: VÌ SAO PHẢI ĐỌC THEO LÔ (CURSOR)?", [
    "ArangoDB không trả hết kết quả trong một lần nếu kết quả lớn; nó trả một ít kèm một con trỏ, "
    "hỏi tiếp thì trả lô nữa. Code phải lặp cho tới khi hết. Nếu không làm, dữ liệu lớn sẽ bị cắt cụt "
    "mà không báo lỗi — kiểu lỗi rất khó tìm.",
], fill="FFF4E5", title_color=ORANGE)

h2("5.7. core.py — trái tim của đồ án")

para("Đây là file quan trọng nhất, khoảng 27 KB. Nó chứa toàn bộ nghiệp vụ và không biết gì về "
     "database. Chương 6 sẽ giải thích từng thuật toán bằng ví dụ số; ở đây chỉ cần nắm bản đồ "
     "các hàm:")

table(
    ["Nhóm hàm", "Tên", "Làm gì"],
    [
        ["Đọc cơ bản", "list_users / get_user", "Danh sách và chi tiết người học"],
        ["", "list_skills / get_skill", "Danh sách và chi tiết kỹ năng"],
        ["", "list_careers / get_career", "Danh sách và chi tiết nghề"],
        ["", "list_courses / get_course", "Danh sách và chi tiết khóa học"],
        ["", "list_providers", "Danh sách nhà cung cấp"],
        ["Quan hệ", "user_skills(user)", "Kỹ năng của một người (cạnh has_skill)"],
        ["", "career_requirements(career)", "Kỹ năng nghề yêu cầu (cạnh requires_skill)"],
        ["", "courses_for_skill(skill)", "Khóa học dạy kỹ năng này (cạnh teaches)"],
        ["★ Thuật toán", "skill_gap(user, career)", "Phân tích còn thiếu gì"],
        ["★", "prerequisite_closure(skill)", "Duyệt toàn bộ kỹ năng nền nhiều tầng"],
        ["★", "career_match(user)", "Chấm điểm phù hợp với từng nghề"],
        ["★", "learning_path(user, career)", "Sinh lộ trình học có thứ tự"],
        ["Đồ thị", "graph_neighborhood(focus, mode)", "Lấy đồ thị con để vẽ"],
    ],
    widths=[3.0, 5.4, 8.0], size=10,
)
caption("Bảng 5.2. Bản đồ các hàm trong core.py — bốn hàm có dấu ★ là phần ăn điểm")

h2("5.8. deps.py — tạo một core dùng chung")

para("Nếu mỗi yêu cầu API đều tạo một core mới thì mỗi lần lại phải đọc lại 12 file dữ liệu — "
     "rất chậm. File này dùng cơ chế lưu kết quả (lru_cache) để cả ứng dụng dùng chung một core. "
     "Có hàm core_from_request để lấy core từ trạng thái ứng dụng, và hàm reset_core_cache "
     "để kiểm thử có thể làm mới khi đổi biến môi trường.")

h2("5.9. routers/ — chia đường dẫn theo chủ đề")

table(
    ["File", "Đường dẫn", "Chức năng"],
    [
        ["meta.py", "/api/v1/meta/health, /release", "Tình trạng hệ thống, số bản ghi từng collection"],
        ["users.py", "/api/v1/users, /{key}, /{key}/skills, /targets, /completed",
         "Người học và các quan hệ của họ"],
        ["skills.py", "/api/v1/skills, /{key}, /{key}/prerequisites, /{key}/courses",
         "Kỹ năng, kỹ năng nền, khóa học dạy kỹ năng"],
        ["careers.py", "/api/v1/careers, /{key}", "Nghề nghiệp kèm yêu cầu kỹ năng"],
        ["courses.py", "/api/v1/courses, /{key}, /api/v1/providers, /{key}", "Khóa học và nhà cung cấp"],
        ["analysis.py", "/api/v1/users/{key}/skill-gap, /career-match, /learning-path, "
                        "/api/v1/graph/neighborhood",
         "★ Bốn chức năng phân tích"],
    ],
    widths=[2.4, 7.0, 7.0], size=9.5,
)
caption("Bảng 5.3. Sáu file router — mỗi file một chủ đề")

para("Vì sao chia nhiều file thay vì một file to: dễ tìm, dễ sửa, và nhiều người trong nhóm "
     "có thể làm song song không giẫm chân nhau. Đây là lý do chính đáng nếu bị hỏi.")

h2("5.10. main.py — nơi mọi thứ được lắp lại")

para("File này làm năm việc, theo thứ tự:")

num("Khởi tạo ứng dụng FastAPI, kèm phần mô tả cho trang tài liệu.", restart=True)
num("Đăng ký hàm chạy một lần lúc khởi động (lifespan): tạo core và gắn vào trạng thái ứng dụng. "
    "Nhờ vậy không phải đọc dữ liệu lại cho mỗi yêu cầu.")
num("Cấu hình CORS để giao diện gọi được API.")
num("Đăng ký sáu router cùng các hàm xử lý lỗi.")
num("Phục vụ trang /demo (file HTML tĩnh) và trang / trả về thông tin giới thiệu.")

para("File này còn có một đoạn nhỏ đặt chế độ mã hoá UTF-8 cho đầu ra console. "
     "Nghe không quan trọng nhưng nếu thiếu, chạy trên Windows sẽ lỗi khi in tiếng Việt — "
     "một lỗi rất hay gặp và rất khó chịu.")

h2("5.11. static/index.html — giao diện demo")

para("Một file HTML duy nhất, không cần cài Node.js, không cần biên dịch. Mở /demo là chạy. "
     "Bên trong có bốn tab:")

bullet("Skill Gap: bảng 11 kỹ năng với nhãn màu — đỏ là chưa có, vàng là chưa đủ mức, "
       "xanh là đã đạt; phía trên là độ phủ 27,3% và biểu đồ thanh.")
bullet("Lộ trình học: 8 bước dạng thẻ, mỗi thẻ có lý do xuất hiện và các khóa học gợi ý.")
bullet("Nghề phù hợp: 12 nghề xếp hạng kèm thanh điểm.")
bullet("Đồ thị: vẽ bằng SVG — nghề ở giữa, các kỹ năng vây quanh, mũi tên giữ đúng chiều "
       "yêu cầu của dữ liệu.")

para("Lựa chọn làm một file HTML thay vì dùng frontend React có sẵn là có lý do: bộ frontend "
     "trong gói bàn giao dùng bộ dữ liệu khác (catalog v3.55, 24 collection) chứ không khớp "
     "lược đồ skill_graph_db của đề tài. Ghép hai bộ dữ liệu khác lược đồ sẽ sinh lỗi khó giải thích. "
     "Vì vậy nhóm làm giao diện demo gọn, đúng dữ liệu, đúng 4 chức năng cần trình bày.")

h2("5.12. smoke_test.py — 42 điểm kiểm thử")

para("Đây là file chứng minh hệ thống chạy đúng. Nó không chỉ kiểm tra API có trả về 200, "
     "mà kiểm tra cả các bất biến nghiệp vụ:")

table(
    ["Nhóm kiểm thử", "Kiểm cái gì", "Vì sao quan trọng"],
    [
        ["Metadata", "12 collection, tổng 1.584 bản ghi", "Chứng minh dữ liệu khớp tài liệu đề tài"],
        ["Danh sách", "Số lượng đúng từng collection", "Phát hiện mất dữ liệu khi trích dump"],
        ["Chi tiết", "Trả về kèm quan hệ", "Đảm bảo không thiếu cạnh"],
        ["Skill Gap", "missing + below + ok = tổng", "Bất biến: không được đếm sót hay đếm trùng"],
        ["Career Match", "29 nghề, điểm trong 0–100, sắp giảm dần", "Bất biến về thang điểm và thứ tự"],
        ["Prerequisite", "Duyệt nhiều tầng, không lặp đỉnh", "Chống lỗi lặp vô hạn"],
        ["Learning Path", "order liên tục từ 1, mọi bước có gap dương, không có khóa đã học",
         "Ba bất biến cốt lõi của lộ trình"],
        ["Đồ thị", "Mọi cạnh trỏ tới đỉnh có trong phản hồi", "Tránh vẽ ra mũi tên treo giữa không trung"],
        ["Lỗi", "404 và 400 đúng khuôn", "Hợp đồng API"],
    ],
    widths=[3.2, 6.4, 6.8], size=10,
)
caption("Bảng 5.4. Chín nhóm kiểm thử — 42 điểm, kết quả 42 đạt 0 lỗi")

box("CÁCH NÓI VỀ KIỂM THỬ KHI THUYẾT TRÌNH", [
    "Đừng nói “em chạy thử thấy được”. Nói: “Nhóm viết 42 điểm kiểm thử tự động, "
    "trong đó có những bất biến nghiệp vụ như tổng ba trạng thái phải bằng tổng yêu cầu, "
    "hoặc thứ tự lộ trình phải liên tục từ 1. Kết quả 42/42 đạt.”",
], fill="E8F6F0", title_color=GREEN)

# ================================================================
# 6. THUẬT TOÁN
# ================================================================
h1("6. Bốn thuật toán nghiệp vụ — giải thích bằng ví dụ số")

para("Đây là chương quan trọng nhất để bảo vệ. Mỗi thuật toán được trình bày theo cùng một cấu trúc: "
     "bài toán là gì, ý tưởng, các bước, kết quả thật, và câu nói khi thuyết trình.")

# ---------------- 6.1
h2("6.1. Skill Gap — phân tích khoảng trống kỹ năng")

h3("Bài toán")
para("Cho một người và một nghề. Hỏi: người này còn thiếu gì so với yêu cầu của nghề?")

h3("Ý tưởng")
para("Nghề yêu cầu kỹ năng ở một mức nào đó (required_level). Người học khai mình đang ở mức nào "
     "(proficiency). Hai con số cùng thang 0–100 nên trừ trực tiếp được.")

h3("Bốn bước")
num("Lấy danh sách kỹ năng nghề yêu cầu, kèm required_level, importance và loại (bắt buộc/tùy chọn).")
num("Lấy trình độ hiện có của người học trên từng kỹ năng.")
num("So từng cặp và gán một trong ba trạng thái.")
num("Đếm: độ phủ = số kỹ năng đạt / tổng số yêu cầu × 100.")

table(
    ["Trạng thái", "Điều kiện", "gapLevel", "Nghĩa với người học"],
    [
        ["missing", "Không có cạnh has_skill cho kỹ năng đó", "= required_level",
         "Phải học từ đầu"],
        ["below_level", "Có proficiency nhưng nhỏ hơn required_level", "= required − current",
         "Đã biết nhưng chưa đủ, cần nâng"],
        ["ok", "proficiency lớn hơn hoặc bằng required_level", "0", "Đã đáp ứng"],
    ],
    widths=[2.6, 5.6, 3.4, 5.0], size=10,
)
caption("Bảng 6.1. Ba trạng thái — nhớ đúng thứ tự này khi nói")

h3("Kết quả thật (user_001, nghề Data Analyst)")

table(
    ["#", "Kỹ năng", "Loại", "Cần", "Hiện có", "Thiếu", "Trạng thái"],
    [
        ["1", "SQL", "Bắt buộc", "70", "—", "70", "missing"],
        ["2", "Python", "Bắt buộc", "70", "—", "70", "missing"],
        ["3", "Pandas", "Bắt buộc", "70", "—", "70", "missing"],
        ["4", "Statistics", "Bắt buộc", "70", "75", "0", "ok"],
        ["5", "Exploratory Data Analysis", "Bắt buộc", "70", "35", "35", "below_level"],
        ["6", "Data Visualization", "Bắt buộc", "70", "—", "70", "missing"],
        ["7", "Power BI", "Bắt buộc", "70", "45", "25", "below_level"],
        ["8", "Tableau", "Tùy chọn", "55", "45", "10", "below_level"],
        ["9", "Data Cleaning", "Tùy chọn", "55", "45", "10", "below_level"],
        ["10", "A/B Testing", "Tùy chọn", "55", "75", "0", "ok"],
        ["11", "Communication", "Tùy chọn", "55", "60", "0", "ok"],
    ],
    widths=[0.9, 5.2, 2.2, 1.5, 1.8, 1.4, 3.4], size=9.5,
)
caption("Bảng 6.2. Mười một yêu cầu: 3 ok, 4 below_level, 4 missing → độ phủ 27,3%")

rich([("Cách tính độ phủ để nói trước lớp: ", False, False, None),
      ("3 chia 11 bằng 0,2727… tức 27,3%", True, False, NAVY),
      (". Con số nhỏ, nhưng đúng — người này còn cách nghề khá xa, và đó chính là lý do "
       "hệ thống cần thiết.", False, False, None)])

box("CÂU NÓI KHI THUYẾT TRÌNH ĐOẠN NÀY", [
    "“Skill Gap là phép so sánh hai con số trên cùng thang 0–100. Nhưng điểm cần chú ý là "
    "ba trạng thái: thiếu hẳn khác với có nhưng chưa đủ. Rất nhiều hệ thống chỉ so sánh có/không, "
    "nên đưa ra lời khuyên sai — bảo người đã biết 45 điểm học lại từ đầu. Ở đây hệ thống nói rõ "
    "cần nâng thêm bao nhiêu.”",
], fill="E8F6F0", title_color=GREEN)

# ---------------- 6.2
h2("6.2. Duyệt kỹ năng tiên quyết nhiều tầng")

h3("Bài toán")
para("Cho một kỹ năng, liệt kê toàn bộ kỹ năng nền cần có trước, kèm mỗi kỹ năng nằm ở tầng thứ mấy.")

h3("Ý tưởng — duyệt theo chiều rộng (BFS)")
para("Xuất phát từ kỹ năng gốc, tìm các kỹ năng cần có ngay trước nó (tầng 1). "
     "Từ mỗi kỹ năng tầng 1, lại tìm các kỹ năng cần trước nó (tầng 2). Cứ thế lan ra. "
     "Đây là cách duyệt theo chiều rộng: xét hết một tầng rồi mới xuống tầng sau.")

h3("Vì sao phải có tập “đã thăm”")
para("Nếu dữ liệu có chu trình — A cần B, B lại cần A — thì vòng lặp sẽ chạy mãi. "
     "Tập đã thăm ghi lại những đỉnh đã xét; gặp lại thì bỏ qua. Đây là chi tiết nhỏ nhưng "
     "là câu trả lời tốt nếu bị hỏi “dữ liệu có chu trình thì sao?”.")

h3("Các bước")
code('hàng đợi = [(kỹ_năng_gốc, 0)]\n'
     'đã_thăm = {kỹ_năng_gốc}\n'
     'kết_quả = []\n'
     '\n'
     'trong khi hàng đợi còn phần tử:\n'
     '    (hiện_tại, độ_sâu) = lấy ra phần tử ĐẦU hàng đợi\n'
     '    nếu độ_sâu đã bằng giới hạn: bỏ qua (không đi sâu thêm)\n'
     '    với mỗi cạnh prerequisite trỏ VÀO hiện_tại:\n'
     '        nguồn = đỉnh xuất phát của cạnh\n'
     '        ghi kết quả (nguồn, độ_sâu + 1)\n'
     '        nếu nguồn chưa có trong đã_thăm:\n'
     '            thêm nguồn vào đã_thăm và vào cuối hàng đợi')

h3("Kết quả thật với Deep Learning")

table(
    ["Đỉnh", "Tầng", "Quan hệ dẫn tới"],
    [
        ["Deep Learning", "0 (gốc)", "—"],
        ["Machine Learning", "1", "Deep Learning cần Machine Learning"],
        ["Linear Algebra", "1", "Deep Learning cần Linear Algebra"],
        ["Python", "2", "Machine Learning cần Python"],
        ["Statistics", "2", "Machine Learning cần Statistics"],
        ["Probability", "2", "Machine Learning cần Probability"],
        ["Math / Linear Algebra (lần 2)", "2", "Machine Learning cần Linear Algebra — đã thăm nên không lặp"],
    ],
    widths=[6.0, 2.6, 7.8], size=10,
)
caption("Bảng 6.3. Duyệt từ Deep Learning: 5 kỹ năng nền, độ sâu tối đa 2")

rich([("Con số cần nhớ: ", False, False, None),
      ("prerequisite_closure(deep_learning) trả về depth = 2", True, False, NAVY),
      (". Nếu bị hỏi “sao chỉ có 2 tầng”, trả lời: “Vì dữ liệu hiện tại chỉ sâu tới đó; "
       "thuật toán cho phép tới 5 tầng, giới hạn này đặt trong tham số max_depth.”", False, False, None)])

h3("Liên hệ với AQL")
para("Trong ArangoDB, cùng phép duyệt này là một câu:")

code('FOR v, e, p IN 1..5 INBOUND s prerequisite\n'
     '  RETURN DISTINCT v')

para("Trong SQL thì phải viết CTE đệ quy, và muốn biết độ sâu từng đỉnh còn phải thêm cột đếm. "
     "Đây là câu trả lời chuẩn cho câu hỏi “vì sao graph database”.")

# ---------------- 6.3
h2("6.3. Điểm phù hợp nghề nghiệp")

h3("Bài toán")
para("Một người gần với nghề nào nhất trong 29 nghề? Dùng để gợi ý khi người học chưa chắc mục tiêu.")

h3("Ý tưởng")
para("Không phải đếm số kỹ năng đã đạt, vì kỹ năng có kỹ năng quan trọng hơn kỹ năng khác. "
     "Mỗi yêu cầu có trường importance. Điểm phù hợp là tỉ lệ importance đã đạt trên tổng importance.")

code('điểm = 100 × (tổng importance của các yêu cầu đã đạt)\n'
     '           ÷ (tổng importance của toàn bộ yêu cầu)')

h3("Vì sao phải nhân theo importance chứ không chia đều")
para("Ví dụ dễ hiểu: nghề A có 10 kỹ năng, trong đó 9 kỹ năng phụ (importance 10) và 1 kỹ năng "
     "cốt lõi (importance 90). Nếu đạt 9 kỹ năng phụ thì chia đều sẽ ra 90% — nghe rất giỏi. "
     "Nhưng thực tế còn thiếu đúng kỹ năng cốt lõi, nên nhân theo importance chỉ được 47%. "
     "Cách thứ hai phản ánh đúng thực tế hơn.")

h3("Kết quả thật")

table(
    ["Hạng", "Nghề", "Điểm", "Đạt / Tổng", "Thiếu kỹ năng bắt buộc"],
    [
        ["1", "Data Analyst", "24,9%", "3 / 11", "6"],
        ["2", "Data Scientist", "13,2%", "2 / 14", "7"],
        ["3", "Android Developer", "10,7%", "1 / 9", "5"],
        ["4", ".NET Developer", "10,3%", "1 / 9", "5"],
        ["5", "Cybersecurity Analyst", "9,1%", "1 / 10", "6"],
        ["6", "Database Administrator", "9,1%", "1 / 10", "6"],
    ],
    widths=[1.4, 5.6, 2.2, 2.8, 4.4], size=10,
)
caption("Bảng 6.4. Sáu nghề phù hợp nhất với user_001 — Data Analyst đứng đầu")

box("ĐIỂM CẦN NÓI RÕ ĐỂ TRÁNH HIỂU SAI", [
    "24,9% KHÔNG có nghĩa “người này giỏi 25% nghề Data Analyst”. Nó có nghĩa: "
    "trong tổng trọng số các yêu cầu của nghề, người này đã đáp ứng được khoảng một phần tư.",
    "Bảng cũng cho thấy một điều thú vị: Data Analyst đứng đầu không phải vì người này giỏi, "
    "mà vì đây là nghề gần nhất với hồ sơ hiện tại. Đó chính là mục đích: tìm điểm xuất phát hợp lý.",
], fill="FFF4E5", title_color=ORANGE)

# ---------------- 6.4
h2("6.4. Sinh lộ trình học — thuật toán trung tâm")

para("Đây là chức năng mà tên đề tài nhắc tới, nên phải nắm kỹ nhất. Gồm bốn bước.")

h3("Bước 1 — Lấy danh sách kỹ năng còn thiếu")
para("Chạy Skill Gap, giữ lại các kỹ năng ở trạng thái missing hoặc below_level. "
     "Kỹ năng ok bị loại vì đã biết rồi.")

h3("Bước 2 — Leo ngược tìm kỹ năng nền")
para("Với mỗi kỹ năng trong danh sách, duyệt ngược cạnh prerequisite để thêm các kỹ năng nền "
     "cũng còn thiếu. Vì sao cần bước này: nghề có thể yêu cầu Pandas nhưng không liệt kê Python "
     "(vì nghề cho rằng ai làm nghề này đều biết Python). Nếu chỉ dựa vào yêu cầu của nghề, "
     "lộ trình sẽ bảo học Pandas luôn — vô lý. Bước 2 sửa lỗi đó.")

box("ĐÂY LÀ CHỖ DỄ BỊ HỎI NHẤT", [
    "Câu hỏi: “Nếu nghề không yêu cầu Python mà Pandas lại cần Python, hệ thống xử lý sao?”",
    "Trả lời: “Bước 2 leo ngược quan hệ prerequisite từ mọi kỹ năng còn thiếu, nên Python được "
    "thêm vào lộ trình dù nghề không nêu tên. Đó là lý do trong kết quả thật, Python xuất hiện "
    "ở bước 2 và Pandas ở bước 3.”",
], fill="FDECEE", title_color=RED)

h3("Bước 3 — Sắp xếp theo thứ tự phụ thuộc (sắp xếp topo)")
para("Ta có một tập kỹ năng cần học và quan hệ “cần trước” giữa chúng. Cần xếp thành hàng dọc sao cho "
     "kỹ năng nền luôn đứng trước kỹ năng phụ thuộc nó. Cách làm cổ điển là thuật toán Kahn:")

num("Đếm bậc vào của mỗi kỹ năng: còn bao nhiêu kỹ năng nền chưa xếp trước nó.", restart=True)
num("Đưa tất cả kỹ năng có bậc vào bằng 0 vào hàng đợi — đây là những kỹ năng không cần gì trước.")
num("Lấy một kỹ năng ra khỏi hàng đợi, ghi vào kết quả.")
num("Giảm bậc vào của các kỹ năng phụ thuộc nó đi 1. Kỹ năng nào về 0 thì đưa vào hàng đợi.")
num("Lặp tới khi hàng đợi rỗng.")

para("Nếu còn kỹ năng chưa xếp được khi hàng đợi rỗng, nghĩa là dữ liệu có chu trình. "
     "Khi đó hệ thống đưa phần còn lại xuống cuối và ghi chú, không tự phá vỡ ràng buộc bằng cách "
     "bỏ qua quan hệ — vì làm vậy sẽ tạo ra lộ trình sai mà không ai biết.")

para("Khi nhiều kỹ năng cùng bậc (không kỹ năng nào bắt buộc phải trước kỹ năng nào), "
     "hệ thống ưu tiên kỹ năng bắt buộc trước, rồi tới importance cao hơn. "
     "Chi tiết này làm lộ trình hợp lý hơn về mặt sư phạm.")

h3("Bước 4 — Gắn khóa học, loại khóa đã học")
para("Với mỗi bước, tìm các khóa học dạy kỹ năng đó qua cạnh teaches, rồi trừ đi những khóa "
     "người dùng đã có cạnh completed. Nếu kỹ năng không có khóa học nào, ghi rõ “chưa có khóa học "
     "trong dữ liệu” — và đây là trường hợp thật, vì có tới 145 trong 248 kỹ năng chưa có khóa dạy.")

h3("Kết quả thật — lộ trình 8 bước")

table(
    ["Bước", "Kỹ năng", "Mức cần", "Còn thiếu", "Mở khoá cho", "Khóa học gợi ý (3 đầu)"],
    [
        ["1", "SQL", "70", "70", "—", "SQL Fundamentals; Advanced SQL; PostgreSQL Essentials"],
        ["2", "Python", "70", "70", "Pandas", "Python Fundamentals; Intermediate Python; FastAPI"],
        ["3", "Pandas", "70", "70", "EDA", "Pandas for Data Analysis; EDA; Feature Engineering"],
        ["4", "Exploratory Data Analysis", "70", "35", "—", "Exploratory Data Analysis"],
        ["5", "Data Visualization", "70", "70", "Power BI, Tableau", "Data Visualization with Python; "
                                                                  "Tableau Fundamentals"],
        ["6", "Power BI", "70", "25", "—", "chưa có khóa học trong dữ liệu"],
        ["7", "Tableau", "55", "10", "—", "Tableau Fundamentals"],
        ["8", "Data Cleaning", "55", "10", "—", "Data Cleaning with Python"],
    ],
    widths=[1.1, 4.2, 1.6, 1.7, 3.0, 5.8], size=9.5,
)
caption("Bảng 6.5. Lộ trình thật cho user_001 → Data Analyst, 8 bước, loại bỏ 4 khóa đã học")

h3("Ba điều đáng nói về kết quả này")

bullet("Python đứng trước Pandas — vì Pandas có quan hệ prerequisite trỏ tới Python. "
       "Đây là bằng chứng thuật toán xếp topo hoạt động đúng, và là điểm nhấn khi demo.")
bullet("Power BI đứng sau Data Visualization — vì Data Visualization là nền của Power BI và Tableau. "
       "Học cách hiểu dữ liệu trước, rồi mới học công cụ.")
bullet("Không có khóa học nào của 4 khóa người dùng đã hoàn thành bị gợi ý lại. "
       "Hệ thống đếm được: đã loại 4 khóa.")

box("CÂU NÓI HOÀN CHỈNH CHO PHẦN NÀY", [
    "“Lộ trình không phải danh sách kỹ năng xếp theo bảng chữ cái. Nó là kết quả của sắp xếp topo "
    "trên đồ thị quan hệ tiên quyết. Có ba bằng chứng: Python trước Pandas, Data Visualization "
    "trước Power BI, và bốn khóa đã học không bị đề xuất lại. Nếu bỏ bước sắp xếp topo, "
    "hệ thống sẽ cho ra thứ tự đúng chữ cái nhưng sai về mặt học thuật.”",
], fill="E8F6F0", title_color=GREEN)

# ================================================================
# 7. AQL
# ================================================================
h1("7. Ba mươi truy vấn AQL — bộ chứng minh cho phần database")

para("Đề tài yêu cầu thao tác dữ liệu trên ArangoDB Web Interface bằng AQL. "
     "File queries/aql_queries.aql gồm 30 câu, chia hai phần: 10 câu cơ bản và 20 câu nâng cao. "
     "Khi demo, chỉ cần chạy khoảng 4 câu là đủ ấn tượng — nhưng phải biết câu nào nói lên điều gì.")

h2("7.1. Phần A — truy vấn cơ bản (A1 đến A10)")

table(
    ["Mã", "Tên", "Trả lời câu hỏi gì", "Có nên demo?"],
    [
        ["A1", "Đếm bản ghi 12 collection", "Database có đúng bao nhiêu dữ liệu?", "★ Nên — mở đầu"],
        ["A2", "Liệt kê 10 nghề", "Hệ thống biết những nghề nào?", "Không cần"],
        ["A3", "Tìm kỹ năng theo từ khoá", "Tìm kiếm hoạt động không?", "Có thể"],
        ["A4", "Lọc kỹ năng theo nhóm", "Nhóm lập trình có kỹ năng gì?", "Không cần"],
        ["A5", "Một người và toàn bộ kỹ năng", "Hồ sơ người học trông thế nào?", "Có thể"],
        ["A6", "Nghề mục tiêu của người dùng", "Người này nhắm nghề gì?", "Không cần"],
        ["A7", "Khoá học đã hoàn thành", "Người này đã học gì rồi?", "Có thể"],
        ["A8", "Thêm người dùng mới", "Chứng minh thao tác ghi dữ liệu", "★ Nên nếu bị hỏi CRUD"],
        ["A9", "Thêm/cập nhật kỹ năng người dùng", "Cập nhật trình độ", "★ Nên nếu bị hỏi CRUD"],
        ["A10", "Xoá người dùng demo và cạnh liên quan", "Xoá có dọn quan hệ không", "Không cần"],
    ],
    widths=[1.2, 4.8, 5.8, 4.0], size=9.5,
)
caption("Bảng 7.1. Mười truy vấn cơ bản — A8, A9, A10 là ba câu CRUD")

box("VÌ SAO CÓ A8–A10 — câu hỏi “đề tài yêu cầu CRUD, em làm chưa?”", [
    "Backend API được thiết kế chỉ đọc. Việc thêm/sửa/xoá dữ liệu thực hiện bằng AQL "
    "trên ArangoDB Web Interface — đúng như yêu cầu của đề tài (“quản trị dữ liệu trên "
    "ArangoDB Web Interface”). Ba truy vấn A8, A9, A10 chứng minh điều đó.",
    "Nếu bị hỏi sao không làm CRUD qua API: trả lời rằng đề tài tập trung vào phân tích đồ thị, "
    "và việc ghi dữ liệu để trên Web Interface là đúng phạm vi; nếu mở rộng thì chỉ cần thêm "
    "router gọi các truy vấn A8–A10 vì logic đã có sẵn.",
], fill="EAF1FB", title_color=NAVY)

h2("7.2. Phần B — truy vấn đồ thị (B1 đến B13)")

table(
    ["Mã", "Tên", "Trả lời câu hỏi gì", "Có nên demo?"],
    [
        ["B1", "Nghề yêu cầu kỹ năng gì", "Một tầng quan hệ requires_skill", "Có thể"],
        ["B2", "★ SKILL GAP", "So yêu cầu với trình độ ngay trong AQL", "★ Nên"],
        ["B3", "★ PREREQUISITE nhiều tầng", "Toàn bộ kỹ năng nền của một kỹ năng", "★ NÊN NHẤT"],
        ["B4", "PREREQUISITE — đường đi đầy đủ", "Chuỗi từ gốc tới đích", "Có thể"],
        ["B5", "Khoá học dạy kỹ năng + nhà cung cấp", "Học ở đâu", "Không cần"],
        ["B6", "★ CAREER FIT", "Chấm điểm mọi nghề trong một câu", "★ Nên"],
        ["B7", "Khoá học chưa học nhưng cần", "Gợi ý khóa, trừ khóa đã học", "Có thể"],
        ["B8", "★ LEARNING PATH", "Sinh lộ trình có thứ tự", "★ Nên"],
        ["B9", "Đảo ngược — kỹ năng mở khoá nghề nào", "Học X thì làm được nghề gì", "Có thể"],
        ["B10", "Top nhà cung cấp theo số khoá", "Ai cung cấp nhiều khóa nhất", "Không cần"],
        ["B11", "Đường đi ngắn nhất giữa 2 kỹ năng", "Python và Deep Learning liên quan sao", "Có thể"],
        ["B12", "Kỹ năng không có khoá học nào dạy", "Phát hiện khoảng trống dữ liệu", "★ Nên — gây ấn tượng"],
        ["B13", "★ Thống kê tổng hợp", "Toàn cảnh hệ thống trong một kết quả", "★ Nên — mở đầu"],
    ],
    widths=[1.2, 5.2, 6.0, 3.4], size=9.5,
)
caption("Bảng 7.2. Mười ba truy vấn đồ thị — sáu câu có dấu ★ là nên chạy khi demo")

h2("7.3. Ba câu AQL nên thuộc lòng")

h3("B3 — duyệt kỹ năng nền nhiều tầng (câu quan trọng nhất)")

code('LET s = DOCUMENT("skills/deep_learning")\n'
     'FOR v, e, p IN 1..5 INBOUND s prerequisite\n'
     '  RETURN DISTINCT {\n'
     '    ky_nang: v.name,\n'
     '    do_sau: LENGTH(p.vertices) - 1,\n'
     '    duong_di: p.vertices[*].name\n'
     '  }')

para("Đọc từng dòng: lấy đỉnh Deep Learning; duyệt ngược cạnh prerequisite sâu 1 tới 5 tầng; "
     "trả về tên kỹ năng, độ sâu (số đỉnh trên đường đi trừ 1), và cả đường đi. "
     "Trong SQL phải viết CTE đệ quy; ở đây là ba dòng.")

h3("B8 — sinh lộ trình học")

para("Câu này khó nhất trong cả file. Ý tưởng: lấy yêu cầu của nghề, trừ những kỹ năng đã đạt, "
     "rồi sắp xếp theo độ sâu tiên quyết tăng dần. Có một chi tiết tinh tế: nếu chỉ dựa vào "
     "quan hệ trực tiếp thì nhiều kỹ năng sẽ hoà nhau và kết quả rơi về thứ tự bảng chữ cái — "
     "sai về mặt sư phạm. Vì vậy phải tính độ sâu tiên quyết toàn cục bằng một phép duyệt phụ.")

code('LET do_sau_toan_cuc = (\n'
     '  FOR v, e, p IN 1..5 INBOUND s prerequisite\n'
     '    COLLECT ky = v._id AGGREGATE d = MAX(LENGTH(p.vertices) - 1)\n'
     '    RETURN { ky: ky, d: d }\n'
     ')')

box("CHI TIẾT NÀY RẤT ĐÁNG NÓI KHI BẢO VỆ", [
    "Trong quá trình làm, nhóm phát hiện một lỗi: phiên bản đầu của truy vấn sinh lộ trình cho ra "
    "thứ tự Python sau Pandas — sai. Nguyên nhân: các kỹ năng đều có độ sâu 0 vì chúng là yêu cầu "
    "trực tiếp của nghề, nên phép sắp xếp rơi về bảng chữ cái.",
    "Cách sửa: tính độ sâu tiên quyết toàn cục (một kỹ năng càng nhiều tầng nền thì càng phải "
    "học sớm), rồi sắp tăng dần theo độ sâu đó. Sau khi sửa, Python đứng trước Pandas.",
    "Kể được câu chuyện này chứng minh nhóm thực sự chạy thử và hiểu dữ liệu, chứ không chỉ "
    "viết ra rồi để đó.",
], fill="E8F6F0", title_color=GREEN)

h3("B12 — kỹ năng không có khoá học nào dạy")

para("Câu này đơn giản nhưng gây ấn tượng vì nó cho thấy ta biết điểm yếu của dữ liệu: "
     "145 trong 248 kỹ năng chưa có khóa học nào. Nếu thầy cô hỏi “dữ liệu có đầy đủ không”, "
     "đây là câu trả lời trung thực và có số liệu.")

h2("7.4. Cách chạy AQL trên ArangoDB Web Interface")

num("Mở http://127.0.0.1:8529, đăng nhập bằng tài khoản root.", restart=True)
num("Chọn database skill_graph_db ở góc trên.")
num("Vào tab QUERIES.")
num("Dán MỘT khối truy vấn (từ dòng “--- A1” tới trước khối kế tiếp). Không bôi đen cả file rồi Run.")
num("Bấm Run, chụp ảnh kết quả để đưa vào báo cáo.")

box("LỖI HAY GẶP KHI CHẠY AQL", [
    "• Chạy cả file một lúc → lỗi cú pháp. Mỗi lần chỉ chạy một khối.",
    "• Sai chiều INBOUND/OUTBOUND → kết quả rỗng hoặc vô nghĩa. INBOUND là đi ngược mũi tên.",
    "• Dùng tên collection sai (has_skill viết hoa) → lỗi không tìm thấy collection. "
    "Tên trong ArangoDB là chữ thường.",
], fill="FDECEE", title_color=RED)

# ================================================================
# 8. CÁCH CHẠY
# ================================================================
h1("8. Cách chạy hệ thống và chuẩn bị demo")

h2("8.1. Chuẩn bị lần đầu")

code('cd skillgraph\\backend\n'
     'pip install -r requirements.txt')

para("Ba gói cần cài: fastapi (khung làm API), uvicorn (máy chủ chạy API), "
     "pydantic (kiểm tra kiểu dữ liệu). Nếu mạng chậm, có thể dùng lệnh pip với tham số "
     "--timeout cao hơn.")

h2("8.2. Chạy server")

code('python run.py')

para("Mở trình duyệt vào một trong ba địa chỉ sau:")

table(
    ["Địa chỉ", "Là gì", "Dùng khi nào"],
    [
        ["http://127.0.0.1:8000/demo", "Giao diện demo 4 tab", "★ Dùng khi thuyết trình"],
        ["http://127.0.0.1:8000/docs", "Swagger — tài liệu API tự sinh, bấm thử được từng API",
         "Khi thầy cô muốn xem chi tiết kỹ thuật"],
        ["http://127.0.0.1:8000/api/v1/meta/health", "Trạng thái hệ thống dạng JSON",
         "Kiểm tra nhanh hệ thống sống hay chết"],
    ],
    widths=[6.4, 6.4, 3.8], size=10,
)
caption("Bảng 8.1. Ba địa chỉ cần nhớ")

box("NẾU GẶP LỖI KHI CHẠY", [
    "“ModuleNotFoundError: No module named 'fastapi'” → chưa cài thư viện. Chạy lại lệnh pip install.",
    "“Address already in use” → cổng 8000 đang bị chương trình khác dùng. Đổi cổng trong run.py "
    "thành 8001.",
    "Chữ tiếng Việt bị lỗi trên console Windows → đặt biến môi trường PYTHONIOENCODING=utf-8 "
    "trước khi chạy.",
    "Trang /demo trắng trơn → kiểm tra server còn chạy không; nhấn F12 mở Console xem lỗi.",
], fill="FFF4E5", title_color=ORANGE)

h2("8.3. Chạy kiểm thử")

code('cd skillgraph\\backend\n'
     'python scripts\\smoke_test.py')

para("Kỳ vọng dòng cuối: PASSED: 42   FAILED: 0. Đây là thứ nên chụp ảnh màn hình để đưa vào báo cáo.")

h2("8.4. Chạy với ArangoDB thật (khi máy có Docker)")

code('cd skillgraph\n'
     'docker compose up -d arangodb\n'
     '# đợi khoảng 20 giây cho ArangoDB khởi động\n'
     'docker exec -i arangodb arangorestore \\\n'
     '  --server.endpoint tcp://127.0.0.1:8529 \\\n'
     '  --server.username root \\\n'
     '  --server.password matkhau_doi_di \\\n'
     '  --input-directory /dump/skill_graph_db \\\n'
     '  --create-database true')

box("CẢNH BÁO QUAN TRỌNG NHẤT CỦA PHẦN NÀY", [
    "KHÔNG dùng chức năng Import JSON trong ArangoDB Web Interface để nạp dump này. "
    "Nó chỉ nạp được document, mất toàn bộ 1.029 cạnh (274 + 40 + 312 + 173 + 172 + 110 + 89). "
    "Mất cạnh nghĩa là mất luôn prerequisite — đồ án mất phần quan trọng nhất.",
    "Cách đúng là dùng arangorestore như trên, vì nó phục hồi cả định nghĩa collection, "
    "cả cạnh, cả named graph.",
], fill="FDECEE", title_color=RED)

para("Sau khi phục hồi xong, chuyển backend sang đọc từ ArangoDB:")

code('cd backend\n'
     '$env:ARANGO_PASSWORD = "matkhau_doi_di"\n'
     '$env:SKILLGRAPH_DATA_MODE = "arango"\n'
     'python run.py')

para("Mở /api/v1/meta/health để kiểm tra. Trường dataMode phải đổi từ jsonl thành arango, "
     "và arango.connected phải là true.")

h2("8.5. Chuẩn bị trước buổi thuyết trình — danh sách kiểm tra")

table(
    ["Thứ tự", "Việc cần làm", "Xong thì đánh dấu"],
    [
        ["1", "Chạy server trước giờ thuyết trình 10 phút, để sẵn ở cổng 8000", "☐"],
        ["2", "Mở sẵn 3 tab trình duyệt: /demo, /docs, ArangoDB Web Interface", "☐"],
        ["3", "Chạy trước một lần toàn bộ luồng demo để chắc không lỗi", "☐"],
        ["4", "Mở sẵn file báo cáo Word ở trang có bảng Skill Gap", "☐"],
        ["5", "Chụp ảnh màn hình kết quả AQL phòng khi mạng lỗi", "☐"],
        ["6", "Chuẩn bị sẵn câu trả lời cho 5 câu hay bị hỏi nhất (chương 10)", "☐"],
        ["7", "Tắt thông báo điện thoại, đóng các tab không liên quan", "☐"],
        ["8", "Nếu máy không có ArangoDB: nói rõ ngay từ đầu, đừng để bị phát hiện", "☐"],
    ],
    widths=[1.6, 12.4, 2.6], size=10,
)
caption("Bảng 8.2. Danh sách kiểm tra trước khi thuyết trình")

# ================================================================
# 9. KỊCH BẢN THUYẾT TRÌNH
# ================================================================
h1("9. Kịch bản thuyết trình từng slide")

para("Chương này cho bạn lời thoại cụ thể cho 10 slide trong file BAO_CAO_SLIDE.pptx. "
     "Đừng đọc thuộc lòng từng chữ — đọc để nắm ý, rồi nói tự nhiên. "
     "Thời lượng gợi ý: 10 phút, tức khoảng 1 phút mỗi slide.")

box("NGUYÊN TẮC NÓI CHUNG", [
    "• Mỗi slide chỉ cần nói MỘT ý chính. Đừng đọc hết chữ trên slide — thầy cô đọc được.",
    "• Con số cụ thể tạo niềm tin: nói “27,3%” tốt hơn “khoảng ba mươi phần trăm”.",
    "• Khi nói tới thuật toán, luôn kèm ví dụ thật: “ví dụ Python đứng trước Pandas vì…”.",
    "• Chuẩn bị sẵn một câu chốt cho mỗi slide, và nói chậm ở câu đó.",
], fill="EAF1FB", title_color=NAVY)

# ---- slide 1
h2("Slide 1 — Bìa: Hệ thống Skill Graph và đề xuất lộ trình học cá nhân hóa")
rich([("Thời lượng: ", True, False, None), ("30 giây", False, False, None)])
para("Lời thoại:")
para("“Chào thầy cô và các bạn. Nhóm em làm đề tài 1: Hệ thống Skill Graph và đề xuất lộ trình "
     "học cá nhân hóa, dựng trên ArangoDB — cơ sở dữ liệu đa mô hình, tức là làm được cả document "
     "lẫn graph. Phần nhóm em làm gồm ba phần: cơ sở dữ liệu với 1.584 bản ghi, bộ 30 truy vấn AQL, "
     "và backend FastAPI xử lý bốn nghiệp vụ. Em xin trình bày trong khoảng 10 phút.”", italic=True)
box("MẸO", [
    "Câu mở đầu nên nêu ngay ba con số: 12 collection, 1.584 bản ghi, 30 truy vấn AQL. "
    "Điều này tạo ấn tượng là nhóm đã làm thật, có khối lượng cụ thể.",
], fill="FFF4E5", title_color=ORANGE)

# ---- slide 2
h2("Slide 2 — Bài toán")
rich([("Thời lượng: ", True, False, None), ("1 phút", False, False, None)])
para("Lời thoại:")
para("“Bài toán xuất phát từ một tình huống rất thực tế: một người muốn chuyển sang làm "
     "Data Analyst sẽ tìm thấy hàng trăm lời khuyên mâu thuẫn nhau trên mạng. Họ không biết "
     "nghề yêu cầu chính xác những gì, mình đang thiếu gì, và nên học theo thứ tự nào.”", italic=True)
para("“Ba câu hỏi đó là ba chức năng của hệ thống. Và điểm mấu chốt nằm ở câu thứ ba — "
     "học gì trước. Vì kỹ năng có quan hệ nhiều tầng với nhau: muốn học Deep Learning phải có "
     "Machine Learning, muốn có Machine Learning phải có Statistics và Python. "
     "Đó là hình dạng của một đồ thị, và đó là lý do nhóm chọn ArangoDB thay vì bảng tính.”", italic=True)

# ---- slide 3
h2("Slide 3 — Mô hình dữ liệu: 4 đỉnh, 6 cạnh")
rich([("Thời lượng: ", True, False, None), ("1,5 phút — slide quan trọng", False, False, None)])
para("Lời thoại:")
para("“Hệ thống có bốn loại thực thể: Người dùng, Kỹ năng, Nghề nghiệp, Khóa học. "
     "Mỗi thực thể là một collection đỉnh. Chúng nối với nhau bằng sáu loại quan hệ chính.”", italic=True)
para("“Em xin nhấn mạnh một quan hệ: PREREQUISITE, nối kỹ năng với kỹ năng. Quy ước chiều là "
     "từ kỹ năng MUỐN HỌC trỏ tới kỹ năng CẦN CÓ TRƯỚC. Ví dụ cạnh Pandas trỏ tới Python nghĩa là "
     "muốn học Pandas thì phải biết Python. Quy ước này rất dễ đọc ngược, và nếu đọc ngược thì "
     "thuật toán sinh lộ trình sẽ cho ra thứ tự sai hoàn toàn — dạy Pandas trước Python. "
     "Vì vậy nhóm đã đưa quy ước này thành hằng số trong code và viết kiểm thử tự động cho nó.”", italic=True)
box("ĐÂY LÀ CHỖ NÊN NÓI CHẬM VÀ NHÌN THẦY CÔ", [
    "Nêu rõ quy ước chiều trước khi bị hỏi thể hiện sự hiểu biết chủ động. "
    "Rất nhiều nhóm làm đề tài dạng này bị mất điểm đúng ở chỗ này.",
], fill="FDECEE", title_color=RED)

# ---- slide 4
h2("Slide 4 — Dữ liệu thật")
rich([("Thời lượng: ", True, False, None), ("1 phút", False, False, None)])
para("Lời thoại:")
para("“Database tên skill_graph_db gồm 12 collection, tổng 1.584 bản ghi. "
     "Năm collection đỉnh: 40 người học, 248 kỹ năng, 29 nghề, 89 khóa học và 8 nhà cung cấp. "
     "Bảy collection cạnh: 274 lượt khai báo kỹ năng, 40 mục tiêu nghề nghiệp, 312 yêu cầu "
     "kỹ năng của nghề, 173 quan hệ tiên quyết, 172 quan hệ dạy học, 110 khóa đã hoàn thành "
     "và 89 quan hệ cung cấp.”", italic=True)
para("“Con số 173 quan hệ tiên quyết là quan trọng nhất — nó đủ dày để thuật toán duyệt "
     "nhiều tầng thực sự có việc để làm.”", italic=True)
box("NẾU BỊ HỎI “DỮ LIỆU THẬT KHÔNG?”", [
    "Trả lời ngay, không vòng vo: “Dữ liệu là dữ liệu mẫu của đề tài, trường data_origin ghi "
    "synthetic_demo. Nhóm không nói đây là người thật. Nhưng cấu trúc và số lượng đúng theo tài liệu "
    "nghiệp vụ của đề tài, và đủ để chứng minh thuật toán chạy đúng.”",
], fill="FFF4E5", title_color=ORANGE)

# ---- slide 5
h2("Slide 5 — Kiến trúc hệ thống")
rich([("Thời lượng: ", True, False, None), ("1,5 phút", False, False, None)])
para("Lời thoại:")
para("“Hệ thống gồm ba tầng: trình duyệt, backend FastAPI viết bằng Python, và ArangoDB. "
     "Trình duyệt không nối thẳng vào database. Có ba lý do: thứ nhất, nối thẳng thì phải nhúng "
     "mật khẩu database vào mã JavaScript — ai mở trang cũng đọc được. Thứ hai, người dùng có thể "
     "gửi bất kỳ truy vấn nào, kể cả truy vấn xoá dữ liệu. Thứ ba, các phép tính nghiệp vụ phải "
     "chạy ở đâu đó, và chạy ở backend thì viết một lần bằng Python, kiểm thử được.”", italic=True)
para("“Trong backend có một quyết định thiết kế quan trọng: chia làm hai lớp. Lớp nghiệp vụ "
     "không biết dữ liệu đến từ đâu, chỉ gọi bốn hàm trừu tượng. Lớp lưu trữ có hai phiên bản: "
     "một đọc file JSONL, một gửi AQL tới ArangoDB. Nhờ vậy cùng một đoạn code nghiệp vụ chạy được "
     "ở cả hai môi trường — đây gọi là Repository Pattern.”", italic=True)

# ---- slide 6
h2("Slide 6 — Skill Gap")
rich([("Thời lượng: ", True, False, None), ("1 phút", False, False, None)])
para("Lời thoại:")
para("“Skill Gap là phép so sánh hai con số trên cùng thang 0 đến 100: nghề yêu cầu mức bao nhiêu, "
     "người học đang ở mức bao nhiêu. Nhưng điểm nhóm em muốn nhấn mạnh là ba trạng thái, không "
     "phải hai. Thiếu hẳn là một chuyện; đã biết nhưng chưa đủ mức là chuyện khác và cần lời khuyên khác.”", italic=True)
para("“Với người dùng user_001 hướng tới nghề Data Analyst, kết quả là 11 yêu cầu: 3 đã đạt, "
     "4 chưa đủ mức, 4 thiếu hẳn. Độ phủ 27,3%. Ví dụ kỹ năng Exploratory Data Analysis người này "
     "có 35 điểm, nghề cần 70 — hệ thống nói cần nâng thêm 35, chứ không bảo học lại từ đầu.”", italic=True)

# ---- slide 7
h2("Slide 7 — Duyệt kỹ năng tiên quyết nhiều tầng")
rich([("Thời lượng: ", True, False, None), ("1 phút — slide ăn điểm nhất", False, False, None)])
para("Lời thoại:")
para("“Đây là chức năng mà graph database thể hiện rõ lợi thế nhất. Cho kỹ năng Deep Learning, "
     "hệ thống tìm ra toàn bộ kỹ năng nền: tầng một gồm Machine Learning, Linear Algebra và "
     "Probability; tầng hai gồm Statistics, Python và cũng Linear Algebra nhưng đã được ghi nhận "
     "nên không lặp lại. Tổng cộng năm kỹ năng nền, độ sâu hai tầng.”", italic=True)
para("“Trong AQL, đây là một câu lệnh duy nhất: FOR v, e, p IN 1..5 INBOUND s prerequisite. "
     "Trong SQL, bài toán này cần CTE đệ quy với nhiều vòng lặp, và muốn biết độ sâu từng đỉnh "
     "còn phải thêm cột đếm. Đó là lý do nhóm chọn ArangoDB.”", italic=True)
box("CÂU CHỐT CHO SLIDE NÀY", [
    "“Một câu AQL thay cho nhiều vòng lặp lồng nhau — và quan trọng hơn, câu lệnh đó đọc lên "
    "là hiểu ngay ý nghĩa: đi ngược từ kỹ năng này, sâu tới năm tầng, theo quan hệ tiên quyết.”",
], fill="E8F6F0", title_color=GREEN)

# ---- slide 8
h2("Slide 8 — Sinh lộ trình học")
rich([("Thời lượng: ", True, False, None), ("1,5 phút", False, False, None)])
para("Lời thoại:")
para("“Đây là chức năng trung tâm, gồm bốn bước. Bước một chạy Skill Gap để lấy kỹ năng còn thiếu. "
     "Bước hai leo ngược quan hệ tiên quyết để thêm kỹ năng nền cũng còn thiếu — bước này quan trọng "
     "vì nghề có thể yêu cầu Pandas mà không liệt kê Python, trong khi Pandas lại cần Python.”", italic=True)
para("“Bước ba sắp xếp theo thứ tự phụ thuộc bằng thuật toán sắp xếp topo của Kahn: kỹ năng nền "
     "luôn đứng trước. Bước bốn gắn khóa học và loại những khóa người dùng đã hoàn thành.”", italic=True)
para("“Kết quả thật là tám bước: SQL, Python, Pandas, Phân tích dữ liệu khám phá, Trực quan hóa, "
     "Power BI, Tableau, Làm sạch dữ liệu. Có ba bằng chứng thuật toán chạy đúng: Python đứng trước "
     "Pandas vì Pandas cần Python; Data Visualization đứng trước Power BI; và bốn khóa đã học "
     "không bị đề xuất lại.”", italic=True)

# ---- slide 9
h2("Slide 9 — Kết quả kiểm thử")
rich([("Thời lượng: ", True, False, None), ("1 phút", False, False, None)])
para("Lời thoại:")
para("“Nhóm viết 42 điểm kiểm thử tự động. Điều đáng nói là nó không chỉ kiểm tra API trả về 200, "
     "mà kiểm tra các bất biến nghiệp vụ. Ví dụ: tổng ba trạng thái phải bằng tổng số yêu cầu; "
     "thứ tự lộ trình phải liên tục từ một; mọi cạnh trong đồ thị phải trỏ tới đỉnh có thật trong "
     "phản hồi, không được có mũi tên treo giữa không trung.”", italic=True)
para("“Kết quả 42 trên 42 đạt. Ngoài ra nhóm kiểm chứng chéo: mô phỏng lại các truy vấn AQL bằng "
     "Python rồi so với kết quả backend — các con số then chốt trùng khớp, gồm độ phủ 27,3%, "
     "thứ hạng nghề và tập tám kỹ năng cần học.”", italic=True)

# ---- slide 10
h2("Slide 10 — Demo và hướng phát triển")
rich([("Thời lượng: ", True, False, None), ("1 phút + demo nếu có", False, False, None)])
para("Lời thoại:")
para("“Phần demo gồm: mở giao diện /demo để xem bốn tab, mở Swagger để thử API trực tiếp, "
     "và nếu máy có ArangoDB thì chạy ba truy vấn AQL — thống kê tổng hợp, duyệt tiên quyết, "
     "và sinh lộ trình.”", italic=True)
para("“Về hạn chế, nhóm xin nói rõ: máy phát triển không cài được Docker nên chưa chạy ArangoDB thật. "
     "Toàn bộ kiểm thử chạy trên dữ liệu đã trích ra từ chính file dump của đề tài, đúng 1.584 bản ghi. "
     "Trong code đã có sẵn chế độ đọc ArangoDB; máy có Docker chỉ cần phục hồi dump và đổi một biến "
     "môi trường. Hướng phát triển tiếp theo là thêm các đường dẫn ghi dữ liệu và nối giao diện "
     "React sang API.”", italic=True)
box("CÁCH NÓI VỀ HẠN CHẾ", [
    "Nói hạn chế một cách bình tĩnh, kèm theo giải pháp đã chuẩn bị sẵn. "
    "Câu mẫu: “Điểm này nhóm chưa làm được vì điều kiện máy không có Docker. Nhưng nhóm đã chuẩn bị "
    "sẵn chế độ kết nối, chỉ cần phục hồi dump là chạy được — đây là lệnh cụ thể.”",
    "Đừng bao giờ nói “em không biết” rồi im lặng. Hãy nói “phần này em chưa kiểm tra trên "
    "môi trường thật, nhưng logic đã được kiểm thử ở mức …”.",
], fill="FDECEE", title_color=RED)

# ---- demo
h2("9.11. Kịch bản demo trực tiếp (nếu được yêu cầu)")
para("Nếu thầy cô nói “cho xem chạy thử”, làm theo đúng thứ tự này — mỗi bước nói một câu:")

table(
    ["Bước", "Thao tác", "Câu nói kèm theo"],
    [
        ["1", "Mở /demo, tab Skill Gap", "“Đây là kết quả phân tích cho user_001 với nghề Data Analyst.”"],
        ["2", "Chỉ vào con số 27,3%", "“Độ phủ hiện tại. Bốn kỹ năng chưa có, bốn chưa đủ mức.”"],
        ["3", "Chỉ vào một dòng below_level", "“Ví dụ EDA: có 35 điểm, nghề cần 70, thiếu 35.”"],
        ["4", "Bấm tab Lộ trình học", "“Tám bước, đúng thứ tự phụ thuộc.”"],
        ["5", "Chỉ vào bước 2 và 3", "“Python trước Pandas — vì Pandas cần Python. Đây là sắp xếp topo.”"],
        ["6", "Bấm tab Nghề phù hợp", "“Data Analyst 24,9% đứng đầu, phù hợp với mục tiêu đã khai.”"],
        ["7", "Bấm tab Đồ thị", "“Nghề ở giữa, kỹ năng vây quanh, mũi tên giữ đúng chiều dữ liệu.”"],
        ["8", "Mở /docs", "“Tài liệu API tự sinh, thử trực tiếp được.”"],
        ["9", "Chạy AQL B3 nếu có DB", "“Một câu traversal tìm toàn bộ kỹ năng nền của Deep Learning.”"],
    ],
    widths=[1.2, 5.4, 10.0], size=9.5,
)
caption("Bảng 9.1. Chín bước demo — tập trước cho quen tay")

box("NẾU DEMO BỊ LỖI GIỮA CHỪNG", [
    "Bình tĩnh, đừng bấm lia lịa. Nói: “Có vẻ server cần khởi động lại, em xin phép một chút.” "
    "Rồi khởi động lại. Nếu vẫn lỗi, chuyển sang ảnh chụp màn hình đã chuẩn bị sẵn và nói "
    "“em có ảnh kết quả đã chạy trước, xin trình bày trên ảnh”.",
    "Luôn chuẩn bị ảnh chụp cho mọi bước demo. Đây là bảo hiểm rẻ nhất.",
], fill="FFF4E5", title_color=ORANGE)

# ================================================================
# 10. CÂU HỎI BẢO VỆ
# ================================================================
h1("10. Hai mươi lăm câu hỏi bảo vệ và câu trả lời mẫu")

para("Nhóm theo bốn chủ đề: lựa chọn công nghệ, dữ liệu, thuật toán, và cách làm. "
     "Câu trả lời viết ở dạng nói được ngay, nhưng nên hiểu ý để trả lời linh hoạt.")

h2("10.1. Nhóm câu hỏi về lựa chọn công nghệ")

h3("Câu 1. Vì sao chọn ArangoDB mà không dùng MySQL hay MongoDB?")
para("“Vì quan hệ giữa các kỹ năng là đồ thị nhiều tầng. Trong MySQL, tìm toàn bộ kỹ năng nền "
     "của Deep Learning phải viết CTE đệ quy, khó đọc và khó biết độ sâu từng đỉnh. "
     "MongoDB thì không hỗ trợ duyệt đồ thị trực tiếp, phải tự viết vòng lặp ở tầng ứng dụng — "
     "chậm và phức tạp. ArangoDB làm được cả document lẫn graph trong một engine và một ngôn ngữ "
     "truy vấn, nên một câu AQL vừa lọc theo thuộc tính vừa duyệt theo cạnh.”")

h3("Câu 2. ArangoDB là gì? Nói ngắn gọn.")
para("“Là cơ sở dữ liệu đa mô hình của hãng ArangoDB. Nó lưu dữ liệu dưới dạng JSON trong các "
     "collection, và hỗ trợ collection cạnh có hai trường bắt buộc là _from và _to. "
     "Ngôn ngữ truy vấn là AQL. Điểm mạnh là một câu lệnh có thể vừa lọc document vừa duyệt đồ thị.”")

h3("Câu 3. Graph database khác relational ở đâu, cụ thể?")
para("“Khác ở chỗ quan hệ được lưu như một bản ghi độc lập, không phải khoá ngoại. "
     "Khoá ngoại chỉ là một con số trỏ sang bảng khác — muốn duyệt nhiều tầng phải JOIN nhiều lần. "
     "Trong graph database, cạnh là bản ghi thật, mang được thuộc tính riêng (ví dụ strength), "
     "và phép duyệt là thao tác có sẵn của database chứ không phải do ứng dụng tự vòng lặp.”")

h3("Câu 4. Vì sao không cho frontend gọi thẳng ArangoDB?")
para("“Ba lý do. Một, phải nhúng mật khẩu database vào mã JavaScript, ai cũng đọc được. "
     "Hai, không kiểm soát được người dùng gửi truy vấn gì — có thể xoá sạch dữ liệu. "
     "Ba, các phép tính nghiệp vụ cần chỗ chạy; đặt ở backend thì viết một lần bằng Python, "
     "kiểm thử được, và không lộ logic ra ngoài.”")

h3("Câu 5. FastAPI là gì, sao không dùng Flask hay Django?")
para("“FastAPI là khung làm API bằng Python. Nó tự kiểm tra kiểu dữ liệu nhờ Pydantic và tự sinh "
     "tài liệu Swagger từ code — nghĩa là mở /docs là thầy cô thử được mọi API. "
     "Flask nhẹ hơn nhưng phải tự làm phần kiểm tra và tài liệu. Django mạnh nhưng nặng, "
     "thừa cho một API đọc dữ liệu như thế này.”")

h2("10.2. Nhóm câu hỏi về dữ liệu")

h3("Câu 6. Dữ liệu thật hay giả?")
para("“Là dữ liệu mẫu của đề tài, trường data_origin ghi synthetic_demo. Nhóm không nói đây là "
     "dữ liệu người thật. Nhưng cấu trúc và quy mô đúng theo tài liệu nghiệp vụ: 12 collection, "
     "1.584 bản ghi, 173 quan hệ tiên quyết — đủ để chứng minh thuật toán chạy đúng.”")

h3("Câu 7. Bao nhiêu bản ghi, chia thế nào?")
para("“1.584 bản ghi trong 12 collection. Năm collection đỉnh: 40 người, 248 kỹ năng, 29 nghề, "
     "89 khóa học, 8 nhà cung cấp. Bảy collection cạnh: 274 has_skill, 40 targets_career, "
     "312 requires_skill, 173 prerequisite, 172 teaches, 110 completed, 89 offered_by.”")

h3("Câu 8. Cạnh prerequisite chiều nào?")
para("“Từ kỹ năng muốn học trỏ tới kỹ năng cần có trước. Pandas trỏ tới Python nghĩa là "
     "muốn học Pandas thì cần Python. Nhóm đã kiểm tra kỹ điểm này vì đọc ngược chiều sẽ làm "
     "lộ trình sai hoàn toàn.”")

h3("Câu 9. Dữ liệu có chu trình không? Xử lý thế nào?")
para("“Với dữ liệu hiện tại thì không — 173 quan hệ tiên quyết tạo thành đồ thị có hướng không "
     "chu trình, nên sắp xếp topo xếp được hết. Nhưng code vẫn xử lý trường hợp xấu: nếu có chu "
     "trình, thuật toán Kahn sẽ không xếp hết, khi đó các kỹ năng còn lại được đưa xuống cuối "
     "và ghi chú rõ, không tự phá vỡ ràng buộc. Phép duyệt BFS cũng có tập đã thăm để chống lặp vô hạn.”")

h3("Câu 10. proficiency và required_level khác nhau thế nào?")
para("“proficiency là trình độ hiện có của người học, nằm trên cạnh has_skill. "
     "required_level là mức nghề yêu cầu, nằm trên cạnh requires_skill. Hai con số cùng thang "
     "0 đến 100 nên so sánh trực tiếp được. Còn importance là mức quan trọng của kỹ năng với nghề, "
     "dùng khi chấm điểm phù hợp.”")

h3("Câu 11. Có bao nhiêu kỹ năng không có khóa học nào?")
para("“145 trong 248 kỹ năng. Đây là điểm yếu của dữ liệu mà nhóm phát hiện khi làm truy vấn B12. "
     "Hệ thống vẫn xử lý được: khi không tìm thấy khóa học, bước đó hiển thị “chưa có khóa học "
     "trong dữ liệu” chứ không bỏ qua im lặng.”")

h2("10.3. Nhóm câu hỏi về thuật toán")

h3("Câu 12. Skill Gap tính thế nào?")
para("“So từng cặp yêu cầu và trình độ hiện có. Ba trạng thái: missing nếu chưa khai báo kỹ năng "
     "đó, below_level nếu có nhưng thấp hơn mức yêu cầu, ok nếu đạt. Độ phủ bằng số ok chia tổng "
     "yêu cầu. Ví dụ user_001: 3 trên 11, tức 27,3%.”")

h3("Câu 13. Vì sao có ba trạng thái mà không phải hai?")
para("“Vì lời khuyên khác nhau. Nếu chỉ có hai trạng thái, người đã có 45 điểm sẽ bị xếp vào "
     "nhóm chưa biết và bị bảo học lại từ đầu — lãng phí. Trạng thái below_level cho phép hệ "
     "thống nói chính xác cần nâng thêm bao nhiêu điểm.”")

h3("Câu 14. Lộ trình đảm bảo đúng thứ tự thế nào?")
para("“Bằng sắp xếp topo, cụ thể là thuật toán Kahn. Đếm bậc vào của mỗi kỹ năng — tức còn bao "
     "nhiêu kỹ năng nền chưa xếp trước nó. Kỹ năng nào bậc vào bằng 0 thì đưa vào hàng đợi. "
     "Lấy ra, ghi vào kết quả, giảm bậc vào của các kỹ năng phụ thuộc đi một. "
     "Lặp tới khi hàng đợi rỗng. Kết quả là kỹ năng nền luôn đứng trước.”")

h3("Câu 15. Nếu nghề không yêu cầu Python mà Pandas lại cần Python thì sao?")
para("“Đó chính là lý do có bước hai của thuật toán sinh lộ trình: leo ngược quan hệ prerequisite "
     "từ mọi kỹ năng còn thiếu để thêm các kỹ năng nền cũng còn thiếu. Trong kết quả thật, "
     "Python xuất hiện ở bước hai và Pandas ở bước ba — dù cả hai đều là yêu cầu trực tiếp "
     "của nghề Data Analyst.”")

h3("Câu 16. Làm sao biết lộ trình đúng? Có kiểm chứng không?")
para("“Ba bằng chứng trong kết quả thật. Một: Python đứng trước Pandas, đúng quan hệ phụ thuộc. "
     "Hai: Data Visualization đứng trước Power BI và Tableau. Ba: bốn khóa người dùng đã hoàn thành "
     "không bị đề xuất lại, hệ thống đếm được đã loại bốn. Ngoài ra kiểm thử tự động có bất biến: "
     "thứ tự phải liên tục từ một và mọi bước phải có khoảng trống dương.”")

h3("Câu 17. Điểm phù hợp nghề tính thế nào, có ý nghĩa gì?")
para("“Là tổng importance của các kỹ năng đã đạt chia tổng importance toàn bộ yêu cầu. "
     "Phải nhân theo importance vì kỹ năng có vai trò khác nhau — đạt nhiều kỹ năng phụ không "
     "bằng đạt một kỹ năng cốt lõi. Điểm này dùng để tìm điểm xuất phát hợp lý, "
     "không phải để đánh giá năng lực.”")

h3("Câu 18. 24,9% nghĩa là người đó giỏi 25% nghề à?")
para("“Không. Nó có nghĩa: trong tổng trọng số các yêu cầu của nghề, người này đã đáp ứng khoảng "
     "một phần tư. Đây là chỉ số khoảng cách, không phải chỉ số năng lực. Nhóm cố ý gọi là "
     "mức độ gần để tránh hiểu sai.”")

h3("Câu 19. Duyệt kỹ năng nền dùng thuật toán gì?")
para("“Duyệt theo chiều rộng, BFS, đi ngược cạnh prerequisite từ kỹ năng gốc. Có tập đã thăm "
     "để không lặp, và có giới hạn độ sâu. Với Deep Learning ra năm kỹ năng nền, độ sâu tối đa hai tầng.”")

h2("10.4. Nhóm câu hỏi về cách làm")

h3("Câu 20. Nhóm làm được gì, chưa làm được gì?")
para("“Làm được: cơ sở dữ liệu với dữ liệu thật từ dump của đề tài, bộ 30 truy vấn AQL, "
     "backend với 12 nhóm API và bốn thuật toán, 42 điểm kiểm thử đạt hết, giao diện demo bốn tab, "
     "báo cáo và slide. Chưa làm được: chưa chạy ArangoDB thật vì máy không có Docker; "
     "backend mới chỉ đọc, phần ghi dữ liệu để trên Web Interface và AQL; giao diện React "
     "trong gói bàn giao chưa nối sang API mới vì dùng lược đồ dữ liệu khác.”")

h3("Câu 21. Nếu không có ArangoDB thì đồ án có ý nghĩa gì?")
para("“Dữ liệu và logic là thật. Toàn bộ 1.584 bản ghi được trích từ chính file dump của đề tài, "
     "không phải tự bịa. Các thuật toán chạy trên đúng dữ liệu đó và cho kết quả kiểm chứng được. "
     "Phần chưa kiểm tra chỉ là khâu kết nối — và code đã có sẵn chế độ arango, chỉ cần đổi biến "
     "môi trường trên máy có Docker.”")

h3("Câu 22. Vì sao viết hai lớp lưu trữ? Có phải làm cho phức tạp?")
para("“Không. Đó là Repository Pattern, và nó giải quyết một vấn đề thật: nhóm không có Docker, "
     "nhưng vẫn cần kiểm thử nghiệp vụ. Nhờ tách lớp, 42 điểm kiểm thử chạy được trên máy bất kỳ, "
     "và khi có database thật thì chỉ đổi một biến môi trường, không sửa logic. "
     "Nếu viết gộp, mỗi lần kiểm thử đều phải có ArangoDB đang chạy.”")

h3("Câu 23. Đề tài yêu cầu CRUD, em làm chưa?")
para("“Có, bằng AQL trên ArangoDB Web Interface — đúng yêu cầu quản trị dữ liệu trên Web Interface "
     "của đề tài. Truy vấn A8 thêm người dùng, A9 thêm hoặc cập nhật kỹ năng của người dùng, "
     "A10 xoá người dùng demo kèm các cạnh liên quan. Backend API được thiết kế chỉ đọc vì phạm vi "
     "đồ án tập trung vào phân tích đồ thị.”")

h3("Câu 24. Làm sao biết code đúng?")
para("“42 điểm kiểm thử tự động, trong đó có các bất biến nghiệp vụ chứ không chỉ kiểm tra mã trạng "
     "thái HTTP. Ví dụ tổng ba trạng thái phải bằng tổng yêu cầu; thứ tự lộ trình liên tục từ một; "
     "mọi cạnh trong đồ thị phải trỏ tới đỉnh có thật. Ngoài ra nhóm kiểm chứng chéo bằng cách "
     "mô phỏng lại các truy vấn AQL bằng Python rồi so với kết quả backend.”")

h3("Câu 25. Nếu có thêm thời gian, nhóm làm gì tiếp?")
para("“Bốn việc theo thứ tự ưu tiên. Một: phục hồi dump vào ArangoDB thật trên máy có Docker "
     "và chạy lại toàn bộ kiểm thử ở chế độ arango. Hai: thêm các đường dẫn ghi dữ liệu để người "
     "học tự cập nhật kỹ năng. Ba: nối giao diện React sang API mới. Bốn: mở rộng thuật toán "
     "lộ trình để tính cả thời lượng và chi phí khóa học, vì dữ liệu đã có trường duration_hours.”")

box("BA CÂU BẠN CHẮC CHẮN SẼ BỊ HỎI — HỌC THUỘC", [
    "1. “Vì sao chọn ArangoDB?” → vì quan hệ kỹ năng là đồ thị nhiều tầng; một câu traversal "
    "thay cho CTE đệ quy.",
    "2. “Lộ trình đảm bảo thứ tự thế nào?” → sắp xếp topo (Kahn), kèm bằng chứng Python trước Pandas.",
    "3. “Dữ liệu thật không?” → dữ liệu mẫu của đề tài, synthetic_demo, nhưng cấu trúc và quy mô "
    "đúng tài liệu, trích từ chính dump của đề tài.",
], fill="FDECEE", title_color=RED)

# ================================================================
# 11. HẠN CHẾ
# ================================================================
h1("11. Hạn chế và việc còn lại — nói thật với nhóm")

para("Chương này để bạn biết chính xác cái gì đã xong, cái gì chưa, và nếu bị hỏi thì trả lời sao. "
     "Biết rõ hạn chế của mình là một điểm mạnh khi bảo vệ, không phải điểm yếu.")

h2("11.1. Bảng trạng thái thật của từng phần")

table(
    ["Phần", "Trạng thái", "Bằng chứng / ghi chú"],
    [
        ["Dữ liệu 12 collection, 1.584 bản ghi", "XONG", "manifest.json và API /meta/release trả đúng số"],
        ["Bộ 30 truy vấn AQL", "XONG", "Đã viết, đã kiểm tra logic, đã mô phỏng bằng Python"],
        ["Backend 12 nhóm API", "XONG", "42/42 kiểm thử đạt"],
        ["Bốn thuật toán nghiệp vụ", "XONG", "Có kết quả thật trên dữ liệu thật"],
        ["Giao diện demo /demo", "XONG", "Bốn tab, đã kiểm tra hiển thị"],
        ["Báo cáo Word + slide", "XONG", "13 trang báo cáo, 10 slide, đã kiểm tra bố cục"],
        ["Chạy ArangoDB thật", "CHƯA", "Máy không có Docker/WSL/podman. Code đã có chế độ arango"],
        ["Kiểm thử AQL trên server thật", "CHƯA", "Cùng lý do trên"],
        ["CRUD qua API", "CHƯA", "Đã có AQL A8–A10; API thiết kế chỉ đọc theo phạm vi đề tài"],
        ["Nối frontend React sang API", "CHƯA", "Frontend bàn giao dùng lược đồ khác (24 collection)"],
        ["Sửa lỗi hiển thị tiếng Việt trong frontend bàn giao", "CHƯA", "Có mojibake trong vài file nguồn"],
    ],
    widths=[5.4, 2.2, 8.8], size=9.5,
)
caption("Bảng 11.1. Bảy phần xong, bốn phần chưa — nói đúng bảng này là an toàn")

h2("11.2. Vì sao chưa chạy được ArangoDB thật")

para("Đã kiểm tra và xác nhận trên máy phát triển: lệnh docker không tồn tại, "
     "wsl không có bản phân phối nào được cài, podman không có, và cổng 8529 không có gì trả lời. "
     "ArangoDB bản 3.12 không có bộ cài Windows, bản 3.11 thì có nhưng nhóm quyết định không cài "
     "lên máy người dùng để tránh thay đổi hệ thống ngoài phạm vi đồ án.")

box("CÁCH NÓI VỀ ĐIỀU NÀY", [
    "“Nhóm đã kiểm tra bốn cách: Docker, WSL, Podman, và cài trực tiếp trên Windows. "
    "Ba cách đầu không có sẵn, cách thứ tư thì bản 3.12 không có bộ cài Windows. "
    "Nhóm quyết định không cài phần mềm hệ thống lên máy cá nhân mà thay vào đó trích toàn bộ "
    "dữ liệu thật ra file và viết sẵn chế độ kết nối. Như vậy phần nghiệp vụ vẫn kiểm chứng được "
    "đầy đủ, chỉ khâu kết nối là chưa bật thử.”",
    "Nói vậy vừa trung thực vừa cho thấy nhóm đã chủ động tìm cách, không phải bỏ dở.",
], fill="EAF1FB", title_color=NAVY)

h2("11.3. Vì sao không nối frontend React có sẵn")

para("Gói bàn giao frontend dùng bộ dữ liệu catalog phiên bản 3.55 với 24 collection và 5.718 bản ghi. "
     "Bộ này khác lược đồ so với database skill_graph_db của đề tài, và quan trọng hơn: "
     "collection prerequisite trong bộ đó không có cạnh nào. Ghép vào thì hai chức năng "
     "duyệt tiên quyết và sinh lộ trình sẽ không có dữ liệu để chạy — tức là mất phần cốt lõi "
     "của đề tài.")

para("Vì vậy nhóm làm giao diện demo gọn, đúng dữ liệu, đúng bốn chức năng cần trình bày. "
     "Đây là quyết định có chủ ý, không phải bỏ sót.")

h2("11.4. Việc cần làm nếu có thêm thời gian (theo thứ tự)")

num("Phục hồi dump vào ArangoDB thật, chạy lại 42 điểm kiểm thử ở chế độ arango. "
    "Đây là việc quan trọng nhất — làm được là đồ án khép kín từ đầu tới cuối.", restart=True)
num("Chạy toàn bộ 30 truy vấn AQL trên server thật, chụp ảnh kết quả cho báo cáo.", restart=True)
num("Thêm các đường dẫn ghi dữ liệu qua API, tái sử dụng truy vấn A8 đến A10.")
num("Nối frontend React sang API mới, hoặc nếu giữ giao diện demo thì mở rộng thêm phần tìm kiếm kỹ năng.")
num("Mở rộng thuật toán lộ trình để tính cả thời lượng khóa học — dữ liệu đã có trường duration_hours, "
    "chỉ cần thêm một tiêu chí khi sắp xếp.")

# ================================================================
# 12. BẢNG TRA NHANH
# ================================================================
h1("12. Bảng tra nhanh tất cả con số")

para("In trang này ra hoặc để mở bên cạnh khi thuyết trình. "
     "Nói số đúng là cách nhanh nhất để tạo niềm tin.")

h2("12.1. Con số về dữ liệu")

table(
    ["Con số", "Giá trị", "Ghi nhớ là"],
    [
        ["Số collection", "12", "5 đỉnh + 7 cạnh"],
        ["Tổng bản ghi", "1.584", "Khớp tài liệu nghiệp vụ đề tài"],
        ["Người dùng", "40", "user_001 là Trần Minh"],
        ["Kỹ năng", "248", "Chia 8 nhóm chính"],
        ["Nghề nghiệp", "29", "data_analyst được dùng trong demo"],
        ["Khóa học", "89", "Trung cấp 51, cơ bản 26, nâng cao 12"],
        ["Nhà cung cấp", "8", "Coursera, edX, MIT, freeCodeCamp…"],
        ["Cạnh has_skill", "274", "Lượt khai báo kỹ năng"],
        ["Cạnh targets_career", "40", "Mục tiêu nghề nghiệp"],
        ["Cạnh requires_skill", "312", "Yêu cầu kỹ năng của nghề"],
        ["Cạnh prerequisite", "173", "Quan hệ tiên quyết — quan trọng nhất"],
        ["Cạnh teaches", "172", "Khóa học dạy kỹ năng"],
        ["Cạnh completed", "110", "Khóa đã hoàn thành"],
        ["Cạnh offered_by", "89", "Khóa do nhà cung cấp cấp"],
        ["Kỹ năng không có khóa học", "145 / 248", "Điểm yếu dữ liệu, đã phát hiện"],
    ],
    widths=[5.0, 3.2, 8.2], size=10,
)
caption("Bảng 12.1. Mọi con số về dữ liệu")

h2("12.2. Con số về kết quả nghiệp vụ")

table(
    ["Con số", "Giá trị", "Xuất hiện ở đâu"],
    [
        ["Yêu cầu của nghề Data Analyst", "11", "Skill Gap của user_001"],
        ["Đã đạt / chưa đủ / thiếu hẳn", "3 / 4 / 4", "Tổng bằng 11"],
        ["Độ phủ kỹ năng", "27,3%", "3 chia 11"],
        ["Số bước lộ trình", "8", "SQL tới Data Cleaning"],
        ["Số khóa đã học bị loại khỏi gợi ý", "4", "Trường skippedCompletedCourses"],
        ["Độ sâu tiên quyết của Deep Learning", "2 tầng", "5 kỹ năng nền"],
        ["Điểm phù hợp cao nhất", "Data Analyst 24,9%", "Career match"],
        ["Nghề đứng thứ hai", "Data Scientist 13,2%", "Career match"],
        ["Điểm kiểm thử", "42 / 42", "smoke_test.py"],
        ["Số truy vấn AQL", "30", "10 cơ bản + 20 nâng cao"],
        ["Số nhóm API", "12", "Xem bảng 4.2 báo cáo"],
        ["Số slide", "10", "BAO_CAO_SLIDE.pptx"],
    ],
    widths=[6.0, 4.0, 6.4], size=10,
)
caption("Bảng 12.2. Con số về kết quả — phần hay được hỏi")

h2("12.3. Ba câu chốt nếu chỉ còn một phút")

box("NÓI BA CÂU NÀY", [
    "1. “Hệ thống trả lời ba câu hỏi: nghề cần gì, tôi thiếu gì, học gì trước.”",
    "2. “Cái làm nên đồ án là graph: quan hệ tiên quyết giữa kỹ năng là đồ thị nhiều tầng, "
    "và một câu AQL traversal thay cho nhiều vòng lặp SQL.”",
    "3. “Lộ trình không phải danh sách theo bảng chữ cái mà là kết quả sắp xếp topo — "
    "bằng chứng là Python đứng trước Pandas.”",
], fill="E8F6F0", title_color=GREEN)

h2("12.4. Từ điển nhanh thuật ngữ")

table(
    ["Thuật ngữ", "Nghĩa ngắn", "Nghĩa trong đồ án"],
    [
        ["Collection", "Thùng chứa bản ghi", "12 thùng: 5 đỉnh, 7 cạnh"],
        ["Document", "Một bản ghi JSON", "Một người dùng, một kỹ năng…"],
        ["Vertex / Đỉnh", "Điểm trong đồ thị", "User, Skill, Career, Course, Provider"],
        ["Edge / Cạnh", "Đường nối hai đỉnh", "has_skill, prerequisite…"],
        ["Traversal", "Phép duyệt đồ thị", "Tìm kỹ năng nền nhiều tầng"],
        ["AQL", "Ngôn ngữ truy vấn ArangoDB", "30 truy vấn trong file .aql"],
        ["Named graph", "Đồ thị có tên, gom nhiều collection", "skill_graph"],
        ["Skill Gap", "Khoảng trống kỹ năng", "Chức năng 1"],
        ["Prerequisite", "Điều kiện tiên quyết", "Chức năng 2"],
        ["Career fit", "Điểm phù hợp nghề", "Chức năng 3"],
        ["Learning path", "Lộ trình học", "Chức năng 4"],
        ["Topological sort", "Sắp xếp theo thứ tự phụ thuộc", "Thuật toán Kahn"],
        ["BFS", "Duyệt theo chiều rộng", "Dùng để tìm kỹ năng nền"],
        ["Repository Pattern", "Tách lớp lấy dữ liệu khỏi lớp xử lý", "storage.py và core.py"],
        ["CRUD", "Thêm, đọc, sửa, xoá", "AQL A8–A10"],
        ["REST API", "Kiểu API dùng HTTP", "12 nhóm đường dẫn"],
        ["JSON", "Định dạng dữ liệu dạng text", "Mọi phản hồi của API"],
        ["Pydantic", "Thư viện kiểm tra kiểu của Python", "models.py"],
        ["CORS", "Quy định trang web nào được gọi API", "config.py"],
        ["Mojibake", "Lỗi hiển thị ký tự do sai bảng mã", "Vấn đề còn lại ở frontend bàn giao"],
    ],
    widths=[3.4, 6.0, 7.0], size=9.5,
)
caption("Bảng 12.3. Từ điển thuật ngữ — đọc trước khi vào phòng thi")

# ---------------- kết
doc.add_paragraph()
p = doc.add_paragraph()
p.alignment = WD_ALIGN_PARAGRAPH.CENTER
r = p.add_run("— HẾT TÀI LIỆU —")
_vi(r)
r.font.size = Pt(12)
r.font.bold = True
r.font.color.rgb = GREY

p = doc.add_paragraph()
p.alignment = WD_ALIGN_PARAGRAPH.CENTER
p.paragraph_format.space_before = Pt(6)
r = p.add_run("Chúc bạn tự tin trình bày. Nhớ ba câu chốt ở mục 12.3.")
_vi(r)
r.font.size = Pt(11)
r.font.italic = True
r.font.color.rgb = GREY

doc.save(OUT)
print("saved:", OUT)
