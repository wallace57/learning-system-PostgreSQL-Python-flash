-- ============================================================================
-- CSDL KHÔNG QUAN HỆ (NoSQL) – Document Store với JSONB trong PostgreSQL
-- PostgreSQL JSONB cung cấp khả năng document store tương đương MongoDB:
--   - Schema-flexible documents
--   - GIN indexing cho query nhanh
--   - JSON path queries ($, @>)
--   - Aggregation trên nested fields
-- ============================================================================

-- ── 1. Course Materials – Document Store (như MongoDB collection) ──────────
CREATE TABLE IF NOT EXISTS course_materials (
    material_id SERIAL PRIMARY KEY,
    course_id   INTEGER REFERENCES courses(course_id),
    -- JSONB: mỗi tài liệu có schema riêng (flexible)
    content     JSONB NOT NULL,
    created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- GIN index: tăng tốc @>, ?, @@ operations
CREATE INDEX IF NOT EXISTS idx_materials_gin       ON course_materials USING GIN(content);
-- Index trên field cụ thể (expression index)
CREATE INDEX IF NOT EXISTS idx_materials_type      ON course_materials ((content->>'type'));
CREATE INDEX IF NOT EXISTS idx_materials_course    ON course_materials (course_id);

COMMENT ON TABLE course_materials IS
    'NoSQL Document Store: tài liệu học tập với schema linh hoạt (JSONB)';

-- Insert documents – mỗi type có cấu trúc khác nhau (schema-less)
INSERT INTO course_materials (course_id, content) VALUES
-- Loại: video
(1, '{"type":"video","title":"Giới thiệu Word 2021","url":"https://t3h.edu.vn/word-intro","duration_sec":1800,"resolution":"1080p","tags":["word","office","beginner"],"views":1250,"rating":4.7}'),
(1, '{"type":"video","title":"Excel cơ bản – Hàm SUM, AVERAGE","url":"https://t3h.edu.vn/excel-01","duration_sec":2100,"tags":["excel","function","beginner"],"views":3400,"rating":4.8}'),
-- Loại: document (cấu trúc khác video)
(1, '{"type":"document","title":"Tài liệu bài tập Word","format":"PDF","pages":45,"size_mb":2.3,"tags":["word","exercise"],"downloads":890,"author":"T3H Team"}'),
(3, '{"type":"document","title":"Hướng dẫn MISA SME 2024","format":"PDF","pages":120,"size_mb":8.5,"tags":["misa","accounting"],"downloads":2100}'),
-- Loại: code / lab
(8, '{"type":"code","title":"Lab 1: Hello World Python","language":"python","difficulty":"easy","estimated_min":20,"starter_code":"print(\"Hello T3H!\")","tags":["python","lab","beginner"]}'),
(8, '{"type":"code","title":"Lab 5: Pandas DataFrame","language":"python","difficulty":"medium","estimated_min":45,"dependencies":["pandas","numpy"],"tags":["python","pandas","data"]}'),
-- Loại: notebook (Jupyter)
(9, '{"type":"notebook","title":"EDA với Pandas","platform":"jupyter","cells":42,"tags":["pandas","eda","visualization"],"kaggle_url":"https://kaggle.com/t3h/eda-pandas"}'),
(9, '{"type":"dataset","title":"Student Performance Dataset","format":"CSV","rows":1000,"columns":["score","attendance","pass_fail","study_hours"],"source":"t3h_internal","license":"CC-BY"}'),
-- Loại: quiz
(8, '{"type":"quiz","title":"Quiz Python Cơ Bản","questions":20,"time_limit_min":30,"passing_score":70,"attempts_allowed":3,"tags":["python","quiz"]}'),
-- Loại: model (AI/ML specific)
(10, '{"type":"model","title":"Linear Regression Demo","framework":"scikit-learn","accuracy":0.87,"metrics":{"rmse":2.34,"r2":0.87},"tags":["ml","regression"]}'),
(11, '{"type":"model","title":"CNN Image Classifier","framework":"tensorflow","accuracy":0.94,"metrics":{"precision":0.93,"recall":0.94,"f1":0.935},"tags":["cnn","deep-learning","vision"]}')
ON CONFLICT DO NOTHING;

-- ── 2. NOSQL QUERIES ─────────────────────────────────────────────────────

-- Q1: Find by type (tương đương MongoDB: db.materials.find({type:"video"}))
SELECT material_id,
       course_id,
       content->>'title'        AS title,
       content->>'duration_sec' AS duration,
       content->>'rating'       AS rating
FROM course_materials
WHERE content->>'type' = 'video'
ORDER BY (content->>'views')::INTEGER DESC;

-- Q2: Contains operator @> (MongoDB: {tags: {$in: ["python"]}})
SELECT content->>'title' AS title,
       content->>'type'  AS type,
       content->'tags'   AS tags
FROM course_materials
WHERE content @> '{"type": "video"}'
  AND content->'tags' ? 'python';

-- Q3: Nested field access + filter
SELECT c.course_name,
       cm.content->>'title'     AS material_title,
       (cm.content->>'accuracy')::FLOAT AS accuracy
FROM course_materials cm
JOIN courses c ON cm.course_id = c.course_id
WHERE cm.content ? 'accuracy'
  AND (cm.content->>'accuracy')::FLOAT >= 0.90
ORDER BY accuracy DESC;

-- Q4: Aggregate trên JSONB (tương MongoDB aggregation pipeline)
SELECT
    content->>'type'                             AS doc_type,
    COUNT(*)                                     AS total_docs,
    SUM(CASE WHEN content ? 'views'
             THEN (content->>'views')::INTEGER ELSE 0 END) AS total_views,
    ROUND(AVG(CASE WHEN content ? 'rating'
             THEN (content->>'rating')::FLOAT END)::NUMERIC, 2) AS avg_rating
FROM course_materials
GROUP BY content->>'type'
ORDER BY total_docs DESC;

-- Q5: Unpack JSON array (jsonb_array_elements)
SELECT cm.material_id,
       cm.content->>'title'    AS title,
       tag.value::TEXT         AS tag
FROM course_materials cm,
     jsonb_array_elements(cm.content->'tags') AS tag
WHERE tag.value::TEXT ILIKE '"%python%"' OR tag.value::TEXT ILIKE '"%data%"'
ORDER BY title;

-- Q6: Update JSON field (MongoDB: $set)
UPDATE course_materials
SET content = content
    || jsonb_build_object('last_updated', CURRENT_DATE::TEXT,
                          'views', COALESCE((content->>'views')::INTEGER, 0) + 1)
WHERE material_id = 1
  AND content ? 'views';

-- Q7: Delete JSON key (MongoDB: $unset)
UPDATE course_materials
SET content = content - 'starter_code'   -- xóa key nhạy cảm
WHERE content ? 'starter_code';

-- Q8: JSON path query (PostgreSQL 12+)
SELECT material_id, content->>'title',
       jsonb_path_query(content, '$.metrics.*') AS metric_values
FROM course_materials
WHERE content ? 'metrics';

-- ── 3. Student Activity Event Log – Event Sourcing Pattern ────────────────
CREATE TABLE IF NOT EXISTS student_activity_log (
    log_id      BIGSERIAL PRIMARY KEY,
    student_id  INTEGER      NOT NULL,
    event_type  VARCHAR(50)  NOT NULL,
    event_data  JSONB        NOT NULL,
    created_at  TIMESTAMP    DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_activity_student    ON student_activity_log(student_id, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_activity_event_gin  ON student_activity_log USING GIN(event_data);
CREATE INDEX IF NOT EXISTS idx_activity_type       ON student_activity_log(event_type);

-- Events có cấu trúc khác nhau (event sourcing)
INSERT INTO student_activity_log (student_id, event_type, event_data) VALUES
(1,'LOGIN',         '{"ip":"192.168.1.1","device":"mobile","browser":"Chrome Mobile","os":"Android"}'),
(1,'VIEW_MATERIAL', '{"material_id":3,"course_id":8,"time_spent_sec":1800,"completed":true}'),
(1,'SUBMIT_QUIZ',   '{"quiz_id":101,"score":85,"attempts":1,"passed":true,"duration_min":24}'),
(1,'ENROLL',        '{"course_id":9,"payment":"Momo","amount":5500000,"discount_pct":0}'),
(2,'LOGIN',         '{"ip":"10.0.0.5","device":"desktop","browser":"Firefox","os":"Windows"}'),
(2,'COMPLETE_LAB',  '{"lab_id":5,"language":"python","execution_ms":234,"score":100}'),
(2,'SUBMIT_QUIZ',   '{"quiz_id":101,"score":60,"attempts":2,"passed":false,"duration_min":30}'),
(3,'ENROLL',        '{"course_id":3,"payment":"Bank Transfer","amount":2800000,"discount_pct":10}')
ON CONFLICT DO NOTHING;

-- Analytics trên event log (time-series style)
SELECT
    event_type,
    COUNT(*)                      AS event_count,
    COUNT(DISTINCT student_id)    AS unique_students,
    MAX(created_at)               AS last_event
FROM student_activity_log
GROUP BY event_type
ORDER BY event_count DESC;

-- Lấy learning path của 1 học viên (event timeline)
SELECT
    created_at,
    event_type,
    event_data->>'course_id' AS course_id,
    event_data->>'score'     AS score,
    event_data->>'passed'    AS passed
FROM student_activity_log
WHERE student_id = 1
ORDER BY created_at;

-- ── 4. System Configuration – Key-Value Store (Redis-like in PostgreSQL) ──
CREATE TABLE IF NOT EXISTS system_config (
    config_key    VARCHAR(100) PRIMARY KEY,
    config_value  JSONB NOT NULL,
    description   TEXT,
    updated_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

INSERT INTO system_config (config_key, config_value, description) VALUES
('pass_threshold',    '{"score": 50}',                        'Điểm đậu tối thiểu'),
('grading_weights',   '{"midterm":0.3,"final":0.4,"project":0.3}', 'Trọng số điểm'),
('attendance_min',    '{"pct": 70}',                          'Tỷ lệ điểm danh tối thiểu'),
('max_class_size',    '{"students": 35}',                     'Sĩ số tối đa mỗi lớp'),
('semester_schedule', '{"hk1":{"start":"09-01","end":"12-31"},"hk2":{"start":"01-01","end":"04-30"}}', 'Lịch học kỳ')
ON CONFLICT DO NOTHING;

-- Đọc config (như Redis GET)
SELECT config_value->>'score' AS pass_threshold
FROM system_config WHERE config_key = 'pass_threshold';

-- ============================================================================
-- END: CSDL Không quan hệ (NoSQL / Document Store)
-- ============================================================================
