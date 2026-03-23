-- ============================================================================
-- CSDL SUY DIỄN (Deductive Database)
-- Mô phỏng các tính năng suy diễn trong PostgreSQL:
--   1. Recursive CTE – suy diễn quan hệ bắc cầu
--   2. PostgreSQL RULE – ghi đè hành vi DML
--   3. Rule-based inference queries
--   4. Eligibility checking (suy diễn điều kiện)
-- Ref: Deductive DB = Facts + Rules → infer new facts (Prolog-like in SQL)
-- ============================================================================

-- ── Bảng dữ kiện (Facts): Quan hệ tiên quyết giữa các khóa học ────────────
CREATE TABLE IF NOT EXISTS course_prerequisites (
    course_id   INTEGER NOT NULL REFERENCES courses(course_id),
    prereq_id   INTEGER NOT NULL REFERENCES courses(course_id),
    is_mandatory BOOLEAN DEFAULT TRUE,
    PRIMARY KEY (course_id, prereq_id),
    CHECK (course_id <> prereq_id)
);

COMMENT ON TABLE course_prerequisites IS
    'Facts: quan hệ tiên quyết (prerequisite) giữa các khóa học T3H';

-- Insert facts: chuỗi khóa học T3H theo trình tự học tập
-- Programming track: PY101(8) → DS201(9) → ML301(10) → AI301(11)
-- Web track: WBF101(5) → React(6) / Node(7)
-- Accounting: KTM101(3) → KTM201(4)
-- Security: DB201(15) → CY201(16)
INSERT INTO course_prerequisites (course_id, prereq_id, is_mandatory) VALUES
  (9,  8,  TRUE),   -- DS201   yêu cầu PY101
  (10, 9,  TRUE),   -- ML301   yêu cầu DS201
  (11, 10, TRUE),   -- AI301   yêu cầu ML301
  (6,  5,  TRUE),   -- React   yêu cầu WBF101
  (7,  5,  FALSE),  -- Node.js khuyến khích WBF101
  (4,  3,  TRUE),   -- KTM201  yêu cầu KTM101
  (16, 15, TRUE),   -- CY201   yêu cầu DB201
  (15, 8,  FALSE)   -- DB201   khuyến khích PY101
ON CONFLICT DO NOTHING;

-- ── RULE 1 – Recursive CTE: Suy diễn tiên quyết gián tiếp ────────────────
-- Từ facts (quan hệ trực tiếp) → suy ra quan hệ gián tiếp nhiều cấp
-- Giống Prolog: prereq(X,Z) :- prereq(X,Y), prereq(Y,Z).

WITH RECURSIVE infer_all_prereqs(course_id, prereq_id, depth, path) AS (
    -- Base case (Facts trực tiếp)
    SELECT course_id, prereq_id, 1,
           ARRAY[course_id, prereq_id]
    FROM course_prerequisites
    WHERE is_mandatory = TRUE

    UNION ALL

    -- Recursive case (Suy diễn)
    SELECT base.course_id, cp.prereq_id,
           base.depth + 1,
           base.path || cp.prereq_id
    FROM infer_all_prereqs base
    JOIN course_prerequisites cp
         ON base.prereq_id = cp.course_id
         AND cp.is_mandatory = TRUE
    WHERE cp.prereq_id <> ALL(base.path)   -- chống vòng lặp
      AND base.depth < 10
)
SELECT
    c1.course_name  AS khoa_hoc,
    c2.course_name  AS yeu_cau_truoc_do,
    depth           AS cap_gian_tiep,
    array_to_string(path, ' → ')          AS chuoi_hoc
FROM infer_all_prereqs iap
JOIN courses c1 ON iap.course_id = c1.course_id
JOIN courses c2 ON iap.prereq_id = c2.course_id
ORDER BY c1.course_name, depth;

-- ── RULE 2 – Suy diễn tính đủ điều kiện đăng ký (Eligibility Inference) ──
CREATE OR REPLACE FUNCTION fn_check_eligibility(
    p_student_id INTEGER,
    p_course_id  INTEGER
) RETURNS TABLE (
    eligible         BOOLEAN,
    missing_courses  TEXT,
    completed_prereqs TEXT
) AS $$
BEGIN
    RETURN QUERY
    WITH RECURSIVE
    -- Suy diễn TẤT CẢ prerequisites bắt buộc (bao gồm gián tiếp)
    all_required(prereq_id) AS (
        SELECT prereq_id FROM course_prerequisites
        WHERE course_id = p_course_id AND is_mandatory = TRUE
        UNION ALL
        SELECT cp.prereq_id FROM all_required ar
        JOIN course_prerequisites cp ON ar.prereq_id = cp.course_id
        WHERE cp.is_mandatory = TRUE
    ),
    -- Facts: học viên đã hoàn thành gì
    completed_courses AS (
        SELECT cl.course_id
        FROM enrollments e
        JOIN classes cl ON e.class_id = cl.class_id
        WHERE e.student_id = p_student_id AND e.status = 'Completed'
    )
    SELECT
        NOT EXISTS(
            SELECT 1 FROM all_required ar
            WHERE ar.prereq_id NOT IN (SELECT course_id FROM completed_courses)
        )                                                              AS eligible,
        COALESCE(
            (SELECT STRING_AGG(c.course_name, ', ')
             FROM all_required ar
             JOIN courses c ON ar.prereq_id = c.course_id
             WHERE ar.prereq_id NOT IN (SELECT course_id FROM completed_courses)),
            'Đủ điều kiện'
        )                                                              AS missing_courses,
        COALESCE(
            (SELECT STRING_AGG(c.course_name, ', ')
             FROM all_required ar
             JOIN courses c ON ar.prereq_id = c.course_id
             WHERE ar.prereq_id IN (SELECT course_id FROM completed_courses)),
            'Không có'
        )                                                              AS completed_prereqs;
