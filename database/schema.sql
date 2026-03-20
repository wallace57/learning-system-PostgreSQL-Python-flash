-- ============================================================================
-- Learning Data Management and Analytics System
-- for Training Centers in Ho Chi Minh City
-- ============================================================================
-- File: schema.sql
-- Description: Database schema definition (PostgreSQL)
-- Author: Database Engineering Team
-- Created: 2026-03-20
-- ============================================================================

-- Drop tables if they exist (in reverse dependency order)
DROP TABLE IF EXISTS grades CASCADE;
DROP TABLE IF EXISTS attendance CASCADE;
DROP TABLE IF EXISTS enrollments CASCADE;
DROP TABLE IF EXISTS classes CASCADE;
DROP TABLE IF EXISTS instructors CASCADE;
DROP TABLE IF EXISTS courses CASCADE;
DROP TABLE IF EXISTS students CASCADE;

-- ============================================================================
-- 1. STUDENTS TABLE
-- Stores information about students enrolled in training center programs
-- ============================================================================
CREATE TABLE students (
    student_id      SERIAL PRIMARY KEY,
    first_name      VARCHAR(50)     NOT NULL,
    last_name       VARCHAR(50)     NOT NULL,
    email           VARCHAR(100)    NOT NULL UNIQUE,
    phone           VARCHAR(15),
    date_of_birth   DATE            NOT NULL,
    gender          VARCHAR(10)     NOT NULL CHECK (gender IN ('Nam', 'Nữ', 'Khác')),
    address         TEXT,
    enrolled_date   DATE            NOT NULL DEFAULT CURRENT_DATE,
    status          VARCHAR(20)     NOT NULL DEFAULT 'Active'
                    CHECK (status IN ('Active', 'Inactive', 'Graduated', 'Suspended')),
    created_at      TIMESTAMP       NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at      TIMESTAMP       NOT NULL DEFAULT CURRENT_TIMESTAMP
);

COMMENT ON TABLE students IS 'Stores student personal and enrollment information';
COMMENT ON COLUMN students.gender IS 'Nam = Male, Nữ = Female, Khác = Other';

-- ============================================================================
-- 2. COURSES TABLE
-- Stores information about courses offered by the training center
-- ============================================================================
CREATE TABLE courses (
    course_id       SERIAL PRIMARY KEY,
    course_code     VARCHAR(20)     NOT NULL UNIQUE,
    course_name     VARCHAR(150)    NOT NULL,
    description     TEXT,
    credits         INTEGER         NOT NULL CHECK (credits > 0 AND credits <= 10),
    duration_hours  INTEGER         NOT NULL CHECK (duration_hours > 0),
    category        VARCHAR(50)     NOT NULL,
    level           VARCHAR(20)     NOT NULL DEFAULT 'Beginner'
                    CHECK (level IN ('Beginner', 'Intermediate', 'Advanced')),
    tuition_fee     NUMERIC(12, 2)  NOT NULL CHECK (tuition_fee >= 0),
    status          VARCHAR(20)     NOT NULL DEFAULT 'Active'
                    CHECK (status IN ('Active', 'Inactive', 'Archived')),
    created_at      TIMESTAMP       NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at      TIMESTAMP       NOT NULL DEFAULT CURRENT_TIMESTAMP
);

COMMENT ON TABLE courses IS 'Catalog of courses offered by the training center';

-- ============================================================================
-- 3. INSTRUCTORS TABLE
-- Stores information about instructors/trainers
-- ============================================================================
CREATE TABLE instructors (
    instructor_id   SERIAL PRIMARY KEY,
    first_name      VARCHAR(50)     NOT NULL,
    last_name       VARCHAR(50)     NOT NULL,
    email           VARCHAR(100)    NOT NULL UNIQUE,
    phone           VARCHAR(15),
    specialization  VARCHAR(100)    NOT NULL,
    hire_date       DATE            NOT NULL,
    qualification   VARCHAR(100),
    experience_years INTEGER        NOT NULL DEFAULT 0 CHECK (experience_years >= 0),
    status          VARCHAR(20)     NOT NULL DEFAULT 'Active'
                    CHECK (status IN ('Active', 'Inactive', 'On Leave')),
    created_at      TIMESTAMP       NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at      TIMESTAMP       NOT NULL DEFAULT CURRENT_TIMESTAMP
);

COMMENT ON TABLE instructors IS 'Stores instructor/trainer information';

