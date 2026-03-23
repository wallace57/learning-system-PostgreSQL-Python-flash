-- ============================================================================
-- CSDL KHÔNG GIAN (Spatial Database) – PostGIS trong PostgreSQL
-- PostGIS cung cấp:
--   - Kiểu dữ liệu hình học: POINT, LINESTRING, POLYGON, GEOMETRY
--   - Spatial indexes: GiST
--   - Spatial functions: ST_Distance, ST_DWithin, ST_Buffer, ST_Intersects
--   - Coordinate Reference Systems (SRID)
-- ============================================================================

-- ── 0. Extensions ──────────────────────────────────────────────────────────
CREATE EXTENSION IF NOT EXISTS postgis;
CREATE EXTENSION IF NOT EXISTS postgis_topology;   -- optional: topology model

-- Kiểm tra version PostGIS
SELECT postgis_version(), postgis_full_version();

-- ── 1. Thêm cột GEOMETRY vào bảng branches ─────────────────────────────────
-- WGS-84 (SRID 4326): hệ tọa độ GPS phổ biến nhất
ALTER TABLE branches
    ADD COLUMN IF NOT EXISTS geom GEOMETRY(POINT, 4326);

-- Tạo spatial index (GiST) – bắt buộc cho spatial query hiệu quả
CREATE INDEX IF NOT EXISTS idx_branches_geom ON branches USING GiST(geom);

-- Cập nhật geometry từ lat/lng đã có
UPDATE branches
SET geom = ST_SetSRID(ST_MakePoint(longitude, latitude), 4326)
WHERE latitude IS NOT NULL AND longitude IS NOT NULL;

COMMENT ON COLUMN branches.geom IS 'Vị trí địa lý chi nhánh (POINT, WGS-84 SRID 4326)';

-- Thêm dữ liệu geometry cho các chi nhánh
-- (đảm bảo branches table đã có dữ liệu từ demo_distributed.sql)
SELECT branch_code, branch_name,
       ST_AsText(geom)    AS wkt,
       ST_AsGeoJSON(geom) AS geojson
FROM branches
WHERE geom IS NOT NULL
ORDER BY branch_code;

