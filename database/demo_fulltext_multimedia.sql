-- ============================================================================
-- CSDL ĐA PHƯƠNG TIỆN & TÌM KIẾM TOÀN VĂN (Full-Text Search / Multimedia)
-- PostgreSQL hỗ trợ natively:
--   - tsvector / tsquery: full-text search engine tích hợp
--   - GIN / GiST indexes: tìm kiếm nhanh trên tsvector
--   - ts_rank / ts_rank_cd: scoring / relevance ranking
--   - ts_headline: highlight kết quả tìm kiếm
--   - Phrase search, proximity search (PostgreSQL 9.6+)
--   - Multimedia metadata management (JSONB + tsvector)
-- ============================================================================

-- ── 1. Full-Text Search trên Courses & Materials ────────────────────────────

-- Thêm tsvector column vào courses (cho FTS hiệu quả)
ALTER TABLE courses
    ADD COLUMN IF NOT EXISTS fts_doc tsvector;

-- GIN index trên tsvector – tối ưu full-text search
CREATE INDEX IF NOT EXISTS idx_courses_fts ON courses USING GIN(fts_doc);

-- Cập nhật tsvector: kết hợp course_name (A=4, cao nhất) + description (B=2)
UPDATE courses SET fts_doc =
    setweight(to_tsvector('simple', COALESCE(course_name, '')), 'A') ||
    setweight(to_tsvector('simple', COALESCE(description,  '')), 'B') ||
    setweight(to_tsvector('simple', COALESCE(category,     '')), 'C') ||
    setweight(to_tsvector('simple', COALESCE(level,        '')), 'D');

-- Trigger tự động cập nhật fts_doc khi INSERT/UPDATE courses
CREATE OR REPLACE FUNCTION fn_courses_fts_update() RETURNS TRIGGER AS $$
BEGIN
    NEW.fts_doc :=
        setweight(to_tsvector('simple', COALESCE(NEW.course_name, '')), 'A') ||
        setweight(to_tsvector('simple', COALESCE(NEW.description,  '')), 'B') ||
        setweight(to_tsvector('simple', COALESCE(NEW.category,     '')), 'C') ||
        setweight(to_tsvector('simple', COALESCE(NEW.level,        '')), 'D');
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trig_courses_fts ON courses;
CREATE TRIGGER trig_courses_fts
    BEFORE INSERT OR UPDATE ON courses
    FOR EACH ROW EXECUTE FUNCTION fn_courses_fts_update();

COMMENT ON COLUMN courses.fts_doc IS
    'tsvector: full-text search index (A=name, B=desc, C=category, D=level)';

