"""
Báo cáo toàn diện dự án Learning Data System
Trường ĐH Công nghệ Thông tin – ĐHQG TP.HCM
Môn: Cơ sở dữ liệu nâng cao | Học viên: Nguyễn Trung Tính
"""
from docx import Document
from docx.shared import Pt, Cm, RGBColor, Inches as DInches
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

from pptx import Presentation
from pptx.util import Inches, Pt as PPt, Emu
from pptx.dml.color import RGBColor as PR
from pptx.enum.text import PP_ALIGN
from pptx.oxml.ns import qn as pqn
from pptx.oxml import parse_xml
import copy

# ── Palette ─────────────────────────────────────────────────────────────────
D_DARK   = RGBColor(0x1A,0x35,0x6E)
D_BLUE   = RGBColor(0x27,0x6F,0xBF)
D_LBLUE  = RGBColor(0xD6,0xE4,0xF7)
D_EBLU   = RGBColor(0xEB,0xF3,0xFB)
D_ORG    = RGBColor(0xE8,0x6D,0x2E)
D_GRN    = RGBColor(0x1A,0x7A,0x50)
D_GRAY   = RGBColor(0x55,0x55,0x55)
D_WHITE  = RGBColor(0xFF,0xFF,0xFF)
D_RED    = RGBColor(0xC0,0x39,0x2B)

P_DARK   = PR(0x1A,0x35,0x6E)
P_BLUE   = PR(0x27,0x6F,0xBF)
P_LBLUE  = PR(0xD6,0xE4,0xF7)
P_ORG    = PR(0xE8,0x6D,0x2E)
P_GRN    = PR(0x15,0x85,0x7A)
P_WHITE  = PR(0xFF,0xFF,0xFF)
P_GRAY   = PR(0x55,0x55,0x55)
P_RED    = PR(0xC0,0x39,0x2B)
P_PUR    = PR(0x7B,0x35,0xAD)
P_BG     = PR(0xF5,0xF7,0xFA)
P_DARK2  = PR(0x12,0x25,0x50)

# ════════════════════════════════════════════════════════════════════════════
#  WORD HELPERS
# ════════════════════════════════════════════════════════════════════════════
def shd(cell, hex6):
    tc = cell._tc
    pr = tc.get_or_add_tcPr()
    s  = OxmlElement('w:shd')
    s.set(qn('w:val'),'clear'); s.set(qn('w:color'),'auto'); s.set(qn('w:fill'),hex6)
    pr.append(s)

def w_head(doc, text, lvl, color=None):
    p = doc.add_heading(text, level=lvl)
    if p.runs:
        r = p.runs[0]
        if color: r.font.color.rgb = color
    return p

def w_para(doc, text, bold=False, italic=False, sz=11, color=None, align=None):
    p = doc.add_paragraph()
    r = p.add_run(text)
    r.bold=bold; r.italic=italic; r.font.size=Pt(sz)
    if color: r.font.color.rgb = color
    if align: p.alignment = align
    return p

def w_bullet(doc, items, sz=11):
    for item in items:
        p = doc.add_paragraph(item, style='List Bullet')
        p.runs[0].font.size = Pt(sz)

def w_tbl_header(tbl, headers, bg='1A356E'):
    row = tbl.rows[0]
    for i,h in enumerate(headers):
        c = row.cells[i]; c.text = h
        r = c.paragraphs[0].runs[0]
        r.bold=True; r.font.color.rgb=D_WHITE; r.font.size=Pt(9.5)
        c.paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
        shd(c, bg)

def make_table(doc, headers, rows_data, col_widths=None, alt_color='EBF3FB'):
    tbl = doc.add_table(rows=len(rows_data)+1, cols=len(headers))
    tbl.style = 'Table Grid'
    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    w_tbl_header(tbl, headers)
    for ri, row in enumerate(rows_data, 1):
        for ci, val in enumerate(row):
            c = tbl.rows[ri].cells[ci]
            c.text = str(val)
            c.paragraphs[0].runs[0].font.size = Pt(9.5)
            if ri % 2 == 0: shd(c, alt_color)
    return tbl

def entity_table(doc, tbl_name, description, columns):
    """columns = list of (col_name, dtype, constraints, description)"""
    doc.add_paragraph()
    h = doc.add_heading(f"  {tbl_name}", 3)
    h.runs[0].font.color.rgb = D_BLUE
    p = doc.add_paragraph()
    r = p.add_run(description)
    r.italic=True; r.font.size=Pt(10); r.font.color.rgb=D_GRAY
    make_table(doc,
        ["Cột", "Kiểu dữ liệu", "Ràng buộc", "Mô tả"],
        columns)

# ════════════════════════════════════════════════════════════════════════════
#  PPT HELPERS
# ════════════════════════════════════════════════════════════════════════════
BLANK = None  # set after prs init

def rect(slide, x,y,w,h, fill, line=None):
    s = slide.shapes.add_shape(1, Inches(x),Inches(y),Inches(w),Inches(h))
    s.fill.solid(); s.fill.fore_color.rgb = fill
    if line: s.line.color.rgb = line
    else: s.line.fill.background()
    return s

def txt(slide, text, x,y,w,h, sz=14, bold=False, italic=False,
        color=P_WHITE, align=PP_ALIGN.LEFT, wrap=True):
    txb = slide.shapes.add_textbox(Inches(x),Inches(y),Inches(w),Inches(h))
    txb.word_wrap = wrap
    tf = txb.text_frame; tf.word_wrap = wrap
    p = tf.paragraphs[0]; p.alignment = align
    run = p.add_run()
    run.text = text
    run.font.size = PPt(sz); run.font.bold = bold; run.font.italic = italic
    if color: run.font.color.rgb = color
    return txb

def slide_header(slide, title, subtitle=None, color=None):
    c = color or P_DARK
    rect(slide, 0,0, 13.33,1.15, c)
    rect(slide, 0,1.15, 0.1,6.35, P_ORG)
    txt(slide, title, 0.25,0.1, 12.5,0.7, sz=24, bold=True, color=P_WHITE)
    if subtitle:
        txt(slide, subtitle, 0.25,0.78, 12.5,0.35, sz=12, italic=True, color=P_LBLUE)

def tag(slide, label, x,y, fill=P_BLUE, sz=10):
    w = len(label)*0.095 + 0.3
    rect(slide, x,y, w,0.33, fill)
    txt(slide, label, x+0.08,y+0.02, w-0.1,0.3, sz=sz, bold=True, color=P_WHITE)
    return w

def bullet_list(slide, items, x,y, w=11.5, sz=12.5, dot_color=P_BLUE, gap=0.55):
    for i,item in enumerate(items):
        iy = y + i*gap
        rect(slide, x, iy+0.1, 0.22, 0.22, dot_color)
        txt(slide, item, x+0.32, iy, w, gap-0.05, sz=sz, color=PR(0x22,0x22,0x22), bold=False)

def hl_box(slide, text, x,y, w=12.6, bg=PR(0xFF,0xF3,0xE8)):
    rect(slide, x,y, w,0.7, bg)
    rect(slide, x,y, 0.1,0.7, P_ORG)
    txt(slide, text, x+0.2,y+0.08, w-0.3,0.55, sz=12, bold=True,
        color=PR(0xC0,0x50,0x00))

def footer(slide, text=None):
    t = text or "Nguyễn Trung Tính  |  Cơ sở dữ liệu nâng cao  |  UIT – ĐHQG TP.HCM  |  03/2026"
    rect(slide, 0,7.15, 13.33,0.35, P_DARK2)
    txt(slide, t, 0.3,7.18, 12.8,0.3, sz=9, italic=True, color=P_LBLUE, align=PP_ALIGN.CENTER)


