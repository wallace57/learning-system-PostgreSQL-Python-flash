-- ============================================================================
-- CSDL QUAN HỆ - ĐỐI TƯỢNG (Object-Relational Database)
-- PostgreSQL hỗ trợ đầy đủ mô hình OO:
--   Domain, Composite Type, Enum, Array, Table Inheritance, Row Functions
-- Ref: PostgreSQL Object-Relational Features (Chapter 8, 5 - PostgreSQL Docs)
-- ============================================================================

-- ── 1. DOMAIN – Kiểu vô hướng tùy chỉnh với ràng buộc ─────────────────────
-- Domain giống "class với validation" trong OOP
-- PostgreSQL không hỗ trợ CREATE DOMAIN IF NOT EXISTS → dùng DO block
DO $$ BEGIN
    CREATE DOMAIN score_t AS NUMERIC(5,2)
        CHECK (VALUE >= 0 AND VALUE <= 100)
        NOT NULL;
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

DO $$ BEGIN
    CREATE DOMAIN vn_phone_t AS VARCHAR(15)
        CHECK (VALUE ~ '^(0[3-9][0-9]{8})$');
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

DO $$ BEGIN
    CREATE DOMAIN positive_int_t AS INTEGER
        CHECK (VALUE > 0);
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

COMMENT ON DOMAIN score_t     IS 'Điểm số hợp lệ trong khoảng 0–100';
COMMENT ON DOMAIN vn_phone_t  IS 'Số điện thoại VN đúng định dạng';

-- ── 2. COMPOSITE TYPE – Kiểu bản ghi cấu trúc ────────────────────────────
-- Giống "struct" / "class" trong các ngôn ngữ OOP
DO $$ BEGIN
    CREATE TYPE address_t AS (
        street   VARCHAR(200),
        district VARCHAR(50),
        city     VARCHAR(50)
    );
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

DO $$ BEGIN
    CREATE TYPE contact_t AS (
        email      VARCHAR(100),
        phone      vn_phone_t,
        zalo       VARCHAR(15),
        links      JSONB
    );
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

DO $$ BEGIN
    CREATE TYPE grade_summary_t AS (
        midterm    NUMERIC(5,2),
        final      NUMERIC(5,2),
        project    NUMERIC(5,2),
        weighted   NUMERIC(5,2)
    );
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

-- ── 3. ENUM TYPE – Kiểu liệt kê tường minh ───────────────────────────────
DO $$ BEGIN
    CREATE TYPE skill_level_t AS ENUM ('Beginner','Intermediate','Advanced','Expert');
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

DO $$ BEGIN
    CREATE TYPE day_of_week_t AS ENUM ('Mon','Tue','Wed','Thu','Fri','Sat','Sun');
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

-- ── 4. TABLE INHERITANCE – Kế thừa bảng ─────────────────────────────────
-- Base table: person (lớp cha)
CREATE TABLE IF NOT EXISTS person_base (
    person_id   SERIAL PRIMARY KEY,
    full_name   VARCHAR(100)   NOT NULL,
    dob         DATE,
    gender      VARCHAR(10),
    contact     contact_t,
    home_addr   address_t,
    created_at  TIMESTAMP      DEFAULT CURRENT_TIMESTAMP
);

-- Student inherits Person (lớp con 1)
CREATE TABLE IF NOT EXISTS student_oo (
    student_code VARCHAR(20)    UNIQUE NOT NULL,
    major        VARCHAR(100),
    gpa          DOUBLE PRECISION DEFAULT 0.0,
    -- ARRAY type: danh sách kỹ năng đã học
    skills       TEXT[],
    -- ARRAY type: chứng chỉ đã có
    certifications VARCHAR(100)[]
) INHERITS (person_base);

-- Instructor inherits Person (lớp con 2)
CREATE TABLE IF NOT EXISTS instructor_oo (
    employee_code   VARCHAR(20)    UNIQUE NOT NULL,
    specialization  VARCHAR(100),
    teaching_level  skill_level_t  DEFAULT 'Intermediate',
    -- ARRAY: ngày trong tuần có thể dạy
    available_days  day_of_week_t[],
    hourly_rate     NUMERIC(10,2)
) INHERITS (person_base);

COMMENT ON TABLE person_base    IS 'Lớp cha – thông tin người dùng chung (OO Inheritance)';
COMMENT ON TABLE student_oo     IS 'Lớp con Student kế thừa person_base';
COMMENT ON TABLE instructor_oo  IS 'Lớp con Instructor kế thừa person_base';

-- ── 5. Dữ liệu mẫu OO ────────────────────────────────────────────────────
INSERT INTO student_oo
    (student_code, full_name, dob, gender, major, gpa, skills, certifications,
     contact, home_addr)
