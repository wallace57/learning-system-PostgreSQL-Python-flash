-- ============================================================================
-- CSDL PHÂN TÁN (Distributed Database)
-- Mô phỏng các kỹ thuật phân tán trong PostgreSQL:
--   1. Horizontal Fragmentation – Table Partitioning theo học kỳ
--   2. Vertical Fragmentation   – Tách bảng theo nhóm cột nhạy cảm
--   3. Foreign Data Wrapper     – Truy cập "node từ xa"
--   4. Partition Pruning demo   – Query optimizer chỉ scan đúng shard
-- ============================================================================

-- ── 1. PHÂN MẢNH NGANG (Horizontal Fragmentation) ─────────────────────────
-- Kỹ thuật: chia bảng lớn theo điều kiện → mỗi partition = 1 "shard/node"
-- Ứng dụng: attendance có nhiều bản ghi → phân theo năm học

CREATE TABLE IF NOT EXISTS attendance_distributed (
    attendance_id   BIGSERIAL,
    enrollment_id   INTEGER         NOT NULL,
    session_date    DATE            NOT NULL,
    status          VARCHAR(10)     NOT NULL DEFAULT 'Present'
                    CHECK (status IN ('Present','Absent','Late','Excused')),
    remarks         TEXT,
    created_at      TIMESTAMP       DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (attendance_id, session_date)   -- PK phải bao gồm partition key
) PARTITION BY RANGE (session_date);

-- Mỗi partition = 1 "node" trong hệ thống phân tán
-- Node HK2/HK3 2023-2024
CREATE TABLE IF NOT EXISTS attendance_shard_2023_2024
    PARTITION OF attendance_distributed
    FOR VALUES FROM ('2023-06-01') TO ('2024-09-01');

-- Node HK1 2024-2025
CREATE TABLE IF NOT EXISTS attendance_shard_2024hk1
    PARTITION OF attendance_distributed
    FOR VALUES FROM ('2024-09-01') TO ('2025-01-01');

-- Node HK2 2024-2025
CREATE TABLE IF NOT EXISTS attendance_shard_2024hk2
    PARTITION OF attendance_distributed
    FOR VALUES FROM ('2025-01-01') TO ('2025-05-01');

-- Node HK3 2024-2025
CREATE TABLE IF NOT EXISTS attendance_shard_2024hk3
    PARTITION OF attendance_distributed
    FOR VALUES FROM ('2025-05-01') TO ('2025-09-01');

-- Default partition (dữ liệu tương lai / ngoài phạm vi)
CREATE TABLE IF NOT EXISTS attendance_shard_default
    PARTITION OF attendance_distributed DEFAULT;

-- Index trên từng shard (tương đương index riêng trên mỗi node)
CREATE INDEX IF NOT EXISTS idx_att_dist_2023_2024   ON attendance_shard_2023_2024(enrollment_id);
CREATE INDEX IF NOT EXISTS idx_att_dist_2024hk1     ON attendance_shard_2024hk1(enrollment_id);
CREATE INDEX IF NOT EXISTS idx_att_dist_2024hk2     ON attendance_shard_2024hk2(enrollment_id);
CREATE INDEX IF NOT EXISTS idx_att_dist_2024hk3     ON attendance_shard_2024hk3(enrollment_id);

-- Migrate dữ liệu từ bảng gốc vào partitioned table
INSERT INTO attendance_distributed
    (enrollment_id, session_date, status, remarks, created_at)
SELECT enrollment_id, session_date, status, remarks, created_at
FROM attendance
ON CONFLICT DO NOTHING;

COMMENT ON TABLE attendance_distributed        IS 'Bảng điểm danh phân mảnh ngang theo học kỳ (Horizontal Fragmentation)';
COMMENT ON TABLE attendance_shard_2023_2024    IS 'Shard – Dữ liệu năm học 2023-2024';
COMMENT ON TABLE attendance_shard_2024hk1      IS 'Shard – HK1 2024-2025 (09-12/2024)';
COMMENT ON TABLE attendance_shard_2024hk2      IS 'Shard – HK2 2024-2025 (01-04/2025)';
COMMENT ON TABLE attendance_shard_2024hk3      IS 'Shard – HK3 2024-2025 (05-08/2025)';

-- Demo Partition Pruning: PostgreSQL chỉ scan đúng shard
-- EXPLAIN (ANALYZE, BUFFERS)
SELECT COUNT(*), status
FROM attendance_distributed
WHERE session_date BETWEEN '2024-09-01' AND '2024-12-31'  -- chỉ scan shard_2024hk1
GROUP BY status;

-- Thống kê phân phối dữ liệu trên các shards
SELECT
    tableoid::regclass              AS shard_name,
    COUNT(*)                        AS row_count,
    MIN(session_date)               AS oldest,
    MAX(session_date)               AS newest
FROM attendance_distributed
GROUP BY tableoid ORDER BY oldest;

