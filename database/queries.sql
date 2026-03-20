-- ============================================================================
-- Learning Data Management and Analytics System
-- File: queries.sql - Advanced Analytics Queries (15+ queries)
-- ============================================================================

-- ============================================================================
-- QUERY 1: Average Score Per Course
-- Tính điểm trung bình theo từng khóa học
-- ============================================================================
SELECT
    c.course_code,
    c.course_name,
    COUNT(DISTINCT e.student_id) AS total_students,
    ROUND(AVG(g.score), 2) AS avg_score,
    ROUND(MIN(g.score), 2) AS min_score,
    ROUND(MAX(g.score), 2) AS max_score
FROM courses c
JOIN classes cl ON c.course_id = cl.course_id
JOIN enrollments e ON cl.class_id = e.class_id
JOIN grades g ON e.enrollment_id = g.enrollment_id
GROUP BY c.course_code, c.course_name
ORDER BY avg_score DESC;

-- ============================================================================
-- QUERY 2: Course Completion Rate
-- Tỷ lệ hoàn thành khóa học
-- ============================================================================
SELECT
    c.course_code,
    c.course_name,
    COUNT(e.enrollment_id) AS total_enrollments,
    COUNT(CASE WHEN e.status = 'Completed' THEN 1 END) AS completed,
    COUNT(CASE WHEN e.status = 'Dropped' THEN 1 END) AS dropped,
    COUNT(CASE WHEN e.status = 'Enrolled' THEN 1 END) AS in_progress,
    ROUND(
        COUNT(CASE WHEN e.status = 'Completed' THEN 1 END) * 100.0
        / NULLIF(COUNT(e.enrollment_id), 0), 2
    ) AS completion_rate_pct
FROM courses c
JOIN classes cl ON c.course_id = cl.course_id
JOIN enrollments e ON cl.class_id = e.class_id
GROUP BY c.course_code, c.course_name
ORDER BY completion_rate_pct DESC;

-- ============================================================================
-- QUERY 3: Top 5 Instructors by Student Performance
-- Top 5 giảng viên theo kết quả học viên
-- ============================================================================
SELECT
    i.instructor_id,
    i.first_name || ' ' || i.last_name AS instructor_name,
    i.specialization,
    COUNT(DISTINCT e.student_id) AS total_students,
    ROUND(AVG(g.score), 2) AS avg_student_score,
    COUNT(DISTINCT cl.class_id) AS classes_taught
FROM instructors i
JOIN classes cl ON i.instructor_id = cl.instructor_id
JOIN enrollments e ON cl.class_id = e.class_id
JOIN grades g ON e.enrollment_id = g.enrollment_id
GROUP BY i.instructor_id, i.first_name, i.last_name, i.specialization
ORDER BY avg_student_score DESC
LIMIT 5;

-- ============================================================================
-- QUERY 4: Students with Lowest Attendance Rate
-- Học viên có tỷ lệ chuyên cần thấp nhất
-- ============================================================================
SELECT
    s.student_id,
    s.first_name || ' ' || s.last_name AS student_name,
    COUNT(a.attendance_id) AS total_sessions,
    COUNT(CASE WHEN a.status = 'Present' THEN 1 END) AS present_count,
    COUNT(CASE WHEN a.status = 'Absent' THEN 1 END) AS absent_count,
    ROUND(
        COUNT(CASE WHEN a.status = 'Present' THEN 1 END) * 100.0
        / NULLIF(COUNT(a.attendance_id), 0), 2
    ) AS attendance_rate_pct
FROM students s
JOIN enrollments e ON s.student_id = e.student_id
JOIN attendance a ON e.enrollment_id = a.enrollment_id
GROUP BY s.student_id, s.first_name, s.last_name
ORDER BY attendance_rate_pct ASC
LIMIT 10;

-- ============================================================================
-- QUERY 5: Monthly Enrollment Trends
-- Xu hướng đăng ký theo tháng
-- ============================================================================
SELECT
    TO_CHAR(e.enrollment_date, 'YYYY-MM') AS enrollment_month,
    COUNT(e.enrollment_id) AS new_enrollments,
    COUNT(DISTINCT e.student_id) AS unique_students,
    COUNT(DISTINCT e.class_id) AS classes_enrolled
FROM enrollments e
GROUP BY TO_CHAR(e.enrollment_date, 'YYYY-MM')
ORDER BY enrollment_month;

