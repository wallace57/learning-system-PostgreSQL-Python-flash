# Hệ Thống Quản Lý Dữ Liệu Học Tập

![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16%2B-blue.svg)
![Python](https://img.shields.io/badge/Python-3.8%2B-green.svg)
![Flask](https://img.shields.io/badge/Flask-2.x-lightgrey.svg)
![Docker](https://img.shields.io/badge/Docker-Compose-2496ED.svg)
![Status](https://img.shields.io/badge/Trạng_thái-Hoàn_thành-success.svg)

Dự án cơ sở dữ liệu PostgreSQL hoàn chỉnh dành cho **Trung tâm Đào tạo Kỹ năng CNTT T3H – TP.HCM**. Bao gồm thiết kế CSDL chuẩn hóa 3NF, dữ liệu mẫu thực tế (~15.000 dòng), 17 truy vấn phân tích nâng cao, giao diện web Flask, và 6 module minh họa các mô hình CSDL nâng cao (môn Thạc sĩ).

---

## Mục Lục

- [Cấu trúc dự án](#cấu-trúc-dự-án)
- [Mô hình cơ sở dữ liệu](#mô-hình-cơ-sở-dữ-liệu)
- [Khởi chạy nhanh (Docker)](#khởi-chạy-nhanh-docker)
- [Khởi chạy thủ công](#khởi-chạy-thủ-công)
- [Giao diện Web](#giao-diện-web)
- [CSDL Nâng cao – 6 Module Demo](#csdl-nâng-cao--6-module-demo)
- [17 Truy Vấn Phân Tích](#17-truy-vấn-phân-tích)

---

## Cấu Trúc Dự Án

```text
learning_data_system/
├── database/
│   ├── schema.sql                  # Schema gốc: 7 bảng (3NF)
│   ├── schema_v2.sql               # Schema nâng cấp: triggers, procedures, materialized views, audit log
│   ├── insert_data.sql             # Dữ liệu mẫu SQL tĩnh (generic)
│   ├── index.sql                   # Indexes tăng hiệu năng truy vấn
│   ├── queries.sql                 # 17 câu truy vấn phân tích nâng cao
│   ├── archive_init.sql            # Khởi tạo bảng lưu trữ lịch sử
│   ├── demo_oop_relational.sql     # Demo: Object-Relational (Domain, Composite, Enum, Array, Inheritance)
│   ├── demo_deductive.sql          # Demo: Deductive DB (Recursive CTE, RULE, Eligibility inference)
│   ├── demo_distributed.sql        # Demo: Distributed DB (Fragmentation, Partitioning, FDW)
│   ├── demo_nosql_jsonb.sql        # Demo: NoSQL/JSONB (Document Store, GIN, Event Sourcing)
│   ├── demo_spatial_postgis.sql    # Demo: Spatial DB (PostGIS, ST_Distance, KNN, GiST)
│   └── demo_fulltext_multimedia.sql# Demo: Full-Text Search & Multimedia (tsvector, ts_rank)
├── web/
│   ├── app.py                      # Flask app: CRUD + 17 API endpoints
│   ├── requirements.txt
│   ├── static/
│   └── templates/                  # 9 templates (dashboard, students, courses, analytics...)
├── report/
│   ├── PHAN_TICH.md                # Báo cáo phân tích đầy đủ
│   ├── BaoCao_CSDL_NangCao_*.docx
│   └── Slide_CSDL_NangCao_*.pptx
├── generate_data.py                # Script tạo dữ liệu generic (200 học viên)
├── generate_data_t3h.py            # Script T3H: 300 học viên, 16 khóa học, 5 học kỳ
├── generate_data_docker.py         # Script dùng trong Docker (đọc env vars)
├── docker-compose.yml              # PostGIS + data-generator + web + pgAdmin
├── Dockerfile.generator
├── Dockerfile.web
├── setup.sh                        # Script khởi động Docker tất-cả-trong-một
├── .env.example                    # Mẫu biến môi trường
└── README.md
```

---

## Mô Hình Cơ Sở Dữ Liệu

### 7 Bảng Schema Gốc (3NF)

| Bảng | Mô tả |
|------|-------|
| `students` | Thông tin học viên (tên, SĐT, email, ngày sinh...) |
| `instructors` | Hồ sơ giảng viên (chuyên môn, bằng cấp...) |
| `courses` | Danh sách khóa học (Python, Data Science, AI...) |
| `classes` | Lớp học thực tế theo từng học kỳ |
| `enrollments` | Đăng ký học phần của học viên |
| `attendance` | Điểm danh từng buổi học |
| `grades` | Điểm số bài tập, giữa kỳ & cuối kỳ |

### 4 Bảng Bổ Sung (Schema V2)

| Bảng | Mô tả |
|------|-------|
| `payments` | Quản lý học phí và lịch sử thanh toán |
| `feedback` | Phản hồi học viên về khóa học |
| `certificates` | Chứng chỉ hoàn thành |
| `audit_log` | Nhật ký thay đổi dữ liệu (triggers tự động) |

---

## Khởi Chạy Nhanh (Docker)

> Yêu cầu: Docker Desktop đang chạy

```bash
# Khởi động đầy đủ với dữ liệu T3H (khuyên dùng)
./setup.sh

# Dùng dữ liệu generic
./setup.sh generic

# Thêm pgAdmin (port 8080)
./setup.sh tools

# Dừng dịch vụ
./setup.sh down

# Xóa toàn bộ và rebuild từ đầu
./setup.sh reset
```

Sau khi chạy xong:
- **Web App:** http://localhost:5000
- **pgAdmin:** http://localhost:8080 (chỉ khi chạy `./setup.sh tools`)

Cấu hình kết nối trong `.env` (copy từ `.env.example`):
```env
POSTGRES_DB=learning_data_system
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your_password
```

---

## Khởi Chạy Thủ Công

### 1. Tạo CSDL và nạp dữ liệu

```bash
psql -U postgres
```

```sql
CREATE DATABASE learning_data_system;
\c learning_data_system
\encoding UTF8

\i database/schema.sql
\i database/insert_data.sql
\i database/index.sql
```

Hoặc dùng Python script (kết nối trực tiếp vào PostgreSQL):

```bash
pip install psycopg2-binary
python generate_data_t3h.py    # T3H: 300 học viên, ~15K dòng
# hoặc
python generate_data.py        # Generic: 200 học viên
```

### 2. Chạy Web App

```bash
cd web
pip install -r requirements.txt
python app.py
# Truy cập: http://localhost:5000
```

---

## Giao Diện Web

Flask web app với Bootstrap 5 + Chart.js, gồm:

| Trang | Chức năng |
|-------|-----------|
| Dashboard | Thống kê tổng quan, biểu đồ Chart.js |
| Students | CRUD học viên |
| Courses | CRUD khóa học |
| Instructors | CRUD giảng viên |
| Classes | CRUD lớp học |
| Enrollments | Quản lý đăng ký học |
| Grades | Nhập và xem điểm |
| Analytics | 17 báo cáo phân tích dữ liệu |

---

## CSDL Nâng Cao – 6 Module Demo

Các file SQL minh họa các mô hình CSDL nâng cao (dành cho môn học Thạc sĩ):

| File | Chủ đề | Kỹ thuật minh họa |
|------|--------|-------------------|
| `demo_oop_relational.sql` | Object-Relational | Domain, Composite Type, Enum, Array, Table Inheritance |
| `demo_deductive.sql` | Deductive DB | Recursive CTE, PostgreSQL RULE, Eligibility inference |
| `demo_distributed.sql` | Distributed DB | Horizontal/Vertical Fragmentation, Partitioning, FDW |
| `demo_nosql_jsonb.sql` | NoSQL / JSONB | Document Store, GIN Index, Event Sourcing, KV Store |
| `demo_spatial_postgis.sql` | Spatial DB | PostGIS, ST_Distance, ST_DWithin, KNN, GiST |
| `demo_fulltext_multimedia.sql` | Full-Text & Multimedia | tsvector/tsquery, ts_rank, ts_headline, media_assets |

Chạy từng module:

```bash
psql -U postgres -d learning_data_system -f database/demo_oop_relational.sql
psql -U postgres -d learning_data_system -f database/demo_nosql_jsonb.sql
# ... tương tự cho các file còn lại
```

> **Lưu ý:** `demo_spatial_postgis.sql` yêu cầu extension PostGIS. Docker image `postgis/postgis:16-3.4` đã tích hợp sẵn.

---

## 17 Truy Vấn Phân Tích

| # | Báo cáo | Kỹ thuật SQL |
|---|---------|-------------|
| 1 | Điểm trung bình mỗi khóa học | JOIN, GROUP BY, AVG |
| 2 | Tỷ lệ hoàn thành khóa học | CASE WHEN, NULLIF |
| 3 | Top 5 giảng viên tốt nhất | Multi-JOIN, LIMIT |
| 4 | Học viên vắng mặt nhiều nhất | Conditional aggregation |
| 5 | Xu hướng đăng ký theo tháng | TO_CHAR, DATE functions |
| 6 | Tỷ lệ Đậu/Rớt | CTE, Weighted averages |
| 7 | Xếp hạng học thuật học viên | RANK, DENSE_RANK, NTILE |
| 8 | Phân tích doanh thu học phí | Window functions |
| 9 | Kết quả học viên nhiều khóa | STRING_AGG, HAVING |
| 10 | Tương quan chuyên cần & điểm | Multiple CTEs, CASE |
| 11 | Tỷ lệ lấp đầy lớp học | LEFT JOIN, toán học |
| 12 | Phân phối điểm số (thống kê) | PERCENTILE_CONT, STDDEV |
| 13 | Khối lượng công việc giảng viên | STRING_AGG, SUM |
| 14 | Cảnh báo học viên rủi ro cao | CTE có điều kiện lọc |
| 15 | GPA tích lũy theo thời gian | ROWS BETWEEN, Moving Average |
| 16 | So sánh kết quả giữa học kỳ | Cross-semester aggregation |
| 17 | Xếp hạng khóa học phổ biến | RANK với PARTITION BY |

Xem toàn bộ SQL tại [`database/queries.sql`](database/queries.sql).

---

## Thông Tin Dự Án

- **Môn học:** Cơ sở dữ liệu nâng cao (Advanced Database)
- **Đơn vị:** Trung tâm Đào tạo T3H – TP. Hồ Chí Minh
- **Stack:** PostgreSQL 16 (PostGIS), Python 3.8+, Flask, Bootstrap 5, Chart.js, Docker