-- ── 2. Bảng Student Home Location – CSDL Không gian học viên ────────────────
CREATE TABLE IF NOT EXISTS student_locations (
    student_id  INTEGER PRIMARY KEY REFERENCES students(student_id) ON DELETE CASCADE,
    district    VARCHAR(50),
    geom        GEOMETRY(POINT, 4326),  -- vị trí nhà học viên
    created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_student_loc_geom ON student_locations USING GiST(geom);

COMMENT ON TABLE student_locations IS
    'Vị trí địa lý học viên – dùng cho phân tích gần chi nhánh (Spatial DB demo)';

-- Insert sample locations (TP.HCM area)
INSERT INTO student_locations (student_id, district, geom)
SELECT
    s.student_id,
    CASE (ROW_NUMBER() OVER (ORDER BY s.student_id) % 12)
        WHEN 0  THEN 'Quận 1'
        WHEN 1  THEN 'Quận 3'
        WHEN 2  THEN 'Quận Bình Thạnh'
        WHEN 3  THEN 'Quận Gò Vấp'
        WHEN 4  THEN 'Quận Tân Bình'
        WHEN 5  THEN 'TP. Thủ Đức'
        WHEN 6  THEN 'Quận 12'
        WHEN 7  THEN 'Quận Phú Nhuận'
        WHEN 8  THEN 'Quận Bình Dương'
        WHEN 9  THEN 'Quận 7'
        WHEN 10 THEN 'Quận Tân Phú'
        ELSE         'Quận 10'
    END,
    ST_SetSRID(
        ST_MakePoint(
            -- Longitude: 106.60–106.85 (TP.HCM)
            106.60 + (s.student_id % 100) * 0.0025,
            -- Latitude:  10.70–10.90
            10.70  + (s.student_id % 80)  * 0.0025
        ), 4326
    )
FROM students s
ON CONFLICT DO NOTHING;

-- ── 3. SPATIAL QUERIES ─────────────────────────────────────────────────────

-- Q1: Khoảng cách giữa các chi nhánh T3H (ST_Distance → geography)
-- Dùng ::geography để tính khoảng cách thực (metres) theo ellipsoid WGS-84
SELECT
    b1.branch_name                                          AS tu_chi_nhanh,
    b2.branch_name                                          AS den_chi_nhanh,
    ROUND(
        (ST_Distance(b1.geom::geography, b2.geom::geography)
        / 1000.0)::NUMERIC, 2
    )                                                       AS khoang_cach_km
FROM branches b1
CROSS JOIN branches b2
WHERE b1.branch_id < b2.branch_id   -- tránh trùng lặp
  AND b1.geom IS NOT NULL
  AND b2.geom IS NOT NULL
ORDER BY khoang_cach_km;

-- Q2: Chi nhánh gần nhau nhất (closest pair)
SELECT
    b1.branch_name  AS chi_nhanh_1,
    b2.branch_name  AS chi_nhanh_2,
    ROUND((ST_Distance(b1.geom::geography, b2.geom::geography) / 1000.0)::NUMERIC, 2) AS km
FROM branches b1
JOIN branches b2 ON b1.branch_id < b2.branch_id
WHERE b1.geom IS NOT NULL AND b2.geom IS NOT NULL
ORDER BY ST_Distance(b1.geom::geography, b2.geom::geography)
LIMIT 3;

-- Q3: ST_DWithin – Học viên sống trong bán kính 3km từ chi nhánh Q1
-- ST_DWithin trên geography: đơn vị metres → dùng spatial index hiệu quả
SELECT
    s.student_id,
    s.first_name || ' ' || s.last_name  AS student_name,
    sl.district,
    ROUND(
        (ST_Distance(sl.geom::geography,
            (SELECT geom FROM branches WHERE branch_code='T3H-Q1')::geography
        ) / 1000.0)::NUMERIC, 2
    ) AS distance_km
FROM students s
JOIN student_locations sl ON s.student_id = sl.student_id
WHERE ST_DWithin(
    sl.geom::geography,
    (SELECT geom FROM branches WHERE branch_code='T3H-Q1')::geography,
    3000   -- 3000 metres = 3 km
)
ORDER BY distance_km
LIMIT 20;

-- Q4: Tìm chi nhánh gần nhất cho từng học viên (Nearest Neighbor)
-- Dùng DISTINCT ON + ORDER BY ST_Distance – tận dụng spatial index
SELECT DISTINCT ON (s.student_id)
    s.student_id,
    s.first_name || ' ' || s.last_name  AS student_name,
    sl.district                         AS student_district,
    b.branch_name                       AS nearest_branch,
    b.branch_code,
    ROUND((ST_Distance(sl.geom::geography, b.geom::geography) / 1000.0)::NUMERIC, 2) AS dist_km
FROM students s
JOIN student_locations sl ON s.student_id = sl.student_id
CROSS JOIN branches b
WHERE sl.geom IS NOT NULL AND b.geom IS NOT NULL
ORDER BY s.student_id,
         ST_Distance(sl.geom::geography, b.geom::geography)
LIMIT 30;

-- Q5: ST_Buffer – Vùng phủ sóng của từng chi nhánh (bán kính 2km)
-- Dùng để phân tích coverage overlap giữa các chi nhánh
SELECT
    branch_name,
    ST_Area(ST_Buffer(geom::geography, 2000)) / 1e6 AS coverage_km2,
    ST_AsGeoJSON(ST_Buffer(geom, 0.018))            AS buffer_geojson
    -- 0.018 degree ≈ 2km ở vĩ độ 10°
FROM branches
WHERE geom IS NOT NULL
ORDER BY branch_name;

-- Q6: ST_Union / ST_Extent – Bounding box toàn bộ hệ thống chi nhánh
SELECT
    COUNT(*)                            AS total_branches,
    ST_AsText(ST_Extent(geom))          AS bounding_box,
    ST_AsGeoJSON(ST_Extent(geom))       AS bounding_box_geojson,
    ST_AsText(
        ST_Centroid(ST_Collect(geom))
    )                                   AS center_point
FROM branches
WHERE geom IS NOT NULL;

-- Q7: Phân tích phân bổ học viên theo bán kính từ chi nhánh gần nhất
-- Thống kê: bao nhiêu học viên cách chi nhánh gần nhất < 2km, 2-5km, > 5km
WITH nearest_dist AS (
    SELECT DISTINCT ON (s.student_id)
        s.student_id,
        ST_Distance(sl.geom::geography, b.geom::geography) / 1000.0 AS dist_km
    FROM students s
    JOIN student_locations sl ON s.student_id = sl.student_id
    CROSS JOIN branches b
    WHERE sl.geom IS NOT NULL AND b.geom IS NOT NULL
    ORDER BY s.student_id, ST_Distance(sl.geom::geography, b.geom::geography)
)
SELECT
    CASE
        WHEN dist_km < 2   THEN '< 2 km (rất gần)'
        WHEN dist_km < 5   THEN '2–5 km (gần)'
        WHEN dist_km < 10  THEN '5–10 km (trung bình)'
        ELSE                    '> 10 km (xa)'
    END                         AS zone,
    COUNT(*)                    AS student_count,
    ROUND((AVG(dist_km))::NUMERIC, 2)      AS avg_dist_km
FROM nearest_dist
GROUP BY zone
ORDER BY MIN(dist_km);

-- Q8: Cluster phân tích – học viên theo quận (district aggregation)
SELECT
    sl.district,
    COUNT(DISTINCT s.student_id)        AS student_count,
    COUNT(DISTINCT e.enrollment_id)     AS total_enrollments,
    ROUND((AVG(ST_Distance(
        sl.geom::geography,
        (SELECT geom FROM branches ORDER BY ST_Distance(sl.geom::geography, b2.geom::geography) LIMIT 1)::geography
    ) / 1000.0))::NUMERIC, 2)           AS avg_dist_to_nearest_km
FROM student_locations sl
JOIN students s ON sl.student_id = s.student_id
LEFT JOIN enrollments e ON s.student_id = e.student_id
GROUP BY sl.district
ORDER BY student_count DESC;

-- Q9: ST_Intersects – Chi nhánh nào nằm trong vùng trung tâm TP.HCM
-- Định nghĩa "trung tâm" = hình chữ nhật: Q1, Q3, Bình Thạnh, Phú Nhuận
WITH center_zone AS (
    SELECT ST_MakeEnvelope(
        106.680, 10.770,   -- SW corner
        106.720, 10.820,   -- NE corner
        4326
    ) AS geom
)
SELECT b.branch_code, b.branch_name, b.district,
       ST_AsText(b.geom) AS location
FROM branches b, center_zone cz
WHERE ST_Intersects(b.geom, cz.geom)
  AND b.geom IS NOT NULL;

-- Q10: KNN Index Scan – 3 chi nhánh gần nhất từ một điểm tùy ý
-- Điểm tham chiếu: Tân Sơn Nhất (10.8184, 106.6592)
SELECT
    branch_code,
    branch_name,
    district,
    ROUND((ST_Distance(
        geom::geography,
        ST_SetSRID(ST_MakePoint(106.6592, 10.8184), 4326)::geography
    ) / 1000.0)::NUMERIC, 2) AS dist_from_airport_km
FROM branches
WHERE geom IS NOT NULL
ORDER BY geom <-> ST_SetSRID(ST_MakePoint(106.6592, 10.8184), 4326)  -- KNN operator
LIMIT 3;

-- ── 4. View tổng hợp Spatial ────────────────────────────────────────────────
CREATE OR REPLACE VIEW v_branch_spatial_stats AS
SELECT
    b.branch_id,
    b.branch_code,
    b.branch_name,
    b.district,
    b.capacity,
    b.latitude,
    b.longitude,
    ST_AsText(b.geom)                        AS geom_wkt,
    COUNT(DISTINCT sl.student_id)            AS students_within_5km
FROM branches b
LEFT JOIN student_locations sl
    ON ST_DWithin(sl.geom::geography, b.geom::geography, 5000)
WHERE b.geom IS NOT NULL
GROUP BY b.branch_id, b.branch_code, b.branch_name,
         b.district, b.capacity, b.latitude, b.longitude, b.geom
ORDER BY b.branch_id;

SELECT * FROM v_branch_spatial_stats;

-- ── 5. Spatial Metadata ────────────────────────────────────────────────────
-- Kiểm tra spatial_ref_sys (coordinate systems)
SELECT srid, auth_name, auth_srid, srtext
FROM spatial_ref_sys
WHERE srid = 4326;   -- WGS-84 (GPS)

-- Geometry columns catalog
SELECT f_table_name, f_geometry_column, coord_dimension, srid, type
FROM geometry_columns
WHERE f_table_schema = 'public'
ORDER BY f_table_name;

-- ============================================================================
-- END: CSDL Không gian (Spatial Database với PostGIS)
-- ============================================================================