-- ============================================================================
-- QUERY 6: Pass/Fail Rate (Pass >= 50, Fail < 50)
-- Tỷ lệ đậu/rớt theo khóa học
-- ============================================================================
WITH weighted_scores AS (
    SELECT
        e.enrollment_id,
        e.student_id,
        cl.course_id,
        ROUND(SUM(g.score * g.weight) / NULLIF(SUM(g.weight), 0), 2) AS weighted_avg
    FROM enrollments e
    JOIN classes cl ON e.class_id = cl.class_id
    JOIN grades g ON e.enrollment_id = g.enrollment_id
    WHERE e.status = 'Completed'
    GROUP BY e.enrollment_id, e.student_id, cl.course_id
)
SELECT
    c.course_code,
    c.course_name,
    COUNT(ws.enrollment_id) AS total_graded,
    COUNT(CASE WHEN ws.weighted_avg >= 50 THEN 1 END) AS passed,
    COUNT(CASE WHEN ws.weighted_avg < 50 THEN 1 END) AS failed,
    ROUND(
        COUNT(CASE WHEN ws.weighted_avg >= 50 THEN 1 END) * 100.0
        / NULLIF(COUNT(ws.enrollment_id), 0), 2
    ) AS pass_rate_pct
FROM weighted_scores ws
JOIN courses c ON ws.course_id = c.course_id
GROUP BY c.course_code, c.course_name
ORDER BY pass_rate_pct DESC;

-- ============================================================================
-- QUERY 7: Ranking Students by Weighted Average (Window Functions)
-- Xếp hạng sinh viên theo điểm trung bình có trọng số
-- ============================================================================
WITH student_scores AS (
    SELECT
        s.student_id,
        s.first_name || ' ' || s.last_name AS student_name,
        c.course_name,
        ROUND(SUM(g.score * g.weight) / NULLIF(SUM(g.weight), 0), 2) AS weighted_avg
    FROM students s
    JOIN enrollments e ON s.student_id = e.student_id
    JOIN classes cl ON e.class_id = cl.class_id
    JOIN courses c ON cl.course_id = c.course_id
    JOIN grades g ON e.enrollment_id = g.enrollment_id
    GROUP BY s.student_id, s.first_name, s.last_name, c.course_name
)
SELECT
    student_id,
    student_name,
    course_name,
    weighted_avg,
    RANK() OVER (PARTITION BY course_name ORDER BY weighted_avg DESC) AS rank_in_course,
    DENSE_RANK() OVER (ORDER BY weighted_avg DESC) AS overall_dense_rank,
    NTILE(4) OVER (ORDER BY weighted_avg DESC) AS quartile
FROM student_scores
ORDER BY course_name, rank_in_course;

-- ============================================================================
-- QUERY 8: Revenue Analysis by Course
-- Phân tích doanh thu theo khóa học
-- ============================================================================
SELECT
    c.course_code,
    c.course_name,
    c.tuition_fee,
    COUNT(e.enrollment_id) AS total_enrollments,
    c.tuition_fee * COUNT(e.enrollment_id) AS total_revenue,
    RANK() OVER (ORDER BY c.tuition_fee * COUNT(e.enrollment_id) DESC) AS revenue_rank
FROM courses c
JOIN classes cl ON c.course_id = cl.course_id
JOIN enrollments e ON cl.class_id = e.class_id
WHERE e.status != 'Dropped'
GROUP BY c.course_code, c.course_name, c.tuition_fee
ORDER BY total_revenue DESC;

-- ============================================================================
-- QUERY 9: Student Performance Across Multiple Courses
-- Kết quả học viên qua nhiều khóa học (Multi-table JOIN)
-- ============================================================================
SELECT
    s.student_id,
    s.first_name || ' ' || s.last_name AS student_name,
    COUNT(DISTINCT cl.course_id) AS courses_taken,
    ROUND(AVG(g.score), 2) AS overall_avg_score,
    STRING_AGG(DISTINCT c.course_name, ', ' ORDER BY c.course_name) AS courses_list
FROM students s
JOIN enrollments e ON s.student_id = e.student_id
JOIN classes cl ON e.class_id = cl.class_id
JOIN courses c ON cl.course_id = c.course_id
JOIN grades g ON e.enrollment_id = g.enrollment_id
GROUP BY s.student_id, s.first_name, s.last_name
HAVING COUNT(DISTINCT cl.course_id) >= 1
ORDER BY overall_avg_score DESC;

