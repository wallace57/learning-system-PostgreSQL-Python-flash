-- ============================================================================
-- Learning Data Management System – Schema V2 (Nâng cấp Master's Level)
-- Trung tâm Tin học T3H – TP. Hồ Chí Minh
-- ============================================================================
-- Bổ sung: Bảng payments, feedback, certificates, audit_log
--          Triggers tự động cập nhật trạng thái
--          Stored procedures nghiệp vụ
--          Materialized Views tăng hiệu năng analytics
--          Indexes tối ưu truy vấn
-- ============================================================================

-- ============================================================================
-- BẢNG MỞ RỘNG 1: PAYMENTS – Theo dõi thanh toán học phí
-- ============================================================================
CREATE TABLE IF NOT EXISTS payments (
    payment_id      SERIAL PRIMARY KEY,
    enrollment_id   INTEGER         NOT NULL,
    student_id      INTEGER         NOT NULL,
    amount          NUMERIC(12,2)   NOT NULL CHECK (amount > 0),
    payment_date    DATE            NOT NULL DEFAULT CURRENT_DATE,
    payment_method  VARCHAR(30)     NOT NULL DEFAULT 'Cash'
                    CHECK (payment_method IN ('Cash','Bank Transfer','Card','Momo','ZaloPay','VNPay')),
    status          VARCHAR(20)     NOT NULL DEFAULT 'Paid'
                    CHECK (status IN ('Paid','Pending','Refunded','Partial')),
    discount_pct    NUMERIC(5,2)    DEFAULT 0 CHECK (discount_pct >= 0 AND discount_pct <= 100),
    receipt_no      VARCHAR(30)     UNIQUE,
    notes           TEXT,
    created_at      TIMESTAMP       NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at      TIMESTAMP       NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_payments_enrollment
        FOREIGN KEY (enrollment_id) REFERENCES enrollments(enrollment_id)
        ON UPDATE CASCADE ON DELETE RESTRICT,
    CONSTRAINT fk_payments_student
        FOREIGN KEY (student_id) REFERENCES students(student_id)
        ON UPDATE CASCADE ON DELETE RESTRICT
);

COMMENT ON TABLE payments IS 'Lịch sử thanh toán học phí của học viên';
CREATE INDEX IF NOT EXISTS idx_payments_student ON payments(student_id);
CREATE INDEX IF NOT EXISTS idx_payments_date ON payments(payment_date);

-- ============================================================================
-- BẢNG MỞ RỘNG 2: FEEDBACK – Đánh giá khóa học và giảng viên
-- ============================================================================
CREATE TABLE IF NOT EXISTS feedback (
    feedback_id         SERIAL PRIMARY KEY,
    enrollment_id       INTEGER         NOT NULL,
    rating_course       INTEGER         NOT NULL CHECK (rating_course BETWEEN 1 AND 5),
    rating_instructor   INTEGER         NOT NULL CHECK (rating_instructor BETWEEN 1 AND 5),
    rating_facility     INTEGER         DEFAULT 3 CHECK (rating_facility BETWEEN 1 AND 5),
    comment             TEXT,
    is_anonymous        BOOLEAN         NOT NULL DEFAULT FALSE,
    created_at          TIMESTAMP       NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_feedback_enrollment
        FOREIGN KEY (enrollment_id) REFERENCES enrollments(enrollment_id)
        ON UPDATE CASCADE ON DELETE CASCADE,
    CONSTRAINT uq_feedback_enrollment UNIQUE (enrollment_id)
);

COMMENT ON TABLE feedback IS 'Đánh giá khóa học và giảng viên từ học viên';
CREATE INDEX IF NOT EXISTS idx_feedback_rating ON feedback(rating_course, rating_instructor);

-- ============================================================================
-- BẢNG MỞ RỘNG 3: CERTIFICATES – Chứng chỉ hoàn thành khóa học
-- ============================================================================
CREATE TABLE IF NOT EXISTS certificates (
    cert_id         SERIAL PRIMARY KEY,
    enrollment_id   INTEGER         NOT NULL UNIQUE,
    student_id      INTEGER         NOT NULL,
    course_id       INTEGER         NOT NULL,
    cert_number     VARCHAR(50)     NOT NULL UNIQUE,
    issue_date      DATE            NOT NULL DEFAULT CURRENT_DATE,
    grade_letter    VARCHAR(5)      NOT NULL CHECK (grade_letter IN ('A+','A','B+','B','C+','C','D','F')),
    final_score     NUMERIC(5,2)    NOT NULL,
    is_valid        BOOLEAN         NOT NULL DEFAULT TRUE,
    expires_at      DATE,
    created_at      TIMESTAMP       NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_cert_enrollment
        FOREIGN KEY (enrollment_id) REFERENCES enrollments(enrollment_id)
        ON UPDATE CASCADE ON DELETE RESTRICT,
    CONSTRAINT fk_cert_student
        FOREIGN KEY (student_id) REFERENCES students(student_id)
        ON UPDATE CASCADE ON DELETE RESTRICT,
    CONSTRAINT fk_cert_course
        FOREIGN KEY (course_id) REFERENCES courses(course_id)
        ON UPDATE CASCADE ON DELETE RESTRICT
);

COMMENT ON TABLE certificates IS 'Chứng chỉ cấp cho học viên hoàn thành khóa học';
CREATE INDEX IF NOT EXISTS idx_certs_student ON certificates(student_id);
CREATE INDEX IF NOT EXISTS idx_certs_course ON certificates(course_id);

-- ============================================================================
-- BẢNG MỞ RỘNG 4: AUDIT_LOG – Ghi lại thay đổi quan trọng
-- ============================================================================
CREATE TABLE IF NOT EXISTS audit_log (
    log_id      SERIAL PRIMARY KEY,
    table_name  VARCHAR(50) NOT NULL,
    operation   VARCHAR(10) NOT NULL CHECK (operation IN ('INSERT','UPDATE','DELETE')),
    record_id   INTEGER     NOT NULL,
    old_data    JSONB,
    new_data    JSONB,
    changed_by  VARCHAR(100) DEFAULT current_user,
    changed_at  TIMESTAMP   NOT NULL DEFAULT CURRENT_TIMESTAMP
);

COMMENT ON TABLE audit_log IS 'Nhật ký thay đổi dữ liệu (audit trail)';
CREATE INDEX IF NOT EXISTS idx_audit_table ON audit_log(table_name, record_id);
CREATE INDEX IF NOT EXISTS idx_audit_time  ON audit_log(changed_at DESC);


-- ============================================================================
-- TRIGGER FUNCTION: Tự động cập nhật updated_at
-- ============================================================================
CREATE OR REPLACE FUNCTION fn_set_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at := CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Áp dụng trigger updated_at cho tất cả các bảng chính
DO $$
DECLARE tbl TEXT;
BEGIN
    FOREACH tbl IN ARRAY ARRAY['students','courses','instructors','classes','enrollments','grades','payments']
    LOOP
        EXECUTE format('
            CREATE OR REPLACE TRIGGER trg_%s_updated_at
            BEFORE UPDATE ON %s
            FOR EACH ROW EXECUTE FUNCTION fn_set_updated_at();
        ', tbl, tbl);
    END LOOP;
END $$;


-- ============================================================================
-- TRIGGER: Tự động cập nhật trạng thái enrollment khi điểm cuối kỳ >= 50
-- ============================================================================
CREATE OR REPLACE FUNCTION fn_auto_complete_enrollment()
RETURNS TRIGGER AS $$
DECLARE
    weighted_avg NUMERIC;
BEGIN
    -- Tính điểm tổng kết khi có đủ điểm Midterm + Final
    SELECT ROUND(SUM(score * weight) / NULLIF(SUM(weight),0), 2)
    INTO weighted_avg
    FROM grades
    WHERE enrollment_id = NEW.enrollment_id;

    -- Nếu điểm >= 50 và là Final, tự động Completed
    IF NEW.assessment_type = 'Final' AND weighted_avg IS NOT NULL AND weighted_avg >= 50 THEN
        UPDATE enrollments
        SET status = 'Completed', completion_date = CURRENT_DATE
        WHERE enrollment_id = NEW.enrollment_id AND status = 'Enrolled';
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE TRIGGER trg_grades_auto_complete
AFTER INSERT OR UPDATE ON grades
FOR EACH ROW EXECUTE FUNCTION fn_auto_complete_enrollment();


-- ============================================================================
-- TRIGGER: Ghi audit log khi xóa học viên / giảng viên
-- ============================================================================
CREATE OR REPLACE FUNCTION fn_audit_delete()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO audit_log (table_name, operation, record_id, old_data)
    VALUES (TG_TABLE_NAME, 'DELETE', OLD.student_id,
            to_jsonb(OLD));
    RETURN OLD;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE TRIGGER trg_audit_students_delete
BEFORE DELETE ON students
FOR EACH ROW EXECUTE FUNCTION fn_audit_delete();


-- ============================================================================
-- TRIGGER: Kiểm tra sĩ số khi đăng ký mới
-- ============================================================================
CREATE OR REPLACE FUNCTION fn_check_class_capacity()
RETURNS TRIGGER AS $$
DECLARE
    cur_enrolled INTEGER;
    max_cap      INTEGER;
BEGIN
    SELECT max_students INTO max_cap FROM classes WHERE class_id = NEW.class_id;
    SELECT COUNT(*) INTO cur_enrolled
    FROM enrollments
    WHERE class_id = NEW.class_id AND status NOT IN ('Dropped','Withdrawn');

    IF cur_enrolled >= max_cap THEN
        RAISE EXCEPTION 'Lớp học đã đủ sĩ số tối đa (% học viên)', max_cap;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE TRIGGER trg_enrollment_capacity
BEFORE INSERT ON enrollments
FOR EACH ROW EXECUTE FUNCTION fn_check_class_capacity();


-- ============================================================================
-- STORED PROCEDURE: Tính điểm chữ tự động và cấp chứng chỉ
-- ============================================================================
CREATE OR REPLACE FUNCTION fn_issue_certificate(p_enrollment_id INTEGER)
RETURNS TEXT AS $$
DECLARE
    v_final_score   NUMERIC;
    v_grade_letter  VARCHAR(5);
    v_student_id    INTEGER;
    v_course_id     INTEGER;
    v_cert_no       VARCHAR(50);
    v_status        VARCHAR(20);
BEGIN
    -- Kiểm tra enrollment đã Completed chưa
    SELECT status, student_id INTO v_status, v_student_id
    FROM enrollments WHERE enrollment_id = p_enrollment_id;

    IF v_status != 'Completed' THEN
        RETURN 'Lỗi: Enrollment chưa hoàn thành (status: ' || v_status || ')';
    END IF;

    -- Lấy course_id
    SELECT c.course_id INTO v_course_id
    FROM enrollments e JOIN classes c ON e.class_id = c.class_id
    WHERE e.enrollment_id = p_enrollment_id;

    -- Tính điểm tổng kết
    SELECT ROUND(SUM(score * weight) / NULLIF(SUM(weight),0), 2)
    INTO v_final_score
    FROM grades WHERE enrollment_id = p_enrollment_id;

    IF v_final_score IS NULL THEN
        RETURN 'Lỗi: Chưa có điểm số';
    END IF;

    -- Xếp loại
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

    IF v_grade_letter = 'F' THEN
        RETURN 'Không đủ điều kiện cấp chứng chỉ (điểm: ' || v_final_score || ')';
    END IF;

    -- Tạo số chứng chỉ
    v_cert_no := 'T3H-' || TO_CHAR(CURRENT_DATE,'YYYY') || '-' || LPAD(p_enrollment_id::TEXT, 6, '0');

    -- Insert hoặc cập nhật chứng chỉ
    INSERT INTO certificates (enrollment_id, student_id, course_id, cert_number, grade_letter, final_score)
    VALUES (p_enrollment_id, v_student_id, v_course_id, v_cert_no, v_grade_letter, v_final_score)
    ON CONFLICT (enrollment_id) DO UPDATE
    SET grade_letter = EXCLUDED.grade_letter,
        final_score  = EXCLUDED.final_score,
        issue_date   = CURRENT_DATE;

    RETURN 'Đã cấp chứng chỉ ' || v_cert_no || ' – Xếp loại: ' || v_grade_letter || ' (' || v_final_score || ')';
END;
$$ LANGUAGE plpgsql;


-- ============================================================================
-- STORED PROCEDURE: Thống kê tổng quan một học viên
-- ============================================================================
CREATE OR REPLACE FUNCTION fn_student_summary(p_student_id INTEGER)
RETURNS TABLE(
    metric VARCHAR(50),
    value  TEXT
) AS $$
BEGIN
    RETURN QUERY
    WITH stats AS (
        SELECT
            COUNT(DISTINCT e.enrollment_id)                        AS total_enrollments,
            COUNT(CASE WHEN e.status='Completed' THEN 1 END)       AS completed,
            COUNT(CASE WHEN e.status='Dropped' THEN 1 END)         AS dropped,
            ROUND(AVG(g.score),2)                                   AS avg_score,
            COUNT(CASE WHEN a.status='Present' THEN 1 END)         AS present,
            COUNT(a.attendance_id)                                  AS total_sessions,
            ROUND(COUNT(CASE WHEN a.status='Present' THEN 1 END)*100.0
                  /NULLIF(COUNT(a.attendance_id),0),1)              AS att_rate,
            COALESCE(SUM(p.amount),0)                               AS paid
        FROM enrollments e
        LEFT JOIN grades g ON e.enrollment_id=g.enrollment_id
        LEFT JOIN attendance a ON e.enrollment_id=a.enrollment_id
        LEFT JOIN payments p ON e.student_id=p.student_id
        WHERE e.student_id = p_student_id
    )
    SELECT 'Tổng đăng ký'::VARCHAR(50), total_enrollments::TEXT FROM stats UNION ALL
    SELECT 'Hoàn thành', completed::TEXT FROM stats UNION ALL
    SELECT 'Bỏ học', dropped::TEXT FROM stats UNION ALL
    SELECT 'Điểm TB', avg_score::TEXT FROM stats UNION ALL
    SELECT 'Tỷ lệ chuyên cần (%)', att_rate::TEXT FROM stats UNION ALL
    SELECT 'Tổng học phí đã nộp (đ)', TO_CHAR(paid,'FM999,999,999') FROM stats;
END;
$$ LANGUAGE plpgsql;


-- ============================================================================
-- MATERIALIZED VIEW: Thống kê tổng hợp học viên (dùng cho analytics)
-- ============================================================================
CREATE MATERIALIZED VIEW IF NOT EXISTS mv_student_stats AS
SELECT
    s.student_id,
    s.first_name || ' ' || s.last_name AS full_name,
    s.email, s.status AS student_status,
    COUNT(DISTINCT e.enrollment_id)                             AS total_enrollments,
    COUNT(CASE WHEN e.status='Completed' THEN 1 END)            AS completed_courses,
    ROUND(AVG(g.score),2)                                        AS avg_score,
    ROUND(COUNT(CASE WHEN a.status='Present' THEN 1 END)*100.0
          /NULLIF(COUNT(a.attendance_id),0),1)                  AS attendance_rate,
    CASE WHEN ROUND(COUNT(CASE WHEN a.status='Present' THEN 1 END)*100.0
                   /NULLIF(COUNT(a.attendance_id),0),1) < 70
              OR ROUND(AVG(g.score),2) < 55
         THEN TRUE ELSE FALSE END                                AS is_at_risk
FROM students s
LEFT JOIN enrollments e  ON s.student_id=e.student_id
LEFT JOIN grades g       ON e.enrollment_id=g.enrollment_id
LEFT JOIN attendance a   ON e.enrollment_id=a.enrollment_id
GROUP BY s.student_id, s.first_name, s.last_name, s.email, s.status;

CREATE UNIQUE INDEX IF NOT EXISTS idx_mv_student_stats ON mv_student_stats(student_id);

COMMENT ON MATERIALIZED VIEW mv_student_stats IS
  'Thống kê tổng hợp học viên – REFRESH MATERIALIZED VIEW mv_student_stats để cập nhật';


-- ============================================================================
-- MATERIALIZED VIEW: Thống kê doanh thu theo khóa học và học kỳ
-- ============================================================================
CREATE MATERIALIZED VIEW IF NOT EXISTS mv_revenue_stats AS
SELECT
    c.category, c.course_code, c.course_name, c.level,
    cl.semester, cl.academic_year,
    COUNT(DISTINCT e.enrollment_id)                             AS enrollments,
    c.tuition_fee,
    c.tuition_fee * COUNT(DISTINCT e.enrollment_id)             AS gross_revenue,
    ROUND(AVG(g.score),2)                                        AS avg_score,
    COUNT(CASE WHEN e.status='Completed' THEN 1 END)*100.0
        /NULLIF(COUNT(e.enrollment_id),0)                       AS completion_rate
FROM courses c
JOIN classes cl     ON c.course_id=cl.course_id
JOIN enrollments e  ON cl.class_id=e.class_id AND e.status!='Dropped'
LEFT JOIN grades g  ON e.enrollment_id=g.enrollment_id
GROUP BY c.category,c.course_code,c.course_name,c.level,c.tuition_fee,cl.semester,cl.academic_year;

COMMENT ON MATERIALIZED VIEW mv_revenue_stats IS 'Thống kê doanh thu và kết quả học tập theo học kỳ';


-- ============================================================================
-- VIEW: Học viên rủi ro cao (sử dụng thường xuyên)
-- ============================================================================
CREATE OR REPLACE VIEW v_at_risk_students AS
SELECT * FROM mv_student_stats WHERE is_at_risk = TRUE ORDER BY avg_score ASC;

-- ============================================================================
-- FUNCTION: Tính GPA theo thang 4.0
-- ============================================================================
CREATE OR REPLACE FUNCTION fn_gpa_4scale(p_score NUMERIC)
RETURNS NUMERIC AS $$
BEGIN
    RETURN CASE
        WHEN p_score >= 93 THEN 4.0
        WHEN p_score >= 85 THEN 3.7
        WHEN p_score >= 80 THEN 3.3
        WHEN p_score >= 75 THEN 3.0
        WHEN p_score >= 70 THEN 2.7
        WHEN p_score >= 65 THEN 2.3
        WHEN p_score >= 60 THEN 2.0
        WHEN p_score >= 55 THEN 1.7
        WHEN p_score >= 50 THEN 1.3
        ELSE 0.0
    END;
END;
$$ LANGUAGE plpgsql IMMUTABLE;

-- ============================================================================
-- ANALYTICS QUERY 18 (bonus): Dự báo học viên có nguy cơ bỏ học
-- Sử dụng scoring model đơn giản dựa trên nhiều yếu tố
-- ============================================================================
CREATE OR REPLACE VIEW v_dropout_risk_score AS
WITH base AS (
    SELECT
        s.student_id, s.first_name||' '||s.last_name AS student_name,
        c.course_name,
        ROUND(COUNT(CASE WHEN a.status='Present' THEN 1 END)*100.0
              /NULLIF(COUNT(a.attendance_id),0),1)  AS att_rate,
        ROUND(AVG(g.score),1)                        AS avg_score,
        COUNT(CASE WHEN g.score < 50 THEN 1 END)     AS fail_count,
        COUNT(a.attendance_id)                        AS total_sessions
    FROM students s
    JOIN enrollments e  ON s.student_id=e.student_id AND e.status='Enrolled'
    JOIN classes cl     ON e.class_id=cl.class_id
    JOIN courses c      ON cl.course_id=c.course_id
    LEFT JOIN attendance a ON e.enrollment_id=a.enrollment_id
    LEFT JOIN grades g     ON e.enrollment_id=g.enrollment_id
    GROUP BY s.student_id,s.first_name,s.last_name,c.course_name
)
SELECT *,
    -- Dropout risk score (0-100, cao = nguy hiểm hơn)
    LEAST(100, GREATEST(0,
        CASE WHEN att_rate < 50 THEN 40 WHEN att_rate < 70 THEN 20 ELSE 0 END +
        CASE WHEN avg_score < 40 THEN 40 WHEN avg_score < 55 THEN 20 ELSE 0 END +
        CASE WHEN fail_count >= 2 THEN 20 WHEN fail_count = 1 THEN 10 ELSE 0 END +
        CASE WHEN total_sessions < 5 THEN 10 ELSE 0 END
    ))::INTEGER AS risk_score,
    CASE
        WHEN LEAST(100, GREATEST(0,
            CASE WHEN att_rate < 50 THEN 40 WHEN att_rate < 70 THEN 20 ELSE 0 END +
            CASE WHEN avg_score < 40 THEN 40 WHEN avg_score < 55 THEN 20 ELSE 0 END +
            CASE WHEN fail_count >= 2 THEN 20 WHEN fail_count = 1 THEN 10 ELSE 0 END +
            CASE WHEN total_sessions < 5 THEN 10 ELSE 0 END
        )) >= 60 THEN 'Rủi ro cao'
        WHEN LEAST(100, GREATEST(0,
            CASE WHEN att_rate < 50 THEN 40 WHEN att_rate < 70 THEN 20 ELSE 0 END +
            CASE WHEN avg_score < 40 THEN 40 WHEN avg_score < 55 THEN 20 ELSE 0 END +
            CASE WHEN fail_count >= 2 THEN 20 WHEN fail_count = 1 THEN 10 ELSE 0 END +
            CASE WHEN total_sessions < 5 THEN 10 ELSE 0 END
        )) >= 30 THEN 'Cần theo dõi'
        ELSE 'Bình thường'
    END AS risk_level
FROM base
ORDER BY risk_score DESC;

COMMENT ON VIEW v_dropout_risk_score IS
  'Mô hình dự báo nguy cơ bỏ học – sử dụng rule-based scoring';


-- ============================================================================
-- PHÂN VÙNG DỮ LIỆU (Partition) cho bảng attendance – nếu dữ liệu lớn
-- (Comment out nếu không dùng partition)
-- ============================================================================
-- Gợi ý cho hệ thống production với >100K bản ghi attendance:
-- ALTER TABLE attendance PARTITION BY RANGE (session_date);
-- CREATE TABLE attendance_2024 PARTITION OF attendance
--   FOR VALUES FROM ('2024-01-01') TO ('2025-01-01');
-- CREATE TABLE attendance_2025 PARTITION OF attendance
--   FOR VALUES FROM ('2025-01-01') TO ('2026-01-01');


-- ============================================================================
-- REFRESH MATERIALIZED VIEWS (chạy sau khi có dữ liệu)
-- ============================================================================
-- REFRESH MATERIALIZED VIEW CONCURRENTLY mv_student_stats;
-- REFRESH MATERIALIZED VIEW CONCURRENTLY mv_revenue_stats;

-- ============================================================================
-- END OF SCHEMA V2
-- ============================================================================