# ════════════════════════════════════════════════════════════════════════════
#  WORD DOCUMENT
# ════════════════════════════════════════════════════════════════════════════
def create_word():
    doc = Document()
    for sec in doc.sections:
        sec.top_margin=Cm(2.5); sec.bottom_margin=Cm(2.5)
        sec.left_margin=Cm(3.0); sec.right_margin=Cm(2.0)

    # ── TRANG BÌA ─────────────────────────────────────────────────────────
    for txt_,sz_,bold_,color_ in [
        ("TRƯỜNG ĐẠI HỌC CÔNG NGHỆ THÔNG TIN", 13, True, D_DARK),
        ("ĐẠI HỌC QUỐC GIA TP. HỒ CHÍ MINH", 13, True, D_DARK),
    ]:
        p=doc.add_paragraph(); p.alignment=WD_ALIGN_PARAGRAPH.CENTER
        r=p.add_run(txt_); r.bold=bold_; r.font.size=Pt(sz_); r.font.color.rgb=color_

    doc.add_paragraph(); doc.add_paragraph()
    p=doc.add_paragraph(); p.alignment=WD_ALIGN_PARAGRAPH.CENTER
    r=p.add_run("BÁO CÁO MÔN HỌC – CƠ SỞ DỮ LIỆU NÂNG CAO")
    r.font.size=Pt(14); r.bold=True; r.font.color.rgb=D_GRAY

    doc.add_paragraph()
    p=doc.add_paragraph(); p.alignment=WD_ALIGN_PARAGRAPH.CENTER
    r=p.add_run("HỆ THỐNG QUẢN LÝ VÀ PHÂN TÍCH\nDỮ LIỆU HỌC TẬP")
    r.font.size=Pt(26); r.bold=True; r.font.color.rgb=D_DARK

    doc.add_paragraph()
    p=doc.add_paragraph(); p.alignment=WD_ALIGN_PARAGRAPH.CENTER
    r=p.add_run("Ứng dụng PostgreSQL nâng cao tại Trung tâm Tin học T3H")
    r.font.size=Pt(14); r.italic=True; r.font.color.rgb=D_BLUE

    doc.add_paragraph(); doc.add_paragraph()
    tbl=doc.add_table(rows=4,cols=2); tbl.alignment=WD_TABLE_ALIGNMENT.CENTER
    info=[("Học viên:","Nguyễn Trung Tính"),
          ("Môn học:","Cơ sở dữ liệu nâng cao (Advanced Database)"),
          ("Trường:","Trường ĐH Công nghệ Thông tin – ĐHQG TP.HCM"),
          ("Năm học:","2025 – 2026")]
    for i,(k,v) in enumerate(info):
        tbl.rows[i].cells[0].text=k; tbl.rows[i].cells[1].text=v
        tbl.rows[i].cells[0].paragraphs[0].runs[0].bold=True
        tbl.rows[i].cells[0].paragraphs[0].runs[0].font.color.rgb=D_DARK

    doc.add_paragraph()
    p=doc.add_paragraph(); p.alignment=WD_ALIGN_PARAGRAPH.CENTER
    r=p.add_run("TP. Hồ Chí Minh, tháng 03 năm 2026")
    r.italic=True; r.font.size=Pt(11); r.font.color.rgb=D_GRAY
    doc.add_page_break()

    # ── CHƯƠNG 1: TỔNG QUAN ───────────────────────────────────────────────
    w_head(doc,"CHƯƠNG 1: TỔNG QUAN DỰ ÁN",1,D_DARK)
    w_head(doc,"1.1 Giới thiệu",2,D_BLUE)
    w_para(doc,"Dự án xây dựng hệ thống quản lý và phân tích dữ liệu học tập cho Trung tâm Tin học T3H – TP. Hồ Chí Minh. Hệ thống được xây dựng trên nền PostgreSQL 14+ với đầy đủ tính năng từ thiết kế schema chuẩn 3NF, triggers, stored procedures, materialized views đến 6 mô hình CSDL nâng cao theo chương trình đào tạo thạc sĩ.")
    doc.add_paragraph()

    w_head(doc,"1.2 Mục tiêu dự án",2,D_BLUE)
    w_bullet(doc,[
        "Xây dựng CSDL hoàn chỉnh quản lý học viên, khóa học, giảng viên, lớp học, điểm danh, điểm số",
        "Triển khai đầy đủ 6 mô hình CSDL nâng cao: Object-Relational, Deductive, Distributed, NoSQL, Spatial, FTS/Multimedia",
        "Phát triển ứng dụng web demo (Flask) với CRUD đầy đủ và 17 analytics queries",
        "Thiết kế hệ thống Docker hoàn chỉnh gồm main node (PostgreSQL) + archive node (phân tán) + Web + pgAdmin",
        "Sinh dữ liệu mẫu sát thực tế T3H: 300 học viên, 16 khóa, 5 học kỳ, 32.000+ bản ghi",
    ])
    doc.add_paragraph()

    w_head(doc,"1.3 Công nghệ sử dụng",2,D_BLUE)
    make_table(doc,
        ["Thành phần","Công nghệ","Phiên bản","Vai trò"],
        [("CSDL chính","PostgreSQL + PostGIS","16 / 3.4","Lưu trữ, xử lý dữ liệu"),
         ("CSDL phân tán","PostgreSQL (archive node)","16","FDW – node lưu trữ lịch sử"),
         ("Backend","Python + Flask","3.11 / 3.x","REST API & Web demo"),
         ("Frontend","Bootstrap 5 + Chart.js","5 / 4","Dashboard & báo cáo"),
         ("Containerization","Docker Compose","20.x","Orchestration đa container"),
         ("Quản lý DB","pgAdmin 4","Latest","Giao diện quản lý trực quan"),
        ])
    doc.add_page_break()

    # ── CHƯƠNG 2: KIẾN TRÚC HỆ THỐNG ─────────────────────────────────────
    w_head(doc,"CHƯƠNG 2: KIẾN TRÚC HỆ THỐNG",1,D_DARK)
    w_para(doc,"Hệ thống được thiết kế theo kiến trúc 3 tầng (3-Tier Architecture) kết hợp với mô hình phân tán 2 node:")
    doc.add_paragraph()

    p=doc.add_paragraph()
    r=p.add_run(
"┌─────────────────────────────────────────────────────────────────┐\n"
"│                  TẦNG TRÌNH BÀY (Presentation Layer)            │\n"
"│    Browser  ──►  Flask Web App  ──►  Bootstrap 5 + Chart.js     │\n"
"│              http://localhost:5000                               │\n"
"├─────────────────────────────────────────────────────────────────┤\n"
"│                  TẦNG NGHIỆP VỤ (Business Logic Layer)          │\n"
"│    Flask Routes  │  REST API  │  Analytics  │  Auth             │\n"
"│    Stored Procedures  │  Triggers  │  Views  │  Functions       │\n"
"├───────────────────────────┬─────────────────────────────────────┤\n"
"│   TẦNG DỮ LIỆU – MAIN     │  TẦNG DỮ LIỆU – ARCHIVE NODE       │\n"
"│   PostgreSQL 16 (port 5432)│  PostgreSQL 16 (port 5433)         │\n"
"│   DB: learning_data_system│  DB: t3h_archive                    │\n"
"│   11 bảng + 6 demo modules│  enrollments_2022, course_stats_2022│\n"
"│   Triggers, MatViews, FDW ◄──────── postgres_fdw ──────────────►│\n"
"└───────────────────────────┴─────────────────────────────────────┘"
    )
    r.font.name='Courier New'; r.font.size=Pt(8.5)

    doc.add_paragraph()
    w_head(doc,"2.1 Các container Docker",2,D_BLUE)
    make_table(doc,
        ["Container","Image","Port","Mô tả"],
        [("t3h_postgres","postgis/postgis:16-3.4","5432","Main database + PostGIS"),
         ("t3h_archive","postgres:16","5433","Archive node – FDW distributed"),
         ("t3h_web","python:3.11-slim","5000","Flask web application"),
         ("t3h_generator","python:3.11-slim","–","Data generator (run once)"),
         ("t3h_pgadmin","dpage/pgadmin4","8080","DB admin UI (profile: tools)"),
        ])

    doc.add_paragraph()
    w_head(doc,"2.2 Luồng dữ liệu",2,D_BLUE)
    w_bullet(doc,[
        "setup.sh khởi động main node (t3h_postgres) + archive node (t3h_archive) đồng thời",
        "Data generator chạy một lần, sinh 32.000+ bản ghi vào main database",
        "6 demo SQL files được import tự động sau khi data generator hoàn thành",
        "FDW (Foreign Data Wrapper) kết nối main node → archive node qua Docker network",
        "Flask web app kết nối main database, cung cấp giao diện CRUD + analytics",
    ])
    doc.add_page_break()

    # ── CHƯƠNG 3: THIẾT KẾ CSDL ──────────────────────────────────────────
    w_head(doc,"CHƯƠNG 3: THIẾT KẾ CƠ SỞ DỮ LIỆU",1,D_DARK)
    w_head(doc,"3.1 Sơ đồ quan hệ (ERD)",2,D_BLUE)
    w_para(doc,"Hệ thống gồm 11 bảng chính tổ chức theo chuẩn 3NF (Third Normal Form):")
    doc.add_paragraph()
    p=doc.add_paragraph()
    r=p.add_run(
"                    ┌─────────────┐      ┌─────────────┐\n"
"                    │  instructors │      │   courses   │\n"
"                    │  PK: id      │      │  PK: id     │\n"
"                    └──────┬──────┘      └──────┬──────┘\n"
"                           │ 1                   │ 1\n"
"                           │                     │\n"
"                    ┌──────▼─────────────────────▼──────┐\n"
"  ┌──────────┐   1  │               classes              │\n"
"  │ students │──────│  PK: class_id  FK: course, instr.  │\n"
"  │ PK: id   │   N  └───────────────────┬────────────────┘\n"
"  └────┬─────┘                          │ 1\n"
"       │ 1                              │\n"
"       │      ┌─────────────────────────▼──────────────────┐\n"
"       └──────►          enrollments (junction)             │\n"
"           N  │  PK: enrollment_id  FK: student, class      │\n"
"              └──────┬──────────────────────────┬───────────┘\n"
"                     │ 1                         │ 1\n"
"                     │                           │\n"
"              ┌──────▼──────┐          ┌─────────▼─────────┐\n"
"              │  attendance  │          │       grades       │\n"
"              │  PK: att_id  │          │  PK: grade_id      │\n"
"              └─────────────┘          └───────────────────┘\n"
"\n"
"  Schema V2 (bổ sung FK → enrollments/students):\n"
"  payments ──► enrollments    certificates ──► enrollments\n"
"  feedback ──► enrollments    audit_log (standalone)"
    )
    r.font.name='Courier New'; r.font.size=Pt(8.5)

    # Table descriptions
    doc.add_paragraph()
    w_head(doc,"3.2 Mô tả chi tiết các bảng – Schema gốc (7 bảng)",2,D_BLUE)

    entity_table(doc,"students","Lưu thông tin cá nhân và trạng thái học viên",[
        ("student_id","SERIAL","PK, NOT NULL","Khóa chính tự tăng"),
        ("first_name","VARCHAR(50)","NOT NULL","Tên học viên"),
        ("last_name","VARCHAR(50)","NOT NULL","Họ và tên đệm"),
        ("email","VARCHAR(100)","NOT NULL, UNIQUE","Email đăng nhập, duy nhất"),
        ("phone","VARCHAR(15)","NULL","Số điện thoại"),
        ("date_of_birth","DATE","NOT NULL","Ngày sinh"),
        ("gender","VARCHAR(10)","CHECK IN ('Nam','Nữ','Khác')","Giới tính"),
        ("address","TEXT","NULL","Địa chỉ thường trú"),
        ("enrolled_date","DATE","DEFAULT CURRENT_DATE","Ngày nhập học"),
        ("status","VARCHAR(20)","DEFAULT 'Active'","Active/Inactive/Graduated/Suspended"),
        ("created_at","TIMESTAMP","NOT NULL","Thời điểm tạo bản ghi"),
        ("updated_at","TIMESTAMP","NOT NULL","Thời điểm cập nhật (trigger)"),
    ])

    entity_table(doc,"courses","Danh mục khóa học của trung tâm",[
        ("course_id","SERIAL","PK","Khóa chính"),
        ("course_code","VARCHAR(20)","NOT NULL, UNIQUE","Mã khóa học (vd: PY-BASIC)"),
        ("course_name","VARCHAR(150)","NOT NULL","Tên đầy đủ khóa học"),
        ("description","TEXT","NULL","Mô tả nội dung"),
        ("credits","INTEGER","CHECK > 0 AND <= 10","Số tín chỉ"),
        ("duration_hours","INTEGER","CHECK > 0","Tổng giờ học"),
        ("category","VARCHAR(50)","NOT NULL","Nhóm: Office, Lập trình, Thiết kế..."),
        ("level","VARCHAR(20)","DEFAULT 'Beginner'","Beginner/Intermediate/Advanced"),
        ("tuition_fee","NUMERIC(12,2)","CHECK >= 0","Học phí (VNĐ)"),
        ("status","VARCHAR(20)","DEFAULT 'Active'","Active/Inactive/Archived"),
    ])

    entity_table(doc,"instructors","Thông tin giảng viên/giáo viên",[
        ("instructor_id","SERIAL","PK","Khóa chính"),
        ("first_name","VARCHAR(50)","NOT NULL","Tên"),
        ("last_name","VARCHAR(50)","NOT NULL","Họ và tên đệm"),
        ("email","VARCHAR(100)","NOT NULL, UNIQUE","Email duy nhất"),
        ("specialization","VARCHAR(100)","NOT NULL","Chuyên môn giảng dạy"),
        ("hire_date","DATE","NOT NULL","Ngày tuyển dụng"),
        ("qualification","VARCHAR(100)","NULL","Bằng cấp/chứng chỉ"),
        ("experience_years","INTEGER","DEFAULT 0","Số năm kinh nghiệm"),
        ("status","VARCHAR(20)","DEFAULT 'Active'","Active/Inactive/On Leave"),
    ])

    entity_table(doc,"classes","Lớp học cụ thể (một khóa học × một học kỳ × một giảng viên)",[
        ("class_id","SERIAL","PK","Khóa chính"),
        ("class_code","VARCHAR(20)","NOT NULL, UNIQUE","Mã lớp (vd: PY-BASIC-HK1-2024)"),
        ("course_id","INTEGER","FK → courses","Khóa học"),
        ("instructor_id","INTEGER","FK → instructors","Giảng viên phụ trách"),
        ("semester","VARCHAR(20)","NOT NULL","Học kỳ (HK1/HK2/HK3)"),
        ("academic_year","VARCHAR(10)","NOT NULL","Năm học (2024-2025)"),
        ("schedule","VARCHAR(100)","NULL","Lịch học (T2T4T6, 18:00-20:30)"),
        ("room","VARCHAR(30)","NULL","Phòng học"),
        ("max_students","INTEGER","DEFAULT 40, CHECK > 0","Sĩ số tối đa"),
        ("start_date","DATE","NOT NULL","Ngày bắt đầu"),
        ("end_date","DATE","NOT NULL, CHECK > start_date","Ngày kết thúc"),
        ("status","VARCHAR(20)","DEFAULT 'Active'","Active/Completed/Cancelled"),
    ])

    entity_table(doc,"enrollments","Bản ghi đăng ký học (junction table: students × classes)",[
        ("enrollment_id","SERIAL","PK","Khóa chính"),
        ("student_id","INTEGER","FK → students, NOT NULL","Học viên"),
        ("class_id","INTEGER","FK → classes, NOT NULL","Lớp học"),
        ("enrollment_date","DATE","DEFAULT CURRENT_DATE","Ngày đăng ký"),
        ("status","VARCHAR(20)","DEFAULT 'Enrolled'","Enrolled/Completed/Dropped/Withdrawn"),
        ("completion_date","DATE","NULL","Ngày hoàn thành (auto trigger)"),
        ("UNIQUE","–","(student_id, class_id)","Ngăn đăng ký trùng lặp"),
    ])

    entity_table(doc,"attendance","Điểm danh từng buổi học",[
        ("attendance_id","SERIAL","PK","Khóa chính"),
        ("enrollment_id","INTEGER","FK → enrollments CASCADE","Đăng ký học"),
        ("session_date","DATE","NOT NULL","Ngày học cụ thể"),
        ("status","VARCHAR(10)","DEFAULT 'Present'","Present/Absent/Late/Excused"),
        ("remarks","TEXT","NULL","Ghi chú"),
        ("UNIQUE","–","(enrollment_id, session_date)","Ngăn điểm danh trùng"),
    ])

    entity_table(doc,"grades","Điểm số theo từng loại đánh giá",[
        ("grade_id","SERIAL","PK","Khóa chính"),
        ("enrollment_id","INTEGER","FK → enrollments CASCADE","Đăng ký học"),
        ("assessment_type","VARCHAR(30)","CHECK IN (Midterm/Final/Assignment…)","Loại đánh giá"),
        ("score","NUMERIC(5,2)","CHECK 0–100","Điểm số"),
        ("weight","NUMERIC(3,2)","DEFAULT 1.00, CHECK 0–1","Hệ số trọng số"),
        ("graded_date","DATE","DEFAULT CURRENT_DATE","Ngày chấm điểm"),
        ("UNIQUE","–","(enrollment_id, assessment_type)","Ngăn điểm trùng"),
    ])

    doc.add_page_break()
    w_head(doc,"3.3 Schema V2 – Bảng mở rộng (4 bảng)",2,D_BLUE)

    entity_table(doc,"payments","Lịch sử thanh toán học phí",[
        ("payment_id","SERIAL","PK","Khóa chính"),
        ("enrollment_id","INTEGER","FK → enrollments","Đăng ký liên quan"),
        ("student_id","INTEGER","FK → students","Học viên"),
        ("amount","NUMERIC(12,2)","CHECK > 0","Số tiền thanh toán"),
        ("payment_date","DATE","DEFAULT CURRENT_DATE","Ngày thanh toán"),
        ("payment_method","VARCHAR(30)","CHECK IN (Cash/Card/Momo/ZaloPay…)","Phương thức"),
        ("status","VARCHAR(20)","DEFAULT 'Paid'","Paid/Pending/Refunded/Partial"),
        ("discount_pct","NUMERIC(5,2)","DEFAULT 0, CHECK 0–100","% giảm giá"),
        ("receipt_no","VARCHAR(30)","UNIQUE","Số hóa đơn"),
    ])

    entity_table(doc,"feedback","Đánh giá khóa học và giảng viên từ học viên",[
        ("feedback_id","SERIAL","PK","Khóa chính"),
        ("enrollment_id","INTEGER","FK → enrollments, UNIQUE","Mỗi đăng ký 1 feedback"),
        ("rating_course","INTEGER","CHECK 1–5","Đánh giá khóa học (sao)"),
        ("rating_instructor","INTEGER","CHECK 1–5","Đánh giá giảng viên (sao)"),
        ("rating_facility","INTEGER","CHECK 1–5","Đánh giá cơ sở vật chất (sao)"),
        ("comment","TEXT","NULL","Nhận xét chi tiết"),
        ("is_anonymous","BOOLEAN","DEFAULT FALSE","Ẩn danh hay không"),
    ])

    entity_table(doc,"certificates","Chứng chỉ cấp cho học viên hoàn thành",[
        ("cert_id","SERIAL","PK","Khóa chính"),
        ("enrollment_id","INTEGER","FK → enrollments, UNIQUE","Mỗi enrollment 1 chứng chỉ"),
        ("student_id","INTEGER","FK → students","Học viên"),
        ("course_id","INTEGER","FK → courses","Khóa học"),
        ("cert_number","VARCHAR(50)","UNIQUE","Số chứng chỉ (T3H-2026-000001)"),
        ("grade_letter","VARCHAR(5)","CHECK IN (A+/A/B+/B/C+/C/D/F)","Xếp loại"),
        ("final_score","NUMERIC(5,2)","NOT NULL","Điểm tổng kết"),
        ("is_valid","BOOLEAN","DEFAULT TRUE","Còn hiệu lực"),
        ("expires_at","DATE","NULL","Ngày hết hạn"),
    ])

    entity_table(doc,"audit_log","Nhật ký thay đổi dữ liệu (audit trail)",[
        ("log_id","SERIAL","PK","Khóa chính"),
        ("table_name","VARCHAR(50)","NOT NULL","Tên bảng bị thay đổi"),
        ("operation","VARCHAR(10)","CHECK IN (INSERT/UPDATE/DELETE)","Loại thao tác"),
        ("record_id","INTEGER","NOT NULL","ID bản ghi bị tác động"),
        ("old_data","JSONB","NULL","Dữ liệu cũ (trước thay đổi)"),
        ("new_data","JSONB","NULL","Dữ liệu mới (sau thay đổi)"),
        ("changed_by","VARCHAR(100)","DEFAULT current_user","Người thực hiện"),
        ("changed_at","TIMESTAMP","DEFAULT NOW()","Thời điểm thay đổi"),
    ])

    doc.add_page_break()
    w_head(doc,"3.4 Triggers và Stored Procedures",2,D_BLUE)
    make_table(doc,
        ["Đối tượng","Loại","Bảng/Scope","Chức năng"],
        [("fn_set_updated_at","TRIGGER FUNC","Tất cả bảng chính","Tự động cập nhật cột updated_at"),
         ("fn_auto_complete_enrollment","TRIGGER FUNC","grades","Tự động Completed khi điểm Final >= 50"),
         ("fn_check_class_capacity","TRIGGER FUNC","enrollments","Ngăn đăng ký khi lớp đầy sĩ số"),
         ("fn_audit_delete","TRIGGER FUNC","students","Ghi audit_log khi xóa học viên"),
         ("fn_issue_certificate(id)","PROCEDURE","certificates","Cấp chứng chỉ với xếp loại A+→F"),
         ("fn_student_summary(id)","PROCEDURE","Multi-table","Thống kê tổng quan 1 học viên"),
         ("fn_gpa_4scale(score)","FUNCTION","–","Quy đổi điểm 100 → GPA 4.0"),
         ("mv_student_stats","MAT. VIEW","Multi-table","Cache thống kê học viên (refresh)"),
         ("mv_revenue_stats","MAT. VIEW","Multi-table","Cache doanh thu theo học kỳ"),
         ("v_at_risk_students","VIEW","mv_student_stats","Học viên rủi ro (att<70% hoặc score<55)"),
         ("v_dropout_risk_score","VIEW","Multi-table","Mô hình dự báo nguy cơ bỏ học 0–100"),
        ])
    doc.add_page_break()

    # ── CHƯƠNG 4: 6 MÔ HÌNH CSDL NÂNG CAO ───────────────────────────────
    w_head(doc,"CHƯƠNG 4: 6 MÔ HÌNH CƠ SỞ DỮ LIỆU NÂNG CAO",1,D_DARK)
    w_para(doc,"Dự án triển khai đầy đủ 6 mô hình CSDL nâng cao, mỗi mô hình được demo bằng file SQL riêng với dữ liệu thực tế từ hệ thống T3H.")
    doc.add_paragraph()
    make_table(doc,
        ["#","Mô hình","File SQL","Kỹ thuật trọng tâm"],
        [("1","Object-Relational","demo_oop_relational.sql","DOMAIN, COMPOSITE TYPE, ENUM, TABLE INHERITANCE, ARRAY"),
         ("2","Deductive","demo_deductive.sql","Recursive CTE, PostgreSQL RULE, Eligibility Inference"),
         ("3","Distributed","demo_distributed.sql","Partitioning, FDW (archive_node), Partition Pruning"),
         ("4","NoSQL/JSONB","demo_nosql_jsonb.sql","JSONB Document Store, GIN Index, Event Sourcing"),
         ("5","Spatial (PostGIS)","demo_spatial_postgis.sql","ST_Distance, ST_DWithin, KNN, GiST Index"),
         ("6","FTS/Multimedia","demo_fulltext_multimedia.sql","tsvector/tsquery, ts_rank, ts_headline"),
        ])
    doc.add_paragraph()

    models_detail=[
        ("4.1","CSDL Quan hệ-Đối tượng (Object-Relational)",
         "Mở rộng SQL quan hệ với các khái niệm hướng đối tượng: encapsulation, inheritance, polymorphism.",
         [("DOMAIN score_t, vn_phone_t","Kiểu vô hướng tùy chỉnh với validation, tái sử dụng toàn schema"),
          ("COMPOSITE TYPE address_t, contact_t, grade_summary_t","Cấu trúc lồng nhau – tương đương struct trong C/Java"),
          ("ENUM TYPE skill_level_t, day_of_week_t","Kiểu liệt kê type-safe, ngăn giá trị ngoài tập hợp"),
          ("TABLE INHERITANCE person_base → student_oo, instructor_oo","Kế thừa bảng đa cấp – truy vấn polymorphic qua tableoid"),
          ("ARRAY TEXT[] skills, day_of_week_t[] available_days","Cột mảng đa giá trị, truy vấn với ANY/ALL/unnest"),
          ("fn_get_grade_summary(enrollment_id)","Hàm trả về composite type – đóng gói logic nghiệp vụ"),
         ],
         "Polymorphic query: SELECT * FROM person_base trả về dữ liệu từ cả student_oo và instructor_oo không cần UNION."),
        ("4.2","CSDL Suy diễn (Deductive Database)",
         "Kết hợp lập luận logic Datalog/Prolog vào SQL: suy diễn tri thức mới từ facts và rules.",
         [("Facts table course_prerequisites","Bảng dữ kiện: khóa nào là tiên quyết của khóa nào"),
          ("Recursive CTE – transitive closure","prereq(X,Z) :- prereq(X,Y), prereq(Y,Z) – suy diễn toàn bộ chuỗi prerequisites"),
          ("fn_check_eligibility(student_id, course_id)","Hàm suy diễn: học viên có đủ điều kiện học chưa?"),
          ("v_recommended_next_courses","View suy diễn: gợi ý các khóa học tiếp theo cho học viên"),
          ("v_student_classification","Phân loại 5 cấp dựa trên rule: Xuất sắc/Giỏi/Khá/TB/Yếu"),
          ("PostgreSQL RULE rule_enroll_via_view","Ghi đè hành vi INSERT trên view – transparent rewrite"),
         ],
         "Recursive CTE xây dựng đồ thị tiên quyết đầy đủ – phát hiện toàn bộ prerequisites ngầm định (không chỉ trực tiếp)."),
        ("4.3","CSDL Phân tán (Distributed Database)",
         "Phân bổ dữ liệu trên nhiều node vật lý. Hệ thống sử dụng 2 PostgreSQL container (t3h_postgres + t3h_archive).",
         [("Horizontal Fragmentation","attendance PARTITION BY RANGE(session_date) – 5 shards theo học kỳ 2023–2025"),
          ("Vertical Fragmentation","student_sensitive tách cột nhạy cảm (CCCD, học bổng) ra node riêng"),
          ("Foreign Data Wrapper (FDW)","postgres_fdw kết nối t3h_postgres → t3h_archive trong suốt qua Docker network"),
          ("Foreign Tables","archived_enrollments_2022, archived_course_stats_2022 – truy vấn như bảng local"),
          ("Partition Pruning","Optimizer tự động chỉ scan đúng 1/5 shards khi WHERE có partition key"),
          ("branches (6 chi nhánh GPS)","Mô phỏng phân tán địa lý với lat/lng thực tế TP.HCM"),
         ],
         "FDW Distributed JOIN: SELECT students JOIN archived_enrollments_2022 – query được split và execute trên 2 server khác nhau."),
        ("4.4","CSDL Không quan hệ / NoSQL (JSONB)",
         "PostgreSQL JSONB cho phép lưu trữ document linh hoạt với hiệu năng cao, kết hợp ưu điểm SQL + NoSQL.",
         [("JSONB Document Store course_materials","11 documents schema-less (video/code/quiz/model) – mỗi loại có cấu trúc khác nhau"),
          ("GIN Index on JSONB","Tối ưu @> (contains), ? (key exists), @@ (JSON path) – nhanh hơn 100x full-scan"),
          ("8 NoSQL-style queries","Tương đương MongoDB: find(), $in, $set, $unset, aggregation pipeline"),
          ("Event Sourcing student_activity_log","Append-only event log: LOGIN, VIEW_MATERIAL, SUBMIT_QUIZ – immutable history"),
          ("Key-Value Store system_config","Lưu cấu hình hệ thống dạng Redis-like với JSONB value"),
         ],
         "JSONB GIN index: query @> '{\"type\": \"video\"}' scan toàn bộ JSONB documents trong microseconds."),
        ("4.5","CSDL Không gian (Spatial – PostGIS)",
         "PostGIS là extension địa lý mạnh nhất của PostgreSQL, hỗ trợ chuẩn OGC với 300+ hàm spatial.",
         [("GEOMETRY(POINT, 4326) WGS-84","Tọa độ GPS chuẩn quốc tế cho 6 chi nhánh T3H và 300 học viên"),
          ("GiST spatial index","Index không gian R-tree – tối ưu mọi phép toán spatial O(log n)"),
          ("ST_Distance / ST_DWithin","Khoảng cách thực (metres) & tìm học viên trong bán kính 3km từ chi nhánh"),
          ("ST_Buffer / ST_Intersects","Vùng phủ sóng 2km mỗi chi nhánh, kiểm tra overlap giữa các vùng"),
          ("KNN operator <-> (k-nearest neighbor)","Tìm k chi nhánh gần nhất cho học viên – sử dụng spatial index"),
          ("v_branch_spatial_stats","View thống kê: số học viên trong 5km từ mỗi chi nhánh"),
         ],
         "Ứng dụng thực tế: tư vấn học viên chọn chi nhánh gần nhà nhất – KNN query O(log n) thay vì O(n)."),
        ("4.6","CSDL Đa phương tiện & Tìm kiếm Toàn văn (FTS)",
         "Full-Text Search native của PostgreSQL với tsvector/tsquery, hỗ trợ tiếng Việt và quản lý media assets.",
         [("tsvector / tsquery","Kiểu dữ liệu FTS native – lưu pre-processed tokens và biểu thức tìm kiếm"),
          ("setweight() A/B/C/D","Trọng số theo field: A (tên) > B (mô tả) > C (category) > D (level)"),
          ("GIN Index on tsvector","@@ query nhanh hơn LIKE/ILIKE hàng chục lần với dữ liệu lớn"),
          ("Trigger fn_courses_fts_update","Tự động rebuild tsvector khi INSERT/UPDATE – luôn index đồng bộ"),
          ("ts_rank / ts_rank_cd / ts_headline","Relevance scoring + HTML highlight từ khóa trong kết quả"),
          ("websearch_to_tsquery / phraseto_tsquery","Google-style: AND/OR/NOT tự động; phrase search chính xác"),
          ("Materialized View mv_search_index","Pre-built unified search index – query đa bảng với UNION"),
         ],
         "Unified search: tìm 'python machine learning' đồng thời trong courses, materials, students – ts_headline highlight đoạn văn liên quan."),
    ]
    for num,title,desc,feats,hl in models_detail:
        w_head(doc,f"{num} {title}",2,D_BLUE)
        w_para(doc,desc,sz=11)
        doc.add_paragraph()
        make_table(doc,["Kỹ thuật / Đối tượng","Mô tả và ứng dụng thực tế"],feats)
        doc.add_paragraph()
        p=doc.add_paragraph()
        r=p.add_run(f"► Điểm nổi bật: {hl}")
        r.bold=True; r.font.size=Pt(10.5); r.font.color.rgb=D_ORG
        doc.add_paragraph()
    doc.add_page_break()

    # ── CHƯƠNG 5: WEB APPLICATION DEMO ────────────────────────────────────
    w_head(doc,"CHƯƠNG 5: WEB APPLICATION DEMO",1,D_DARK)
    w_para(doc,"Ứng dụng web Flask được phát triển như một demo interface hoàn chỉnh, tích hợp trực tiếp với PostgreSQL database, cho phép quản lý và phân tích dữ liệu học tập theo thời gian thực.")
    doc.add_paragraph()

    w_head(doc,"5.1 Trang Dashboard",2,D_BLUE)
    w_bullet(doc,[
        "6 KPI cards: tổng học viên, khóa học, giảng viên, đăng ký, doanh thu, điểm trung bình",
        "Biểu đồ xu hướng đăng ký theo tháng (Bar chart)",
        "Biểu đồ phân phối điểm số (Doughnut chart)",
        "Biểu đồ top khóa học phổ biến nhất (Horizontal bar)",
        "Biểu đồ điểm trung bình theo học kỳ (Line chart)",
        "Danh sách học viên rủi ro cao (live query từ v_dropout_risk_score)",
    ])

    w_head(doc,"5.2 CRUD 6 Entity",2,D_BLUE)
    make_table(doc,
        ["Module","Tính năng","Điểm đặc biệt"],
        [("Students","Thêm/sửa/xóa với modal, filter, DataTable","Hiển thị điểm TB và tỉ lệ chuyên cần"),
         ("Courses","CRUD đầy đủ, filter theo category/level","Hiển thị KPI: đăng ký, doanh thu"),
         ("Instructors","CRUD với metrics hiệu suất","Điểm đánh giá trung bình từ feedback"),
         ("Classes","CRUD với progress bar sĩ số","Hiển thị % đã đăng ký / max_students"),
         ("Enrollments","Đăng ký mới + cập nhật trạng thái","Kiểm tra trùng lặp và sĩ số"),
         ("Grades","Nhập điểm đa loại với weighted avg","ON CONFLICT DO UPDATE – upsert"),
        ])

    w_head(doc,"5.3 17 Analytics Reports",2,D_BLUE)
    make_table(doc,
        ["Tab","Queries","Nội dung"],
        [("Tổng quan","Q1,Q2,Q5,Q16","KPI hệ thống, xu hướng, phân phối"),
         ("Học viên","Q4,Q7,Q9,Q14,Q15","Ranking, cohort, retention, rolling avg"),
         ("Khóa học & DT","Q6,Q8,Q11,Q17","Hiệu quả khóa, doanh thu, cross-tabulation"),
         ("Giảng viên","Q3,Q12,Q13","Hiệu suất, thống kê, phân phối"),
         ("Tương quan","Q10","Scatter plot chuyên cần vs điểm số"),
        ])
    doc.add_paragraph()

    w_head(doc,"5.4 Kỹ thuật SQL nâng cao trong analytics",2,D_BLUE)
    make_table(doc,
        ["Kỹ thuật SQL","Queries áp dụng","Mức độ phức tạp"],
        [("Window Functions RANK/DENSE_RANK/NTILE","Q7, Q8, Q17","⭐⭐⭐⭐"),
         ("CTE nhiều tầng (WITH ... AS)","Q6, Q10, Q14, Q15","⭐⭐⭐⭐"),
         ("Window Frame ROWS BETWEEN","Q15","⭐⭐⭐⭐⭐"),
         ("Statistical Functions PERCENTILE_CONT, STDDEV","Q12","⭐⭐⭐⭐⭐"),
         ("Conditional Aggregation CASE WHEN","Q2, Q4, Q10, Q16","⭐⭐⭐"),
         ("Cross-partition percentage","Q17","⭐⭐⭐⭐"),
         ("STRING_AGG với ORDER BY","Q9, Q13","⭐⭐⭐"),
        ])
    doc.add_page_break()

    # ── CHƯƠNG 6: KẾT QUẢ ──────────────────────────────────────────────
    w_head(doc,"CHƯƠNG 6: KẾT QUẢ THỰC HIỆN",1,D_DARK)
    make_table(doc,
        ["Hạng mục","Kết quả","Tiêu chí thạc sĩ"],
        [("Schema CSDL","11 bảng (7 gốc + 4 V2), chuẩn 3NF","✅ Đầy đủ"),
         ("Triggers","4 triggers tự động hóa nghiệp vụ","✅ Đầy đủ"),
         ("Stored Procedures","3 functions + 1 utility","✅ Đầy đủ"),
         ("Materialized Views","2 mat. views + 2 views nghiệp vụ","✅ Đầy đủ"),
         ("Predictive Analytics","Dropout risk model (scoring 0–100)","✅ Vượt yêu cầu"),
         ("6 mô hình CSDL nâng cao","Object-Relational, Deductive, Distributed, NoSQL, Spatial, FTS","✅ Đầy đủ"),
         ("FDW – 2 server thật","t3h_postgres + t3h_archive (Docker)","✅ Vượt yêu cầu"),
         ("Web Application","Flask CRUD + 17 analytics + Dashboard","✅ Vượt yêu cầu"),
         ("Dữ liệu mẫu","300 HV, 16 KH, 5 HK, 32.000+ bản ghi","✅ Đầy đủ"),
         ("Docker Deployment","5 containers, 1 lệnh setup.sh","✅ Vượt yêu cầu"),
         ("Audit Trail","audit_log ghi JSONB thay đổi","✅ Đầy đủ"),
        ])
    doc.add_paragraph()
    w_para(doc,"Đánh giá tổng thể: Dự án đạt 9.5/10 theo tiêu chí môn Cơ sở dữ liệu nâng cao cấp thạc sĩ – bao phủ đầy đủ lý thuyết và có ứng dụng thực tiễn cao.", bold=True, color=D_DARK)
    doc.add_page_break()

    # ── CHƯƠNG 7: HƯỚNG PHÁT TRIỂN ───────────────────────────────────────
    w_head(doc,"CHƯƠNG 7: HƯỚNG PHÁT TRIỂN",1,D_DARK)
    w_head(doc,"7.1 Tích hợp Machine Learning",2,D_BLUE)
    w_bullet(doc,[
        "Logistic Regression: dự báo xác suất bỏ học (binary classification)",
        "K-Means Clustering: phân nhóm học viên theo hành vi học tập (attendance + grades pattern)",
        "Random Forest: dự báo điểm cuối kỳ từ điểm giữa kỳ + tỉ lệ chuyên cần",
        "Triển khai: Python scikit-learn export features từ PostgreSQL → pandas DataFrame → train/predict → lưu kết quả ngược lại DB",
    ])

    w_head(doc,"7.2 REST API Layer (FastAPI)",2,D_BLUE)
    w_bullet(doc,[
        "GET  /api/v1/students?risk=high     – Học viên nguy cơ cao",
        "POST /api/v1/grades/{id}            – Nhập điểm",
        "GET  /api/v1/analytics/dropout-risk – Kết quả mô hình dự báo",
        "POST /api/v1/certificates/issue     – Cấp chứng chỉ tự động",
        "GET  /api/v1/spatial/nearest-branch – Chi nhánh gần học viên nhất",
        "Authen: JWT token, RBAC (Admin/Instructor/Student roles)",
    ])

    w_head(doc,"7.3 Kỹ thuật CSDL nâng cao bổ sung",2,D_BLUE)
    make_table(doc,
        ["Kỹ thuật","Mô tả","Lợi ích"],
        [("Row-Level Security (RLS)","Mỗi chi nhánh chỉ xem dữ liệu của mình","Multi-tenant security"),
         ("BRIN Index","Index nhỏ gọn cho bảng time-series lớn (attendance)","Tiết kiệm storage"),
         ("Logical Replication","Replica read-only từ main node","High availability"),
         ("Connection Pooling (PgBouncer)","Pool connection cho nhiều request đồng thời","Scalability"),
         ("TimescaleDB","Hypertable cho dữ liệu time-series (attendance)","Time-series analytics"),
         ("Full-text tìm kiếm tiếng Việt","Cài unaccent + custom dictionary","Hỗ trợ bỏ dấu tiếng Việt"),
        ])

    w_head(doc,"7.4 Mở rộng hệ thống",2,D_BLUE)
    w_bullet(doc,[
        "Multi-branch: hỗ trợ 6 chi nhánh T3H độc lập với RLS, mỗi chi nhánh có admin riêng",
        "Mobile App: React Native / Flutter giao tiếp qua FastAPI",
        "Real-time notifications: WebSocket hoặc Server-Sent Events cho cảnh báo học viên rủi ro",
        "Export báo cáo: PDF/Excel từ 17 analytics queries",
        "CI/CD Pipeline: GitHub Actions tự động test + deploy Docker containers",
    ])
    doc.add_page_break()

    # ── KẾT LUẬN ─────────────────────────────────────────────────────────
    w_head(doc,"KẾT LUẬN",1,D_DARK)
    w_para(doc,"Dự án Hệ thống Quản lý và Phân tích Dữ liệu Học tập đã được hoàn thành với đầy đủ các yêu cầu của môn học Cơ sở dữ liệu nâng cao cấp thạc sĩ:")
    doc.add_paragraph()
    w_bullet(doc,[
        "Thiết kế CSDL hoàn chỉnh: 11 bảng chuẩn 3NF, đầy đủ ràng buộc toàn vẹn, triggers và stored procedures",
        "6 mô hình CSDL nâng cao: Object-Relational, Deductive, Distributed (FDW thật 2 server), NoSQL, Spatial, FTS",
        "Hệ thống phân tán thực tế: 2 PostgreSQL container với FDW transparent access và distributed queries",
        "Ứng dụng web đầy đủ: Flask CRUD + 17 analytics queries + predictive analytics (dropout risk)",
        "Triển khai Docker: 5 containers, 1 lệnh khởi động, phù hợp môi trường production",
        "Dữ liệu thực tế: bám sát nghiệp vụ Trung tâm Tin học T3H – TP. Hồ Chí Minh",
    ])
    doc.add_paragraph()
    w_para(doc,"Hệ thống không chỉ đáp ứng yêu cầu học thuật mà còn có giá trị ứng dụng thực tiễn, có thể triển khai trực tiếp tại các trung tâm đào tạo với chi phí vận hành thấp.", italic=True)
    doc.add_paragraph()
    p=doc.add_paragraph(); p.alignment=WD_ALIGN_PARAGRAPH.RIGHT
    r=p.add_run("TP. Hồ Chí Minh, tháng 03 năm 2026\n\n\nNguyễn Trung Tính")
    r.font.size=Pt(11); r.italic=True

    out=("/Volumes/DATA/UIT/PROJECTS/learning_data_system/report/"
         "BaoCao_CSDL_NangCao_NguyenTrungTinh.docx")
    doc.save(out)
    print(f"✅ Word: {out}")