-- ── 2. PHÂN MẢNH DỌC (Vertical Fragmentation) ────────────────────────────
-- Kỹ thuật: tách các cột nhạy cảm / ít dùng ra node riêng
-- Node chính: students (thông tin chung, truy vấn thường xuyên)
-- Node phụ:   student_sensitive (thông tin riêng tư, ít truy vấn)
CREATE TABLE IF NOT EXISTS student_sensitive (
    student_id          INTEGER PRIMARY KEY
                        REFERENCES students(student_id)
                        ON DELETE CASCADE,
    identity_number     VARCHAR(20),            -- CCCD – node riêng biệt
    emergency_contact   VARCHAR(200),
    health_notes        TEXT,
    scholarship         BOOLEAN DEFAULT FALSE,
    scholarship_pct     NUMERIC(5,2) DEFAULT 0,
    financial_support   BOOLEAN DEFAULT FALSE,
    notes               TEXT,
    -- Chỉ admin mới xem được (mô phỏng node phân tán có phân quyền)
    updated_at          TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

COMMENT ON TABLE student_sensitive IS
    'Vertical Shard – Cột nhạy cảm của học viên (node riêng, phân quyền cao)';

-- Insert sample sensitive data
INSERT INTO student_sensitive (student_id, scholarship, scholarship_pct, financial_support)
SELECT student_id, random() < 0.15, CASE WHEN random() < 0.15 THEN 50.0 ELSE 0 END, random() < 0.05
FROM students
ON CONFLICT DO NOTHING;

-- Distributed JOIN: kết hợp 2 "nodes" (tương tự FDW join trong thực tế)
SELECT s.student_id,
       s.first_name||' '||s.last_name AS full_name,
       s.status,
       ss.scholarship,
       ss.scholarship_pct
FROM students s                    -- Node chính
JOIN student_sensitive ss          -- Node phụ (vertical shard)
     ON s.student_id = ss.student_id
WHERE ss.scholarship = TRUE
ORDER BY ss.scholarship_pct DESC;

-- ── 3. CHI NHÁNH T3H – Mô phỏng phân tán theo địa lý ────────────────────
CREATE TABLE IF NOT EXISTS branches (
    branch_id    SERIAL PRIMARY KEY,
    branch_code  VARCHAR(10) UNIQUE NOT NULL,
    branch_name  VARCHAR(100) NOT NULL,
    address      VARCHAR(200),
    district     VARCHAR(50),
    latitude     DOUBLE PRECISION,
    longitude    DOUBLE PRECISION,
    phone        VARCHAR(15),
    capacity     INTEGER DEFAULT 100,
    opened_date  DATE,
    is_active    BOOLEAN DEFAULT TRUE
);

INSERT INTO branches (branch_code, branch_name, address, district, latitude, longitude, opened_date) VALUES
('T3H-Q1',  'Chi nhánh Quận 1',       '47 Điện Biên Phủ, P.Đakao',            'Quận 1',         10.7873, 106.6988, '2010-01-01'),
('T3H-BTH', 'Chi nhánh Bình Thạnh',   '228 Đinh Tiên Hoàng, P.3',             'Quận Bình Thạnh',10.8075, 106.7081, '2012-06-01'),
('T3H-Q12', 'Chi nhánh Quận 12',      '32 Nguyễn Văn Quá, P.Đ.H.Thuận',      'Quận 12',        10.8728, 106.6547, '2015-03-01'),
('T3H-GV',  'Chi nhánh Gò Vấp',       '55 Phan Văn Trị, P.7',                 'Quận Gò Vấp',    10.8326, 106.6889, '2016-08-01'),
('T3H-TB',  'Chi nhánh Tân Bình',     '12 Cộng Hòa, P.4',                     'Quận Tân Bình',  10.8012, 106.6524, '2018-01-01'),
('T3H-TD',  'Chi nhánh Thủ Đức',      '100 Kha Vạn Cân, P.Linh Trung',        'TP. Thủ Đức',    10.8769, 106.7770, '2020-05-01')
ON CONFLICT DO NOTHING;

-- ── 4. FOREIGN DATA WRAPPER (FDW) – Truy cập node từ xa ──────────────────
-- FDW cho phép truy vấn CSDL khác như bảng local (trong thực tế: khác server)
CREATE EXTENSION IF NOT EXISTS postgres_fdw;
CREATE EXTENSION IF NOT EXISTS file_fdw;

-- Mô phỏng: connect đến "archive node" (trong lab này dùng cùng DB)
-- Trong production: host = địa chỉ IP của node khác
/*
CREATE SERVER archive_node
    FOREIGN DATA WRAPPER postgres_fdw
    OPTIONS (host '10.0.0.2', port '5432', dbname 't3h_archive');

CREATE USER MAPPING FOR CURRENT_USER
    SERVER archive_node
    OPTIONS (user 'archive_reader', password 'readonly123');

-- Bảng nằm trên node archive (transparent access)
CREATE FOREIGN TABLE archived_enrollments_2022 (
    enrollment_id   INTEGER,
    student_id      INTEGER,
    class_id        INTEGER,
    enrollment_date DATE,
    status          VARCHAR(20)
) SERVER archive_node
  OPTIONS (schema_name 'public', table_name 'enrollments_2022');

-- Distributed query: join local + remote transparent
SELECT COUNT(*) FROM archived_enrollments_2022;  -- Query sent to archive_node
*/

-- ── 5. Thống kê sharding ─────────────────────────────────────────────────
-- Minh họa hiệu quả partitioning vs. non-partitioned
SELECT
    'attendance (gốc)'          AS table_name,
    COUNT(*)                    AS total_rows,
    pg_size_pretty(pg_relation_size('attendance')) AS size
FROM attendance
UNION ALL
SELECT
    'attendance_distributed',
    COUNT(*),
    pg_size_pretty(pg_total_relation_size('attendance_distributed'))
FROM attendance_distributed;

-- ============================================================================
-- END: CSDL Phân tán
-- ============================================================================
