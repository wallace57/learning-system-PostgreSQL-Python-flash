SELECT
    i.instructor_id,
    i.first_name || ' ' || i.last_name AS instructor_name,
    COUNT(DISTINCT e.student_id) AS total_students,
    ROUND(AVG(g.score), 2) AS avg_student_score
FROM instructors i
JOIN classes cl ON i.instructor_id = cl.instructor_id
JOIN enrollments e ON cl.class_id = e.class_id
JOIN grades g ON e.enrollment_id = g.enrollment_id
GROUP BY i.instructor_id, i.first_name, i.last_name
ORDER BY avg_student_score DESC
LIMIT 5;
