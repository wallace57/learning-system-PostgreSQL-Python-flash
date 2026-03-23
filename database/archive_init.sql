-- ============================================================================
-- ARCHIVE NODE – PostgreSQL Server thứ 2 (t3h_archive)
-- Mô phỏng node lưu trữ dữ liệu lịch sử năm 2022
-- Host: archive_node (Docker network) | Port: 5432 (internal) / 5433 (host)
-- User: archive_reader / Password: readonly123
-- ============================================================================

-- Bảng lưu trữ đăng ký học năm 2022
CREATE TABLE IF NOT EXISTS enrollments_2022 (
    enrollment_id   SERIAL PRIMARY KEY,
    student_id      INTEGER NOT NULL,
    class_code      VARCHAR(20),
    course_name     VARCHAR(100),
    enrollment_date DATE,
    status          VARCHAR(20) DEFAULT 'Completed',
    final_grade     NUMERIC(5,2),
    semester        VARCHAR(20)
);

COMMENT ON TABLE enrollments_2022 IS
    'Dữ liệu đăng ký lịch sử năm 2022 – lưu trữ trên archive node';

-- Dữ liệu mẫu: 30 bản ghi đại diện năm học 2022
INSERT INTO enrollments_2022
    (student_id, class_code, course_name, enrollment_date, status, final_grade, semester)
VALUES
(1,  'OFC22A',  'Microsoft Office cơ bản',      '2022-01-10', 'Completed', 88.5, 'HK1-2022'),
(2,  'OFC22A',  'Microsoft Office cơ bản',      '2022-01-10', 'Completed', 76.0, 'HK1-2022'),
(3,  'WEB22A',  'Lập trình Web HTML/CSS/JS',    '2022-01-15', 'Completed', 91.0, 'HK1-2022'),
(4,  'WEB22A',  'Lập trình Web HTML/CSS/JS',    '2022-01-15', 'Completed', 65.5, 'HK1-2022'),
(5,  'PY22A',   'Python cơ bản',                '2022-01-20', 'Completed', 84.0, 'HK1-2022'),
(6,  'PY22A',   'Python cơ bản',                '2022-01-20', 'Dropped',   NULL, 'HK1-2022'),
(7,  'ACC22A',  'Kế toán máy tính',             '2022-02-01', 'Completed', 79.5, 'HK1-2022'),
(8,  'ACC22A',  'Kế toán máy tính',             '2022-02-01', 'Completed', 93.0, 'HK1-2022'),
(9,  'PS22A',   'Photoshop cơ bản',             '2022-02-10', 'Completed', 87.5, 'HK1-2022'),
(10, 'PS22A',   'Photoshop cơ bản',             '2022-02-10', 'Completed', 72.0, 'HK1-2022'),
(11, 'OFC22B',  'Microsoft Office cơ bản',      '2022-06-01', 'Completed', 80.0, 'HK2-2022'),
(12, 'OFC22B',  'Microsoft Office cơ bản',      '2022-06-01', 'Completed', 68.5, 'HK2-2022'),
(13, 'WEB22B',  'Lập trình Web HTML/CSS/JS',    '2022-06-05', 'Completed', 95.0, 'HK2-2022'),
(14, 'WEB22B',  'Lập trình Web HTML/CSS/JS',    '2022-06-05', 'Completed', 55.0, 'HK2-2022'),
(15, 'PY22B',   'Python cơ bản',                '2022-06-10', 'Completed', 88.0, 'HK2-2022'),
(16, 'DS22A',   'Data Science cơ bản',          '2022-06-15', 'Completed', 76.5, 'HK2-2022'),
(17, 'DS22A',   'Data Science cơ bản',          '2022-06-15', 'Dropped',   NULL, 'HK2-2022'),
(18, 'CAD22A',  'AutoCAD cơ bản',               '2022-07-01', 'Completed', 82.0, 'HK2-2022'),
(19, 'CAD22A',  'AutoCAD cơ bản',               '2022-07-01', 'Completed', 90.5, 'HK2-2022'),
(20, 'ACC22B',  'Kế toán máy tính',             '2022-07-05', 'Completed', 71.0, 'HK2-2022'),
(21, 'OFC22C',  'Microsoft Office cơ bản',      '2022-09-01', 'Completed', 85.0, 'HK3-2022'),
(22, 'WEB22C',  'Lập trình Web HTML/CSS/JS',    '2022-09-05', 'Completed', 92.5, 'HK3-2022'),
(23, 'PY22C',   'Python cơ bản',                '2022-09-10', 'Completed', 78.0, 'HK3-2022'),
(24, 'ML22A',   'Machine Learning cơ bản',      '2022-09-15', 'Completed', 88.5, 'HK3-2022'),
(25, 'ML22A',   'Machine Learning cơ bản',      '2022-09-15', 'Completed', 94.0, 'HK3-2022'),
(26, 'PS22B',   'Photoshop cơ bản',             '2022-10-01', 'Completed', 67.5, 'HK3-2022'),
(27, 'DS22B',   'Data Science cơ bản',          '2022-10-05', 'Completed', 83.0, 'HK3-2022'),
(28, 'CAD22B',  'AutoCAD cơ bản',               '2022-10-10', 'Completed', 77.5, 'HK3-2022'),
(29, 'ACC22C',  'Kế toán máy tính',             '2022-10-15', 'Completed', 89.0, 'HK3-2022'),
(30, 'OFC22D',  'Microsoft Office cơ bản',      '2022-11-01', 'Completed', 74.0, 'HK3-2022');

-- Bảng thống kê tổng hợp theo khóa học (năm 2022)
CREATE TABLE IF NOT EXISTS course_stats_2022 (
    course_name     VARCHAR(100) PRIMARY KEY,
    total_enrolled  INTEGER,
    avg_grade       NUMERIC(5,2),
    pass_rate       NUMERIC(5,2),
    year            INTEGER DEFAULT 2022
);

INSERT INTO course_stats_2022 (course_name, total_enrolled, avg_grade, pass_rate) VALUES
('Microsoft Office cơ bản',   8,  81.8, 100.0),
('Lập trình Web HTML/CSS/JS', 6,  79.8,  83.3),
('Python cơ bản',             4,  83.3,  75.0),
('Kế toán máy tính',          4,  83.1, 100.0),
('Photoshop cơ bản',          3,  75.7, 100.0),
('Data Science cơ bản',       3,  79.8,  66.7),
('AutoCAD cơ bản',            3,  83.3, 100.0),
('Machine Learning cơ bản',   2,  91.3, 100.0);

-- Index cho FDW queries
CREATE INDEX IF NOT EXISTS idx_enroll22_student ON enrollments_2022(student_id);
CREATE INDEX IF NOT EXISTS idx_enroll22_semester ON enrollments_2022(semester);
CREATE INDEX IF NOT EXISTS idx_enroll22_status   ON enrollments_2022(status);

-- ============================================================================
-- END: Archive Node Init
-- ============================================================================