END;
$$ LANGUAGE plpgsql;

-- Demo: kiểm tra học viên 1 có đủ điều kiện học AI301 (id=11) không
SELECT * FROM fn_check_eligibility(1, 11);
SELECT * FROM fn_check_eligibility(1, 9);   -- DS201

-- ── RULE 3 – Suy diễn học viên nên học gì tiếp theo (Recommendation) ─────
-- Logic: Nếu học xong A và A là prereq của B → suy ra nên học B
CREATE OR REPLACE VIEW v_recommended_next_courses AS
WITH student_completed AS (
    SELECT e.student_id, cl.course_id
    FROM enrollments e
    JOIN classes cl ON e.class_id = cl.class_id
    WHERE e.status = 'Completed'
),
student_enrolled AS (
    SELECT e.student_id, cl.course_id
    FROM enrollments e
    JOIN classes cl ON e.class_id = cl.class_id
    WHERE e.status IN ('Enrolled','Completed')
)
SELECT DISTINCT
    s.student_id,
    s.first_name||' '||s.last_name AS student_name,
    c_next.course_id                AS recommended_course_id,
    c_next.course_name              AS recommended_course,
    c_next.category,
    c_next.level,
    c_done.course_name              AS because_completed
FROM student_completed sc
JOIN course_prerequisites cp    ON sc.course_id = cp.prereq_id
JOIN courses c_next             ON cp.course_id = c_next.course_id
JOIN courses c_done             ON sc.course_id = c_done.course_id
JOIN students s                 ON sc.student_id = s.student_id
-- Lọc: chưa đăng ký khóa đó
WHERE NOT EXISTS (
    SELECT 1 FROM student_enrolled se
    WHERE se.student_id = sc.student_id
      AND se.course_id  = cp.course_id
)
ORDER BY s.student_id, c_next.level;

SELECT * FROM v_recommended_next_courses LIMIT 20;

-- ── RULE 4 – Suy diễn phân loại học viên theo tiến độ (tiered logic) ──────
-- Inference rules:
--   "Xuất sắc"   :- attendance >= 90 AND avg_score >= 85
--   "Giỏi"       :- attendance >= 80 AND avg_score >= 70
--   "Trung bình" :- attendance >= 65 AND avg_score >= 55
--   "Yếu"        :- (otherwise)
CREATE OR REPLACE VIEW v_student_classification AS
WITH stats AS (
    SELECT s.student_id,
           s.first_name||' '||s.last_name                              AS student_name,
           ROUND(COUNT(CASE WHEN a.status='Present' THEN 1 END)*100.0
                 /NULLIF(COUNT(a.attendance_id),0),1)                  AS att_rate,
           ROUND(AVG(g.score),1)                                        AS avg_score
    FROM students s
    JOIN enrollments e  ON s.student_id=e.student_id
    LEFT JOIN attendance a  ON e.enrollment_id=a.enrollment_id
    LEFT JOIN grades g      ON e.enrollment_id=g.enrollment_id
    GROUP BY s.student_id, s.first_name, s.last_name
)
SELECT student_id, student_name, att_rate, avg_score,
    CASE
        WHEN att_rate >= 90 AND avg_score >= 85 THEN 'Xuất sắc'
        WHEN att_rate >= 80 AND avg_score >= 70 THEN 'Giỏi'
        WHEN att_rate >= 65 AND avg_score >= 55 THEN 'Trung bình'
        WHEN att_rate IS NULL OR avg_score IS NULL  THEN 'Chưa có dữ liệu'
        ELSE 'Yếu – cần hỗ trợ'
    END AS classification,
    CASE
        WHEN att_rate >= 90 AND avg_score >= 85 THEN 4
        WHEN att_rate >= 80 AND avg_score >= 70 THEN 3
        WHEN att_rate >= 65 AND avg_score >= 55 THEN 2
        ELSE 1
    END AS tier
FROM stats
ORDER BY tier DESC, avg_score DESC NULLS LAST;

SELECT classification, COUNT(*) AS student_count,
       ROUND(AVG(avg_score),1) AS avg_score_in_tier
FROM v_student_classification
GROUP BY classification ORDER BY MIN(tier) DESC;

-- ── RULE 5 – PostgreSQL RULE system (view rewrite rules) ──────────────────
-- Rule: khi INSERT vào view sẽ redirect sang bảng gốc
CREATE OR REPLACE VIEW v_enroll_shortcut AS
SELECT enrollment_id, student_id, class_id, enrollment_date, status
FROM enrollments WHERE status = 'Enrolled';

CREATE OR REPLACE RULE rule_enroll_via_view AS
ON INSERT TO v_enroll_shortcut
DO INSTEAD
    INSERT INTO enrollments (student_id, class_id, enrollment_date, status)
    VALUES (NEW.student_id, NEW.class_id,
            COALESCE(NEW.enrollment_date, CURRENT_DATE), 'Enrolled');

-- Dùng rule: INSERT vào view thay vì bảng
-- INSERT INTO v_enroll_shortcut (student_id, class_id) VALUES (1, 5);

-- ============================================================================
-- END: CSDL Suy diễn
-- ============================================================================
