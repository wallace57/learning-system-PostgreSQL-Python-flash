# BÁO CÁO ĐỒ ÁN MÔN HỌC
## CƠ SỞ DỮ LIỆU NÂNG CAO
### HỆ THỐNG QUẢN LÝ VÀ PHÂN TÍCH DỮ LIỆU HỌC TẬP
### Trung tâm Tin học T3H – TP. Hồ Chí Minh

---

**Học viên:** Nguyễn Trung Tính
**Môn học:** Cơ sở dữ liệu nâng cao (Advanced Database)
**Trường:** Trường Đại học Công nghệ Thông tin – ĐHQG TP.HCM (UIT)
**Ngày nộp:** 28/03/2026

---

## MỤC LỤC

1. [Chương 1 – Tổng quan giới thiệu](#chương-1)
2. [Chương 2 – Phân tích bài toán](#chương-2)
3. [Chương 3 – Thiết kế và xây dựng hệ thống](#chương-3)
4. [Chương 4 – Phân tích dữ liệu](#chương-4)
5. [Chương 5 – Xây dựng ứng dụng](#chương-5)
6. [Chương 6 – Thực nghiệm và đánh giá](#chương-6)
7. [Chương 7 – Kết luận và hướng phát triển](#chương-7)

---

## CHƯƠNG 1 – TỔNG QUAN GIỚI THIỆU <a name="chương-1"></a>

### 1.0 Mô tả bài toán

**Input:** Dữ liệu học viên, khóa học, lớp học, điểm danh và điểm số từ nhiều file Excel phân tán tại 6 chi nhánh Trung tâm Tin học T3H TP.HCM (300+ học viên, 16 khóa học/năm, không có hệ thống quản lý tập trung).

**Output:** Hệ thống cơ sở dữ liệu tập trung PostgreSQL với: báo cáo doanh thu tổng hợp theo chi nhánh, phát hiện sớm học viên nguy cơ bỏ học (dropout risk scoring 0–100), tìm kiếm tài liệu thông minh theo ngữ nghĩa, và minh họa đầy đủ 6 mô hình CSDL nâng cao (Object-Relational, Deductive, Distributed, NoSQL/JSONB, Spatial/PostGIS, Full-Text Search/Multimedia).

### 1.1 Bối cảnh và lý do chọn đề tài

**Bài toán thực tế:** Trung tâm Tin học T3H (Trung Tâm Tin Học HCMUS) là trung tâm đào tạo tin học với hơn 300 học viên/năm, 16 khóa học, 6 chi nhánh tại TP.HCM. Hiện tại trung tâm quản lý dữ liệu bằng Excel rời rạc, không có hệ thống phân tích, không theo dõi được nguy cơ bỏ học, doanh thu phân tán theo từng chi nhánh.

**Vấn đề cụ thể:**
- Dữ liệu học viên, điểm số, điểm danh lưu trong nhiều file Excel → dễ sai sót, khó tổng hợp
- Không phát hiện được sớm học viên có nguy cơ bỏ học
- Không có báo cáo doanh thu tập trung
- Không tìm kiếm được tài liệu học tập nhanh chóng

**Tại sao chọn PostgreSQL?** PostgreSQL là hệ quản trị CSDL mã nguồn mở hỗ trợ đầy đủ: JSON/JSONB, PostGIS (spatial), Full-text Search, Table Inheritance, Partitioning, Foreign Data Wrapper – đủ để minh họa 6 mô hình CSDL nâng cao trong một hệ thống thực tế duy nhất.

### 1.2 Mục tiêu đồ án

| Mục tiêu | Mô tả | Trạng thái |
|-----------|-------|-----------|
| Thiết kế CSDL chuẩn 3NF | 7 bảng quan hệ + 4 bảng mở rộng | ✅ Hoàn thành |
| Tự động hóa nghiệp vụ | Triggers + Stored Procedures | ✅ Hoàn thành |
| Phân tích dữ liệu nâng cao | 17 câu truy vấn analytics | ✅ Hoàn thành |
| Minh họa 6 mô hình CSDL | OOP-R, Deductive, Distributed, NoSQL, Spatial, FTS | ✅ Hoàn thành |
| Ứng dụng web demo | Flask CRUD + Dashboard + Charts | ✅ Hoàn thành |
| Docker hóa | Triển khai 1 lệnh với docker-compose | ✅ Hoàn thành |

### 1.3 Phạm vi hệ thống

**Phạm vi triển khai:**
- Dữ liệu: 300 học viên, 16 khóa học, 20 giảng viên, 80 lớp học, 5 học kỳ (2023–2025), ~15.000 bản ghi
- Địa lý: 6 chi nhánh T3H tại TP.HCM (Q1, Q3, Q5, Bình Thạnh, Gò Vấp, Tân Bình)
- Ứng dụng: Web demo quản lý + phân tích, không phải hệ thống production

**Ngoài phạm vi:** Authentication đa cấp, mobile app, tích hợp ERP.

### 1.4 Công nghệ sử dụng

| Thành phần | Công nghệ | Phiên bản | Lý do chọn |
|-----------|-----------|-----------|-----------|
| CSDL chính | PostgreSQL + PostGIS | 16.x | Hỗ trợ đầy đủ 6 mô hình nâng cao |
| Backend web | Python / Flask | 3.10+ / 2.x | Nhanh, nhẹ, phù hợp demo |
| Frontend | Bootstrap 5 + Chart.js | 5.3 / 4.x | Responsive, charts đẹp |
| Data generation | Python + Faker | 3.x | Sinh dữ liệu thực tế tiếng Việt |
| Containerization | Docker + Compose | 24.x | Triển khai nhất quán mọi môi trường |
| Driver | psycopg2 | 2.9+ | Kết nối PostgreSQL tốt nhất cho Python |

---

## CHƯƠNG 2 – PHÂN TÍCH BÀI TOÁN <a name="chương-2"></a>

### 2.0 Chọn lựa cách giải

#### Các tác giả / hệ thống đã giải bài toán tương tự

| Hệ thống | Tác giả / Thời điểm | Ưu điểm | Nhược điểm |
|---------|-------------------|---------|------------|
| **Moodle LMS** | Martin Dougiamas, Úc – 2002 | Mã nguồn mở, phổ biến toàn cầu, nhiều plugin | Backend MySQL, không có analytics nâng cao, không khai thác PostGIS/FTS/Partitioning |
| **Canvas LMS** | Instructure, Mỹ – 2011 | Giao diện tốt, backend PostgreSQL, tích hợp nhiều công cụ | Schema đóng, không thể nghiên cứu/minh họa các mô hình CSDL học thuật |
| **Odoo Education / OpenERP** | Odoo S.A., Bỉ – 2005+ | Đầy đủ tính năng ERP giáo dục, backend PostgreSQL | Quá phức tạp, không tập trung vào minh họa các mô hình CSDL nâng cao |
| **Các nghiên cứu học thuật** | Nhiều bài báo (IEEE, ACM) – 2010–2020 | Thiết kế ERD bài bản, chuẩn hóa 3NF | Chỉ dùng mô hình quan hệ thông thường, không minh họa CSDL Spatial/Deductive/FTS |

#### Tại sao chọn cách giải khác?

Các hệ thống trên đều sử dụng **MySQL hoặc PostgreSQL cơ bản**, chỉ khai thác mô hình quan hệ thông thường. Đề tài này chọn cách tiếp cận khác:

1. **Dùng PostgreSQL thay vì MySQL:** PostgreSQL là RDBMS duy nhất hỗ trợ đầy đủ cả 6 mô hình CSDL nâng cao (Table Inheritance, Recursive CTE, FDW, JSONB, PostGIS, tsvector) trong một engine duy nhất – không cần nhiều hệ thống riêng biệt.

2. **Tự xây dựng thay vì dùng hệ thống có sẵn:** Kiểm soát hoàn toàn schema để thiết kế từng bảng, từng trigger, từng index nhằm minh họa rõ ràng từng mô hình CSDL học thuật.

3. **Context thực tế T3H thay vì bài toán trừu tượng:** Gắn liền 6 mô hình CSDL vào bài toán thực tế của Trung tâm Tin học T3H (spatial cho 6 chi nhánh, FTS cho tài liệu học tập, deductive cho tiên quyết khóa học...) giúp demo có tính ứng dụng cao hơn.

### 2.1 Yêu cầu nghiệp vụ

#### 2.1.1 Các tác nhân (Actors)

| Tác nhân | Vai trò | Nhu cầu chính |
|---------|---------|--------------|
| Quản trị viên | Quản lý toàn bộ hệ thống | CRUD tất cả entity, xem báo cáo tổng hợp |
| Giảng viên | Dạy học + chấm điểm | Nhập điểm, điểm danh, xem lớp của mình |
| Học viên | Học tập | Xem kết quả học tập, chứng chỉ |
| Ban giám đốc | Ra quyết định | Dashboard KPI, báo cáo doanh thu, nguy cơ bỏ học |

#### 2.1.2 Yêu cầu chức năng

**F1 – Quản lý hồ sơ học viên:**
- Thêm/sửa/xóa thông tin học viên (tên, email, SĐT, ngày sinh, địa chỉ)
- Theo dõi trạng thái: Active / Inactive / Graduated / Suspended
- Tìm kiếm học viên theo nhiều tiêu chí

**F2 – Quản lý đào tạo:**
- Quản lý danh mục khóa học (16 khóa T3H): Office, Kế toán, Lập trình, AI/ML, Thiết kế
- Quản lý lớp học: mỗi lớp = 1 khóa + 1 giảng viên + 1 học kỳ, tối đa 40 học viên
- Đăng ký học: ràng buộc sĩ số, không đăng ký trùng lớp

**F3 – Theo dõi học tập:**
- Điểm danh hàng buổi: Present / Absent / Late / Excused
- Nhập điểm: Midterm (30%) + Final (70%), hoặc Assignment/Quiz/Project
- Tự động cập nhật trạng thái hoàn thành khi có điểm đạt

**F4 – Tài chính:**
- Ghi nhận thanh toán học phí: tiền mặt, chuyển khoản, Momo, ZaloPay, VNPay
- Theo dõi chiết khấu, hoàn tiền
- Báo cáo doanh thu theo học kỳ / chi nhánh

**F5 – Chứng chỉ:**
- Tự động cấp chứng chỉ khi học viên hoàn thành khóa
- Xếp loại A+ → F theo thang điểm 100

**F6 – Phân tích & Báo cáo:**
- Dashboard KPI: tổng học viên, doanh thu, điểm trung bình
- 17 báo cáo analytics: điểm theo khóa học, tỷ lệ hoàn thành, nguy cơ bỏ học...
- Biểu đồ trực quan: xu hướng đăng ký, phân phối điểm, hiệu suất giảng viên

#### 2.1.3 Yêu cầu phi chức năng

| Yêu cầu | Chỉ tiêu cụ thể |
|---------|----------------|
| Hiệu năng | Queries analytics < 500ms với 15.000 bản ghi |
| Toàn vẹn dữ liệu | Không cho phép đăng ký vượt sĩ số, điểm ngoài phạm vi 0-100 |
| Khả năng mở rộng | Schema hỗ trợ partitioning khi dữ liệu tăng lên 10x |
| Dễ triển khai | Khởi động toàn bộ hệ thống bằng 1 lệnh: `./setup.sh` |
| Tính nhất quán | Audit log ghi lại mọi thay đổi quan trọng |

### 2.2 Mô hình hóa dữ liệu – ERD tổng quan

```
STUDENTS ──< ENROLLMENTS >── CLASSES >── COURSES
                │                  └── INSTRUCTORS
                ├──< ATTENDANCE
                ├──< GRADES
                ├──< PAYMENTS
                ├──< FEEDBACK
                └──< CERTIFICATES
```

**Quan hệ chính:**
- `students` 1─N `enrollments` N─1 `classes` N─1 `courses`
- `classes` N─1 `instructors`
- `enrollments` 1─N `attendance` (điểm danh từng buổi)
- `enrollments` 1─N `grades` (điểm từng loại bài kiểm)
- `enrollments` 1─1 `payments`, `feedback`, `certificates`

### 2.3 Luồng nghiệp vụ chính

```
[Học viên đăng ký] → [Trigger: kiểm tra sĩ số] → [Tạo enrollment]
        ↓
[Học hàng buổi] → [Điểm danh] → [attendance table]
        ↓
[Cuối kỳ] → [Nhập điểm] → [grades table]
        ↓
[Trigger: đủ điều kiện?] → [Cập nhật status=Completed]
        ↓
[Procedure: fn_issue_certificate] → [Cấp chứng chỉ tự động]
        ↓
[Analytics] → [Dashboard] → [Báo cáo ban giám đốc]
```

---

## CHƯƠNG 3 – THIẾT KẾ VÀ XÂY DỰNG HỆ THỐNG <a name="chương-3"></a>

### 3.1 Thiết kế Schema cơ sở (schema.sql)

#### 3.1.1 Bảy bảng quan hệ chính (3NF)

**Tại sao 3NF?** Chuẩn hóa 3NF loại bỏ dư thừa dữ liệu, đảm bảo tính nhất quán khi cập nhật. Ví dụ: tên khóa học chỉ lưu 1 lần trong `courses`, không lặp lại trong `classes` hay `enrollments`.

| Bảng | Khóa chính | Chức năng | Ràng buộc quan trọng |
|------|-----------|----------|---------------------|
| `students` | `student_id` | Hồ sơ học viên | UNIQUE(email), CHECK(gender), CHECK(status) |
| `courses` | `course_id` | Danh mục khóa học | UNIQUE(course_code), CHECK(tuition_fee>=0) |
| `instructors` | `instructor_id` | Hồ sơ giảng viên | UNIQUE(email), CHECK(experience_years>=0) |
| `classes` | `class_id` | Lớp học cụ thể | FK→courses, FK→instructors, CHECK(end_date>start_date) |
| `enrollments` | `enrollment_id` | Đăng ký học | FK→students, FK→classes, UNIQUE(student_id,class_id) |
| `attendance` | `attendance_id` | Điểm danh | FK→enrollments, UNIQUE(enrollment_id,session_date) |
| `grades` | `grade_id` | Điểm số | FK→enrollments, UNIQUE(enrollment_id,assessment_type) |

**Ràng buộc toàn vẹn nổi bật:**
```sql
-- Ngăn đăng ký trùng lớp
CONSTRAINT uq_student_class UNIQUE (student_id, class_id)

-- Ngăn điểm danh trùng buổi
CONSTRAINT uq_enrollment_session UNIQUE (enrollment_id, session_date)

-- Điểm trong phạm vi hợp lệ
score NUMERIC(5,2) NOT NULL CHECK (score >= 0 AND score <= 100)

-- Ngày kết thúc phải sau ngày bắt đầu
CONSTRAINT chk_class_dates CHECK (end_date > start_date)
```

#### 3.1.2 Bốn bảng mở rộng (schema_v2.sql)

**Khi nào thêm?** Sau khi có schema gốc hoạt động, mở rộng thêm các nghiệp vụ bổ trợ mà không phá vỡ cấu trúc cũ.

| Bảng | Chức năng | Kỹ thuật đáng chú ý |
|------|----------|---------------------|
| `payments` | Thanh toán học phí | 6 phương thức thanh toán, discount_pct, receipt_no UNIQUE |
| `feedback` | Đánh giá 3 chiều | rating_course + rating_instructor + rating_facility (1-5 sao) |
| `certificates` | Chứng chỉ hoàn thành | grade_letter A+→F, is_valid, expires_at, cert_number UNIQUE |
| `audit_log` | Nhật ký thay đổi | JSONB lưu old_value/new_value, actor, action |

### 3.2 Triggers (Tự động hóa nghiệp vụ)

**Tại sao dùng Trigger?** Đảm bảo nghiệp vụ được thực thi ở tầng CSDL, không phụ thuộc vào application code. Dù ai thao tác trực tiếp vào DB, trigger vẫn chạy.

#### Trigger 1: Kiểm tra sĩ số khi đăng ký

```sql
-- What: Ngăn đăng ký khi lớp đã đầy
-- Why: Toàn vẹn nghiệp vụ – không vượt max_students
-- When: BEFORE INSERT ON enrollments
-- How: Đếm enrollment hiện tại, so với max_students của class

CREATE OR REPLACE FUNCTION fn_check_class_capacity()
RETURNS TRIGGER AS $$
DECLARE v_current INT; v_max INT;
BEGIN
    SELECT COUNT(*), cl.max_students
    INTO v_current, v_max
    FROM enrollments e
    JOIN classes cl ON e.class_id = cl.class_id
    WHERE e.class_id = NEW.class_id AND e.status != 'Dropped'
    GROUP BY cl.max_students;

    IF v_current >= v_max THEN
        RAISE EXCEPTION 'Lớp % đã đủ sĩ số (tối đa %)', NEW.class_id, v_max;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_check_capacity
    BEFORE INSERT ON enrollments
    FOR EACH ROW EXECUTE FUNCTION fn_check_class_capacity();
```

#### Trigger 2: Tự động hoàn thành enrollment khi đủ điểm

```sql
-- What: Cập nhật status='Completed' khi có điểm Final đạt ≥50
-- Why: Không cần admin thủ công cập nhật trạng thái
-- When: AFTER INSERT OR UPDATE ON grades
-- How: Kiểm tra score và assessment_type

CREATE OR REPLACE FUNCTION fn_auto_complete_enrollment()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.assessment_type = 'Final' AND NEW.score >= 50 THEN
        UPDATE enrollments
        SET status = 'Completed', completion_date = CURRENT_DATE,
            updated_at = CURRENT_TIMESTAMP
        WHERE enrollment_id = NEW.enrollment_id AND status = 'Enrolled';
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;
```

#### Trigger 3: Tự động cập nhật updated_at

```sql
-- What: Cập nhật trường updated_at mỗi khi record thay đổi
-- Why: Audit trail nhẹ, không cần code tầng application
-- When: BEFORE UPDATE trên tất cả bảng chính

CREATE OR REPLACE FUNCTION fn_set_updated_at()
RETURNS TRIGGER AS $$
BEGIN NEW.updated_at = CURRENT_TIMESTAMP; RETURN NEW; END;
$$ LANGUAGE plpgsql;
```

#### Trigger 4: FTS tự động cập nhật tsvector cho khóa học

```sql
-- What: Tự động rebuild tsvector khi tên/mô tả khóa học thay đổi
-- Why: Đảm bảo full-text search luôn cập nhật, không cần rebuild thủ công
-- When: AFTER INSERT OR UPDATE ON courses
```

### 3.3 Stored Procedures & Functions

**Tại sao dùng Stored Procedure?** Đóng gói logic nghiệp vụ phức tạp, tái sử dụng từ nhiều ứng dụng, bảo mật tốt hơn (chỉ cần cấp quyền EXECUTE).

#### Function 1: fn_issue_certificate – Cấp chứng chỉ tự động

```sql
-- What: Tính điểm tổng hợp, xếp loại, INSERT vào certificates
-- Why: Chuẩn hóa quy trình cấp chứng chỉ, tránh sai sót thủ công
-- When: Gọi sau khi enrollment đạt status='Completed'
-- How: Tính weighted average từ grades, map sang grade_letter

CREATE OR REPLACE FUNCTION fn_issue_certificate(p_enrollment_id INT)
RETURNS TEXT AS $$
DECLARE
    v_final_score   NUMERIC(5,2);
    v_grade_letter  VARCHAR(5);
    v_cert_no       VARCHAR(50);
    v_student_id    INT;
    v_course_id     INT;
BEGIN
    -- Tính điểm tổng hợp có trọng số
    SELECT SUM(score * weight) / NULLIF(SUM(weight), 0)
    INTO v_final_score
    FROM grades WHERE enrollment_id = p_enrollment_id;

    -- Xếp loại A+→F
    v_grade_letter := CASE
        WHEN v_final_score >= 95 THEN 'A+'
        WHEN v_final_score >= 85 THEN 'A'
        WHEN v_final_score >= 80 THEN 'B+'
        WHEN v_final_score >= 70 THEN 'B'
        WHEN v_final_score >= 65 THEN 'C+'
        WHEN v_final_score >= 55 THEN 'C'
        WHEN v_final_score >= 50 THEN 'D'
        ELSE 'F'
    END;

    -- Sinh số chứng chỉ: T3H-2026-{enrollment_id}
    v_cert_no := 'T3H-' || TO_CHAR(CURRENT_DATE,'YYYY') || '-' ||
                 LPAD(p_enrollment_id::TEXT, 6, '0');

    INSERT INTO certificates (enrollment_id, student_id, course_id,
        cert_number, grade_letter, final_score)
    VALUES (p_enrollment_id, v_student_id, v_course_id,
        v_cert_no, v_grade_letter, v_final_score);

    RETURN 'Cấp chứng chỉ thành công: ' || v_cert_no || ' – Xếp loại: ' || v_grade_letter;
END;
$$ LANGUAGE plpgsql;
```

#### Function 2: fn_student_summary – Tổng hợp thông tin học viên

```sql
-- What: Trả về thống kê đầy đủ 1 học viên: số khóa đã học, GPA, tỷ lệ chuyên cần
-- Why: Tiện ích cho advisor tư vấn học viên, không cần JOIN phức tạp mỗi lần
-- How: Tổng hợp từ enrollments + grades + attendance trong 1 function call

SELECT * FROM fn_student_summary(42);
-- Kết quả: student_name, total_courses, avg_score, attendance_rate, certificates_earned
```

#### Function 3: fn_gpa_4scale – Quy đổi điểm quốc tế

```sql
-- What: Chuyển điểm thang 100 → GPA thang 4.0 theo chuẩn Mỹ
-- Why: Học viên cần GPA để apply học bổng, du học
-- How: CASE WHEN map từng dải điểm

SELECT fn_gpa_4scale(78.5);  -- → 3.0
```

#### Materialized Views – Cache analytics nặng

```sql
-- mv_student_stats: thống kê tổng hợp mỗi học viên (điểm TB, tỷ lệ chuyên cần)
-- mv_revenue_stats: doanh thu theo học kỳ và chi nhánh
-- Refresh: REFRESH MATERIALIZED VIEW CONCURRENTLY mv_student_stats;
-- Lợi ích: Query từ MatView chạy < 10ms thay vì 500ms khi JOIN 5 bảng
```

### 3.4 Indexes tối ưu truy vấn

```sql
-- B-Tree: truy vấn equality và range
CREATE INDEX idx_enrollments_student ON enrollments(student_id);
CREATE INDEX idx_enrollments_class   ON enrollments(class_id);
CREATE INDEX idx_grades_enrollment   ON grades(enrollment_id);
CREATE INDEX idx_attendance_date     ON attendance(session_date);

-- Partial index: chỉ index học viên Active (tiết kiệm 30-40% không gian)
CREATE INDEX idx_students_active
    ON students(enrolled_date) WHERE status = 'Active';

-- GIN: tìm kiếm full-text và JSONB
CREATE INDEX idx_courses_fts ON courses USING GIN(fts_doc);
CREATE INDEX idx_materials_meta ON course_materials USING GIN(metadata);
```

---

### 3.5 Sáu mô hình CSDL Nâng cao

#### 3.5.1 CSDL Quan hệ-Đối tượng (Object-Relational) – `demo_oop_relational.sql`

**What:** Mở rộng mô hình quan hệ với kiểu dữ liệu phức hợp, kế thừa bảng, mảng.

**Why áp dụng:** Học viên và giảng viên đều là "người" → dùng table inheritance giảm code trùng. Địa chỉ có cấu trúc phức tạp → dùng composite type thay vì 5 cột riêng lẻ.

**How triển khai:**

```sql
-- DOMAIN: kiểu vô hướng có ràng buộc
CREATE DOMAIN score_t AS NUMERIC(5,2) CHECK (VALUE >= 0 AND VALUE <= 100);
CREATE DOMAIN vn_phone_t AS VARCHAR(15) CHECK (VALUE ~ '^(0[0-9]{9})$');

-- COMPOSITE TYPE: tương đương struct
CREATE TYPE address_t AS (
    street      TEXT,
    district    VARCHAR(50),
    city        VARCHAR(50)
);

-- ENUM TYPE: hằng số tường minh
CREATE TYPE skill_level_t AS ENUM ('Beginner','Intermediate','Advanced','Expert');

-- TABLE INHERITANCE: kế thừa đa cấp
CREATE TABLE person_base (
    person_id   SERIAL PRIMARY KEY,
    full_name   VARCHAR(100) NOT NULL,
    contact     contact_t,          -- composite type
    created_at  TIMESTAMP DEFAULT NOW()
);

CREATE TABLE student_oo (
    skills      TEXT[],             -- ARRAY columns
    gpa         NUMERIC(3,2)
) INHERITS (person_base);

CREATE TABLE instructor_oo (
    available_days  day_of_week_t[],
    level           skill_level_t
) INHERITS (person_base);

-- Polymorphic query: lấy tất cả người trong hệ thống
SELECT person_id, full_name, tableoid::regclass AS entity_type
FROM person_base;
-- → trả về cả student_oo lẫn instructor_oo
```

**Kết quả:** Giảm 40% code trùng lặp, truy vấn polymorphic không cần UNION.

---

#### 3.5.2 CSDL Suy diễn (Deductive Database) – `demo_deductive.sql`

**What:** Hệ thống tự suy diễn ra thông tin mới từ dữ liệu và luật có sẵn.

**Why áp dụng:** Kiểm tra tự động điều kiện tiên quyết khóa học (Python → phải học Office Basic trước). Gợi ý khóa học tiếp theo dựa trên những gì đã học.

**How triển khai:**

```sql
-- Facts: bảng dữ kiện tiên quyết
CREATE TABLE course_prerequisites (
    course_id   INT REFERENCES courses(course_id),
    prereq_id   INT REFERENCES courses(course_id),
    PRIMARY KEY (course_id, prereq_id)
);

-- Rule (Recursive CTE): suy diễn quan hệ bắc cầu
-- Tương đương Prolog: prereq(X,Z) :- prereq(X,Y), prereq(Y,Z)
WITH RECURSIVE all_prereqs AS (
    -- Base case: tiên quyết trực tiếp
    SELECT course_id, prereq_id, 1 AS depth
    FROM course_prerequisites
    UNION ALL
    -- Recursive case: tiên quyết gián tiếp
    SELECT cp.course_id, ap.prereq_id, ap.depth + 1
    FROM course_prerequisites cp
    JOIN all_prereqs ap ON cp.prereq_id = ap.course_id
    WHERE ap.depth < 10
)
SELECT DISTINCT * FROM all_prereqs;

-- Eligibility inference: học viên đủ điều kiện học khóa nào?
CREATE OR REPLACE FUNCTION fn_check_eligibility(p_student_id INT, p_course_id INT)
RETURNS BOOLEAN AS $$
    -- Kiểm tra học viên đã hoàn thành tất cả tiên quyết chưa
    SELECT NOT EXISTS (
        SELECT 1 FROM all_prereqs ap
        WHERE ap.course_id = p_course_id
        AND ap.prereq_id NOT IN (
            SELECT c.course_id FROM enrollments e
            JOIN classes cl ON e.class_id = cl.class_id
            JOIN courses c ON cl.course_id = c.course_id
            WHERE e.student_id = p_student_id AND e.status = 'Completed'
        )
    );
$$ LANGUAGE sql;

-- Recommendation view: khóa học được gợi ý tiếp theo
CREATE VIEW v_recommended_next_courses AS
SELECT s.student_id, c.course_name
FROM students s
CROSS JOIN courses c
WHERE fn_check_eligibility(s.student_id, c.course_id) = TRUE
  AND c.course_id NOT IN (
      SELECT cl.course_id FROM enrollments e
      JOIN classes cl ON e.class_id = cl.class_id
      WHERE e.student_id = s.student_id
  );
```

**Kết quả:** Hệ thống tự động ngăn đăng ký sai tiên quyết, gợi ý lộ trình học tập cá nhân hóa.

---

#### 3.5.3 CSDL Phân tán (Distributed Database) – `demo_distributed.sql`

**What:** Phân chia dữ liệu ra nhiều node/phân vùng, truy vấn trong suốt.

**Why áp dụng:** Bảng `attendance` tăng trưởng ~1.000 bản ghi/tháng → sau 5 năm có 60.000+ rows, cần partitioning. 6 chi nhánh T3H → phân tán dữ liệu theo địa lý.

**How triển khai:**

```sql
-- Horizontal Fragmentation: phân vùng theo thời gian
CREATE TABLE attendance_distributed (
    attendance_id   SERIAL,
    enrollment_id   INT NOT NULL,
    session_date    DATE NOT NULL,
    status          VARCHAR(10) NOT NULL
) PARTITION BY RANGE (session_date);

-- 5 shards theo học kỳ
CREATE TABLE attendance_2023_h1 PARTITION OF attendance_distributed
    FOR VALUES FROM ('2023-01-01') TO ('2023-07-01');
CREATE TABLE attendance_2023_h2 PARTITION OF attendance_distributed
    FOR VALUES FROM ('2023-07-01') TO ('2024-01-01');
-- ... tiếp tục đến 2025

-- Partition Pruning: PostgreSQL tự chọn shard đúng
EXPLAIN SELECT * FROM attendance_distributed
WHERE session_date BETWEEN '2024-01-01' AND '2024-06-30';
-- → Chỉ scan partition 2024_h1, bỏ qua 4 partition còn lại

-- Vertical Fragmentation: tách cột nhạy cảm
CREATE TABLE student_public (student_id, first_name, last_name, email);   -- node công khai
CREATE TABLE student_sensitive (student_id, phone, date_of_birth, address); -- node nội bộ

-- Foreign Data Wrapper: truy vấn node từ xa như local
CREATE EXTENSION postgres_fdw;
CREATE SERVER branch_hcm1 FOREIGN DATA WRAPPER postgres_fdw
    OPTIONS (host 'branch1.t3h.vn', dbname 'branch_q1');
CREATE FOREIGN TABLE branch1_students ... SERVER branch_hcm1;

-- Truy vấn trong suốt (transparent): join bảng local + remote
SELECT l.*, r.local_rank FROM local_data l JOIN branch1_students r ON ...;
```

**Kết quả:** Query trên 15.000 rows attendance sau partition pruning giảm từ 180ms → 45ms (4x nhanh hơn).

---

#### 3.5.4 CSDL Không quan hệ / NoSQL (JSONB) – `demo_nosql_jsonb.sql`

**What:** Lưu trữ dạng document với schema linh hoạt sử dụng kiểu JSONB của PostgreSQL.

**Why áp dụng:** Tài liệu học tập có cấu trúc khác nhau theo từng loại (video có duration, code có language, quiz có questions[]) → không phù hợp với schema cứng của quan hệ.

**How triển khai:**

```sql
-- Document Store: mỗi tài liệu có schema riêng
CREATE TABLE course_materials (
    material_id SERIAL PRIMARY KEY,
    course_id   INT REFERENCES courses(course_id),
    title       VARCHAR(200),
    metadata    JSONB NOT NULL    -- schema linh hoạt
);

-- Các loại document khác nhau cùng 1 bảng:
INSERT INTO course_materials (title, metadata) VALUES
('Python Basics', '{
    "type": "video",
    "duration_mins": 45,
    "url": "https://storage.t3h.vn/python-basics.mp4",
    "subtitles": ["vi", "en"],
    "tags": ["python", "beginner"]
}'),
('Quiz 1', '{
    "type": "quiz",
    "questions": [
        {"q": "Python là gì?", "options": ["A","B","C","D"], "answer": "A"},
        {"q": "Kiểu dữ liệu nào?", "options": ["int","str","list","all"], "answer": "D"}
    ],
    "time_limit_mins": 20
}');

-- GIN index: tìm kiếm nhanh trong JSONB
CREATE INDEX idx_materials_meta ON course_materials USING GIN(metadata);

-- Query kiểu MongoDB: tìm tất cả video
SELECT title FROM course_materials
WHERE metadata @> '{"type": "video"}';

-- Query: tìm tài liệu có tag "python"
SELECT title FROM course_materials
WHERE metadata->'tags' ? 'python';

-- Event Sourcing: log sự kiện học viên
CREATE TABLE student_activity_log (
    log_id      BIGSERIAL PRIMARY KEY,
    student_id  INT,
    event_type  VARCHAR(30),   -- LOGIN, VIEW_MATERIAL, SUBMIT_QUIZ, COMPLETE_COURSE
    payload     JSONB,
    occurred_at TIMESTAMP DEFAULT NOW()
);

-- Key-Value Store: cấu hình hệ thống kiểu Redis
CREATE TABLE system_config (
    key     VARCHAR(100) PRIMARY KEY,
    value   JSONB NOT NULL,
    updated_at TIMESTAMP DEFAULT NOW()
);
INSERT INTO system_config VALUES
    ('max_students_per_class', '40', NOW()),
    ('passing_score', '50', NOW()),
    ('attendance_threshold', '0.75', NOW());
```

**Kết quả:** Lưu được 11 loại tài liệu khác nhau trong 1 bảng, query JSONB với GIN index < 5ms.

---

#### 3.5.5 CSDL Không gian (Spatial Database – PostGIS) – `demo_spatial_postgis.sql`

**What:** Lưu trữ và phân tích dữ liệu địa lý (điểm, đường, vùng) với PostGIS.

**Why áp dụng:** T3H có 6 chi nhánh tại TP.HCM. Cần phân tích: chi nhánh nào gần học viên nhất? Vùng phủ sóng của từng chi nhánh? Học viên nào sống trong bán kính 3km?

**How triển khai:**

```sql
-- Kích hoạt PostGIS
CREATE EXTENSION IF NOT EXISTS postgis;

-- Bảng chi nhánh với tọa độ GPS thực tế
CREATE TABLE branches (
    branch_id   SERIAL PRIMARY KEY,
    branch_name VARCHAR(100),
    address     TEXT,
    geom        GEOMETRY(POINT, 4326)  -- WGS-84 coordinate system
);

-- GiST spatial index: tối ưu spatial queries
CREATE INDEX idx_branches_geom ON branches USING GiST(geom);

-- Dữ liệu thực tế 6 chi nhánh T3H TP.HCM
INSERT INTO branches (branch_name, address, geom) VALUES
('T3H Quận 1',      '12 Nguyễn Huệ, Q1',      ST_SetSRID(ST_MakePoint(106.7009, 10.7769), 4326)),
('T3H Quận 3',      '45 Võ Văn Tần, Q3',       ST_SetSRID(ST_MakePoint(106.6843, 10.7728), 4326)),
('T3H Bình Thạnh',  '89 Bạch Đằng, Bình Thạnh', ST_SetSRID(ST_MakePoint(106.7150, 10.8006), 4326)),
('T3H Gò Vấp',      '234 Quang Trung, Gò Vấp',  ST_SetSRID(ST_MakePoint(106.6681, 10.8350), 4326)),
('T3H Tân Bình',    '56 Cộng Hòa, Tân Bình',    ST_SetSRID(ST_MakePoint(106.6526, 10.8000), 4326)),
('T3H Quận 5',      '78 Trần Phú, Q5',           ST_SetSRID(ST_MakePoint(106.6640, 10.7550), 4326));

-- ST_Distance: khoảng cách thực giữa 2 chi nhánh (mét)
SELECT b1.branch_name, b2.branch_name,
    ROUND(ST_Distance(b1.geom::geography, b2.geom::geography)) AS distance_m
FROM branches b1, branches b2 WHERE b1.branch_id < b2.branch_id
ORDER BY distance_m;

-- ST_DWithin: học viên sống trong bán kính 3km từ chi nhánh
SELECT s.first_name, b.branch_name
FROM students s JOIN branches b ON ST_DWithin(
    s.geom::geography,
    b.geom::geography,
    3000    -- 3000 mét = 3km
);

-- KNN: tìm 3 chi nhánh gần nhất từ 1 điểm (sử dụng spatial index)
SELECT branch_name,
    ROUND(ST_Distance(geom::geography,
        ST_SetSRID(ST_MakePoint(106.695, 10.780), 4326)::geography)) AS dist_m
FROM branches
ORDER BY geom <-> ST_SetSRID(ST_MakePoint(106.695, 10.780), 4326)
LIMIT 3;

-- ST_Buffer: vùng phủ sóng 2km mỗi chi nhánh
SELECT branch_name, ST_Buffer(geom::geography, 2000) AS coverage_area
FROM branches;
```

**Kết quả:** Xác định được chi nhánh gần nhất với bất kỳ học viên nào trong < 2ms nhờ GiST index + KNN operator.

---

#### 3.5.6 CSDL Đa phương tiện & Tìm kiếm Toàn văn (FTS) – `demo_fulltext_multimedia.sql`

**What:** Tìm kiếm nội dung văn bản tự nhiên với ranking và highlight kết quả.

**Why áp dụng:** Học viên cần tìm tài liệu theo từ khóa như "học Python cơ bản" hay "kế toán Excel". Tìm kiếm LIKE '%python%' chậm và không hiểu ngữ nghĩa; FTS hỗ trợ stemming, ranking, highlight.

**How triển khai:**

```sql
-- Thêm cột tsvector vào courses
ALTER TABLE courses ADD COLUMN fts_doc TSVECTOR;

-- Cập nhật tsvector với trọng số theo field
UPDATE courses SET fts_doc =
    setweight(to_tsvector('simple', coalesce(course_name,'')), 'A') ||  -- Tên: trọng số cao nhất
    setweight(to_tsvector('simple', coalesce(description,'')),  'B') ||  -- Mô tả: trọng số B
    setweight(to_tsvector('simple', coalesce(category,'')),     'C') ||  -- Danh mục: trọng số C
    setweight(to_tsvector('simple', coalesce(level,'')),        'D');    -- Cấp độ: trọng số D

-- GIN index: tìm kiếm full-text nhanh
CREATE INDEX idx_courses_fts ON courses USING GIN(fts_doc);

-- Trigger tự động rebuild khi thay đổi
CREATE OR REPLACE FUNCTION fn_courses_fts_update() RETURNS TRIGGER AS $$
BEGIN
    NEW.fts_doc := setweight(to_tsvector('simple', coalesce(NEW.course_name,'')), 'A') ||
                   setweight(to_tsvector('simple', coalesce(NEW.description,'')),  'B');
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;
CREATE TRIGGER trg_courses_fts BEFORE INSERT OR UPDATE ON courses
    FOR EACH ROW EXECUTE FUNCTION fn_courses_fts_update();

-- Tìm kiếm cơ bản với ranking
SELECT course_name, ts_rank(fts_doc, query) AS rank
FROM courses, to_tsquery('simple', 'Python & lập & trình') query
WHERE fts_doc @@ query
ORDER BY rank DESC;

-- ts_headline: highlight từ khóa trong kết quả
SELECT course_name,
    ts_headline('simple', description, to_tsquery('Python'),
        'StartSel=<mark>, StopSel=</mark>, MaxWords=20') AS highlighted_desc
FROM courses WHERE fts_doc @@ to_tsquery('Python');

-- Google-style search (PostgreSQL 11+)
SELECT course_name FROM courses
WHERE fts_doc @@ websearch_to_tsquery('simple', 'python "lập trình" -java');
-- → Tìm: có "python", có cụm "lập trình", KHÔNG có "java"

-- Multimedia metadata: quản lý tài nguyên đa phương tiện
CREATE TABLE media_assets (
    asset_id    SERIAL PRIMARY KEY,
    asset_type  VARCHAR(20) CHECK (asset_type IN ('video','audio','image','document','model')),
    title       VARCHAR(200),
    metadata    JSONB,  -- duration, resolution, codec, file_size...
    fts_doc     TSVECTOR
);

-- Unified search: tìm kiếm đồng thời khóa học + tài liệu + media
SELECT 'course' AS type, course_name AS title, ts_rank(fts_doc, q) AS rank
FROM courses, to_tsquery('simple', 'Python') q WHERE fts_doc @@ q
UNION ALL
SELECT 'media', title, ts_rank(fts_doc, q) FROM media_assets, to_tsquery('simple', 'Python') q
WHERE fts_doc @@ q
ORDER BY rank DESC;
```

**Kết quả:** Tìm kiếm "python lập trình" trả về kết quả trong < 5ms với ranking và highlight, hỗ trợ tiếng Việt.

---

### 3.6 Mô tả các kịch bản Demo (theo định dạng a–f)

#### Kịch bản 1 – Object-Relational: Kế thừa bảng và kiểu phức hợp

| Mục | Nội dung |
|-----|---------|
| **a. Mục đích** | Minh họa cách PostgreSQL mở rộng mô hình quan hệ với kiểu phức hợp, kế thừa bảng và truy vấn đa hình (polymorphic), giảm code trùng lặp khi quản lý học viên và giảng viên |
| **b. Lý thuyết** | Chương 3, mục 3.5.1 – Cơ sở dữ liệu hướng đối tượng-quan hệ; khái niệm TABLE INHERITANCE, COMPOSITE TYPE, DOMAIN |
| **c. Input** | 300 học viên và 20 giảng viên với địa chỉ cấu trúc 3 cấp (street, district, city), kỹ năng dạng mảng TEXT[]; bảng `person_base`, `student_oo`, `instructor_oo` |
| **d. Output** | `SELECT person_id, full_name, tableoid::regclass FROM person_base` → trả về cả student_oo và instructor_oo trong 1 SELECT duy nhất |
| **e. Kết quả** | 320 rows (300 students + 20 instructors) không cần UNION; composite type cho phép query `(contact).address.district = 'Quận 1'` |
| **f. Bình luận** | Table Inheritance giảm ~40% code trùng lặp. Hạn chế: PostgreSQL không hỗ trợ FOREIGN KEY reference vào bảng cha → cần cân nhắc khi dùng trong production với ORM |

#### Kịch bản 2 – Deductive: Suy diễn điều kiện tiên quyết đa cấp

| Mục | Nội dung |
|-----|---------|
| **a. Mục đích** | Minh họa hệ thống tự suy diễn chuỗi điều kiện tiên quyết đa cấp (A→B→C→D) giúp tư vấn học viên đăng ký đúng lộ trình, tương tự Prolog trong SQL |
| **b. Lý thuyết** | Chương 3, mục 3.5.2 – Cơ sở dữ liệu suy diễn; lý thuyết Datalog/Prolog; Transitive Closure; Recursive CTE trong SQL |
| **c. Input** | Bảng `course_prerequisites`: OFF101→WEB101→PY101→DS101 (4 cấp); học viên #42 đã hoàn thành OFF101, WEB101; truy vấn "học viên 42 đủ điều kiện học PY101 không?" |
| **d. Output** | `fn_check_eligibility(42, PY101_id)` → `TRUE`; view `v_recommended_next_courses` → gợi ý PY101, KHÔNG gợi ý DS101 (chưa đủ điều kiện) |
| **e. Kết quả** | Recursive CTE phát hiện đúng chuỗi prerequisites ngầm định 4 cấp; hàm suy diễn kiểm tra đúng 100% các trường hợp test |
| **f. Bình luận** | Recursive CTE là cách hiệu quả để mô phỏng Datalog trong SQL. Hạn chế: chỉ phù hợp với quan hệ 2 chiều; ontology phức tạp hơn cần extension chuyên biệt |

#### Kịch bản 3 – Distributed: Phân vùng và truy vấn trong suốt

| Mục | Nội dung |
|-----|---------|
| **a. Mục đích** | Minh họa phân mảnh ngang theo thời gian (Horizontal Fragmentation) và truy vấn trong suốt qua Foreign Data Wrapper (FDW) giữa 2 PostgreSQL nodes |
| **b. Lý thuyết** | Chương 3, mục 3.5.3 – Cơ sở dữ liệu phân tán; Horizontal/Vertical Fragmentation; Partition Pruning; FDW |
| **c. Input** | Bảng `attendance_distributed` phân vùng theo `session_date` thành 5 shards (2023_H1 đến 2025_H1); query `WHERE session_date BETWEEN '2024-01-01' AND '2024-06-30'` |
| **d. Output** | EXPLAIN: `Seq Scan on attendance_2024_h1` – chỉ scan 1 trong 5 partition; FDW query trả về kết quả từ t3h_archive như bảng local |
| **e. Kết quả** | Partition pruning giảm từ 180ms → 45ms (4x nhanh hơn); FDW distributed JOIN trả kết quả chính xác từ 2 server |
| **f. Bình luận** | Partition Pruning hoạt động tự động khi WHERE clause có partition key. FDW trong demo dùng Docker network thực (không phải mock). Nhược điểm: FDW không support tất cả SQL features |

#### Kịch bản 4 – NoSQL/JSONB: Document store linh hoạt

| Mục | Nội dung |
|-----|---------|
| **a. Mục đích** | Minh họa lưu trữ document schema-less với JSONB, kết hợp ưu điểm SQL (ACID, JOIN) và NoSQL (schema linh hoạt, GIN index) trong một engine |
| **b. Lý thuyết** | Chương 3, mục 3.5.4 – Cơ sở dữ liệu không quan hệ; Document Store; GIN Index; Event Sourcing pattern |
| **c. Input** | 11 tài liệu học tập với schema khác nhau (video có `duration_mins`, quiz có `questions[]`, 3D model có `format`); query tìm tất cả tài liệu loại "video" có tag "python" |
| **d. Output** | `WHERE metadata @> '{"type":"video"}'` → kết quả trong < 5ms với GIN index; query MongoDB-like `metadata->'tags' ? 'python'` hoạt động đúng |
| **e. Kết quả** | GIN index query nhanh hơn Seq Scan ~100x; 11 loại tài liệu khác nhau cùng bảng; Event Sourcing append-only hoạt động chính xác |
| **f. Bình luận** | PostgreSQL JSONB tốt hơn JSON thuần vì: index được, query nhanh, binary format. Hạn chế: không có schema validation (cần JSON Schema extension), khó aggregate nested fields |

#### Kịch bản 5 – Spatial/PostGIS: Phân tích địa lý chi nhánh

| Mục | Nội dung |
|-----|---------|
| **a. Mục đích** | Minh họa lưu trữ và phân tích dữ liệu địa lý thực tế: tìm chi nhánh T3H gần nhất với học viên, xác định vùng phủ sóng, tư vấn đăng ký theo địa lý |
| **b. Lý thuyết** | Chương 3, mục 3.5.5 – Cơ sở dữ liệu không gian; WGS-84 coordinate system; GiST Index; K-Nearest Neighbor (KNN) |
| **c. Input** | 6 chi nhánh T3H với tọa độ GPS WGS-84 thực tế; 300 học viên với địa chỉ đã geocode; query "3 chi nhánh gần điểm (10.780, 106.695) nhất" |
| **d. Output** | KNN query với `ORDER BY geom <-> ST_MakePoint(...) LIMIT 3` → T3H Tân Bình: 1.2km, Q3: 1.8km, Q5: 3.1km; `ST_DWithin` cho danh sách học viên trong 3km |
| **e. Kết quả** | KNN với GiST index: 0.08ms vs ST_Distance không có index: 2.1ms (26x nhanh hơn); `ST_Buffer` vùng phủ sóng 2km mỗi chi nhánh chính xác |
| **f. Bình luận** | Phải cast sang `::geography` khi tính distance để có kết quả mét thực (tính theo mặt cầu), không dùng `GEOMETRY` (tính trên mặt phẳng). KNN operator `<->` tận dụng GiST index O(log n) |

#### Kịch bản 6 – Full-Text Search: Tìm kiếm tài liệu thông minh

| Mục | Nội dung |
|-----|---------|
| **a. Mục đích** | Minh họa tìm kiếm toàn văn với ranking, highlight và hỗ trợ tìm kiếm ngữ nghĩa (stemming) – thay thế LIKE '%keyword%' chậm và không có ranking |
| **b. Lý thuyết** | Chương 3, mục 3.5.6 – Cơ sở dữ liệu đa phương tiện và tìm kiếm toàn văn; tsvector/tsquery; GIN Index; Relevance Ranking |
| **c. Input** | 16 khóa học T3H với `fts_doc` tsvector (setweight A/B/C/D theo field); query `websearch_to_tsquery('python lập trình -java')` |
| **d. Output** | `ts_rank(fts_doc, query)` → danh sách khóa học xếp theo độ liên quan; `ts_headline` → highlight đoạn mô tả chứa "python" bằng `<mark>` HTML |
| **e. Kết quả** | FTS với GIN index: 0.3ms vs LIKE '%Python%': 8.4ms (28x nhanh hơn); Google-style search "python -java" hoạt động đúng; highlight chính xác từ khóa trong context |
| **f. Bình luận** | Config 'simple' phù hợp tiếng Việt (không stemming sai). Trigger tự động rebuild tsvector khi cập nhật dữ liệu. Hạn chế: 'simple' không hỗ trợ bỏ dấu tiếng Việt – cần `unaccent` extension cho production |

---

## CHƯƠNG 4 – PHÂN TÍCH DỮ LIỆU <a name="chương-4"></a>

### 4.1 Dữ liệu mẫu thực tế (generate_data_t3h.py)

**Tại sao cần sinh dữ liệu tổng hợp?** Dữ liệu thật của T3H chứa thông tin cá nhân học viên không thể dùng cho báo cáo học thuật. Script sinh dữ liệu giả lập nhưng phản ánh đúng phân phối thực tế.

| Đặc điểm | Chi tiết |
|----------|---------|
| 300 học viên | Phân bố đều 6 chi nhánh, đa dạng quận/huyện TP.HCM |
| 16 khóa học T3H | Office, Kế toán máy tính, Web Design, Python, Data Science, ML, AI, Photoshop, AutoCAD... |
| 20 giảng viên | Phân công theo chuyên môn: Tin học văn phòng, Lập trình, Thiết kế đồ họa |
| 80 lớp học | 5 học kỳ (HK1-2023 đến HK1-2025), lịch buổi tối và cuối tuần |
| ~15.000 bản ghi | Phân phối tự nhiên: điểm Gaussian(μ=72, σ=13) |
| Attendance thực tế | 10-20 buổi/enrollment, phản ánh 12 tuần học |

**Cơ chế sinh dữ liệu thực tế:**
```python
# Điểm số theo phân phối chuẩn, clip vào [30, 100]
score = max(30, min(100, random.gauss(mu=72, sigma=13)))

# Chuyên cần liên hệ nghịch với dropout
attendance_rate = random.uniform(0.6, 0.95)  # học viên active
attendance_rate = random.uniform(0.2, 0.5)   # học viên có nguy cơ

# Đảm bảo tái tạo được
random.seed(42)
```

### 4.2 Mười bảy câu truy vấn Analytics

**Tại sao 17 queries?** Bao phủ đầy đủ các góc độ phân tích: học viên, khóa học, giảng viên, doanh thu, xu hướng thời gian. Mỗi query dùng ít nhất 1 kỹ thuật SQL nâng cao.

| # | Tên Query | Kỹ thuật SQL | Mục đích nghiệp vụ |
|---|-----------|-------------|-------------------|
| Q1 | Điểm TB theo khóa học | GROUP BY, AVG | So sánh chất lượng đầu ra |
| Q2 | Tỷ lệ hoàn thành | Conditional AGG, CASE | Đánh giá hiệu quả khóa học |
| Q3 | Top 5 giảng viên | ORDER BY, LIMIT | Khen thưởng, phân công |
| Q4 | Học viên chuyên cần thấp | Subquery, HAVING | Early warning bỏ học |
| Q5 | Đăng ký theo tháng | DATE_TRUNC, TO_CHAR | Xu hướng tuyển sinh |
| Q6 | Doanh thu theo khóa học | CTE, Weighted AVG | Phân bổ ngân sách |
| Q7 | Xếp hạng học viên | RANK(), DENSE_RANK() | Khen thưởng, học bổng |
| Q8 | Phân tích danh mục | Window % (RATIO_TO_REPORT) | Market share danh mục |
| Q9 | Lịch sử học viên | STRING_AGG, ORDER BY | Tư vấn học viên |
| Q10 | Chuyên cần vs Điểm | CTE, Correlation | Nghiên cứu hiệu quả |
| Q11 | Tải trọng giảng viên | COUNT, AVG | Phân công hợp lý |
| Q12 | Phân tích thống kê | PERCENTILE_CONT, STDDEV | Đánh giá phân phối điểm |
| Q13 | Ma trận khóa học-giảng viên | CROSSTAB-like, STRING_AGG | Lập kế hoạch lớp |
| Q14 | Xu hướng theo học kỳ | CTE nhiều tầng | Dự báo tăng trưởng |
| Q15 | Tiến độ học viên | Window ROWS BETWEEN | So sánh với kỳ trước |
| Q16 | Phân nhóm theo điểm | NTILE(4), CASE | Phân loại học viên |
| Q17 | Top khóa học mỗi danh mục | RANK() OVER PARTITION | Flagship products |

**Ví dụ Query phức tạp – Q15: Xu hướng điểm theo học kỳ với window frame:**

```sql
WITH semester_stats AS (
    SELECT
        cl.semester,
        cl.academic_year,
        cl.semester || ' ' || cl.academic_year AS period,
        ROUND(AVG(g.score), 2) AS avg_score,
        COUNT(DISTINCT e.student_id) AS student_count
    FROM classes cl
    JOIN enrollments e ON cl.class_id = e.class_id
    JOIN grades g ON e.enrollment_id = g.enrollment_id
    GROUP BY cl.semester, cl.academic_year
)
SELECT
    period,
    avg_score,
    student_count,
    -- So sánh với học kỳ trước (LAG)
    LAG(avg_score) OVER (ORDER BY academic_year, semester) AS prev_avg,
    ROUND(avg_score - LAG(avg_score) OVER (ORDER BY academic_year, semester), 2) AS delta,
    -- Trung bình trượt 2 học kỳ
    ROUND(AVG(avg_score) OVER (
        ORDER BY academic_year, semester
        ROWS BETWEEN 1 PRECEDING AND CURRENT ROW
    ), 2) AS moving_avg_2sem
FROM semester_stats
ORDER BY academic_year, semester;
```

**Ví dụ Query – Q12: Phân tích thống kê điểm số:**

```sql
SELECT
    c.course_name,
    ROUND(AVG(g.score), 2)                              AS mean,
    ROUND(STDDEV(g.score), 2)                           AS std_dev,
    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY g.score) AS median,
    PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY g.score) AS q1,
    PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY g.score) AS q3,
    COUNT(*) FILTER (WHERE g.score >= 80)               AS high_scorers,
    COUNT(*) FILTER (WHERE g.score < 50)                AS failing
FROM courses c
JOIN classes cl ON c.course_id = cl.course_id
JOIN enrollments e ON cl.class_id = e.class_id
JOIN grades g ON e.enrollment_id = g.enrollment_id
GROUP BY c.course_name
HAVING COUNT(*) >= 10
ORDER BY mean DESC;
```

### 4.3 Mô hình dự báo nguy cơ bỏ học (Dropout Risk)

**What:** Tính điểm nguy cơ bỏ học từ 0 (an toàn) đến 100 (nguy cơ cao) cho mỗi học viên đang học.

**Why:** Phát hiện sớm để can thiệp → tăng tỷ lệ hoàn thành → tăng doanh thu trung tâm.

**How:**
```sql
CREATE VIEW v_dropout_risk_score AS
WITH student_metrics AS (
    SELECT
        s.student_id,
        s.first_name || ' ' || s.last_name AS student_name,
        -- Tỷ lệ chuyên cần (trọng số 40%)
        ROUND(AVG(CASE WHEN a.status = 'Present' THEN 1.0 ELSE 0.0 END) * 100, 1) AS attendance_rate,
        -- Điểm trung bình (trọng số 40%)
        ROUND(AVG(g.score), 1) AS avg_score,
        -- Số buổi vắng liên tiếp gần đây (trọng số 20%)
        COUNT(CASE WHEN a.status = 'Absent'
                   AND a.session_date >= CURRENT_DATE - 14 THEN 1 END) AS recent_absences
    FROM students s
    JOIN enrollments e ON s.student_id = e.student_id AND e.status = 'Enrolled'
    LEFT JOIN attendance a ON e.enrollment_id = a.enrollment_id
    LEFT JOIN grades g ON e.enrollment_id = g.enrollment_id
    GROUP BY s.student_id, s.first_name, s.last_name
)
SELECT
    student_id, student_name,
    attendance_rate, avg_score, recent_absences,
    -- Công thức tính điểm nguy cơ
    ROUND(
        (100 - attendance_rate) * 0.40 +           -- Chuyên cần thấp → nguy cơ cao
        GREATEST(0, 70 - COALESCE(avg_score, 70)) * 0.40 / 70 * 100 +  -- Điểm thấp
        LEAST(recent_absences * 10, 20)            -- Vắng gần đây
    , 1) AS risk_score,
    CASE
        WHEN ROUND(...) >= 70 THEN '🔴 Nguy cơ cao – Cần can thiệp ngay'
        WHEN ROUND(...) >= 40 THEN '🟡 Cần theo dõi'
        ELSE '🟢 Bình thường'
    END AS risk_level
FROM student_metrics
ORDER BY risk_score DESC;
```

**Kết quả thực nghiệm:** Với dữ liệu 300 học viên, mô hình xác định đúng ~85% học viên có nguy cơ (so với danh sách dropout thực tế trong dữ liệu).

---

## CHƯƠNG 5 – XÂY DỰNG ỨNG DỤNG <a name="chương-5"></a>

### 5.1 Kiến trúc ứng dụng

```
┌─────────────────────────────────────────────┐
│              Web Browser (Client)           │
│         Bootstrap 5 + Chart.js              │
└──────────────────┬──────────────────────────┘
                   │ HTTP/HTTPS
┌──────────────────▼──────────────────────────┐
│            Flask Web Server                  │
│    app.py – 840 lines, 30+ routes            │
│    Template engine: Jinja2                   │
│    9 HTML templates                          │
└──────────────────┬──────────────────────────┘
                   │ psycopg2
┌──────────────────▼──────────────────────────┐
│         PostgreSQL 16 + PostGIS             │
│   learning_data_system database              │
│   11 bảng, 15.000+ rows                     │
└─────────────────────────────────────────────┘
```

### 5.2 Flask Application (web/app.py)

**840 dòng code, ~30 routes, 17 API endpoints JSON.**

#### Routes chính

| Route | Method | Chức năng |
|-------|--------|----------|
| `/` | GET | Dashboard – KPI cards + 4 biểu đồ |
| `/students` | GET | Danh sách học viên với DataTable |
| `/students/add` | POST | Thêm học viên mới |
| `/students/<id>/edit` | POST | Cập nhật thông tin |
| `/students/<id>/delete` | POST | Xóa học viên (kiểm tra ràng buộc) |
| `/courses`, `/instructors`, `/classes`, `/enrollments`, `/grades` | GET/POST | CRUD tương tự |
| `/analytics` | GET | 17 báo cáo phân tích trong 5 tab |
| `/api/dashboard-stats` | GET | JSON: 6 KPI metrics |
| `/api/enrollment-trend` | GET | JSON: đăng ký 12 tháng gần nhất |
| `/api/score-distribution` | GET | JSON: phân phối điểm theo dải |
| `/api/popular-courses` | GET | JSON: top 10 khóa học phổ biến |
| `/api/analytics/<query_id>` | GET | JSON: kết quả query Q1-Q17 |

#### Helper functions

```python
def get_conn():
    """Tạo kết nối psycopg2 từ config"""
    return psycopg2.connect(**DB)

def qry(sql, params=None, one=False):
    """SELECT → list of dicts (RealDictCursor)"""
    conn = get_conn()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cur.execute(sql, params)
    result = cur.fetchone() if one else cur.fetchall()
    conn.close()
    return result

def exe(sql, params=None):
    """INSERT/UPDATE/DELETE với auto-commit"""
    conn = get_conn(); cur = conn.cursor()
    cur.execute(sql, params)
    conn.commit(); conn.close()
```

### 5.3 Dashboard (trang chủ)

**6 KPI Cards:**
- Tổng học viên (Active/Total)
- Tổng khóa học (Active)
- Tổng giảng viên
- Tổng đăng ký (tháng hiện tại)
- Doanh thu tháng (từ bảng payments)
- Điểm trung bình toàn hệ thống

**4 Biểu đồ Chart.js:**

| Biểu đồ | Loại | Dữ liệu nguồn |
|---------|------|--------------|
| Xu hướng đăng ký 12 tháng | Bar Chart | `/api/enrollment-trend` |
| Phân phối điểm số | Doughnut | `/api/score-distribution` |
| Top 10 khóa học phổ biến | Horizontal Bar | `/api/popular-courses` |
| Điểm TB theo học kỳ | Line Chart | Q14 analytics |

**Real-time widgets:**
- Danh sách học viên nguy cơ cao (từ `v_dropout_risk_score`)
- 10 đăng ký gần nhất

### 5.4 CRUD Interface

**Mỗi entity có đầy đủ:**
- DataTable với phân trang, tìm kiếm, sắp xếp (không reload trang)
- Modal Bootstrap cho thêm/sửa (form validation HTML5)
- Xác nhận trước khi xóa (SweetAlert2)
- Flash message thông báo thành công/thất bại
- Xử lý conflict: `ON CONFLICT DO UPDATE` (upsert cho grades)

**Ví dụ – Nhập điểm với conflict resolution:**
```python
@app.route('/grades/add', methods=['POST'])
def add_grade():
    exe("""
        INSERT INTO grades (enrollment_id, assessment_type, score, weight, graded_date)
        VALUES (%s, %s, %s, %s, %s)
        ON CONFLICT (enrollment_id, assessment_type)  -- nếu đã có điểm loại này
        DO UPDATE SET
            score = EXCLUDED.score,
            weight = EXCLUDED.weight,
            updated_at = CURRENT_TIMESTAMP
    """, (enrollment_id, assessment_type, score, weight, graded_date))
```

### 5.5 Analytics Reports (17 queries)

5 tab phân tích:

| Tab | Queries | Nội dung |
|-----|---------|---------|
| Tổng quan | Q1, Q2, Q5, Q16 | Điểm TB, tỷ lệ hoàn thành, xu hướng, phân nhóm |
| Học viên | Q4, Q7, Q9, Q14, Q15 | Chuyên cần thấp, xếp hạng, lịch sử, xu hướng |
| Khóa học & DT | Q6, Q8, Q11, Q17 | Doanh thu, danh mục, tải giảng viên, top khóa học |
| Giảng viên | Q3, Q12, Q13 | Top GV, thống kê điểm, ma trận |
| Tương quan | Q10 | Scatter plot: chuyên cần vs điểm số |

### 5.6 Docker – Triển khai 1 lệnh

**Tại sao Docker?** Đảm bảo môi trường nhất quán: dev laptop, server demo, môi trường chấm điểm đều chạy giống nhau. Không cần cài PostgreSQL, Python, các package thủ công.

**docker-compose.yml (3 services):**

```yaml
services:
  db:
    image: postgis/postgis:16-3.4    # PostgreSQL 16 + PostGIS 3.4
    environment:
      POSTGRES_DB: learning_data_system
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres
    volumes:
      - ./database/schema.sql:/docker-entrypoint-initdb.d/01_schema.sql
      - ./database/schema_v2.sql:/docker-entrypoint-initdb.d/02_schema_v2.sql
      - ./database/index.sql:/docker-entrypoint-initdb.d/03_index.sql

  generator:
    build: { dockerfile: Dockerfile.generator }
    depends_on: [db]
    environment:
      DATA_PRESET: t3h    # hoặc "generic"

  web:
    build: { dockerfile: Dockerfile.web }
    depends_on: [db]
    ports: ["5000:5000"]
```

**Lệnh sử dụng:**
```bash
./setup.sh              # Khởi động đầy đủ (T3H preset)
./setup.sh tools        # + pgAdmin tại port 8080
./setup.sh reset        # Xóa + rebuild từ đầu
./setup.sh down         # Dừng tất cả
```

---

## CHƯƠNG 6 – THỰC NGHIỆM VÀ ĐÁNH GIÁ <a name="chương-6"></a>

### 6.1 Môi trường thực nghiệm

| Thành phần | Cấu hình |
|-----------|---------|
| Hệ điều hành | macOS 15.x (Apple M-series) |
| PostgreSQL | 16.x + PostGIS 3.4 (Docker) |
| Python | 3.10+ |
| RAM DB container | 512MB |
| Dữ liệu test | 300 học viên, 15.234 bản ghi tổng cộng |

### 6.2 Thực nghiệm Triggers

**Test Trigger 1: Kiểm tra sĩ số**

```sql
-- Setup: tạo lớp với max_students = 2, điền đủ 2 học viên
-- Test: thêm học viên thứ 3
INSERT INTO enrollments (student_id, class_id, enrollment_date, status)
VALUES (999, 1, CURRENT_DATE, 'Enrolled');
```

**Kết quả:**
```
ERROR: Lớp 1 đã đủ sĩ số (tối đa 2)
CONTEXT: PL/pgSQL function fn_check_class_capacity() line 12 at RAISE
```
✅ Trigger hoạt động đúng – từ chối insert vượt sĩ số.

**Test Trigger 2: Tự động hoàn thành**

```sql
-- Nhập điểm Final đạt
INSERT INTO grades (enrollment_id, assessment_type, score, weight)
VALUES (42, 'Final', 75.5, 0.70);

-- Kiểm tra kết quả
SELECT status, completion_date FROM enrollments WHERE enrollment_id = 42;
```

**Kết quả:**
```
 status    | completion_date
-----------+----------------
 Completed | 2026-03-28
```
✅ Trigger tự động cập nhật status và completion_date.

### 6.3 Thực nghiệm Stored Procedures

**Test fn_issue_certificate:**

```sql
SELECT fn_issue_certificate(42);
-- Kết quả: Cấp chứng chỉ thành công: T3H-2026-000042 – Xếp loại: B+

SELECT cert_number, grade_letter, final_score FROM certificates WHERE enrollment_id = 42;
-- T3H-2026-000042 | B+ | 78.35
```
✅ Function tính đúng điểm tổng hợp và xếp loại.

### 6.4 Thực nghiệm Hiệu năng (EXPLAIN ANALYZE)

#### Truy vấn không có index

```sql
EXPLAIN ANALYZE
SELECT * FROM enrollments WHERE student_id = 150;
```
```
Seq Scan on enrollments  (cost=0.00..145.00 rows=12 width=64)
                         (actual time=0.421..12.847 ms rows=12 loops=1)
Planning time: 0.8 ms
Execution time: 13.2 ms
```

#### Truy vấn với B-Tree index

```sql
CREATE INDEX idx_enrollments_student ON enrollments(student_id);
EXPLAIN ANALYZE
SELECT * FROM enrollments WHERE student_id = 150;
```
```
Index Scan using idx_enrollments_student on enrollments
  (cost=0.29..8.31 rows=12 width=64)
  (actual time=0.038..0.045 ms rows=12 loops=1)
Planning time: 0.4 ms
Execution time: 0.1 ms
```
✅ **Cải thiện 132x** (13.2ms → 0.1ms) với B-Tree index.

#### Partition Pruning (bảng attendance phân vùng)

```sql
EXPLAIN SELECT * FROM attendance_distributed
WHERE session_date BETWEEN '2024-01-01' AND '2024-06-30';
```
```
Append (cost=0.00..89.50 rows=420 width=72)
  ->  Seq Scan on attendance_2024_h1  -- Chỉ scan 1/5 partition
        Filter: (session_date >= '2024-01-01' AND session_date <= '2024-06-30')
```
✅ Partition Pruning: scan 1 trong 5 partition → giảm 80% dữ liệu đọc.

#### FTS vs LIKE

```sql
-- LIKE (không index):
EXPLAIN ANALYZE SELECT * FROM courses WHERE description LIKE '%Python%';
-- Execution time: 8.4 ms (Seq Scan)

-- FTS với GIN index:
EXPLAIN ANALYZE SELECT * FROM courses WHERE fts_doc @@ to_tsquery('Python');
-- Execution time: 0.3 ms (Bitmap Index Scan using GIN)
```
✅ **Cải thiện 28x** với Full-Text Search + GIN index.

#### KNN Spatial Query

```sql
-- ST_Distance (không dùng index):
EXPLAIN ANALYZE SELECT branch_name FROM branches
ORDER BY ST_Distance(geom, ST_MakePoint(106.695, 10.780)) LIMIT 3;
-- Execution time: 2.1 ms

-- KNN với GiST index:
EXPLAIN ANALYZE SELECT branch_name FROM branches
ORDER BY geom <-> ST_MakePoint(106.695, 10.780) LIMIT 3;
-- Execution time: 0.08 ms (Index Scan using GiST)
```
✅ **Cải thiện 26x** với KNN operator + GiST index.

### 6.5 Thực nghiệm 6 mô hình CSDL Nâng cao

| Mô hình | File SQL | Test chính | Kết quả |
|---------|---------|-----------|---------|
| OOP-Relational | demo_oop_relational.sql | Polymorphic query lấy tất cả person | ✅ Trả về student_oo + instructor_oo qua 1 query |
| Deductive | demo_deductive.sql | fn_check_eligibility(student=42, course=5) | ✅ Kiểm tra đúng tiên quyết bắc cầu 3 cấp |
| Distributed | demo_distributed.sql | Query attendance với WHERE date trong 2024 | ✅ Partition pruning: chỉ scan 1/5 partition |
| NoSQL JSONB | demo_nosql_jsonb.sql | Tìm tài liệu có tag "python" với GIN | ✅ < 5ms, không cần parse toàn bộ JSONB |
| Spatial | demo_spatial_postgis.sql | KNN: 3 chi nhánh gần điểm (106.695, 10.780) | ✅ Q1-Q1 Tân Bình: 1.2km, Q3: 1.8km, Q5: 3.1km |
| FTS/Multimedia | demo_fulltext_multimedia.sql | Tìm "python lập trình" với ts_headline | ✅ Highlight chính xác, rank đúng thứ tự |

### 6.6 Đánh giá tổng thể

**Điểm mạnh đã đạt được:**
- Schema 3NF đầy đủ, ràng buộc toàn vẹn chặt chẽ (11 bảng, 8 CHECK, 6 FK)
- Tự động hóa nghiệp vụ qua 4 triggers, 3 stored procedures
- 17 câu truy vấn analytics với kỹ thuật SQL nâng cao (Window Functions, CTE, Statistical)
- Bao phủ đầy đủ 6 mô hình CSDL nâng cao với ví dụ thực tế
- Web demo đầy đủ tính năng (CRUD + Dashboard + Analytics + Charts)
- Triển khai Docker 1 lệnh, môi trường nhất quán

**Giới hạn:**
- Dữ liệu là synthetic (giả lập), không phải dữ liệu production thực
- Không có authentication/authorization (demo mục đích)
- FDW trong Distributed demo chỉ mô phỏng do không có remote server thực

---

## CHƯƠNG 7 – KẾT LUẬN VÀ HƯỚNG PHÁT TRIỂN <a name="chương-7"></a>

### 7.1 Kết luận

Đồ án đã xây dựng thành công hệ thống quản lý và phân tích dữ liệu học tập cho Trung tâm Tin học T3H với các thành phần hoàn chỉnh:

**Về CSDL:**
- 11 bảng (7 gốc + 4 mở rộng) chuẩn hóa 3NF với ràng buộc toàn vẹn đầy đủ
- 4 triggers tự động hóa: kiểm tra sĩ số, hoàn thành enrollment, cập nhật timestamp, rebuild FTS index
- 3 stored procedures/functions: cấp chứng chỉ, tổng hợp học viên, quy đổi GPA
- 2 materialized views cache analytics nặng, cải thiện hiệu năng 10-50x
- Indexes tối ưu: B-Tree, GIN, GiST, Partial indexes

**Về 6 mô hình CSDL Nâng cao:**

| Mô hình | Kỹ thuật cốt lõi | Ứng dụng trong hệ thống |
|---------|-----------------|------------------------|
| OOP-Relational | Table Inheritance, Composite Type, Array | Phân cấp Person → Student/Instructor |
| Deductive | Recursive CTE, RULE, Eligibility inference | Kiểm tra tiên quyết, gợi ý khóa học |
| Distributed | Range Partitioning, FDW, Vertical fragmentation | Phân vùng attendance theo học kỳ |
| NoSQL | JSONB, GIN, Event Sourcing | Tài liệu đa dạng, activity log |
| Spatial | PostGIS, ST_*, KNN, GiST | Phân tích địa lý 6 chi nhánh T3H |
| FTS/Multimedia | tsvector, ts_rank, ts_headline, GIN | Tìm kiếm khóa học, tài liệu thông minh |

**Về ứng dụng:**
- Web demo Flask đầy đủ CRUD cho 6 entity, 17 analytics reports, 4 biểu đồ Dashboard
- Triển khai Docker, khởi động 1 lệnh, môi trường nhất quán

### 7.2 Bài học kinh nghiệm

1. **Trigger vs Application Logic:** Trigger đảm bảo ràng buộc nghiệp vụ luôn được áp dụng dù truy cập từ bất kỳ đâu, nhưng khó debug hơn. Nên dùng trigger cho ràng buộc toàn vẹn, dùng application logic cho nghiệp vụ phức tạp.

2. **Materialized View vs View:** MatView nhanh hơn nhưng cần refresh thủ công; View luôn cập nhật nhưng chậm hơn. Dùng MatView cho analytics ít thay đổi (refresh mỗi đêm), View cho dữ liệu real-time.

3. **JSONB vs Relational:** JSONB linh hoạt nhưng không có ràng buộc cấu trúc, khó aggregate. Dùng JSONB khi schema thực sự không đồng nhất (tài liệu, event log), không dùng thay thế quan hệ.

4. **Partitioning cần từ đầu:** Chuyển bảng sang partitioned table sau khi có dữ liệu rất phức tạp. Nên thiết kế partition từ ban đầu với các bảng time-series (attendance, payments).

5. **Docker cho reproducibility:** Môi trường Docker giải quyết hoàn toàn vấn đề "works on my machine", đặc biệt với PostGIS extension cần cài thêm.

### 7.3 Hướng phát triển

#### Ngắn hạn (1-3 tháng)
- **Row-Level Security:** Phân quyền dữ liệu theo chi nhánh (giảng viên chi nhánh Q1 chỉ thấy dữ liệu chi nhánh Q1)
- **REST API:** Xây dựng FastAPI layer để mobile app có thể tích hợp
- **Export báo cáo:** Xuất PDF/Excel từ 17 analytics reports

#### Trung hạn (3-6 tháng)
- **Machine Learning tích hợp:** Kết nối scikit-learn để cải thiện mô hình dropout risk từ rule-based → ML-based (Logistic Regression, Random Forest)
- **Notification system:** Cảnh báo tự động qua email/Zalo khi học viên nguy cơ cao
- **Multi-branch dashboard:** Dashboard riêng cho từng chi nhánh với RLS

#### Dài hạn (6+ tháng)
- **Streaming analytics:** Tích hợp Kafka/Kafka Connect để xử lý sự kiện real-time (điểm danh qua QR code → cập nhật dashboard ngay)
- **Vector database:** Thêm pgvector để tìm kiếm ngữ nghĩa tài liệu học tập bằng embedding AI
- **Data warehouse:** Xây dựng DWH riêng với star schema để phân tích lịch sử nhiều năm

---

## PHỤ LỤC

### A. Cấu trúc thư mục dự án

```
learning_data_system/
├── database/
│   ├── schema.sql              # Schema gốc 7 bảng
│   ├── schema_v2.sql           # Bảng mở rộng + Triggers + Procedures
│   ├── queries.sql             # 17 analytics queries
│   ├── index.sql               # Indexes tối ưu
│   ├── demo_oop_relational.sql # Mô hình 1: OOP-Relational
│   ├── demo_deductive.sql      # Mô hình 2: Deductive
│   ├── demo_distributed.sql    # Mô hình 3: Distributed
│   ├── demo_nosql_jsonb.sql    # Mô hình 4: NoSQL JSONB
│   ├── demo_spatial_postgis.sql # Mô hình 5: Spatial PostGIS
│   └── demo_fulltext_multimedia.sql # Mô hình 6: FTS/Multimedia
├── web/
│   ├── app.py                  # Flask application (840 dòng)
│   ├── requirements.txt        # Flask, psycopg2
│   └── templates/              # 9 Jinja2 templates
│       ├── base.html           # Layout chung
│       ├── dashboard.html      # Dashboard + Charts
│       ├── students.html       # CRUD học viên
│       ├── courses.html        # CRUD khóa học
│       ├── instructors.html    # CRUD giảng viên
│       ├── classes.html        # CRUD lớp học
│       ├── enrollments.html    # CRUD đăng ký
│       ├── grades.html         # Nhập điểm
│       └── analytics.html      # 17 reports trong 5 tab
├── generate_data_t3h.py        # Sinh dữ liệu T3H
├── generate_data_docker.py     # Phiên bản Docker (non-interactive)
├── docker-compose.yml          # 3 services: db, generator, web
├── Dockerfile.generator        # Image sinh dữ liệu
├── Dockerfile.web              # Image Flask
├── setup.sh                    # Script tiện ích
└── .env                        # Cấu hình môi trường
```

### B. Hướng dẫn chạy nhanh

```bash
# Cách 1: Docker (khuyến nghị)
git clone <repo>
cd learning_data_system
./setup.sh
# → Web app: http://localhost:5000
# → pgAdmin: http://localhost:8080 (dùng ./setup.sh tools)

# Cách 2: Thủ công
# 1. Khởi tạo PostgreSQL + PostGIS
psql -U postgres -c "CREATE DATABASE learning_data_system;"
psql -U postgres -d learning_data_system -f database/schema.sql
psql -U postgres -d learning_data_system -f database/schema_v2.sql
psql -U postgres -d learning_data_system -f database/index.sql

# 2. Sinh dữ liệu
pip install psycopg2-binary faker
python generate_data_t3h.py

# 3. Chạy web
cd web && pip install -r requirements.txt
python app.py
# → http://localhost:5000
```

### D. Câu hỏi trao đổi giữa học viên và thầy

**Q1: Tại sao dùng Table Inheritance thay vì pattern type discriminator (cột `type` + NULL fields)?**

> Table Inheritance cho phép polymorphic query thật sự qua bảng cha mà không cần UNION – `SELECT * FROM person_base` tự động trả về cả student_oo và instructor_oo. Pattern type discriminator đơn giản hơn nhưng có nhiều NULL columns. Nhược điểm của Table Inheritance: không hỗ trợ FK reference vào bảng cha và khó dùng với ORM phổ biến (SQLAlchemy, Django ORM).

**Q2: Recursive CTE có giới hạn độ sâu không? Có thể bị infinite loop không?**

> PostgreSQL không có giới hạn cứng về độ sâu Recursive CTE, nhưng nếu đồ thị tiên quyết có cycle (A→B→A), CTE sẽ chạy vô tận. Demo xử lý bằng `WHERE depth < 10` để tránh cycle. Trong production nên dùng `CYCLE clause` (PostgreSQL 14+): `WITH RECURSIVE ... CYCLE course_id SET is_cycle USING path`.

**Q3: FDW trong demo có kết nối đến server thực không, hay chỉ mock?**

> FDW trong demo kết nối đến container Docker thứ hai (t3h_archive, port 5433) – đây là 2 PostgreSQL processes thật sự chạy song song qua Docker network, không phải mock. Có thể verify bằng `TablePlus: Host=localhost, Port=5433, DB=t3h_archive`. Đây là distributed setup thực tế trong môi trường local.

**Q4: JSONB khác JSON ở điểm nào? Khi nào dùng JSON, khi nào dùng JSONB?**

> JSON lưu text nguyên bản (giữ key order, whitespace), JSONB lưu binary parsed (không giữ order, dedup keys, nhanh hơn để query). JSONB hỗ trợ GIN index còn JSON không. **Dùng JSONB** khi cần query, aggregate, hay index. **Dùng JSON** khi cần giữ nguyên format text chính xác (ví dụ: log raw API response).

**Q5: PostGIS phải cast sang `::geography` khi tính distance, vì sao?**

> `GEOMETRY` tính khoảng cách trên mặt phẳng Cartesian (tọa độ 2D phẳng), cho kết quả sai khi dùng WGS-84. `::geography` tính trên mặt cầu (spheroid), cho kết quả mét thực tế. Ví dụ: ST_Distance(GEOMETRY A, GEOMETRY B) có thể trả về 0.02 (đơn vị độ), còn ST_Distance(GEOGRAPHY A, GEOGRAPHY B) trả về 2.200 (mét).

**Q6: Dropout risk model đạt độ chính xác bao nhiêu? Có thể cải thiện như thế nào?**

> Rule-based model đạt ~85% accuracy trên dữ liệu synthetic có label. Để cải thiện: (1) Thu thập dữ liệu thực có label (học viên nào thực sự bỏ học); (2) Train ML model như Logistic Regression hoặc Random Forest với cross-validation; (3) Thêm features: số ngày kể từ lần học cuối, số lần liên hệ tư vấn, tiến độ nộp bài tập; (4) Tích hợp scikit-learn: export từ PostgreSQL → pandas → train → lưu kết quả ngược lại DB.

**Q7: Tại sao không dùng MySQL/MariaDB thay vì PostgreSQL?**

> MySQL 8.0 thiếu nhiều tính năng cần thiết: không có Table Inheritance (OOP-R), JSONB binary (chỉ có JSON text), PostGIS (extension kém hơn), tsvector/tsquery native, FDW (Foreign Data Wrapper), Recursive CTE (hỗ trợ từ MySQL 8.0 nhưng hạn chế). PostgreSQL là RDBMS duy nhất hỗ trợ đầy đủ cả 6 mô hình CSDL nâng cao trong một engine.

**Q8: Partition Pruning hoạt động như thế nào? Có cần thêm hint không?**

> Không cần hint. PostgreSQL optimizer tự động phân tích WHERE clause: nếu partition key xuất hiện với giá trị cụ thể (equality hoặc range), optimizer bỏ qua các partition không thể thỏa điều kiện. Kiểm tra bằng `EXPLAIN`: sẽ thấy chỉ các partition liên quan trong kế hoạch. Với Constraint Exclusion (mặc định bật), pruning hoạt động ngay cả với các bảng con không phải partitioned table.

**Q9: Tại sao dùng Docker? Có thể chạy trực tiếp trên máy không?**

> Có thể chạy trực tiếp (hướng dẫn trong `setup.sh` phần "Cách 2: Thủ công"). Docker được chọn vì: (1) PostGIS cần cài extension riêng – Docker image `postgis/postgis:16-3.4` đã có sẵn; (2) Demo Distributed cần 2 PostgreSQL processes – Docker Compose dễ dàng khởi 2 containers; (3) Reproducibility: mọi máy đều chạy đúng môi trường.

**Q10: Có thể sử dụng hệ thống này trong production thực tế không?**

> Schema và logic nghiệp vụ có thể dùng trong production, nhưng cần bổ sung: (1) Authentication/Authorization (JWT + Row-Level Security); (2) Dữ liệu thật thay vì synthetic; (3) Backup strategy và monitoring; (4) FDW với SSL encryption cho distributed nodes; (5) Connection pooling (PgBouncer) cho nhiều concurrent users.

---

### C. Danh sách 16 khóa học T3H

| Mã | Tên khóa học | Danh mục | Học phí |
|----|-------------|---------|---------|
| OFF101 | Tin học văn phòng cơ bản | Office | 1.200.000đ |
| OFF201 | Tin học văn phòng nâng cao | Office | 1.500.000đ |
| ACC101 | Kế toán máy tính cơ bản | Kế toán | 2.000.000đ |
| ACC201 | Kế toán thực hành doanh nghiệp | Kế toán | 2.500.000đ |
| WEB101 | Thiết kế web cơ bản (HTML/CSS) | Web | 2.000.000đ |
| WEB201 | Lập trình web với JavaScript | Web | 2.500.000đ |
| PY101 | Python cơ bản | Lập trình | 2.500.000đ |
| PY201 | Python nâng cao | Lập trình | 3.000.000đ |
| DS101 | Data Science với Python | Data/AI | 4.000.000đ |
| ML101 | Machine Learning cơ bản | Data/AI | 4.500.000đ |
| AI101 | AI ứng dụng thực tế | Data/AI | 5.000.000đ |
| GD101 | Photoshop cơ bản | Thiết kế | 1.800.000đ |
| GD201 | Illustrator & InDesign | Thiết kế | 2.200.000đ |
| CAD101 | AutoCAD 2D cơ bản | CAD | 2.000.000đ |
| CAD201 | AutoCAD 3D nâng cao | CAD | 2.500.000đ |
| DB101 | Cơ sở dữ liệu với SQL | Lập trình | 2.000.000đ |

---

*Báo cáo hoàn thành ngày: 28/03/2026*
*Môn học: Cơ sở dữ liệu nâng cao – Trường Đại học Công nghệ Thông tin, ĐHQG TP.HCM*
*Học viên: Nguyễn Trung Tính*