VALUES
    ('HV2024001','Nguyễn Văn Minh','2001-05-12','Nam','Công nghệ thông tin',3.2,
     ARRAY['Python','SQL','HTML/CSS'],
     ARRAY['MOS Excel 2019','Python Basics Certificate'],
     ROW('minh.nv001@gmail.com','0901234567','0901234567','{"linkedin":"linkedin.com/minh"}'::JSONB)::contact_t,
     ROW('123 Nguyễn Thị Minh Khai','Quận 3','TP.HCM')::address_t),
    ('HV2024002','Trần Thị Hương','2002-08-20','Nữ','Kế toán',3.5,
     ARRAY['Excel','MISA','PowerBI'],
     ARRAY['Chứng chỉ kế toán hành chính','MOS Word'],
     ROW('huong.tt002@yahoo.com','0912345678','0912345678',NULL::JSONB)::contact_t,
     ROW('456 Điện Biên Phủ','Quận Bình Thạnh','TP.HCM')::address_t)
ON CONFLICT DO NOTHING;

INSERT INTO instructor_oo
    (employee_code, full_name, dob, gender, specialization, teaching_level,
     available_days, hourly_rate, contact, home_addr)
VALUES
    ('GV001','Lê Đức Khoa','1985-03-15','Nam','Python & Data Science','Expert',
     ARRAY['Mon','Wed','Fri','Sat']::day_of_week_t[],350000,
     ROW('khoa.ld.gv01@t3h.edu.vn','0933111222','0933111222',
         '{"linkedin":"linkedin.com/khoale"}'::JSONB)::contact_t,
     ROW('789 Cộng Hòa','Quận Tân Bình','TP.HCM')::address_t),
    ('GV002','Phạm Ngọc Lan','1990-07-22','Nữ','Kế toán & MISA','Advanced',
     ARRAY['Tue','Thu','Sat','Sun']::day_of_week_t[],280000,
     ROW('lan.pn.gv02@t3h.edu.vn','0944222333','0944222333',NULL::JSONB)::contact_t,
     ROW('12 Nguyễn Oanh','Quận Gò Vấp','TP.HCM')::address_t)
ON CONFLICT DO NOTHING;

-- ── 6. Object-Relational Queries ─────────────────────────────────────────

-- Q1: Truy cập thuộc tính của composite type
SELECT student_code, full_name,
       (contact).email          AS email,
       (home_addr).district     AS district,
       gpa,
       array_length(skills,1)   AS skill_count
FROM student_oo;

-- Q2: Tìm học viên có kỹ năng Python (ANY trên ARRAY)
SELECT student_code, full_name, skills
FROM student_oo
WHERE 'Python' = ANY(skills);

-- Q3: Tìm giảng viên dạy vào cuối tuần
SELECT employee_code, full_name, available_days,
       teaching_level::TEXT AS level
FROM instructor_oo
WHERE 'Sat' = ANY(available_days) OR 'Sun' = ANY(available_days);

-- Q4: Polymorphic query – lấy tất cả "person" (cả student + instructor)
-- Đây là tính năng Inheritance – truy vấn lớp cha lấy cả lớp con
SELECT person_id, full_name, (contact).email,
       CASE WHEN tableoid = 'student_oo'::regclass    THEN 'Học viên'
            WHEN tableoid = 'instructor_oo'::regclass THEN 'Giảng viên'
            ELSE 'Khác' END AS role
FROM person_base
ORDER BY role, full_name;

-- Q5: Array operations – thêm kỹ năng mới
-- UPDATE student_oo SET skills = skills || ARRAY['React.js'] WHERE student_code='HV2024001';

-- Q6: Unnest array – mở rộng array thành rows (cho GROUP BY)
SELECT full_name, unnest(skills) AS skill
FROM student_oo
ORDER BY full_name, skill;

-- ── 7. Function trả về composite type ────────────────────────────────────
CREATE OR REPLACE FUNCTION fn_get_grade_summary(p_enrollment_id INTEGER)
RETURNS grade_summary_t AS $$
DECLARE result grade_summary_t;
BEGIN
    SELECT
        MAX(CASE WHEN assessment_type='Midterm' THEN score END),
        MAX(CASE WHEN assessment_type='Final'   THEN score END),
        MAX(CASE WHEN assessment_type='Project' THEN score END),
        ROUND(SUM(score*weight)/NULLIF(SUM(weight),0),2)
    INTO result.midterm, result.final, result.project, result.weighted
    FROM grades WHERE enrollment_id = p_enrollment_id;
    RETURN result;
END;
$$ LANGUAGE plpgsql;

-- Gọi function trả về composite type
SELECT e.enrollment_id,
       s.first_name||' '||s.last_name AS student,
       c.course_name,
       (fn_get_grade_summary(e.enrollment_id)).midterm   AS midterm,
       (fn_get_grade_summary(e.enrollment_id)).final     AS final,
       (fn_get_grade_summary(e.enrollment_id)).weighted  AS weighted_avg
FROM enrollments e
JOIN students s ON e.student_id=s.student_id
JOIN classes cl ON e.class_id=cl.class_id
JOIN courses c  ON cl.course_id=c.course_id
WHERE e.status='Completed'
LIMIT 10;

-- ============================================================================
-- END: CSDL Quan hệ-Đối tượng
-- ============================================================================