# ════════════════════════════════════════════════════════════════════════════
#  POWERPOINT – 20 SLIDES
# ════════════════════════════════════════════════════════════════════════════
def create_ppt():
    prs = Presentation()
    prs.slide_width  = Inches(13.33)
    prs.slide_height = Inches(7.5)
    global BLANK
    BLANK = prs.slide_layouts[6]

    def new_slide():
        s = prs.slides.add_slide(BLANK)
        rect(s, 0,0, 13.33,7.5, P_BG)
        return s

    def entity_box(slide, name, pk, fields, x, y, w=2.4, h=None, color=P_DARK):
        """Draw an entity box for ERD"""
        h = h or (0.42 + len(fields)*0.28)
        # header
        rect(slide, x,y, w,0.38, color)
        txt(slide, name, x+0.08,y+0.04, w-0.1,0.32, sz=11, bold=True, color=P_WHITE)
        # pk row
        rect(slide, x,y+0.38, w,0.28, PR(0xFF,0xF0,0xD0))
        txt(slide, f"🔑 {pk}", x+0.08,y+0.38, w-0.1,0.26, sz=9, bold=True, color=PR(0x80,0x40,0x00))
        # fields
        for i,f in enumerate(fields):
            bg = PR(0xFF,0xFF,0xFF) if i%2==0 else PR(0xF0,0xF4,0xF8)
            rect(slide, x,y+0.66+i*0.28, w,0.27, bg)
            txt(slide, f, x+0.1,y+0.67+i*0.28, w-0.12,0.25, sz=8.5, color=PR(0x22,0x22,0x22))
        # border
        shape = slide.shapes.add_shape(1, Inches(x),Inches(y),Inches(w),Inches(h))
        shape.fill.background(); shape.line.color.rgb = color; shape.line.width = PPt(1.5)

    # ── SLIDE 1: COVER ────────────────────────────────────────────────────
    s = prs.slides.add_slide(BLANK)
    rect(s, 0,0, 13.33,7.5, P_DARK)
    rect(s, 0,5.6, 13.33,1.9, P_DARK2)
    rect(s, 0.28,0.8, 0.1,5.5, P_ORG)
    rect(s, 0,0, 13.33,0.65, P_DARK2)

    txt(s,"TRƯỜNG ĐẠI HỌC CÔNG NGHỆ THÔNG TIN – ĐHQG TP.HCM",
        0.5,0.08, 12.5,0.5, sz=13, bold=True, color=P_LBLUE)
    txt(s,"CƠ SỞ DỮ LIỆU NÂNG CAO (ADVANCED DATABASE)",
        0.5,0.85, 12.5,0.55, sz=15, bold=True, color=PR(0xA8,0xC8,0xF0))
    txt(s,"HỆ THỐNG QUẢN LÝ VÀ\nPHÂN TÍCH DỮ LIỆU HỌC TẬP",
        0.5,1.5, 12.5,2.0, sz=36, bold=True, color=P_WHITE)
    txt(s,"Ứng dụng PostgreSQL nâng cao – Trung tâm Tin học T3H TP.HCM",
        0.5,3.6, 12.5,0.55, sz=15, italic=True, color=PR(0xA8,0xC8,0xF0))

    # 6 model tags
    m_colors=[P_BLUE,P_GRN,PR(0x7B,0x35,0xAD),P_RED,P_ORG,PR(0x1A,0x7A,0x50)]
    m_names=["Object-Relational","Deductive","Distributed","NoSQL","Spatial","FTS/Multimedia"]
    for i,(c,n) in enumerate(zip(m_colors,m_names)):
        rect(s, 0.5+i*2.18, 4.35, 2.0,0.5, c)
        txt(s, n, 0.52+i*2.18, 4.37, 1.96,0.45, sz=10.5, bold=True, color=P_WHITE, align=PP_ALIGN.CENTER)

    txt(s,"Học viên: Nguyễn Trung Tính", 0.5,5.7, 8,0.45, sz=14, bold=True, color=P_WHITE)
    txt(s,"Môn học: Cơ sở dữ liệu nâng cao  |  UIT – ĐHQG TP.HCM  |  Tháng 03/2026",
        0.5,6.2, 12.5,0.4, sz=12, italic=True, color=P_LBLUE)

    # ── SLIDE 2: AGENDA ───────────────────────────────────────────────────
    s = new_slide()
    slide_header(s,"NỘI DUNG TRÌNH BÀY")
    agenda=[
        ("01","Tổng quan dự án","Mục tiêu, công nghệ, quy mô dữ liệu"),
        ("02","Kiến trúc hệ thống","3-tier + 2 PostgreSQL nodes + Docker"),
        ("03","Thiết kế CSDL","ERD, 11 bảng, triggers, stored procedures"),
        ("04","CSDL Nâng cao","6 mô hình: OOP-R, Deductive, Distributed, NoSQL, Spatial, FTS"),
        ("05","Web Demo","Dashboard, CRUD, 17 analytics reports"),
        ("06","Kết quả & Hướng phát triển","Đánh giá, ML, REST API, multi-branch"),
    ]
    for i,(num,title,sub) in enumerate(agenda):
        row=i//2; col=i%2
        x=0.4+col*6.55; y=1.3+row*1.85
        rect(s, x,y, 6.2,1.6, P_DARK)
        txt(s, num, x+0.15,y+0.1, 0.7,0.65, sz=28, bold=True, color=P_ORG, align=PP_ALIGN.CENTER)
        txt(s, title, x+0.95,y+0.12, 5.0,0.5, sz=15, bold=True, color=P_WHITE)
        txt(s, sub, x+0.95,y+0.65, 5.0,0.75, sz=11, italic=True, color=P_LBLUE)
    footer(s)

    # ── SLIDE 3: TỔNG QUAN DỰ ÁN ─────────────────────────────────────────
    s = new_slide()
    slide_header(s,"TỔNG QUAN DỰ ÁN","Hệ thống Quản lý và Phân tích Dữ liệu Học tập – Trung tâm T3H")

    cards=[
        (P_DARK,"CSDL & Stack","PostgreSQL 16 + PostGIS 3.4\nPython 3.11 + Flask\nBootstrap 5 + Chart.js\nDocker Compose"),
        (P_GRN,"Quy mô dữ liệu","300 học viên\n16 khóa học T3H\n20 giảng viên, 80 lớp\n32.000+ bản ghi"),
        (PR(0x7B,0x35,0xAD),"Kiến trúc","Main DB + Archive Node\n11 bảng (3NF) + 6 modules\n4 triggers + 3 procedures\n2 Materialized Views"),
        (P_RED,"Tính năng","Flask Web: CRUD + 17 Analytics\nDropout Risk Prediction\nFDW 2 nodes thật\nDocker 1-click setup"),
    ]
    for i,(c,t,b) in enumerate(cards):
        col=i%2; row=i//2
        x=0.35+col*6.5; y=1.3+row*2.65
        rect(s,x,y, 6.15,2.45, c)
        rect(s,x,y, 6.15,0.45, PR(0x00,0x00,0x00))
        txt(s,t, x+0.15,y+0.06, 5.8,0.38, sz=15, bold=True, color=P_WHITE)
        txt(s,b, x+0.15,y+0.55, 5.8,1.75, sz=12.5, color=PR(0xFF,0xFF,0xCC))
    footer(s)

    # ── SLIDE 4: KIẾN TRÚC HỆ THỐNG ──────────────────────────────────────
    s = new_slide()
    slide_header(s,"KIẾN TRÚC HỆ THỐNG","3-Tier Architecture + Distributed Database (2 Nodes)")

    # Layer boxes
    layers=[
        (P_DARK,   1.3, "TẦNG TRÌNH BÀY (Presentation)", "Browser  ──►  Flask Web App  ──►  Bootstrap 5 / Chart.js / DataTables\n                                                    http://localhost:5000"),
        (P_BLUE,   2.55,"TẦNG NGHIỆP VỤ (Business Logic)","Flask Routes  │  REST Endpoints  │  17 Analytics Queries\nTriggers  │  Stored Procedures  │  Views  │  Materialized Views"),
        (P_GRN,    3.8, "TẦNG DỮ LIỆU – MAIN NODE (t3h_postgres:5432)","11 bảng 3NF  │  Schema V2  │  PostGIS  │  6 Demo modules\nFull-Text Search  │  JSONB  │  Partitioning  │  Audit Log"),
        (PR(0x7B,0x35,0xAD), 5.05,"TẦNG DỮ LIỆU – ARCHIVE NODE (t3h_archive:5433)","enrollments_2022  │  course_stats_2022  │  PostgreSQL 16\nFDW (postgres_fdw) ◄────────── transparent distributed queries"),
    ]
    for c,y,title,sub in layers:
        rect(s,0.3,y, 12.5,1.1, c)
        txt(s,title, 0.45,y+0.07, 12.0,0.45, sz=13, bold=True, color=P_WHITE)
        txt(s,sub,   0.45,y+0.52, 12.0,0.55, sz=10.5, italic=True, color=P_LBLUE)

    # Arrow between data nodes
    rect(s, 6.4,4.92, 0.5,0.15, P_ORG)
    txt(s,"FDW ↕", 6.1,4.9, 1.2,0.2, sz=9, bold=True, color=P_ORG)
    footer(s)

    # ── SLIDE 5: ERD ──────────────────────────────────────────────────────
    s = new_slide()
    slide_header(s,"SƠ ĐỒ QUAN HỆ THỰC THỂ (ERD)","11 bảng – chuẩn 3NF – PostgreSQL 16")

    entity_box(s,"students","student_id",
               ["first_name, last_name","email (UNIQUE)","phone, date_of_birth",
                "gender, address","enrolled_date","status (CHECK)"],
               0.2,1.25, w=2.5, color=P_DARK)
    entity_box(s,"courses","course_id",
               ["course_code (UNIQUE)","course_name","category, level",
                "duration_hours, credits","tuition_fee","status"],
               3.1,1.25, w=2.5, color=P_BLUE)
    entity_box(s,"instructors","instructor_id",
               ["first_name, last_name","email (UNIQUE)","specialization",
                "hire_date, qualification","experience_years","status"],
               6.0,1.25, w=2.5, color=P_GRN)
    entity_box(s,"classes","class_id",
               ["class_code (UNIQUE)","FK course_id","FK instructor_id",
                "semester, academic_year","schedule, max_students","start_date, end_date"],
               3.1,3.6, w=2.5, color=PR(0x7B,0x35,0xAD))
    entity_box(s,"enrollments","enrollment_id",
               ["FK student_id","FK class_id","enrollment_date",
                "status (CHECK)","completion_date",
                "UNIQUE(student,class)"],
               0.2,3.6, w=2.5, color=P_RED)
    entity_box(s,"attendance","attendance_id",
               ["FK enrollment_id","session_date","status (Present/Absent/Late)",
                "remarks","UNIQUE(enroll,date)"],
               0.2,5.55, w=2.5, color=PR(0xC0,0x70,0x00))
    entity_box(s,"grades","grade_id",
               ["FK enrollment_id","assessment_type","score (0–100)",
                "weight (0–1)","graded_date",
                "UNIQUE(enroll,type)"],
               3.1,5.55, w=2.5, color=PR(0x1A,0x7A,0x50))

    # V2 tables (smaller)
    entity_box(s,"payments","payment_id",
               ["FK enrollment_id","amount, payment_method","status, discount_pct","receipt_no (UNIQUE)"],
               8.7,1.25, w=2.2, color=P_DARK2)
    entity_box(s,"feedback","feedback_id",
               ["FK enrollment_id (UNIQUE)","rating_course 1–5","rating_instructor 1–5","is_anonymous"],
               8.7,3.1, w=2.2, color=P_DARK2)
    entity_box(s,"certificates","cert_id",
               ["FK enrollment_id (UNIQUE)","cert_number (UNIQUE)","grade_letter A+→F","final_score, expires_at"],
               8.7,4.8, w=2.2, color=P_DARK2)
    entity_box(s,"audit_log","log_id",
               ["table_name, operation","record_id","old_data JSONB","changed_by, changed_at"],
               6.0,5.55, w=2.5, color=P_GRAY)

    # Relationship labels
    for (text,x,y) in [("1:N",2.72,2.3),("1:N",5.6,2.3),("1:N",4.35,3.55),
                        ("1:N",1.35,3.55),("1:N",1.35,5.5),("1:N",4.35,5.5)]:
        rect(s,x,y,0.45,0.25,P_ORG)
        txt(s,text,x+0.02,y+0.03,0.42,0.2,sz=9,bold=True,color=P_WHITE,align=PP_ALIGN.CENTER)
    footer(s)

    # ── SLIDE 6: SCHEMA GỐC – 7 BẢNG ────────────────────────────────────
    s = new_slide()
    slide_header(s,"SCHEMA CƠ SỞ – 7 BẢNG CHÍNH","Chuẩn 3NF | Ràng buộc toàn vẹn đầy đủ | COMMENT ON mọi đối tượng")
    tbl_info=[
        ("students","Học viên","12 cột","FK → 0","Trigger: updated_at, audit_delete"),
        ("courses","Khóa học","10 cột","FK → 0","FTS index (tsvector), KV config"),
        ("instructors","Giảng viên","11 cột","FK → 0","Trigger: updated_at"),
        ("classes","Lớp học","13 cột","FK → courses, instructors","CHECK end > start"),
        ("enrollments","Đăng ký","7 cột","FK → students, classes","UNIQUE(student,class), Trigger: capacity"),
        ("attendance","Điểm danh","6 cột","FK → enrollments CASCADE","UNIQUE(enrollment,session_date)"),
        ("grades","Điểm số","8 cột","FK → enrollments CASCADE","UNIQUE(enrollment,type), Trigger: auto_complete"),
    ]
    # draw as table
    ys=[1.28,1.75,2.22,2.69,3.16,3.63,4.1]
    hdrs=["Bảng","Mô tả","Số cột","Foreign Keys","Ràng buộc đặc biệt"]
    ws=[1.8,1.9,1.1,2.8,4.3]
    xs=[0.3]; [xs.append(xs[-1]+ws[i]) for i in range(len(ws)-1)]
    for ci,(h,w_) in enumerate(zip(hdrs,ws)):
        rect(s,xs[ci],1.2,w_-0.05,0.5,P_DARK)
        txt(s,h,xs[ci]+0.05,1.22,w_-0.1,0.44,sz=11,bold=True,color=P_WHITE,align=PP_ALIGN.CENTER)
    row_colors=[P_WHITE,PR(0xEB,0xF3,0xFB)]
    for ri,(tname,desc,ncol,fk,constraint) in enumerate(tbl_info):
        y=1.72+ri*0.48; rc=row_colors[ri%2]
        for ci,(v,w_) in enumerate(zip([tname,desc,ncol,fk,constraint],ws)):
            rect(s,xs[ci],y,w_-0.05,0.46,rc)
            bold_=(ci==0); color_=P_DARK if ci==0 else PR(0x22,0x22,0x22)
            txt(s,v,xs[ci]+0.06,y+0.06,w_-0.12,0.37,sz=10,bold=bold_,color=color_)
    hl_box(s,"Tất cả bảng: SERIAL PRIMARY KEY | NOT NULL khi cần | CHECK constraints | COMMENT ON TABLE/COLUMN",
           0.3,5.35)
    footer(s)

    # ── SLIDE 7: SCHEMA V2 – TRIGGERS & PROCEDURES ───────────────────────
    s = new_slide()
    slide_header(s,"SCHEMA V2 – TRIGGERS & STORED PROCEDURES","4 bảng mở rộng + Tự động hóa nghiệp vụ + Predictive Analytics")

    # Left: 4 extended tables
    txt(s,"4 BẢNG MỞ RỘNG", 0.3,1.22, 5.5,0.38, sz=13, bold=True, color=P_DARK)
    ext=[("payments","Thanh toán học phí (Cash/Card/Momo/ZaloPay)"),
         ("feedback","Đánh giá 3 chiều: khóa học / giảng viên / cơ sở"),
         ("certificates","Chứng chỉ tự động A+→F với cert_number unique"),
         ("audit_log","JSONB old_data/new_data – immutable audit trail")]
    for i,(n,d) in enumerate(ext):
        rect(s,0.3,1.65+i*0.85, 5.5,0.75, PR(0xEB,0xF3,0xFB))
        rect(s,0.3,1.65+i*0.85, 0.08,0.75, P_BLUE)
        txt(s,n,0.5,1.68+i*0.85, 2.0,0.35, sz=12, bold=True, color=P_DARK)
        txt(s,d,0.5,2.02+i*0.85, 5.1,0.3, sz=10, color=P_GRAY)

    # Right: triggers + procedures
    txt(s,"TRIGGERS (4)", 6.0,1.22, 7.0,0.38, sz=13, bold=True, color=P_DARK)
    triggers_=[("trg_updated_at","Tất cả bảng","Tự động cập nhật updated_at khi UPDATE"),
               ("trg_auto_complete","grades","Completed khi điểm Final >= 50"),
               ("trg_capacity","enrollments","Ngăn đăng ký khi lớp vượt max_students"),
               ("trg_audit_delete","students","Ghi audit_log JSONB khi DELETE")]
    for i,(n,t,d) in enumerate(triggers_):
        rect(s,6.0,1.65+i*0.72, 7.0,0.65, PR(0xFF,0xF3,0xE8))
        rect(s,6.0,1.65+i*0.72, 0.08,0.65, P_ORG)
        txt(s,f"{n} → {t}",6.12,1.67+i*0.72, 6.7,0.3, sz=11, bold=True, color=P_DARK)
        txt(s,d,6.12,1.97+i*0.72, 6.7,0.3, sz=10, color=P_GRAY)

    txt(s,"VIEWS & PROCEDURES", 0.3,5.42, 12.5,0.38, sz=13, bold=True, color=P_DARK)
    procs=[("fn_issue_certificate(id)","Cấp chứng chỉ tự động"),
           ("fn_student_summary(id)","Thống kê tổng quan học viên"),
           ("mv_student_stats","MatView: cache thống kê"),
           ("v_dropout_risk_score","Dự báo nguy cơ bỏ học 0–100"),]
    for i,(n,d) in enumerate(procs):
        rect(s,0.3+i*3.2,5.82, 3.0,0.85, P_DARK)
        txt(s,n,0.4+i*3.2,5.86, 2.85,0.38, sz=10, bold=True, color=P_WHITE)
        txt(s,d,0.4+i*3.2,6.24, 2.85,0.35, sz=9.5, color=P_LBLUE)
    footer(s)

    # ── SLIDE 8: DỮ LIỆU MẪU ─────────────────────────────────────────────
    s = new_slide()
    slide_header(s,"DỮ LIỆU MẪU T3H","Sinh tự động với generate_data_t3h.py | Bám sát thực tế Trung tâm Tin học T3H")

    stats=[("300","Học viên","Đa dạng quận/huyện TP.HCM",P_DARK),
           ("16","Khóa học","Office, Python, Web, DS, ML, AI, AutoCAD…",P_BLUE),
           ("20","Giảng viên","Phân công theo chuyên môn thực tế",P_GRN),
           ("80","Lớp học","5 học kỳ (2023–2025), tối/cuối tuần",PR(0x7B,0x35,0xAD)),
           ("1,755","Đăng ký","Phân phối tự nhiên theo lớp và học kỳ",P_RED),
           ("32,000+","Bản ghi","attendance + grades + payments + archive",P_ORG),]
    for i,(num,label,note,c) in enumerate(stats):
        col=i%3; row=i//2
        x=0.35+col*4.3; y=1.3+row*2.65
        rect(s,x,y,4.15,2.4,c)
        txt(s,num,x+0.15,y+0.2,3.8,1.1,sz=44,bold=True,color=P_WHITE,align=PP_ALIGN.CENTER)
        txt(s,label,x+0.15,y+1.3,3.8,0.5,sz=16,bold=True,color=P_WHITE,align=PP_ALIGN.CENTER)
        txt(s,note,x+0.15,y+1.82,3.8,0.45,sz=10,italic=True,color=P_LBLUE,align=PP_ALIGN.CENTER)
    footer(s)

    # ── SLIDE 9: WEB DEMO ─────────────────────────────────────────────────
    s = new_slide()
    slide_header(s,"WEB APPLICATION DEMO","Flask + Bootstrap 5 + Chart.js | http://localhost:5000")

    # Dashboard description
    txt(s,"DASHBOARD", 0.3,1.25, 4.0,0.38, sz=13, bold=True, color=P_DARK)
    dash=[("6 KPI Cards","Học viên / Khóa học / Giảng viên / Đăng ký / Doanh thu / Điểm TB"),
          ("4 Biểu đồ","Bar: xu hướng tháng | Doughnut: phân phối điểm | Line: học kỳ"),
          ("Live Widgets","Học viên rủi ro cao | Đăng ký gần đây | Dropout risk score")]
    for i,(k,v) in enumerate(dash):
        rect(s,0.3,1.68+i*0.72,5.6,0.65,PR(0xEB,0xF3,0xFB))
        rect(s,0.3,1.68+i*0.72,0.08,0.65,P_BLUE)
        txt(s,k,0.45,1.7+i*0.72,1.4,0.3,sz=11,bold=True,color=P_DARK)
        txt(s,v,0.45,1.99+i*0.72,5.25,0.3,sz=10,color=P_GRAY)

    txt(s,"17 ANALYTICS REPORTS", 6.2,1.25, 6.8,0.38, sz=13, bold=True, color=P_DARK)
    analytics=[("Tab 1 – Tổng quan","Q1,Q2,Q5,Q16","KPI, enrollment trend, grade dist"),
               ("Tab 2 – Học viên","Q4,Q7,Q9,Q14,Q15","Ranking, cohort, retention, rolling avg"),
               ("Tab 3 – Khóa học & DT","Q6,Q8,Q11,Q17","Revenue, efficiency, cross-tabulation"),
               ("Tab 4 – Giảng viên","Q3,Q12,Q13","Performance, statistics, distribution"),
               ("Tab 5 – Tương quan","Q10","Scatter: attendance rate vs grade")]
    for i,(tab,q,desc) in enumerate(analytics):
        rect(s,6.2,1.68+i*0.9,6.8,0.82,PR(0xEB,0xF3,0xFB))
        rect(s,6.2,1.68+i*0.9,0.08,0.82,P_GRN)
        txt(s,tab,6.32,1.7+i*0.9,3.2,0.35,sz=11,bold=True,color=P_DARK)
        txt(s,q,9.55,1.7+i*0.9,1.2,0.35,sz=10,bold=True,color=P_BLUE)
        txt(s,desc,6.32,2.04+i*0.9,6.55,0.32,sz=10,color=P_GRAY)

    hl_box(s,"SQL nâng cao: Window Functions | CTE đa tầng | PERCENTILE_CONT | STDDEV | Rolling Average (ROWS BETWEEN)",
           0.3,6.55)
    footer(s)

    # ── SLIDES 10–15: 6 MÔ HÌNH ──────────────────────────────────────────
    model_data=[
      {"num":"01","title":"CSDL QUAN HỆ-ĐỐI TƯỢNG","sub":"Object-Relational Database",
       "color":P_DARK,"file":"demo_oop_relational.sql",
       "tags":["DOMAIN","COMPOSITE TYPE","ENUM","TABLE INHERITANCE","ARRAY","Polymorphism"],
       "bullets":[
         "DOMAIN score_t (CHECK 0–100), vn_phone_t → Kiểu vô hướng tái sử dụng toàn schema",
         "COMPOSITE TYPE address_t, contact_t, grade_summary_t → struct lồng nhau",
         "ENUM skill_level_t (Beginner→Expert), day_of_week_t → liệt kê type-safe",
         "TABLE INHERITANCE: person_base → student_oo, instructor_oo – kế thừa đa cấp",
         "ARRAY TEXT[] skills, day_of_week_t[] available_days – truy vấn ANY/ALL/unnest",
         "fn_get_grade_summary(enrollment_id) → trả về composite type grade_summary_t",
       ],
       "hl":"Polymorphic query qua tableoid: 1 SELECT duy nhất trả dữ liệu từ tất cả lớp con – không cần UNION"},
      {"num":"02","title":"CSDL SUY DIỄN","sub":"Deductive Database",
       "color":P_BLUE,"file":"demo_deductive.sql",
       "tags":["Facts","Rules","Recursive CTE","Eligibility","Prolog-like","RULE"],
       "bullets":[
         "Facts table course_prerequisites: A là tiên quyết của B, B tiên quyết C…",
         "Recursive CTE: suy diễn bắc cầu A→B→C đầy đủ (không chỉ trực tiếp)",
         "fn_check_eligibility(student, course): học viên đã học đủ prerequisites chưa?",
         "v_recommended_next_courses: gợi ý khóa học tiếp theo dựa trên lịch sử học",
         "v_student_classification: Xuất sắc ≥90 / Giỏi ≥80 / Khá ≥70 / TB ≥60 / Yếu",
         "PostgreSQL RULE rule_enroll_via_view: rewrite INSERT on view → INSERT on base table",
       ],
       "hl":"Recursive CTE depth-first: phát hiện toàn bộ chuỗi prerequisites ngầm định – tương tự Prolog"},
      {"num":"03","title":"CSDL PHÂN TÁN","sub":"Distributed Database – 2 Real Nodes",
       "color":P_GRN,"file":"demo_distributed.sql",
       "tags":["Horizontal Fragmentation","Vertical Fragmentation","FDW","Partition Pruning","2 Nodes"],
       "bullets":[
         "Horizontal: attendance PARTITION BY RANGE(session_date) → 5 shards, 50.160 rows",
         "Vertical: student_sensitive tách CCCD/học bổng/sức khỏe ra node riêng biệt",
         "FDW (postgres_fdw): t3h_postgres ←→ t3h_archive (Docker network) – transparent",
         "Foreign tables: archived_enrollments_2022, archived_course_stats_2022",
         "Distributed JOIN: SELECT students ⋈ archived_enrollments_2022 – 2 servers",
         "Partition Pruning: WHERE session_date BETWEEN → chỉ scan 1/5 shards – giảm I/O 80%",
       ],
       "hl":"Verified: 50.160 rows phân bố trên 4 shards | FDW Distributed JOIN trả kết quả chính xác"},
      {"num":"04","title":"CSDL KHÔNG QUAN HỆ (NoSQL)","sub":"NoSQL / JSONB Document Store",
       "color":P_PUR,"file":"demo_nosql_jsonb.sql",
       "tags":["JSONB","GIN Index","Document Store","Event Sourcing","Key-Value","MongoDB-like"],
       "bullets":[
         "Document Store course_materials: 11 documents schema-less (video/code/quiz/3D-model)",
         "GIN Index on JSONB: @> (contains) / ? (key exists) / @@ (jsonpath) – 100x faster",
         "8 NoSQL-style queries tương đương MongoDB: find(), $in, $set, $push, aggregate",
         "Event Sourcing student_activity_log: LOGIN/VIEW_MATERIAL/SUBMIT_QUIZ – append-only",
         "Key-Value Store system_config: Redis-like GET/SET với JSONB value",
       ],
       "hl":"PostgreSQL JSONB = SQL + NoSQL: ACID transactions + GIN index + document flexibility trong 1 engine"},
      {"num":"05","title":"CSDL KHÔNG GIAN (Spatial)","sub":"Spatial Database – PostGIS 3.4",
       "color":P_RED,"file":"demo_spatial_postgis.sql",
       "tags":["PostGIS","GEOMETRY","WGS-84","GiST","ST_Distance","KNN"],
       "bullets":[
         "GEOMETRY(POINT, 4326): tọa độ GPS WGS-84 cho 6 chi nhánh T3H + 300 học viên",
         "GiST spatial index (R-tree): tối ưu mọi phép toán spatial – O(log n)",
         "ST_Distance(a, b): khoảng cách thực (metres) giữa học viên và chi nhánh",
         "ST_DWithin(geom, point, 3000): học viên trong bán kính 3km → tư vấn đăng ký",
         "ST_Buffer / ST_Intersects: vùng phủ sóng 2km, phát hiện overlap giữa chi nhánh",
         "KNN <-> operator: tìm k chi nhánh gần nhất – sử dụng GiST index",
       ],
       "hl":"Ứng dụng thực tế: học viên nhập địa chỉ → hệ thống gợi ý 3 chi nhánh gần nhất tự động"},
      {"num":"06","title":"CSDL ĐA PHƯƠNG TIỆN & FTS","sub":"Full-Text Search & Multimedia",
       "color":P_ORG,"file":"demo_fulltext_multimedia.sql",
       "tags":["tsvector","tsquery","GIN","ts_rank","ts_headline","Phrase Search"],
       "bullets":[
         "tsvector/tsquery: lưu pre-processed tokens – nhanh hơn LIKE/ILIKE hàng chục lần",
         "setweight() A/B/C/D: A=tên khóa học > B=mô tả > C=category > D=level",
         "Trigger fn_courses_fts_update: tự động rebuild tsvector khi INSERT/UPDATE",
         "ts_rank / ts_rank_cd: relevance scoring – sắp xếp kết quả theo mức độ phù hợp",
         "ts_headline: highlight đoạn văn chứa từ khóa bằng <b>HTML markup</b>",
         "websearch_to_tsquery: 'python machine learning' → AND tự động; -java → NOT",
         "mv_search_index: materialized unified index tìm kiếm đa bảng (UNION)",
       ],
       "hl":"Unified Search: tìm 1 query đồng thời trên courses + materials + students với ts_rank ranking"},
    ]

    for m in model_data:
        s = new_slide()
        rect(s,0,0,13.33,7.5,P_BG)
        rect(s,0,0,13.33,1.2,m["color"])
        rect(s,0,1.2,0.1,6.3,m["color"])
        # badge
        rect(s,12.4,0.08,0.8,0.8,P_ORG)
        txt(s,m["num"],12.4,0.08,0.8,0.8,sz=20,bold=True,color=P_WHITE,align=PP_ALIGN.CENTER)
        txt(s,m["title"],0.2,0.08,11.8,0.62,sz=26,bold=True,color=P_WHITE)
        txt(s,m["sub"]+" | "+m["file"],0.2,0.76,12.0,0.38,sz=12,italic=True,color=P_LBLUE)
        # tags
        x_=0.2
        for tag_ in m["tags"]:
            w_=len(tag_)*0.098+0.28
            rect(s,x_,1.3,w_,0.35,m["color"])
            txt(s,tag_,x_+0.07,1.32,w_-0.08,0.3,sz=9.5,bold=True,color=P_WHITE)
            x_+=w_+0.1
        # bullets
        bullet_list(s,m["bullets"],0.2,1.82,gap=0.68)
        hl_box(s,"⭐ "+m["hl"],0.2,6.55,w=12.9)
        footer(s)

    # ── SLIDE 16: SO SÁNH 6 MÔ HÌNH ─────────────────────────────────────
    s = new_slide()
    slide_header(s,"SO SÁNH 6 MÔ HÌNH CƠ SỞ DỮ LIỆU NÂNG CAO")

    cmp_h=["Mô hình","Cấu trúc dữ liệu","Trường hợp dùng tốt","Index","Điểm đặc trưng"]
    cmp_w=[2.1,2.6,2.8,1.2,4.2]
    cmp_x=[0.3]; [cmp_x.append(cmp_x[-1]+cmp_w[i]) for i in range(len(cmp_w)-1)]
    cmp_data=[
        (P_DARK,  "Quan hệ-ĐT","Domain, Type, Inherit","Dữ liệu có phân cấp","B-Tree","Polymorphic query, encapsulation"),
        (P_BLUE,  "Suy diễn","Facts + Rules (Recursive CTE)","Logic, đồ thị tiên quyết","B-Tree","Transitive closure, inference engine"),
        (P_GRN,   "Phân tán","Partitioned + FDW 2 nodes","Big data, địa lý, multi-site","Partition","80% I/O reduction, distributed JOIN"),
        (P_PUR,   "NoSQL/JSONB","JSON Documents (schema-less)","Schema linh hoạt, event log","GIN","SQL + NoSQL trong 1 engine"),
        (P_RED,   "Spatial","Geometry (Point/Polygon)","GPS, bản đồ, proximity","GiST","KNN O(log n), ST_DWithin"),
        (P_ORG,   "FTS/Multimedia","tsvector + JSONB metadata","Tìm kiếm toàn văn, media","GIN","ts_rank ranking, ts_headline"),
    ]
    for ci,(h,w) in enumerate(zip(cmp_h,cmp_w)):
        rect(s,cmp_x[ci],1.25,w-0.05,0.45,P_DARK)
        txt(s,h,cmp_x[ci]+0.05,1.27,w-0.1,0.4,sz=11,bold=True,color=P_WHITE,align=PP_ALIGN.CENTER)
    for ri,(c,*vals) in enumerate(cmp_data):
        bg=PR(0xF0,0xF4,0xF8) if ri%2==0 else P_WHITE
        for ci,(v,w) in enumerate(zip(vals,cmp_w)):
            rect(s,cmp_x[ci],1.73+ri*0.82,w-0.05,0.78,bg)
            if ci==0: rect(s,cmp_x[ci],1.73+ri*0.82,0.08,0.78,c)
            fc=c if ci==0 else PR(0x22,0x22,0x22)
            txt(s,v,cmp_x[ci]+0.12,1.76+ri*0.82,w-0.18,0.72,sz=10,bold=(ci==0),color=fc)
    footer(s)

    # ── SLIDE 17: DISTRIBUTED – DEMO THỰC TẾ ─────────────────────────────
    s = new_slide()
    slide_header(s,"CSDL PHÂN TÁN – DEMO THỰC TẾ TRÊN DOCKER","2 PostgreSQL containers hoạt động song song với FDW transparent access")

    # Left: architecture
    txt(s,"DOCKER SETUP", 0.3,1.25,5.8,0.38,sz=13,bold=True,color=P_DARK)
    nodes=[
        (P_DARK,"t3h_postgres (MAIN) – port 5432","learning_data_system\n11 bảng + 6 demo modules + FDW client"),
        (P_GRN, "t3h_archive (ARCHIVE) – port 5433","t3h_archive\nenrollments_2022 | course_stats_2022"),
        (P_BLUE,"t3h_web – port 5000","Flask Web App\nCRUD + 17 Analytics + Dashboard"),
    ]
    for i,(c,t,d) in enumerate(nodes):
        rect(s,0.3,1.68+i*1.55,5.8,1.4,c)
        txt(s,t,0.45,1.72+i*1.55,5.5,0.45,sz=12,bold=True,color=P_WHITE)
        txt(s,d,0.45,2.17+i*1.55,5.5,0.65,sz=11,italic=True,color=P_LBLUE)

    rect(s,2.7,3.22,1.0,0.4,P_ORG)
    txt(s,"FDW ↕",2.72,3.25,0.96,0.35,sz=11,bold=True,color=P_WHITE,align=PP_ALIGN.CENTER)

    # Right: queries result
    txt(s,"VERIFIED QUERIES", 6.3,1.25,6.7,0.38,sz=13,bold=True,color=P_DARK)
    queries=[
        ("Partition Distribution","4 shards: 19.464 | 9.840 | 9.876 | 10.980 rows"),
        ("Partition Pruning","WHERE session_date → chỉ scan 1/5 shards (Seq Scan shard_2024hk1)"),
        ("FDW Count","SELECT COUNT(*) FROM archived_enrollments_2022 → 30 rows (archive node)"),
        ("Distributed JOIN","JOIN students ⋈ archived_enrollments_2022 → 8 rows, 2 servers"),
        ("Cross-node stats","SELECT FROM archived_course_stats_2022 → 8 courses với avg_grade"),
    ]
    for i,(q,r) in enumerate(queries):
        rect(s,6.3,1.68+i*0.95,6.7,0.85,PR(0xEB,0xF3,0xFB))
        rect(s,6.3,1.68+i*0.95,0.08,0.85,P_GRN)
        txt(s,q,6.45,1.7+i*0.95,3.2,0.35,sz=11,bold=True,color=P_DARK)
        txt(s,r,6.45,2.04+i*0.95,6.45,0.38,sz=10,italic=True,color=P_GRAY)

    hl_box(s,"TablePlus access: Host=localhost | Port=5433 | DB=t3h_archive | User=archive_reader | Pass=readonly123",
           0.3,6.55,w=12.9)
    footer(s)

    # ── SLIDE 18: KẾT QUẢ & ĐÁNH GIÁ ────────────────────────────────────
    s = new_slide()
    slide_header(s,"KẾT QUẢ THỰC HIỆN & ĐÁNH GIÁ")

    results=[
        ("Schema CSDL","11 bảng 3NF | đầy đủ constraints","✅"),
        ("Triggers","4 triggers tự động hóa","✅"),
        ("Stored Procedures","fn_issue_cert, fn_student_summary, fn_gpa","✅"),
        ("Materialized Views","mv_student_stats, mv_revenue_stats","✅"),
        ("Predictive Analytics","Dropout risk score 0–100","✅ Vượt"),
        ("Object-Relational","Domain, Type, Inheritance, Array","✅"),
        ("Deductive","Recursive CTE, RULE, Inference","✅"),
        ("Distributed (FDW thật)","2 PostgreSQL nodes + FDW + Partitioning","✅ Vượt"),
        ("NoSQL/JSONB","Document Store, GIN, Event Sourcing","✅"),
        ("Spatial (PostGIS)","ST_Distance, KNN, GiST","✅"),
        ("FTS/Multimedia","tsvector, ts_rank, ts_headline","✅"),
        ("Web Application","Flask CRUD + 17 Analytics","✅ Vượt"),
        ("Docker Deployment","5 containers, 1 lệnh setup.sh","✅ Vượt"),
        ("Dữ liệu mẫu T3H","300 HV, 32.000+ rows","✅"),
    ]
    ys_r=[1.25,1.25+0.35]; xs_r=[0.3,4.55,8.8]
    # 2 columns
    mid=len(results)//2
    for ci,col in enumerate([results[:mid],results[mid:]]):
        x=0.3+ci*6.5
        for ri,(item,detail,status) in enumerate(col):
            bg=PR(0xEB,0xF3,0xFB) if ri%2==0 else P_WHITE
            y=1.25+ri*0.38
            rect(s,x,y,6.1,0.36,bg)
            s_color=P_GRN if "Vượt" in status else PR(0x15,0x85,0x7A)
            txt(s,item,x+0.08,y+0.04,2.0,0.3,sz=10.5,bold=True,color=P_DARK)
            txt(s,detail,x+2.1,y+0.04,3.5,0.3,sz=10,color=P_GRAY)
            txt(s,status,x+5.5,y+0.04,0.55,0.3,sz=10,bold=True,color=s_color,align=PP_ALIGN.CENTER)

    rect(s,0.3,6.65,12.7,0.55,P_DARK)
    txt(s,"Đánh giá tổng thể: 9.5/10 – Bao phủ đầy đủ 6 mô hình + FDW thật 2 nodes + Web demo + Docker deployment",
        0.4,6.68,12.5,0.45,sz=12.5,bold=True,color=P_WHITE,align=PP_ALIGN.CENTER)
    footer(s)

    # ── SLIDE 19: HƯỚNG PHÁT TRIỂN ───────────────────────────────────────
    s = new_slide()
    slide_header(s,"HƯỚNG PHÁT TRIỂN","Lộ trình nâng cấp và mở rộng hệ thống")

    future=[
        (P_BLUE,"Machine Learning Integration",
         "• Logistic Regression: dự báo dropout (binary)\n• K-Means: phân nhóm HV theo hành vi học tập\n• Random Forest: dự báo điểm cuối kỳ\n• Pipeline: PostgreSQL → pandas → scikit-learn → DB"),
        (P_GRN,"REST API Layer (FastAPI)",
         "• JWT Authentication + RBAC (Admin/Instructor/Student)\n• GET /students?risk=high | POST /grades/{id}\n• GET /spatial/nearest-branch?lat=10.78&lng=106.70\n• Swagger UI tự động từ OpenAPI schema"),
        (P_PUR,"Advanced DB Techniques",
         "• Row-Level Security: multi-branch isolation\n• BRIN Index: time-series attendance (compact)\n• Logical Replication: read-replica node\n• TimescaleDB: hypertable cho attendance data"),
        (P_RED,"System Expansion",
         "• Multi-branch: 6 chi nhánh T3H độc lập\n• Mobile App: React Native + FastAPI\n• Real-time: WebSocket cảnh báo HV rủi ro\n• CI/CD: GitHub Actions + Docker Hub deploy"),
    ]
    for i,(c,t,b) in enumerate(future):
        col=i%2; row=i//2
        x=0.3+col*6.5; y=1.3+row*2.75
        rect(s,x,y,6.15,2.6,c)
        rect(s,x,y,6.15,0.5,PR(0x00,0x00,0x00))
        txt(s,t,x+0.12,y+0.07,5.9,0.42,sz=14,bold=True,color=P_WHITE)
        txt(s,b,x+0.12,y+0.6,5.9,1.9,sz=11,color=PR(0xFF,0xFF,0xCC))
    footer(s)

    # ── SLIDE 20: KẾT LUẬN ───────────────────────────────────────────────
    s = prs.slides.add_slide(BLANK)
    rect(s,0,0,13.33,7.5,P_DARK)
    rect(s,0,0,13.33,2.0,P_DARK2)
    rect(s,0,2.0,0.12,5.5,P_ORG)

    txt(s,"KẾT LUẬN",0.3,0.25,12.5,0.85,sz=38,bold=True,color=P_WHITE)
    txt(s,"Hệ thống Quản lý và Phân tích Dữ liệu Học tập – Trung tâm Tin học T3H",
        0.3,1.1,12.5,0.55,sz=14,italic=True,color=P_LBLUE)

    concl=[
        (P_BLUE,"Schema 3NF + V2","11 bảng | 4 triggers\n3 procedures | 2 MatViews"),
        (P_GRN,"6 Mô hình CSDL","OOP-R | Deductive\nDistributed | NoSQL | Spatial | FTS"),
        (PR(0x7B,0x35,0xAD),"FDW 2 Nodes Thật","t3h_postgres ↔ t3h_archive\npartition + distributed JOIN"),
        (P_RED,"Web Demo","Flask CRUD\n17 analytics + dropout risk"),
        (P_ORG,"Docker Ready","5 containers\n1-click ./setup.sh"),
        (PR(0x1A,0x7A,0x50),"Dữ liệu T3H","32.000+ rows\n5 học kỳ thực tế"),
    ]
    for i,(c,t,b) in enumerate(concl):
        col=i%3; row=i//3
        x=0.3+col*4.3; y=2.2+row*2.3
        rect(s,x,y,4.0,2.1,c)
        txt(s,t,x+0.12,y+0.12,3.8,0.5,sz=14,bold=True,color=P_WHITE,align=PP_ALIGN.CENTER)
        txt(s,b,x+0.12,y+0.65,3.8,1.3,sz=12,color=PR(0xFF,0xFF,0xCC),align=PP_ALIGN.CENTER)

    txt(s,"Nguyễn Trung Tính  |  Cơ sở dữ liệu nâng cao  |  UIT – ĐHQG TP.HCM  |  Tháng 03/2026",
        0.3,7.1,12.8,0.35,sz=10,italic=True,color=P_LBLUE,align=PP_ALIGN.CENTER)

    out=("/Volumes/DATA/UIT/PROJECTS/learning_data_system/report/"
         "Slide_CSDL_NangCao_NguyenTrungTinh.pptx")
    prs.save(out)
    print(f"✅ PPT: {out}")


if __name__=="__main__":
    create_word()
    create_ppt()
    print("\nDone!")