-- ── 2. Bảng Multimedia Content ──────────────────────────────────────────────
-- Mô hình: lưu trữ metadata đa phương tiện (audio, video, image, document)
-- Nội dung thực tế lưu trên object storage (S3/MinIO), DB chỉ lưu metadata
CREATE TABLE IF NOT EXISTS media_assets (
    asset_id        BIGSERIAL PRIMARY KEY,
    course_id       INTEGER REFERENCES courses(course_id),
    asset_type      VARCHAR(20) NOT NULL
                    CHECK (asset_type IN ('video','audio','image','document','subtitle','thumbnail')),
    title           VARCHAR(200) NOT NULL,
    description     TEXT,
    -- Storage info
    storage_url     VARCHAR(500),
    file_size_bytes BIGINT,
    mime_type       VARCHAR(100),
    -- Media-specific metadata (flexible JSONB)
    media_meta      JSONB,
    -- Full-text search
    fts_doc         tsvector,
    -- Timestamps
    uploaded_at     TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- GIN indexes cho FTS và JSONB
CREATE INDEX IF NOT EXISTS idx_media_fts      ON media_assets USING GIN(fts_doc);
CREATE INDEX IF NOT EXISTS idx_media_meta_gin ON media_assets USING GIN(media_meta);
CREATE INDEX IF NOT EXISTS idx_media_type     ON media_assets(asset_type);
CREATE INDEX IF NOT EXISTS idx_media_course   ON media_assets(course_id);

COMMENT ON TABLE media_assets IS
    'Multimedia DB: metadata âm thanh, video, hình ảnh, tài liệu (lưu trên object storage)';

-- Insert sample media assets
INSERT INTO media_assets (course_id, asset_type, title, description, file_size_bytes, mime_type, media_meta) VALUES
-- Video bài giảng
(1, 'video',    'Bài 1: Giới thiệu Microsoft Word 2021',
    'Video hướng dẫn giao diện và các công cụ cơ bản Word 2021',
    524288000, 'video/mp4',
    '{"duration_sec":1800,"resolution":"1920x1080","fps":30,"codec":"H.264","bitrate_kbps":2500,"chapters":["Giao diện","Ribbon","Quick Access"]}'),
(1, 'video',    'Bài 2: Định dạng văn bản và Paragraph',
    'Font, size, color, alignment, spacing, indentation',
    314572800, 'video/mp4',
    '{"duration_sec":2100,"resolution":"1920x1080","fps":30,"codec":"H.264","bitrate_kbps":2000,"subtitles":["vi","en"]}'),
(8, 'video',    'Python Lesson 1: Variables và Data Types',
    'Biến, kiểu dữ liệu int, float, str, bool, list trong Python',
    419430400, 'video/mp4',
    '{"duration_sec":2700,"resolution":"1920x1080","fps":24,"codec":"H.265","bitrate_kbps":1800,"chapters":["Biến","Kiểu số","Chuỗi","List"]}'),
(9, 'video',    'Data Science: Pandas DataFrame Fundamentals',
    'Series, DataFrame, indexing, slicing, groupby, merge trong Pandas',
    629145600, 'video/mp4',
    '{"duration_sec":3600,"resolution":"1920x1080","fps":30,"codec":"H.264","bitrate_kbps":2200,"language":"vi","level":"intermediate"}'),
(10,'video',    'Machine Learning: Linear Regression từ đầu',
    'Gradient descent, cost function, train/test split, scikit-learn',
    524288000, 'video/mp4',
    '{"duration_sec":4500,"resolution":"2560x1440","fps":30,"codec":"H.265","bitrate_kbps":3000,"has_notebook":true}'),
-- Audio (podcast/audio summary)
(8, 'audio',    'Python Quick Review – Audio Summary',
    'Tóm tắt các khái niệm Python cơ bản dạng audio',
    18874368, 'audio/mpeg',
    '{"duration_sec":600,"bitrate_kbps":128,"sample_rate_hz":44100,"channels":2,"codec":"MP3"}'),
-- Images / Diagrams
(1, 'image',    'Word 2021 – Sơ đồ giao diện Ribbon',
    'Hình minh họa Ribbon: File, Home, Insert, Layout, References',
    2097152, 'image/png',
    '{"width":1920,"height":1080,"color_space":"RGB","dpi":96,"format":"PNG"}'),
(8, 'image',    'Python – Mind map cú pháp cơ bản',
    'Mindmap tổng quan: biến, vòng lặp, hàm, class',
    3145728, 'image/jpeg',
    '{"width":3000,"height":2000,"color_space":"RGB","dpi":150,"format":"JPEG","quality":90}'),
(10,'image',    'ML Workflow Diagram',
    'Quy trình Machine Learning: Data → Preprocessing → Model → Evaluate → Deploy',
    1572864, 'image/svg+xml',
    '{"width":1200,"height":800,"vector":true,"format":"SVG"}'),
-- Documents
(3, 'document', 'MISA SME 2024 – Hướng dẫn kế toán doanh nghiệp',
    'Tài liệu PDF 120 trang hướng dẫn sử dụng phần mềm MISA SME 2024',
    8912896, 'application/pdf',
    '{"pages":120,"toc":true,"searchable":true,"version":"2024.1","language":"vi"}'),
(9, 'document', 'Data Science Cheat Sheet – Pandas & NumPy',
    'Cheatsheet các hàm thường dùng trong Pandas và NumPy',
    524288, 'application/pdf',
    '{"pages":4,"printable":true,"version":"2.0","tags":["pandas","numpy","reference"]}'),
-- Subtitles
(8, 'subtitle', 'Python Lesson 1 – Phụ đề tiếng Việt',
    'File phụ đề .SRT cho video Python Lesson 1',
    51200, 'text/plain',
    '{"format":"SRT","language":"vi","sync_to_asset_id":3,"lines":280}'),
-- Thumbnail
(10,'thumbnail','ML Course – Thumbnail 16:9',
    'Ảnh thumbnail cho khóa học Machine Learning',
    204800, 'image/jpeg',
    '{"width":1280,"height":720,"format":"JPEG","optimized_web":true}')
ON CONFLICT DO NOTHING;

-- Cập nhật tsvector cho media_assets
UPDATE media_assets SET fts_doc =
    setweight(to_tsvector('simple', COALESCE(title, '')),       'A') ||
    setweight(to_tsvector('simple', COALESCE(description, '')), 'B') ||
    setweight(to_tsvector('simple', COALESCE(asset_type, '')),  'C');

-- Trigger auto-update FTS cho media_assets
CREATE OR REPLACE FUNCTION fn_media_fts_update() RETURNS TRIGGER AS $$
BEGIN
    NEW.fts_doc :=
        setweight(to_tsvector('simple', COALESCE(NEW.title, '')),       'A') ||
        setweight(to_tsvector('simple', COALESCE(NEW.description, '')), 'B') ||
        setweight(to_tsvector('simple', COALESCE(NEW.asset_type, '')),  'C');
    NEW.updated_at := CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trig_media_fts ON media_assets;
CREATE TRIGGER trig_media_fts
    BEFORE INSERT OR UPDATE ON media_assets
    FOR EACH ROW EXECUTE FUNCTION fn_media_fts_update();

-- ── 3. FULL-TEXT SEARCH QUERIES ─────────────────────────────────────────────

-- Q1: Tìm kiếm khóa học (basic search)
SELECT course_id,
       course_name,
       category,
       level,
       ts_rank(fts_doc, query) AS relevance
FROM courses,
     to_tsquery('simple', 'Python') AS query
WHERE fts_doc @@ query
ORDER BY relevance DESC;

-- Q2: Multi-keyword search – tìm "Python" VÀ "data"
SELECT course_id, course_name, category,
       ts_rank_cd(fts_doc, query) AS rank
FROM courses,
     to_tsquery('simple', 'Python & data') AS query
WHERE fts_doc @@ query
ORDER BY rank DESC;

-- Q3: OR search – tìm "excel" HOẶC "word" HOẶC "misa"
SELECT course_id, course_name, category,
       ts_rank(fts_doc, query) AS rank
FROM courses,
     to_tsquery('simple', 'excel | word | misa') AS query
WHERE fts_doc @@ query
ORDER BY rank DESC;

-- Q4: Prefix search – tìm khóa học bắt đầu với "learn"
SELECT course_id, course_name,
       ts_rank(fts_doc, query) AS rank
FROM courses,
     to_tsquery('simple', 'machine:*') AS query
WHERE fts_doc @@ query
ORDER BY rank DESC;

-- Q5: ts_headline – highlight kết quả trong đoạn văn
SELECT
    course_id,
    course_name,
    ts_headline(
        'simple',
        COALESCE(description, course_name),
        to_tsquery('simple', 'python | data | machine'),
        'StartSel=<mark>, StopSel=</mark>, MaxWords=20, MinWords=5'
    ) AS highlighted_excerpt
FROM courses
WHERE fts_doc @@ to_tsquery('simple', 'python | data | machine')
ORDER BY ts_rank(fts_doc, to_tsquery('simple', 'python | data | machine')) DESC;

-- Q6: Tìm kiếm trong media assets
SELECT
    ma.asset_id,
    c.course_name,
    ma.asset_type,
    ma.title,
    ROUND(ma.file_size_bytes / 1048576.0, 1) AS size_mb,
    ts_rank(ma.fts_doc, query) AS relevance,
    ts_headline('simple', ma.title, query,
        'StartSel=[, StopSel=], MaxFragments=1') AS highlighted_title
FROM media_assets ma
JOIN courses c ON ma.course_id = c.course_id,
     to_tsquery('simple', 'python') AS query
WHERE ma.fts_doc @@ query
ORDER BY relevance DESC;

-- Q7: Phrase search (tìm cụm từ chính xác – PostgreSQL 9.6+)
SELECT course_name, description
FROM courses
WHERE fts_doc @@ phraseto_tsquery('simple', 'machine learning')
   OR fts_doc @@ phraseto_tsquery('simple', 'data science');

-- Q8: Thống kê từ khóa phổ biến (tần suất xuất hiện trong tsvector)
SELECT word, ndoc, nentry
FROM ts_stat(
    'SELECT fts_doc FROM courses WHERE fts_doc IS NOT NULL'
)
WHERE length(word) > 3    -- bỏ từ ngắn
ORDER BY ndoc DESC, nentry DESC
LIMIT 20;

-- Q9: Tìm kiếm kết hợp metadata + FTS (Multimedia query)
-- Tìm video Python có chất lượng HD (1080p trở lên)
SELECT
    ma.asset_id,
    c.course_name,
    ma.title,
    ma.media_meta->>'resolution'                AS resolution,
    (ma.media_meta->>'duration_sec')::INTEGER / 60 AS duration_min,
    ROUND(ma.file_size_bytes / 1048576.0, 0)    AS size_mb
FROM media_assets ma
JOIN courses c ON ma.course_id = c.course_id
WHERE ma.asset_type = 'video'
  AND ma.fts_doc @@ to_tsquery('simple', 'python | data | machine')
  AND (ma.media_meta->>'resolution') IN ('1920x1080','2560x1440','3840x2160')
ORDER BY (ma.media_meta->>'duration_sec')::INTEGER DESC;

-- Q10: Aggregation multimedia – thống kê theo loại media
SELECT
    asset_type,
    COUNT(*)                                      AS asset_count,
    ROUND(SUM(file_size_bytes) / 1073741824.0, 2) AS total_gb,
    ROUND(AVG(file_size_bytes) / 1048576.0, 1)   AS avg_mb,
    COUNT(DISTINCT course_id)                     AS courses_with_media
FROM media_assets
GROUP BY asset_type
ORDER BY total_gb DESC;

-- Q11: websearch_to_tsquery (PostgreSQL 11+) – giống Google search syntax
-- Hỗ trợ: "python data", python -java (NOT), python | excel
SELECT course_id, course_name,
       ts_rank(fts_doc, query) AS rank
FROM courses,
     websearch_to_tsquery('simple', 'python data science') AS query
WHERE fts_doc @@ query
ORDER BY rank DESC;

-- ── 4. Unified Search – Tìm kiếm đa nguồn ──────────────────────────────────
-- Tìm kiếm đồng thời trên courses + media_assets (UNION)
SELECT 'Khóa học'   AS source_type,
       course_id    AS id,
       course_name  AS title,
       category     AS context,
       ts_rank(fts_doc, query) AS relevance
FROM courses,
     to_tsquery('simple', 'python') AS query
WHERE fts_doc @@ query

UNION ALL

SELECT 'Tài liệu học'        AS source_type,
       ma.asset_id::INTEGER  AS id,
       ma.title,
       ma.asset_type         AS context,
       ts_rank(ma.fts_doc, query) AS relevance
FROM media_assets ma,
     to_tsquery('simple', 'python') AS query
WHERE ma.fts_doc @@ query

ORDER BY relevance DESC
LIMIT 15;

-- ── 5. Materialized View – Search Index ─────────────────────────────────────
-- Pre-built search index gộp nhiều bảng lại
CREATE MATERIALIZED VIEW IF NOT EXISTS mv_search_index AS
SELECT
    'course'::TEXT          AS entity_type,
    course_id               AS entity_id,
    course_name             AS title,
    description             AS body,
    category                AS tags,
    setweight(to_tsvector('simple', COALESCE(course_name, '')), 'A') ||
    setweight(to_tsvector('simple', COALESCE(description,  '')), 'B') ||
    setweight(to_tsvector('simple', COALESCE(category,     '')), 'C') AS search_vector
FROM courses

UNION ALL

SELECT
    'media'::TEXT           AS entity_type,
    asset_id                AS entity_id,
    title,
    description             AS body,
    asset_type              AS tags,
    setweight(to_tsvector('simple', COALESCE(title,       '')), 'A') ||
    setweight(to_tsvector('simple', COALESCE(description, '')), 'B') ||
    setweight(to_tsvector('simple', COALESCE(asset_type,  '')), 'C') AS search_vector
FROM media_assets;

CREATE INDEX IF NOT EXISTS idx_search_mv_fts
    ON mv_search_index USING GIN(search_vector);

-- Dùng materialized view để tìm kiếm nhanh
SELECT entity_type, entity_id, title, tags,
       ts_rank(search_vector, query) AS rank
FROM mv_search_index,
     websearch_to_tsquery('simple', 'python video') AS query
WHERE search_vector @@ query
ORDER BY rank DESC
LIMIT 10;

-- Refresh index khi có dữ liệu mới
-- REFRESH MATERIALIZED VIEW CONCURRENTLY mv_search_index;

-- ── 6. Multimedia Storage Stats ─────────────────────────────────────────────
SELECT
    c.course_name,
    COUNT(ma.asset_id)                            AS total_assets,
    COUNT(CASE WHEN ma.asset_type='video'    THEN 1 END) AS videos,
    COUNT(CASE WHEN ma.asset_type='document' THEN 1 END) AS docs,
    COUNT(CASE WHEN ma.asset_type='image'    THEN 1 END) AS images,
    ROUND(SUM(ma.file_size_bytes) / 1073741824.0, 2) AS total_gb,
    -- Tổng thời lượng video (phút)
    SUM(CASE WHEN ma.asset_type='video'
        THEN (ma.media_meta->>'duration_sec')::INTEGER / 60
        ELSE 0 END)                               AS total_video_min
FROM courses c
LEFT JOIN media_assets ma ON c.course_id = ma.course_id
GROUP BY c.course_id, c.course_name
HAVING COUNT(ma.asset_id) > 0
ORDER BY total_gb DESC;

-- ============================================================================
-- END: CSDL Đa phương tiện & Tìm kiếm toàn văn (Full-Text Search)
-- ============================================================================
