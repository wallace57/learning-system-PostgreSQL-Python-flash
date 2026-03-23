-- ============================================================================
-- Learning Data Management and Analytics System
-- File: index.sql - Performance Optimization Indexes
-- ============================================================================

-- ============================================================================
-- INDEXES FOR STUDENTS TABLE
-- ============================================================================
CREATE INDEX idx_students_email ON students(email);
CREATE INDEX idx_students_status ON students(status);
CREATE INDEX idx_students_enrolled_date ON students(enrolled_date);
CREATE INDEX idx_students_name ON students(last_name, first_name);

-- ============================================================================
-- INDEXES FOR COURSES TABLE
-- ============================================================================
CREATE INDEX idx_courses_category ON courses(category);
CREATE INDEX idx_courses_level ON courses(level);
CREATE INDEX idx_courses_status ON courses(status);

-- ============================================================================
-- INDEXES FOR INSTRUCTORS TABLE
-- ============================================================================
CREATE INDEX idx_instructors_specialization ON instructors(specialization);
CREATE INDEX idx_instructors_status ON instructors(status);

-- ============================================================================
-- INDEXES FOR CLASSES TABLE
-- ============================================================================
CREATE INDEX idx_classes_course_id ON classes(course_id);
CREATE INDEX idx_classes_instructor_id ON classes(instructor_id);
CREATE INDEX idx_classes_semester ON classes(semester, academic_year);
CREATE INDEX idx_classes_status ON classes(status);
CREATE INDEX idx_classes_dates ON classes(start_date, end_date);

-- ============================================================================
-- INDEXES FOR ENROLLMENTS TABLE
-- ============================================================================
CREATE INDEX idx_enrollments_student_id ON enrollments(student_id);
CREATE INDEX idx_enrollments_class_id ON enrollments(class_id);
CREATE INDEX idx_enrollments_status ON enrollments(status);
CREATE INDEX idx_enrollments_date ON enrollments(enrollment_date);
-- Composite index for common query patterns
CREATE INDEX idx_enrollments_student_class ON enrollments(student_id, class_id);

-- ============================================================================
-- INDEXES FOR ATTENDANCE TABLE
-- ============================================================================
CREATE INDEX idx_attendance_enrollment_id ON attendance(enrollment_id);
CREATE INDEX idx_attendance_session_date ON attendance(session_date);
CREATE INDEX idx_attendance_status ON attendance(status);
-- Composite for attendance lookup
CREATE INDEX idx_attendance_enrollment_date ON attendance(enrollment_id, session_date);

-- ============================================================================
-- INDEXES FOR GRADES TABLE
-- ============================================================================
CREATE INDEX idx_grades_enrollment_id ON grades(enrollment_id);
CREATE INDEX idx_grades_assessment_type ON grades(assessment_type);
CREATE INDEX idx_grades_graded_date ON grades(graded_date);
-- Composite for score analysis
CREATE INDEX idx_grades_enrollment_type ON grades(enrollment_id, assessment_type);

-- ============================================================================
-- EXPLAIN ANALYZE EXAMPLES
-- Run these after loading data to analyze query performance
-- ============================================================================

-- Example 1: Analyze average score query performance
EXPLAIN ANALYZE
SELECT c.course_name, ROUND(AVG(g.score), 2) AS avg_score
FROM courses c
JOIN classes cl ON c.course_id = cl.course_id
JOIN enrollments e ON cl.class_id = e.class_id
JOIN grades g ON e.enrollment_id = g.enrollment_id
GROUP BY c.course_name
ORDER BY avg_score DESC;

-- Example 2: Analyze student attendance lookup performance
EXPLAIN ANALYZE
SELECT s.first_name, s.last_name, a.session_date, a.status
FROM students s
JOIN enrollments e ON s.student_id = e.student_id
JOIN attendance a ON e.enrollment_id = a.enrollment_id
WHERE s.student_id = 1;

-- Example 3: Analyze enrollment trend query performance
EXPLAIN ANALYZE
SELECT
    TO_CHAR(enrollment_date, 'YYYY-MM') AS month,
    COUNT(*) AS enrollments
FROM enrollments
GROUP BY TO_CHAR(enrollment_date, 'YYYY-MM')
ORDER BY month;

-- ============================================================================
-- END OF INDEX DEFINITIONS
-- ============================================================================