-- ============================================================================
-- QUERY 10: Attendance vs Grade Correlation
-- Mối tương quan giữa chuyên cần và điểm số
-- ============================================================================
WITH attendance_stats AS (
    SELECT
        e.enrollment_id,
        COUNT(a.attendance_id) AS total_sessions,
        COUNT(CASE WHEN a.status = 'Present' THEN 1 END) AS present_sessions,
        ROUND(
            COUNT(CASE WHEN a.status = 'Present' THEN 1 END) * 100.0
            / NULLIF(COUNT(a.attendance_id), 0), 2
        ) AS attendance_pct
    FROM enrollments e
    JOIN attendance a ON e.enrollment_id = a.enrollment_id
    GROUP BY e.enrollment_id
),
grade_stats AS (
    SELECT
        enrollment_id,
        ROUND(AVG(score), 2) AS avg_score
    FROM grades
    GROUP BY enrollment_id
)
SELECT
    s.first_name || ' ' || s.last_name AS student_name,
    c.course_name,
    att.attendance_pct,
    gs.avg_score,
    CASE
        WHEN att.attendance_pct >= 80 AND gs.avg_score >= 70 THEN 'Tốt'
        WHEN att.attendance_pct >= 60 AND gs.avg_score >= 50 THEN 'Trung bình'
        ELSE 'Cần cải thiện'
    END AS performance_category
FROM attendance_stats att
JOIN grade_stats gs ON att.enrollment_id = gs.enrollment_id
JOIN enrollments e ON att.enrollment_id = e.enrollment_id
JOIN students s ON e.student_id = s.student_id
JOIN classes cl ON e.class_id = cl.class_id
JOIN courses c ON cl.course_id = c.course_id
ORDER BY att.attendance_pct DESC;

-- ============================================================================
-- QUERY 11: Class Capacity Utilization
-- Tỷ lệ sử dụng sức chứa lớp học
-- ============================================================================
SELECT
    cl.class_code,
    c.course_name,
    i.first_name || ' ' || i.last_name AS instructor_name,
    cl.max_students,
    COUNT(e.enrollment_id) AS enrolled_count,
    ROUND(
        COUNT(e.enrollment_id) * 100.0 / cl.max_students, 2
    ) AS utilization_pct,
    cl.max_students - COUNT(e.enrollment_id) AS available_seats
FROM classes cl
JOIN courses c ON cl.course_id = c.course_id
JOIN instructors i ON cl.instructor_id = i.instructor_id
LEFT JOIN enrollments e ON cl.class_id = e.class_id AND e.status != 'Dropped'
GROUP BY cl.class_code, c.course_name, i.first_name, i.last_name, cl.max_students
ORDER BY utilization_pct DESC;

-- ============================================================================
-- QUERY 12: Score Distribution by Assessment Type
-- Phân phối điểm theo loại bài kiểm tra
-- ============================================================================
SELECT
    assessment_type,
    COUNT(*) AS total_grades,
    ROUND(AVG(score), 2) AS avg_score,
    ROUND(STDDEV(score), 2) AS std_dev,
    PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY score) AS percentile_25,
    PERCENTILE_CONT(0.50) WITHIN GROUP (ORDER BY score) AS median,
    PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY score) AS percentile_75
FROM grades
GROUP BY assessment_type
ORDER BY avg_score DESC;

-- ============================================================================
-- QUERY 13: Instructor Workload Analysis
-- Phân tích khối lượng công việc giảng viên
-- ============================================================================
SELECT
    i.instructor_id,
    i.first_name || ' ' || i.last_name AS instructor_name,
    i.specialization,
    COUNT(DISTINCT cl.class_id) AS total_classes,
    COUNT(DISTINCT e.student_id) AS total_students,
    SUM(cr.duration_hours) AS total_teaching_hours,
    STRING_AGG(DISTINCT cl.class_code, ', ' ORDER BY cl.class_code) AS class_list
FROM instructors i
JOIN classes cl ON i.instructor_id = cl.instructor_id
JOIN courses cr ON cl.course_id = cr.course_id
LEFT JOIN enrollments e ON cl.class_id = e.class_id AND e.status != 'Dropped'
GROUP BY i.instructor_id, i.first_name, i.last_name, i.specialization
ORDER BY total_teaching_hours DESC;

