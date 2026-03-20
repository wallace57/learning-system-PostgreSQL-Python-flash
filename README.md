# 📚 Learning Data Management and Analytics System
### Hệ thống Quản lý Dữ liệu Học tập và Phân tích cho các Trung tâm Đào tạo tại TP.HCM

---

## 📖 Mô tả dự án / Project Description

Dự án xây dựng hệ thống cơ sở dữ liệu quản lý dữ liệu học tập cho các trung tâm đào tạo tại Thành phố Hồ Chí Minh. Hệ thống bao gồm quản lý sinh viên, khóa học, giảng viên, lớp học, đăng ký, điểm danh và điểm số.

This project implements a comprehensive database system for managing learning data at training centers in Ho Chi Minh City. It covers student management, course catalog, instructor assignments, class scheduling, enrollment tracking, attendance monitoring, and grade analytics.

---

## 🛠️ Tech Stack

| Component | Technology |
|-----------|-----------|
| Database | PostgreSQL 14+ |
| Language | SQL (PL/pgSQL) |
| Editor | Visual Studio Code |
| Extensions | SQLTools, PostgreSQL (VSCode) |
| Version Control | Git & GitHub |

---

## 📁 Project Structure

```
learning-data-system/
├── database/
│   ├── schema.sql        # Table definitions (DDL)
│   ├── insert_data.sql   # Sample data (7,434 rows)
│   ├── queries.sql       # 17 analytics queries
│   └── index.sql         # Indexes & EXPLAIN ANALYZE
├── data/                 # Exported data (CSV, JSON)
├── diagrams/             # ER diagrams & architecture
├── report/               # Project reports & documentation
├── .gitignore
└── README.md
```

---

## 🗄️ Database Schema

### Entity-Relationship Overview

```
Students ──┐
            ├── Enrollments ──┬── Attendance
Courses ──┐ │                 └── Grades
          ├── Classes
Instructors ┘
```

### Tables

| Table | Description | Key Columns |
|-------|-------------|-------------|
| `students` | Student records | student_id, name, email, status |
| `courses` | Course catalog | course_id, course_code, category, level |
| `instructors` | Instructor profiles | instructor_id, specialization |
| `classes` | Class sections | class_id, course_id (FK), instructor_id (FK) |
| `enrollments` | Student-Class registrations | enrollment_id, student_id (FK), class_id (FK) |
| `attendance` | Session attendance tracking | attendance_id, enrollment_id (FK), status |
| `grades` | Assessment scores | grade_id, enrollment_id (FK), score, weight |

---

## 🚀 How to Run

### Prerequisites
- PostgreSQL 14 or higher installed
- VSCode with SQLTools extension (recommended)
- pgAdmin 4 (optional)

### Step-by-Step Setup

**1. Create Database**
```sql
CREATE DATABASE learning_data_system;
```

**2. Connect to the Database**
```bash
psql -U postgres -d learning_data_system
```

**3. Run Schema**
```bash
psql -U postgres -d learning_data_system -f database/schema.sql
```

**4. Load Sample Data**
```bash
psql -U postgres -d learning_data_system -f database/insert_data.sql
```

**5. Create Indexes**
```bash
psql -U postgres -d learning_data_system -f database/index.sql
```

**6. Run Analytics Queries**
```bash
psql -U postgres -d learning_data_system -f database/queries.sql
```

### Using VSCode
1. Install the **SQLTools** and **SQLTools PostgreSQL** extensions
2. Configure a new connection to `learning_data_system`
3. Open any `.sql` file and click **Run on Active Connection**

---

## 📊 Sample Queries

### Average Score per Course
```sql
SELECT c.course_name, ROUND(AVG(g.score), 2) AS avg_score
FROM courses c
JOIN classes cl ON c.course_id = cl.course_id
JOIN enrollments e ON cl.class_id = e.class_id
JOIN grades g ON e.enrollment_id = g.enrollment_id
GROUP BY c.course_name
ORDER BY avg_score DESC;
```

### Student Ranking with Window Functions
```sql
SELECT student_name, course_name, weighted_avg,
       RANK() OVER (PARTITION BY course_name ORDER BY weighted_avg DESC) AS rank
FROM student_scores;
```

### Monthly Enrollment Trends
```sql
SELECT TO_CHAR(enrollment_date, 'YYYY-MM') AS month,
       COUNT(*) AS new_enrollments
FROM enrollments
GROUP BY TO_CHAR(enrollment_date, 'YYYY-MM')
ORDER BY month;
```

---

## 📈 Analytics Queries Included

| # | Query | Techniques Used |
|---|-------|----------------|
| 1 | Average score per course | JOIN, GROUP BY, AVG |
| 2 | Course completion rate | CASE WHEN, NULLIF |
| 3 | Top 5 instructors | Multi-JOIN, LIMIT |
| 4 | Lowest attendance students | Conditional aggregation |
| 5 | Monthly enrollment trends | TO_CHAR, DATE functions |
| 6 | Pass/fail rate | CTE, weighted averages |
| 7 | Student ranking | RANK, DENSE_RANK, NTILE |
| 8 | Revenue analysis | Window functions |
| 9 | Multi-course performance | STRING_AGG, HAVING |
| 10 | Attendance vs grades | Multiple CTEs, CASE |
| 11 | Class capacity utilization | LEFT JOIN, calculations |
| 12 | Score distribution | PERCENTILE_CONT, STDDEV |
| 13 | Instructor workload | STRING_AGG, SUM |
| 14 | At-risk students | CTE with conditions |
| 15 | Cumulative GPA | Window frame (ROWS BETWEEN) |
| 16 | Semester comparison | Cross-semester aggregation |
| 17 | Course popularity ranking | RANK with PARTITION |

---

## 👨‍💻 Author

- **Project**: Learning Data Management and Analytics System
- **Course**: Cơ sở dữ liệu nâng cao (Advanced Database)
- **Institution**: Training Centers in Ho Chi Minh City

---

## 📝 License

This project is for educational purposes. Feel free to use and modify.
