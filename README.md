# Xây dựng hệ thống quản lý và phân tích dữ liệu học tập cho trung tâm đào tạo tại TP. Hồ Chí Minh
# 🎓 Hệ Thống Quản Lý Dữ Liệu Học Tập (Learning Data System)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-14%2B-blue.svg)
![Python](https://img.shields.io/badge/Python-3.8%2B-blue.svg)
![Status](https://img.shields.io/badge/Trạng_thái-Hoàn_thành-success.svg)

Dự án Cơ sở dữ liệu PostgreSQL hoàn chỉnh dành cho Trung tâm Đào tạo Kỹ năng CNTT tại TP.HCM. Dự án bao gồm thiết kế CSDL chuẩn hóa (3NF), 7.434 dòng dữ liệu mẫu thực tế, và 17 truy vấn phân tích dữ liệu nâng cao.

## 🗂 Cấu Trúc Dự Án

```text
learning-data-system/
├── database/
│   ├── schema.sql        # Tạo bảng (Students, Courses, Classes...)
│   ├── insert_data.sql   # File SQL nạp dữ liệu (7.434 dòng)
│   ├── index.sql         # Tạo indexes giúp tăng tốc độ truy vấn
│   └── queries.sql       # 17 câu truy vấn phân tích nâng cao
├── generate_data.py      # Script Python tạo dữ liệu tự động
├── README.md             # Tài liệu hướng dẫn
└── .gitignore
```

## 🗄 Mô Hình Cơ Sở Dữ Liệu

Hệ thống sử dụng 7 bảng có liên kết chặt chẽ với nhau:
- **`students`**: Thông tin học viên (Tên, SĐT, Email...)
- **`instructors`**: Hồ sơ giảng viên (Chuyên môn, Bằng cấp...)
- **`courses`**: Danh sách khóa học (Python, Data Science, AI...)
- **`classes`**: Lớp học thực tế mở theo từng học kỳ
- **`enrollments`**: Đăng ký môn học của học viên
- **`attendance`**: Theo dõi điểm danh từng buổi
- **`grades`**: Điểm số bài tập, thi giữa kỳ & cuối kỳ

---

## 🚀 Hướng Dẫn Cài Đặt & Chạy

Có 2 cách để nạp 7.434+ dòng dữ liệu vào máy của bạn. Cách 1 là an toàn và nhanh nhất.

### Cách 1: Chạy bằng Python Script (Khuyên dùng)
Cách này sẽ tự động kết nối, xóa dữ liệu cũ và nạp thẳng dữ liệu vào CSDL PostgreSQL.

1. Mở Terminal và cài đặt thư viện kết nối PostgreSQL:
```bash
pip install psycopg2-binary
```
2. Chạy file script:
```bash
python generate_data.py
```
*(Chỉ cần nhấn Enter để chọn database mặc định, sau đó nhập mật khẩu PostgreSQL của bạn)*

### Cách 2: Chạy bằng dòng lệnh `psql` (Thủ công)
*Lưu ý: Do dữ liệu có chứa tiếng Việt, bạn PHẢI cài đặt `UTF8` trước khi chạy để tránh lỗi font chữ.*

1. Mở Command Prompt (cmd) và đăng nhập:
```bash
psql -U postgres
```
2. Cài đặt chuẩn mã hóa tiếng Việt và chạy các file theo thứ tự:
```sql
CREATE DATABASE learning_data_system;
\c learning_data_system

-- (QUAN TRỌNG) Bật tiếng Việt:
\encoding UTF8

-- Chạy các file SQL:
\i 'C:/temp/learning-db/schema.sql'
\i 'C:/temp/learning-db/insert_data.sql'
\i 'C:/temp/learning-db/index.sql'
\i 'C:/temp/learning-db/queries.sql'
```

---

## 📈 17 Các Truy Vấn Phân Tích Dữ Liệu (Analytics)

Dự án bao gồm 17 câu lệnh SQL phức tạp giúp chiết xuất báo cáo thực tế:

| # | Báo cáo Phân tích | Kỹ thuật SQL sử dụng |
|---|-------|----------------|
| 1 | Điểm trung bình mỗi khóa học | JOIN, GROUP BY, AVG |
| 2 | Tỷ lệ hoàn thành khóa học | CASE WHEN, NULLIF |
| 3 | Top 5 giảng viên tốt nhất | Multi-JOIN, LIMIT |
| 4 | Học viên vắng mặt nhiều nhất | Conditional aggregation |
| 5 | Xu hướng đăng ký theo tháng | TO_CHAR, DATE functions |
| 6 | Tỷ lệ Đậu/Rớt | CTE, Weighted averages |
| 7 | Xếp hạng học thuật sinh viên | RANK, DENSE_RANK, NTILE |
| 8 | Phân tích doanh thu học phí | Window functions |
| 9 | Điểm trung bình tích lũy hệ thống | STRING_AGG, HAVING |
| 10 | Tương quan Giữa Chuyên Cần & Điểm | Multiple CTEs, CASE |
| 11 | Tỷ lệ lấp đầy lớp học | LEFT JOIN, toán học |
| 12 | Phân phối điểm số (Thống kê) | PERCENTILE_CONT, STDDEV |
| 13 | Khối lượng công việc giảng viên | STRING_AGG, SUM |
| 14 | Cảnh báo học viên rủi ro cao | CTE có điều kiện lọc |
| 15 | Tính điểm GPA tự động | Window frame (ROWS BETWEEN) |
| 16 | So sánh kết quả giữa các học kỳ | Cross-semester aggregation |
| 17 | Xếp hạng khóa học phổ biến | RANK với PARTITION |

### 📝 Mã Nguồn Chi Tiết Của Các Truy Vấn

Bấm để xem ngay code SQL của bất kỳ báo cáo nào:

Click to expand and view the exact SQL code for any of the 17 queries:

<details>
<summary><b>Query 1: Average Score Per Course</b> (JOIN, GROUP BY, AVG)</summary>

```sql
SELECT
    c.course_code, c.course_name,
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
```
</details>


<details>
<summary><b>Query 2: Course Completion Rate</b> (CASE WHEN, NULLIF)</summary>

```sql
SELECT
    c.course_code, c.course_name,
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
```
</details>


<details>
<summary><b>Query 3: Top 5 Instructors by Student Performance</b> (Multi-JOIN, LIMIT)</summary>

```sql
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
ORDER BY avg_student_score DESC LIMIT 5;
```
</details>


<details>
<summary><b>Query 4: Lowest Attendance Students</b> (Conditional Aggregation)</summary>

```sql
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
ORDER BY attendance_rate_pct ASC LIMIT 10;
```
</details>


<details>
<summary><b>Query 5: Monthly Enrollment Trends</b> (TO_CHAR, Date functions)</summary>

```sql
SELECT
    TO_CHAR(e.enrollment_date, 'YYYY-MM') AS enrollment_month,
    COUNT(e.enrollment_id) AS new_enrollments,
    COUNT(DISTINCT e.student_id) AS unique_students,
    COUNT(DISTINCT e.class_id) AS classes_enrolled
FROM enrollments e
GROUP BY TO_CHAR(e.enrollment_date, 'YYYY-MM')
ORDER BY enrollment_month;
```
</details>


<details>
<summary><b>Query 6: Pass/Fail Rate</b> (CTE, Weighted Averages)</summary>

```sql
WITH weighted_scores AS (
    SELECT
        e.enrollment_id, e.student_id, cl.course_id,
        ROUND(SUM(g.score * g.weight) / NULLIF(SUM(g.weight), 0), 2) AS avg_score
    FROM enrollments e
    JOIN classes cl ON e.class_id = cl.class_id
    JOIN grades g ON e.enrollment_id = g.enrollment_id
    WHERE e.status = 'Completed'
    GROUP BY e.enrollment_id, e.student_id, cl.course_id
)
SELECT
    c.course_code, c.course_name,
    COUNT(ws.enrollment_id) AS total_graded,
    COUNT(CASE WHEN ws.avg_score >= 50 THEN 1 END) AS passed,
    COUNT(CASE WHEN ws.avg_score < 50 THEN 1 END) AS failed,
    ROUND(
        COUNT(CASE WHEN ws.avg_score >= 50 THEN 1 END) * 100.0
        / NULLIF(COUNT(ws.enrollment_id), 0), 2
    ) AS pass_rate_pct
FROM weighted_scores ws
JOIN courses c ON ws.course_id = c.course_id
GROUP BY c.course_code, c.course_name
ORDER BY pass_rate_pct DESC;
```
</details>


<details>
<summary><b>Query 7: Student Ranking</b> (RANK, DENSE_RANK, NTILE)</summary>

```sql
WITH student_scores AS (
    SELECT
        s.student_id, s.first_name || ' ' || s.last_name AS student_name,
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
    student_id, student_name, course_name, weighted_avg,
    RANK() OVER (PARTITION BY course_name ORDER BY weighted_avg DESC) AS rank,
    DENSE_RANK() OVER (ORDER BY weighted_avg DESC) AS dense_rank,
    NTILE(4) OVER (ORDER BY weighted_avg DESC) AS quartile
FROM student_scores
ORDER BY course_name, rank;
```
</details>


<details>
<summary><b>Query 8: Revenue Analysis by Course</b> (Window Functions)</summary>

```sql
SELECT
    c.course_code, c.course_name, c.tuition_fee,
    COUNT(e.enrollment_id) AS total_enrollments,
    c.tuition_fee * COUNT(e.enrollment_id) AS total_revenue,
    RANK() OVER (ORDER BY c.tuition_fee * COUNT(e.enrollment_id) DESC) AS revenue_rank
FROM courses c
JOIN classes cl ON c.course_id = cl.course_id
JOIN enrollments e ON cl.class_id = e.class_id
WHERE e.status != 'Dropped'
GROUP BY c.course_code, c.course_name, c.tuition_fee
ORDER BY total_revenue DESC;
```
</details>


<details>
<summary><b>Query 9: Student Performance Across Multiple Courses</b> (STRING_AGG, HAVING)</summary>

```sql
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
```
</details>


<details>
<summary><b>Query 10: Attendance vs Grade Correlation</b> (Multiple CTEs, CASE)</summary>

```sql
WITH att_stats AS (
    SELECT
        e.enrollment_id,
        ROUND(COUNT(CASE WHEN a.status = 'Present' THEN 1 END) * 100.0 / NULLIF(COUNT(a.attendance_id), 0), 2) AS att_pct
    FROM enrollments e JOIN attendance a ON e.enrollment_id = a.enrollment_id GROUP BY e.enrollment_id
),
grade_stats AS (
    SELECT enrollment_id, ROUND(AVG(score), 2) AS avg_score FROM grades GROUP BY enrollment_id
)
SELECT
    s.first_name || ' ' || s.last_name AS student_name,
    c.course_name, att.att_pct, gs.avg_score,
    CASE
        WHEN att.att_pct >= 80 AND gs.avg_score >= 70 THEN 'Tốt'
        WHEN att.att_pct >= 60 AND gs.avg_score >= 50 THEN 'Trung bình'
        ELSE 'Cần cải thiện'
    END AS performance_category
FROM att_stats att
JOIN grade_stats gs ON att.enrollment_id = gs.enrollment_id
JOIN enrollments e ON att.enrollment_id = e.enrollment_id
JOIN students s ON e.student_id = s.student_id
JOIN classes cl ON e.class_id = cl.class_id
JOIN courses c ON cl.course_id = c.course_id
ORDER BY att.att_pct DESC;
```
</details>


<details>
<summary><b>Query 11: Class Capacity Utilization</b> (LEFT JOIN, Calculations)</summary>

```sql
SELECT
    cl.class_code, c.course_name,
    i.first_name || ' ' || i.last_name AS instructor_name,
    cl.max_students,
    COUNT(e.enrollment_id) AS enrolled_count,
    ROUND(COUNT(e.enrollment_id) * 100.0 / cl.max_students, 2) AS utilization_pct,
    cl.max_students - COUNT(e.enrollment_id) AS available_seats
FROM classes cl
JOIN courses c ON cl.course_id = c.course_id
JOIN instructors i ON cl.instructor_id = i.instructor_id
LEFT JOIN enrollments e ON cl.class_id = e.class_id AND e.status != 'Dropped'
GROUP BY cl.class_code, c.course_name, i.first_name, i.last_name, cl.max_students
ORDER BY utilization_pct DESC;
```
</details>


<details>
<summary><b>Query 12: Score Distribution by Assessment Type</b> (PERCENTILE_CONT, STDDEV)</summary>

```sql
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
```
</details>


<details>
<summary><b>Query 13: Instructor Workload Analysis</b> (STRING_AGG, SUM)</summary>

```sql
SELECT
    i.instructor_id,
    i.first_name || ' ' || i.last_name AS instructor_name,
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
```
</details>


<details>
<summary><b>Query 14: Students At Risk</b> (CTE with Conditions)</summary>

```sql
WITH risk_data AS (
    SELECT
        s.student_id, s.first_name || ' ' || s.last_name AS student_name,
        c.course_name,
        ROUND(COUNT(CASE WHEN a.status = 'Present' THEN 1 END) * 100.0 / NULLIF(COUNT(a.attendance_id), 0), 2) AS att_rate,
        ROUND(AVG(g.score), 2) AS avg_score
    FROM students s
    JOIN enrollments e ON s.student_id = e.student_id
    JOIN classes cl ON e.class_id = cl.class_id
    JOIN courses c ON cl.course_id = c.course_id
    LEFT JOIN attendance a ON e.enrollment_id = a.enrollment_id
    LEFT JOIN grades g ON e.enrollment_id = g.enrollment_id
    GROUP BY s.student_id, s.first_name, s.last_name, c.course_name
)
SELECT * FROM risk_data
WHERE att_rate < 70 OR avg_score < 55
ORDER BY avg_score ASC, att_rate ASC;
```
</details>

<details>
<summary><b>Query 15: Cumulative GPA</b> (Moving Average, ROWS BETWEEN)</summary>

```sql
WITH enrollment_scores AS (
    SELECT
        e.student_id,
        s.first_name || ' ' || s.last_name AS student_name,
        e.enrollment_date, c.course_name,
        ROUND(SUM(g.score * g.weight) / NULLIF(SUM(g.weight), 0), 2) AS course_score
    FROM enrollments e
    JOIN students s ON e.student_id = s.student_id
    JOIN classes cl ON e.class_id = cl.class_id
    JOIN courses c ON cl.course_id = c.course_id
    JOIN grades g ON e.enrollment_id = g.enrollment_id
    GROUP BY e.student_id, s.first_name, s.last_name, e.enrollment_date, c.course_name
)
SELECT
    student_id, student_name, course_name, course_score,
    ROUND(AVG(course_score) OVER (
        PARTITION BY student_id ORDER BY enrollment_date
        ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
    ), 2) AS cumulative_avg,
    ROW_NUMBER() OVER (PARTITION BY student_id ORDER BY enrollment_date) AS course_sequence
FROM enrollment_scores
ORDER BY student_id, course_sequence;
```
</details>

<details>
<summary><b>Query 16: Semester-over-Semester Comparison</b> (Cross-semester Aggregation)</summary>

```sql
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
```
</details>

<details>
<summary><b>Query 17: Course Popularity Ranking</b> (RANK with PARTITION)</summary>

```sql
SELECT
    c.category, c.course_code, c.course_name, c.level,
    COUNT(e.enrollment_id) AS enrollment_count,
    RANK() OVER (PARTITION BY c.category ORDER BY COUNT(e.enrollment_id) DESC) AS rank,
    ROUND(
        COUNT(e.enrollment_id) * 100.0 /
        SUM(COUNT(e.enrollment_id)) OVER (PARTITION BY c.category), 2
    ) AS pct_of_category
FROM courses c
JOIN classes cl ON c.course_id = cl.course_id
JOIN enrollments e ON cl.class_id = e.class_id
GROUP BY c.category, c.course_code, c.course_name, c.level
ORDER BY c.category, rank;
```
</details>

---

## 👨‍💻 Author

- **Project**: Learning Data Management and Analytics System
- **Course**: Cơ sở dữ liệu nâng cao (Advanced Database)
- **Institution**: Training Centers in Ho Chi Minh City

---

## 📝 License

This project is for educational purposes. Feel free to use and modify.