-- ============================================================================
-- QUERY 14: Students At Risk (Low Attendance + Low Grades)
-- Sinh viên có nguy cơ (điểm danh thấp + điểm số thấp)
-- ============================================================================
WITH risk_data AS (
    SELECT
        s.student_id,
        s.first_name || ' ' || s.last_name AS student_name,
        s.email,
        c.course_name,
        ROUND(
            COUNT(CASE WHEN a.status = 'Present' THEN 1 END) * 100.0
            / NULLIF(COUNT(a.attendance_id), 0), 2
        ) AS attendance_rate,
        ROUND(AVG(g.score), 2) AS avg_score
    FROM students s
    JOIN enrollments e ON s.student_id = e.student_id
    JOIN classes cl ON e.class_id = cl.class_id
    JOIN courses c ON cl.course_id = c.course_id
    LEFT JOIN attendance a ON e.enrollment_id = a.enrollment_id
    LEFT JOIN grades g ON e.enrollment_id = g.enrollment_id
    GROUP BY s.student_id, s.first_name, s.last_name, s.email, c.course_name
)
SELECT *
FROM risk_data
WHERE attendance_rate < 70 OR avg_score < 55
ORDER BY avg_score ASC, attendance_rate ASC;

-- ============================================================================
-- QUERY 15: Cumulative GPA with Running Average (Window Function)
-- GPA tích lũy với trung bình chạy
-- ============================================================================
WITH enrollment_scores AS (
    SELECT
        e.student_id,
        s.first_name || ' ' || s.last_name AS student_name,
        e.enrollment_date,
        c.course_name,
        ROUND(SUM(g.score * g.weight) / NULLIF(SUM(g.weight), 0), 2) AS course_score
    FROM enrollments e
    JOIN students s ON e.student_id = s.student_id
    JOIN classes cl ON e.class_id = cl.class_id
    JOIN courses c ON cl.course_id = c.course_id
    JOIN grades g ON e.enrollment_id = g.enrollment_id
    GROUP BY e.student_id, s.first_name, s.last_name, e.enrollment_date, c.course_name
)
SELECT
    student_id,
    student_name,
    course_name,
    course_score,
    ROUND(AVG(course_score) OVER (
        PARTITION BY student_id
        ORDER BY enrollment_date
        ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
    ), 2) AS cumulative_avg,
    ROW_NUMBER() OVER (PARTITION BY student_id ORDER BY enrollment_date) AS course_sequence
FROM enrollment_scores
ORDER BY student_id, course_sequence;

-- ============================================================================
-- QUERY 16: Semester-over-Semester Comparison
-- So sánh kết quả giữa các học kỳ
-- ============================================================================
SELECT
    cl.semester,
    cl.academic_year,
    COUNT(DISTINCT e.student_id) AS total_students,
    COUNT(DISTINCT cl.class_id) AS total_classes,
    ROUND(AVG(g.score), 2) AS avg_score,
    COUNT(CASE WHEN g.score >= 80 THEN 1 END) AS excellent_scores,
    COUNT(CASE WHEN g.score < 50 THEN 1 END) AS failing_scores
FROM classes cl
JOIN enrollments e ON cl.class_id = e.class_id
JOIN grades g ON e.enrollment_id = g.enrollment_id
GROUP BY cl.semester, cl.academic_year
ORDER BY cl.academic_year, cl.semester;

-- ============================================================================
-- QUERY 17: Course Popularity Ranking by Category
-- Xếp hạng độ phổ biến khóa học theo danh mục
-- ============================================================================
SELECT
    c.category,
    c.course_code,
    c.course_name,
    c.level,
    COUNT(e.enrollment_id) AS enrollment_count,
    RANK() OVER (PARTITION BY c.category ORDER BY COUNT(e.enrollment_id) DESC) AS rank_in_category,
    ROUND(
        COUNT(e.enrollment_id) * 100.0 /
        SUM(COUNT(e.enrollment_id)) OVER (PARTITION BY c.category), 2
    ) AS pct_of_category
FROM courses c
JOIN classes cl ON c.course_id = cl.course_id
JOIN enrollments e ON cl.class_id = e.class_id
GROUP BY c.category, c.course_code, c.course_name, c.level
ORDER BY c.category, rank_in_category;

-- ============================================================================
-- END OF ANALYTICS QUERIES
-- ============================================================================