-- ============================================================================
-- 4. CLASSES TABLE
-- Represents specific class sections (a course taught by an instructor in a term)
-- ============================================================================
CREATE TABLE classes (
    class_id        SERIAL PRIMARY KEY,
    class_code      VARCHAR(20)     NOT NULL UNIQUE,
    course_id       INTEGER         NOT NULL,
    instructor_id   INTEGER         NOT NULL,
    semester        VARCHAR(20)     NOT NULL,
    academic_year   VARCHAR(10)     NOT NULL,
    schedule        VARCHAR(100),
    room            VARCHAR(30),
    max_students    INTEGER         NOT NULL DEFAULT 40 CHECK (max_students > 0),
    start_date      DATE            NOT NULL,
    end_date        DATE            NOT NULL,
    status          VARCHAR(20)     NOT NULL DEFAULT 'Active'
                    CHECK (status IN ('Active', 'Completed', 'Cancelled')),
    created_at      TIMESTAMP       NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at      TIMESTAMP       NOT NULL DEFAULT CURRENT_TIMESTAMP,

    -- Foreign Keys
    CONSTRAINT fk_classes_course
        FOREIGN KEY (course_id) REFERENCES courses(course_id)
        ON UPDATE CASCADE ON DELETE RESTRICT,
    CONSTRAINT fk_classes_instructor
        FOREIGN KEY (instructor_id) REFERENCES instructors(instructor_id)
        ON UPDATE CASCADE ON DELETE RESTRICT,

    -- Ensure end_date is after start_date
    CONSTRAINT chk_class_dates CHECK (end_date > start_date)
);

COMMENT ON TABLE classes IS 'Specific class sections linking courses to instructors and schedules';

-- ============================================================================
-- 5. ENROLLMENTS TABLE
-- Records student enrollments in classes
-- ============================================================================
CREATE TABLE enrollments (
    enrollment_id   SERIAL PRIMARY KEY,
    student_id      INTEGER         NOT NULL,
    class_id        INTEGER         NOT NULL,
    enrollment_date DATE            NOT NULL DEFAULT CURRENT_DATE,
    status          VARCHAR(20)     NOT NULL DEFAULT 'Enrolled'
                    CHECK (status IN ('Enrolled', 'Completed', 'Dropped', 'Withdrawn')),
    completion_date DATE,
    created_at      TIMESTAMP       NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at      TIMESTAMP       NOT NULL DEFAULT CURRENT_TIMESTAMP,

    -- Foreign Keys
    CONSTRAINT fk_enrollments_student
        FOREIGN KEY (student_id) REFERENCES students(student_id)
        ON UPDATE CASCADE ON DELETE RESTRICT,
    CONSTRAINT fk_enrollments_class
        FOREIGN KEY (class_id) REFERENCES classes(class_id)
        ON UPDATE CASCADE ON DELETE RESTRICT,

    -- Prevent duplicate enrollments
    CONSTRAINT uq_student_class UNIQUE (student_id, class_id)
);

COMMENT ON TABLE enrollments IS 'Student enrollment records for specific classes';

-- ============================================================================
-- 6. ATTENDANCE TABLE
-- Tracks student attendance for each class session
-- ============================================================================
CREATE TABLE attendance (
    attendance_id   SERIAL PRIMARY KEY,
    enrollment_id   INTEGER         NOT NULL,
    session_date    DATE            NOT NULL,
    status          VARCHAR(10)     NOT NULL DEFAULT 'Present'
                    CHECK (status IN ('Present', 'Absent', 'Late', 'Excused')),
    remarks         TEXT,
    created_at      TIMESTAMP       NOT NULL DEFAULT CURRENT_TIMESTAMP,

    -- Foreign Keys
    CONSTRAINT fk_attendance_enrollment
        FOREIGN KEY (enrollment_id) REFERENCES enrollments(enrollment_id)
        ON UPDATE CASCADE ON DELETE CASCADE,

    -- Prevent duplicate attendance records per session
    CONSTRAINT uq_enrollment_session UNIQUE (enrollment_id, session_date)
);

COMMENT ON TABLE attendance IS 'Daily attendance tracking for enrolled students';

-- ============================================================================
-- 7. GRADES TABLE
-- Stores assessment scores and final grades for each enrollment
-- ============================================================================
CREATE TABLE grades (
    grade_id        SERIAL PRIMARY KEY,
    enrollment_id   INTEGER         NOT NULL,
    assessment_type VARCHAR(30)     NOT NULL
                    CHECK (assessment_type IN (
                        'Midterm', 'Final', 'Assignment', 'Quiz', 'Project', 'Participation'
                    )),
    score           NUMERIC(5, 2)   NOT NULL CHECK (score >= 0 AND score <= 100),
    weight          NUMERIC(3, 2)   NOT NULL DEFAULT 1.00
                    CHECK (weight > 0 AND weight <= 1),
    graded_date     DATE            NOT NULL DEFAULT CURRENT_DATE,
    remarks         TEXT,
    created_at      TIMESTAMP       NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at      TIMESTAMP       NOT NULL DEFAULT CURRENT_TIMESTAMP,

    -- Foreign Keys
    CONSTRAINT fk_grades_enrollment
        FOREIGN KEY (enrollment_id) REFERENCES enrollments(enrollment_id)
        ON UPDATE CASCADE ON DELETE CASCADE,

    -- Prevent duplicate assessment types per enrollment
    CONSTRAINT uq_enrollment_assessment UNIQUE (enrollment_id, assessment_type)
);

COMMENT ON TABLE grades IS 'Assessment scores and grades for enrolled students';

-- ============================================================================
-- END OF SCHEMA
-- ============================================================================
