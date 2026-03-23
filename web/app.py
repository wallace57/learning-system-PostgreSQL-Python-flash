"""
Learning Data System - Web Demo
Flask application for T3H Training Center
"""
import os, json
from decimal import Decimal
import datetime
from flask import Flask, render_template, request, jsonify, redirect, url_for, flash

try:
    import psycopg2
    import psycopg2.extras
except ImportError:
    print("Cài đặt: pip install psycopg2-binary")
    exit(1)

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'ldsystem_t3h_2026')

DB = {
    'host':     os.environ.get('DB_HOST', 'localhost'),
    'dbname':   os.environ.get('DB_NAME', 'learning_data_system'),
    'user':     os.environ.get('DB_USER', 'postgres'),
    'password': os.environ.get('DB_PASS', 'postgres'),
    'port':     int(os.environ.get('DB_PORT', 5432)),
}


# ─── DB helpers ───────────────────────────────────────────────────────────────

def get_conn():
    return psycopg2.connect(**DB)

def qry(sql, params=None, one=False):
    """Execute SELECT, return list of dicts (or single dict if one=True)."""
    try:
        conn = get_conn()
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cur.execute(sql, params)
        result = cur.fetchone() if one else cur.fetchall()
        cur.close()
        conn.close()
        return result
    except Exception as e:
        return None if one else []

def exe(sql, params=None):
    """Execute INSERT/UPDATE/DELETE."""
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(sql, params)
    conn.commit()
    cur.close()
    conn.close()


class CustomEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, Decimal):   return float(o)
        if isinstance(o, (datetime.date, datetime.datetime)): return o.isoformat()
        return super().default(o)

def to_json(data):
    if data is None: return json.dumps([])
    return json.dumps([dict(r) for r in data] if isinstance(data, list) else dict(data), cls=CustomEncoder)


# ─── Context ──────────────────────────────────────────────────────────────────

@app.context_processor
def inject_now():
    return {'now': datetime.date.today().strftime('%d/%m/%Y')}


# ─── DASHBOARD ────────────────────────────────────────────────────────────────

@app.route('/')
def dashboard():
    stats = {}
    try:
        stats['total_students']      = (qry("SELECT COUNT(*) AS n FROM students WHERE status='Active'", one=True) or {}).get('n', 0)
        stats['total_courses']       = (qry("SELECT COUNT(*) AS n FROM courses WHERE status='Active'", one=True) or {}).get('n', 0)
        stats['total_instructors']   = (qry("SELECT COUNT(*) AS n FROM instructors WHERE status='Active'", one=True) or {}).get('n', 0)
        stats['total_enrollments']   = (qry("SELECT COUNT(*) AS n FROM enrollments WHERE status!='Dropped'", one=True) or {}).get('n', 0)

        rev = qry("""
            SELECT COALESCE(SUM(c.tuition_fee),0) AS rev
            FROM enrollments e
            JOIN classes cl ON e.class_id=cl.class_id
            JOIN courses c  ON cl.course_id=c.course_id
            WHERE e.status!='Dropped'
        """, one=True)
        stats['total_revenue'] = float(rev['rev']) if rev else 0

        avg = qry("SELECT ROUND(AVG(score),2) AS avg FROM grades", one=True)
        stats['avg_score'] = float(avg['avg']) if avg and avg['avg'] else 0

        monthly = qry("""
            SELECT TO_CHAR(enrollment_date,'YYYY-MM') AS month, COUNT(*) AS cnt
            FROM enrollments GROUP BY 1 ORDER BY 1 LIMIT 12
        """)

        popular = qry("""
            SELECT c.course_name, COUNT(e.enrollment_id) AS cnt
            FROM courses c
            JOIN classes cl ON c.course_id=cl.course_id
            JOIN enrollments e ON cl.class_id=e.class_id
            WHERE e.status!='Dropped'
            GROUP BY c.course_name ORDER BY cnt DESC LIMIT 6
        """)

        score_dist = qry("""
            SELECT
                COUNT(CASE WHEN score>=90 THEN 1 END) AS excellent,
                COUNT(CASE WHEN score>=70 AND score<90 THEN 1 END) AS good,
                COUNT(CASE WHEN score>=50 AND score<70 THEN 1 END) AS average,
                COUNT(CASE WHEN score<50 THEN 1 END) AS poor
            FROM grades
        """, one=True)

        at_risk = qry("""
            WITH risk AS (
                SELECT s.student_id,
                       s.first_name||' '||s.last_name AS student_name,
                       s.email, c.course_name,
                       ROUND(COUNT(CASE WHEN a.status='Present' THEN 1 END)*100.0
                             /NULLIF(COUNT(a.attendance_id),0),1) AS att_pct,
                       ROUND(AVG(g.score),1) AS avg_score
                FROM students s
                JOIN enrollments e  ON s.student_id=e.student_id
                JOIN classes cl     ON e.class_id=cl.class_id
                JOIN courses c      ON cl.course_id=c.course_id
                LEFT JOIN attendance a ON e.enrollment_id=a.enrollment_id
                LEFT JOIN grades g     ON e.enrollment_id=g.enrollment_id
                GROUP BY s.student_id, s.first_name, s.last_name, s.email, c.course_name
            )
            SELECT * FROM risk WHERE att_pct < 70 OR avg_score < 55
            ORDER BY avg_score ASC NULLS LAST, att_pct ASC LIMIT 8
        """)

        recent_enroll = qry("""
            SELECT s.first_name||' '||s.last_name AS student_name,
                   c.course_name, e.enrollment_date, e.status
            FROM enrollments e
            JOIN students s ON e.student_id=s.student_id
            JOIN classes cl ON e.class_id=cl.class_id
            JOIN courses c  ON cl.course_id=c.course_id
            ORDER BY e.enrollment_date DESC LIMIT 8
        """)

        sem_stats = qry("""
            SELECT cl.semester||'/'||cl.academic_year AS semester,
                   COUNT(DISTINCT e.student_id) AS students,
                   ROUND(AVG(g.score),1) AS avg_score
            FROM classes cl
            JOIN enrollments e ON cl.class_id=e.class_id
            LEFT JOIN grades g  ON e.enrollment_id=g.enrollment_id
            GROUP BY cl.semester, cl.academic_year ORDER BY cl.academic_year, cl.semester
        """)

    except Exception as ex:
        flash(f'Lỗi kết nối database: {ex}', 'danger')
        monthly = popular = at_risk = recent_enroll = sem_stats = []
        score_dist = None

    return render_template('dashboard.html',
        stats=stats,
        monthly_labels=json.dumps([r['month'] for r in monthly], cls=CustomEncoder),
        monthly_data=json.dumps([int(r['cnt']) for r in monthly], cls=CustomEncoder),
        popular_labels=json.dumps([r['course_name'] for r in popular], cls=CustomEncoder),
        popular_data=json.dumps([int(r['cnt']) for r in popular], cls=CustomEncoder),
        score_dist=score_dist,
        at_risk=at_risk,
        recent_enroll=recent_enroll,
        sem_labels=json.dumps([r['semester'] for r in sem_stats], cls=CustomEncoder),
        sem_data=json.dumps([float(r['avg_score'] or 0) for r in sem_stats], cls=CustomEncoder),
    )


# ─── STUDENTS ─────────────────────────────────────────────────────────────────

@app.route('/students')
def students():
    rows = qry("""
        SELECT s.*,
               COUNT(DISTINCT e.enrollment_id) AS num_courses,
               ROUND(AVG(g.score),1) AS avg_score,
               ROUND(COUNT(CASE WHEN a.status='Present' THEN 1 END)*100.0
                     /NULLIF(COUNT(a.attendance_id),0),0) AS att_pct
        FROM students s
        LEFT JOIN enrollments e  ON s.student_id=e.student_id
        LEFT JOIN grades g       ON e.enrollment_id=g.enrollment_id
        LEFT JOIN attendance a   ON e.enrollment_id=a.enrollment_id
        GROUP BY s.student_id
        ORDER BY s.student_id
    """)
    return render_template('students.html', students=rows or [])

@app.route('/students/add', methods=['POST'])
def add_student():
    d = request.form
    try:
        exe("""
            INSERT INTO students
                (first_name,last_name,email,phone,date_of_birth,gender,address,enrolled_date,status)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)
        """, (d['first_name'], d['last_name'], d['email'],
              d.get('phone'), d['date_of_birth'], d['gender'],
              d.get('address'), d['enrolled_date'], d.get('status','Active')))
        flash('Thêm học viên thành công!', 'success')
    except Exception as e:
        flash(f'Lỗi: {e}', 'danger')
    return redirect(url_for('students'))

@app.route('/students/<int:sid>/edit', methods=['POST'])
def edit_student(sid):
    d = request.form
    try:
        exe("""
            UPDATE students SET first_name=%s,last_name=%s,email=%s,phone=%s,
                date_of_birth=%s,gender=%s,address=%s,status=%s,updated_at=NOW()
            WHERE student_id=%s
        """, (d['first_name'], d['last_name'], d['email'],
              d.get('phone'), d['date_of_birth'], d['gender'],
              d.get('address'), d['status'], sid))
        flash('Cập nhật học viên thành công!', 'success')
    except Exception as e:
        flash(f'Lỗi: {e}', 'danger')
    return redirect(url_for('students'))

@app.route('/students/<int:sid>/delete', methods=['POST'])
def delete_student(sid):
    try:
        exe("DELETE FROM students WHERE student_id=%s", (sid,))
        flash('Đã xóa học viên!', 'warning')
    except Exception as e:
        flash(f'Không thể xóa (có dữ liệu liên quan): {e}', 'danger')
    return redirect(url_for('students'))


# ─── COURSES ──────────────────────────────────────────────────────────────────

@app.route('/courses')
def courses():
    rows = qry("""
        SELECT c.*,
               COUNT(DISTINCT cl.class_id) AS num_classes,
               COUNT(DISTINCT e.enrollment_id) AS total_enrollments,
               ROUND(AVG(g.score),1) AS avg_score
        FROM courses c
        LEFT JOIN classes cl    ON c.course_id=cl.course_id
        LEFT JOIN enrollments e ON cl.class_id=e.class_id AND e.status!='Dropped'
        LEFT JOIN grades g      ON e.enrollment_id=g.enrollment_id
        GROUP BY c.course_id
        ORDER BY total_enrollments DESC NULLS LAST
    """)
    return render_template('courses.html', courses=rows or [])

@app.route('/courses/add', methods=['POST'])
def add_course():
    d = request.form
    try:
        exe("""
            INSERT INTO courses
                (course_code,course_name,description,credits,duration_hours,category,level,tuition_fee,status)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)
        """, (d['course_code'], d['course_name'], d.get('description'),
              int(d['credits']), int(d['duration_hours']), d['category'],
              d['level'], float(d['tuition_fee']), d.get('status','Active')))
        flash('Thêm khóa học thành công!', 'success')
    except Exception as e:
        flash(f'Lỗi: {e}', 'danger')
    return redirect(url_for('courses'))

@app.route('/courses/<int:cid>/edit', methods=['POST'])
def edit_course(cid):
    d = request.form
    try:
        exe("""
            UPDATE courses SET course_code=%s,course_name=%s,description=%s,
                credits=%s,duration_hours=%s,category=%s,level=%s,tuition_fee=%s,
                status=%s,updated_at=NOW()
            WHERE course_id=%s
        """, (d['course_code'], d['course_name'], d.get('description'),
              int(d['credits']), int(d['duration_hours']), d['category'],
              d['level'], float(d['tuition_fee']), d['status'], cid))
        flash('Cập nhật khóa học thành công!', 'success')
    except Exception as e:
        flash(f'Lỗi: {e}', 'danger')
    return redirect(url_for('courses'))

@app.route('/courses/<int:cid>/delete', methods=['POST'])
def delete_course(cid):
    try:
        exe("DELETE FROM courses WHERE course_id=%s", (cid,))
        flash('Đã xóa khóa học!', 'warning')
    except Exception as e:
        flash(f'Không thể xóa: {e}', 'danger')
    return redirect(url_for('courses'))


# ─── INSTRUCTORS ──────────────────────────────────────────────────────────────

@app.route('/instructors')
def instructors():
    rows = qry("""
        SELECT i.*,
               COUNT(DISTINCT cl.class_id) AS classes_taught,
               COUNT(DISTINCT e.student_id) AS total_students,
               ROUND(AVG(g.score),1) AS avg_student_score,
               SUM(cr.duration_hours) AS total_hours
        FROM instructors i
        LEFT JOIN classes cl    ON i.instructor_id=cl.instructor_id
        LEFT JOIN courses cr    ON cl.course_id=cr.course_id
        LEFT JOIN enrollments e ON cl.class_id=e.class_id AND e.status!='Dropped'
        LEFT JOIN grades g      ON e.enrollment_id=g.enrollment_id
        GROUP BY i.instructor_id
        ORDER BY avg_student_score DESC NULLS LAST
    """)
    return render_template('instructors.html', instructors=rows or [])

@app.route('/instructors/add', methods=['POST'])
def add_instructor():
    d = request.form
    try:
        exe("""
            INSERT INTO instructors
                (first_name,last_name,email,phone,specialization,hire_date,qualification,experience_years,status)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)
        """, (d['first_name'], d['last_name'], d['email'],
              d.get('phone'), d['specialization'], d['hire_date'],
              d.get('qualification'), int(d.get('experience_years',0)), d.get('status','Active')))
        flash('Thêm giảng viên thành công!', 'success')
    except Exception as e:
        flash(f'Lỗi: {e}', 'danger')
    return redirect(url_for('instructors'))

@app.route('/instructors/<int:iid>/edit', methods=['POST'])
def edit_instructor(iid):
    d = request.form
    try:
        exe("""
            UPDATE instructors SET first_name=%s,last_name=%s,email=%s,phone=%s,
                specialization=%s,hire_date=%s,qualification=%s,experience_years=%s,
                status=%s,updated_at=NOW()
            WHERE instructor_id=%s
        """, (d['first_name'], d['last_name'], d['email'], d.get('phone'),
              d['specialization'], d['hire_date'], d.get('qualification'),
              int(d.get('experience_years',0)), d['status'], iid))
        flash('Cập nhật giảng viên thành công!', 'success')
    except Exception as e:
        flash(f'Lỗi: {e}', 'danger')
    return redirect(url_for('instructors'))

@app.route('/instructors/<int:iid>/delete', methods=['POST'])
def delete_instructor(iid):
    try:
        exe("DELETE FROM instructors WHERE instructor_id=%s", (iid,))
        flash('Đã xóa giảng viên!', 'warning')
    except Exception as e:
        flash(f'Không thể xóa: {e}', 'danger')
    return redirect(url_for('instructors'))


# ─── CLASSES ──────────────────────────────────────────────────────────────────

@app.route('/classes')
def classes():
    rows = qry("""
        SELECT cl.*,
               c.course_name, c.category, c.level,
               i.first_name||' '||i.last_name AS instructor_name,
               COUNT(DISTINCT e.enrollment_id) AS enrolled,
               ROUND(COUNT(DISTINCT e.enrollment_id)*100.0/cl.max_students,0) AS fill_pct
        FROM classes cl
        JOIN courses c     ON cl.course_id=c.course_id
        JOIN instructors i ON cl.instructor_id=i.instructor_id
        LEFT JOIN enrollments e ON cl.class_id=e.class_id AND e.status!='Dropped'
        GROUP BY cl.class_id, c.course_name, c.category, c.level, i.first_name, i.last_name
        ORDER BY cl.class_id
    """)
    courses_list = qry("SELECT course_id, course_code, course_name FROM courses WHERE status='Active' ORDER BY course_name")
    instructors_list = qry("SELECT instructor_id, first_name||' '||last_name AS name FROM instructors WHERE status='Active' ORDER BY last_name")
    return render_template('classes.html', classes=rows or [], courses=courses_list or [], instructors=instructors_list or [])

@app.route('/classes/add', methods=['POST'])
def add_class():
    d = request.form
    try:
        exe("""
            INSERT INTO classes
                (class_code,course_id,instructor_id,semester,academic_year,schedule,room,max_students,start_date,end_date,status)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
        """, (d['class_code'], int(d['course_id']), int(d['instructor_id']),
              d['semester'], d['academic_year'], d.get('schedule'), d.get('room'),
              int(d.get('max_students',40)), d['start_date'], d['end_date'], d.get('status','Active')))
        flash('Thêm lớp học thành công!', 'success')
    except Exception as e:
        flash(f'Lỗi: {e}', 'danger')
    return redirect(url_for('classes'))

@app.route('/classes/<int:clid>/delete', methods=['POST'])
def delete_class(clid):
    try:
        exe("DELETE FROM classes WHERE class_id=%s", (clid,))
        flash('Đã xóa lớp học!', 'warning')
    except Exception as e:
        flash(f'Không thể xóa: {e}', 'danger')
    return redirect(url_for('classes'))


# ─── ENROLLMENTS ──────────────────────────────────────────────────────────────

@app.route('/enrollments')
def enrollments():
    rows = qry("""
        SELECT e.*,
               s.first_name||' '||s.last_name AS student_name,
               c.course_name, cl.class_code, cl.semester, cl.academic_year,
               ROUND(AVG(g.score),1) AS avg_score
        FROM enrollments e
        JOIN students s ON e.student_id=s.student_id
        JOIN classes cl ON e.class_id=cl.class_id
        JOIN courses c  ON cl.course_id=c.course_id
        LEFT JOIN grades g ON e.enrollment_id=g.enrollment_id
        GROUP BY e.enrollment_id, s.first_name, s.last_name, c.course_name, cl.class_code, cl.semester, cl.academic_year
        ORDER BY e.enrollment_date DESC
        LIMIT 300
    """)
    students_list = qry("SELECT student_id, first_name||' '||last_name AS name FROM students WHERE status='Active' ORDER BY last_name LIMIT 300")
    classes_list = qry("""
        SELECT cl.class_id, cl.class_code||' - '||c.course_name AS label
        FROM classes cl JOIN courses c ON cl.course_id=c.course_id
        WHERE cl.status!='Cancelled' ORDER BY cl.class_id DESC LIMIT 50
    """)
    return render_template('enrollments.html', enrollments=rows or [],
                           students=students_list or [], classes=classes_list or [])

@app.route('/enrollments/add', methods=['POST'])
def add_enrollment():
    d = request.form
    try:
        exe("""
            INSERT INTO enrollments (student_id, class_id, enrollment_date, status)
            VALUES (%s,%s,%s,%s)
        """, (int(d['student_id']), int(d['class_id']),
              d['enrollment_date'], d.get('status','Enrolled')))
        flash('Đăng ký thành công!', 'success')
    except Exception as e:
        flash(f'Lỗi: {e}', 'danger')
    return redirect(url_for('enrollments'))

@app.route('/enrollments/<int:eid>/status', methods=['POST'])
def update_enrollment_status(eid):
    status = request.form.get('status')
    try:
        exe("UPDATE enrollments SET status=%s, updated_at=NOW() WHERE enrollment_id=%s", (status, eid))
        flash(f'Cập nhật trạng thái: {status}', 'success')
    except Exception as e:
        flash(f'Lỗi: {e}', 'danger')
    return redirect(url_for('enrollments'))


# ─── GRADES ───────────────────────────────────────────────────────────────────

@app.route('/grades')
def grades():
    rows = qry("""
        SELECT g.*,
               s.first_name||' '||s.last_name AS student_name,
               c.course_name, cl.class_code, cl.semester
        FROM grades g
        JOIN enrollments e ON g.enrollment_id=e.enrollment_id
        JOIN students s    ON e.student_id=s.student_id
        JOIN classes cl    ON e.class_id=cl.class_id
        JOIN courses c     ON cl.course_id=c.course_id
        ORDER BY g.graded_date DESC
        LIMIT 300
    """)
    enrollments_list = qry("""
        SELECT e.enrollment_id,
               s.first_name||' '||s.last_name||' - '||c.course_name AS label
        FROM enrollments e
        JOIN students s ON e.student_id=s.student_id
        JOIN classes cl ON e.class_id=cl.class_id
        JOIN courses c  ON cl.course_id=c.course_id
        WHERE e.status='Enrolled'
        ORDER BY e.enrollment_id DESC LIMIT 100
    """)
    return render_template('grades.html', grades=rows or [], enrollments=enrollments_list or [])

@app.route('/grades/add', methods=['POST'])
def add_grade():
    d = request.form
    try:
        exe("""
            INSERT INTO grades (enrollment_id, assessment_type, score, weight, graded_date, remarks)
            VALUES (%s,%s,%s,%s,%s,%s)
            ON CONFLICT (enrollment_id, assessment_type)
            DO UPDATE SET score=%s, weight=%s, graded_date=%s, remarks=%s, updated_at=NOW()
        """, (int(d['enrollment_id']), d['assessment_type'],
              float(d['score']), float(d.get('weight',1.0)), d['graded_date'], d.get('remarks'),
              float(d['score']), float(d.get('weight',1.0)), d['graded_date'], d.get('remarks')))
        flash('Nhập điểm thành công!', 'success')
    except Exception as e:
        flash(f'Lỗi: {e}', 'danger')
    return redirect(url_for('grades'))


# ─── ANALYTICS PAGE ───────────────────────────────────────────────────────────

@app.route('/analytics')
def analytics():
    return render_template('analytics.html')


# ─── ANALYTICS API (17 queries → JSON) ───────────────────────────────────────

@app.route('/api/q1')   # Avg score per course
def api_q1():
    d = qry("""
        SELECT c.course_code, c.course_name,
               COUNT(DISTINCT e.student_id) AS total_students,
               ROUND(AVG(g.score),2) AS avg_score,
               ROUND(MIN(g.score),2) AS min_score,
               ROUND(MAX(g.score),2) AS max_score
        FROM courses c
        JOIN classes cl ON c.course_id=cl.course_id
        JOIN enrollments e ON cl.class_id=e.class_id
        JOIN grades g ON e.enrollment_id=g.enrollment_id
        GROUP BY c.course_code, c.course_name ORDER BY avg_score DESC
    """)
    return app.response_class(to_json(d), mimetype='application/json')

@app.route('/api/q2')   # Completion rate
def api_q2():
    d = qry("""
        SELECT c.course_code, c.course_name,
               COUNT(e.enrollment_id) AS total_enrollments,
               COUNT(CASE WHEN e.status='Completed' THEN 1 END) AS completed,
               COUNT(CASE WHEN e.status='Dropped' THEN 1 END) AS dropped,
               COUNT(CASE WHEN e.status='Enrolled' THEN 1 END) AS in_progress,
               ROUND(COUNT(CASE WHEN e.status='Completed' THEN 1 END)*100.0
                     /NULLIF(COUNT(e.enrollment_id),0),2) AS completion_rate_pct
        FROM courses c
        JOIN classes cl ON c.course_id=cl.course_id
        JOIN enrollments e ON cl.class_id=e.class_id
        GROUP BY c.course_code, c.course_name ORDER BY completion_rate_pct DESC
    """)
    return app.response_class(to_json(d), mimetype='application/json')

@app.route('/api/q3')   # Top 5 instructors
def api_q3():
    d = qry("""
        SELECT i.instructor_id,
               i.first_name||' '||i.last_name AS instructor_name,
               i.specialization,
               COUNT(DISTINCT e.student_id) AS total_students,
               ROUND(AVG(g.score),2) AS avg_student_score,
               COUNT(DISTINCT cl.class_id) AS classes_taught
        FROM instructors i
        JOIN classes cl ON i.instructor_id=cl.instructor_id
        JOIN enrollments e ON cl.class_id=e.class_id
        JOIN grades g ON e.enrollment_id=g.enrollment_id
        GROUP BY i.instructor_id, i.first_name, i.last_name, i.specialization
        ORDER BY avg_student_score DESC LIMIT 5
    """)
    return app.response_class(to_json(d), mimetype='application/json')

@app.route('/api/q4')   # Lowest attendance
def api_q4():
    d = qry("""
        SELECT s.student_id,
               s.first_name||' '||s.last_name AS student_name,
               COUNT(a.attendance_id) AS total_sessions,
               COUNT(CASE WHEN a.status='Present' THEN 1 END) AS present_count,
               COUNT(CASE WHEN a.status='Absent' THEN 1 END) AS absent_count,
               ROUND(COUNT(CASE WHEN a.status='Present' THEN 1 END)*100.0
                     /NULLIF(COUNT(a.attendance_id),0),2) AS attendance_rate_pct
        FROM students s
        JOIN enrollments e ON s.student_id=e.student_id
        JOIN attendance a ON e.enrollment_id=a.enrollment_id
        GROUP BY s.student_id, s.first_name, s.last_name
        ORDER BY attendance_rate_pct ASC LIMIT 10
    """)
    return app.response_class(to_json(d), mimetype='application/json')

@app.route('/api/q5')   # Monthly enrollment trends
def api_q5():
    d = qry("""
        SELECT TO_CHAR(e.enrollment_date,'YYYY-MM') AS enrollment_month,
               COUNT(e.enrollment_id) AS new_enrollments,
               COUNT(DISTINCT e.student_id) AS unique_students
        FROM enrollments e
        GROUP BY 1 ORDER BY 1
    """)
    return app.response_class(to_json(d), mimetype='application/json')

@app.route('/api/q6')   # Pass/fail rate
def api_q6():
    d = qry("""
        WITH ws AS (
            SELECT e.enrollment_id, cl.course_id,
                   ROUND(SUM(g.score*g.weight)/NULLIF(SUM(g.weight),0),2) AS weighted_avg
            FROM enrollments e
            JOIN classes cl ON e.class_id=cl.class_id
            JOIN grades g ON e.enrollment_id=g.enrollment_id
            WHERE e.status='Completed'
            GROUP BY e.enrollment_id, cl.course_id
        )
        SELECT c.course_code, c.course_name,
               COUNT(ws.enrollment_id) AS total_graded,
               COUNT(CASE WHEN ws.weighted_avg>=50 THEN 1 END) AS passed,
               COUNT(CASE WHEN ws.weighted_avg<50 THEN 1 END) AS failed,
               ROUND(COUNT(CASE WHEN ws.weighted_avg>=50 THEN 1 END)*100.0
                     /NULLIF(COUNT(ws.enrollment_id),0),2) AS pass_rate_pct
        FROM ws JOIN courses c ON ws.course_id=c.course_id
        GROUP BY c.course_code, c.course_name ORDER BY pass_rate_pct DESC
    """)
    return app.response_class(to_json(d), mimetype='application/json')

@app.route('/api/q7')   # Student ranking
def api_q7():
    d = qry("""
        WITH ss AS (
            SELECT s.student_id, s.first_name||' '||s.last_name AS student_name,
                   c.course_name,
                   ROUND(SUM(g.score*g.weight)/NULLIF(SUM(g.weight),0),2) AS weighted_avg
            FROM students s
            JOIN enrollments e ON s.student_id=e.student_id
            JOIN classes cl ON e.class_id=cl.class_id
            JOIN courses c ON cl.course_id=c.course_id
            JOIN grades g ON e.enrollment_id=g.enrollment_id
            GROUP BY s.student_id, s.first_name, s.last_name, c.course_name
        )
        SELECT student_id, student_name, course_name, weighted_avg,
               RANK() OVER (PARTITION BY course_name ORDER BY weighted_avg DESC) AS rank_in_course,
               NTILE(4) OVER (ORDER BY weighted_avg DESC) AS quartile
        FROM ss ORDER BY course_name, rank_in_course LIMIT 50
    """)
    return app.response_class(to_json(d), mimetype='application/json')

@app.route('/api/q8')   # Revenue analysis
def api_q8():
    d = qry("""
        SELECT c.course_code, c.course_name, c.tuition_fee,
               COUNT(e.enrollment_id) AS total_enrollments,
               c.tuition_fee*COUNT(e.enrollment_id) AS total_revenue,
               RANK() OVER (ORDER BY c.tuition_fee*COUNT(e.enrollment_id) DESC) AS revenue_rank
        FROM courses c
        JOIN classes cl ON c.course_id=cl.course_id
        JOIN enrollments e ON cl.class_id=e.class_id
        WHERE e.status!='Dropped'
        GROUP BY c.course_code, c.course_name, c.tuition_fee
        ORDER BY total_revenue DESC
    """)
    return app.response_class(to_json(d), mimetype='application/json')

@app.route('/api/q9')   # Multi-course performance
def api_q9():
    d = qry("""
        SELECT s.student_id, s.first_name||' '||s.last_name AS student_name,
               COUNT(DISTINCT cl.course_id) AS courses_taken,
               ROUND(AVG(g.score),2) AS overall_avg_score,
               STRING_AGG(DISTINCT c.course_name, ', ' ORDER BY c.course_name) AS courses_list
        FROM students s
        JOIN enrollments e ON s.student_id=e.student_id
        JOIN classes cl ON e.class_id=cl.class_id
        JOIN courses c ON cl.course_id=c.course_id
        JOIN grades g ON e.enrollment_id=g.enrollment_id
        GROUP BY s.student_id, s.first_name, s.last_name
        HAVING COUNT(DISTINCT cl.course_id)>=2
        ORDER BY overall_avg_score DESC LIMIT 20
    """)
    return app.response_class(to_json(d), mimetype='application/json')

@app.route('/api/q10')  # Attendance vs grade correlation
def api_q10():
    d = qry("""
        WITH att AS (
            SELECT e.enrollment_id,
                   ROUND(COUNT(CASE WHEN a.status='Present' THEN 1 END)*100.0
                         /NULLIF(COUNT(a.attendance_id),0),2) AS att_pct
            FROM enrollments e
            JOIN attendance a ON e.enrollment_id=a.enrollment_id
            GROUP BY e.enrollment_id
        ),
        gs AS (
            SELECT enrollment_id, ROUND(AVG(score),2) AS avg_score FROM grades GROUP BY 1
        )
        SELECT s.first_name||' '||s.last_name AS student_name,
               c.course_name, att.att_pct, gs.avg_score,
               CASE WHEN att.att_pct>=80 AND gs.avg_score>=70 THEN 'Tốt'
                    WHEN att.att_pct>=60 AND gs.avg_score>=50 THEN 'Trung bình'
                    ELSE 'Cần cải thiện' END AS performance_category
        FROM att
        JOIN gs ON att.enrollment_id=gs.enrollment_id
        JOIN enrollments e ON att.enrollment_id=e.enrollment_id
        JOIN students s ON e.student_id=s.student_id
        JOIN classes cl ON e.class_id=cl.class_id
        JOIN courses c ON cl.course_id=c.course_id
        ORDER BY att.att_pct DESC LIMIT 50
    """)
    return app.response_class(to_json(d), mimetype='application/json')

@app.route('/api/q11')  # Class capacity
def api_q11():
    d = qry("""
        SELECT cl.class_code, c.course_name,
               i.first_name||' '||i.last_name AS instructor_name,
               cl.max_students,
               COUNT(e.enrollment_id) AS enrolled_count,
               ROUND(COUNT(e.enrollment_id)*100.0/cl.max_students,2) AS utilization_pct,
               cl.max_students-COUNT(e.enrollment_id) AS available_seats
        FROM classes cl
        JOIN courses c ON cl.course_id=c.course_id
        JOIN instructors i ON cl.instructor_id=i.instructor_id
        LEFT JOIN enrollments e ON cl.class_id=e.class_id AND e.status!='Dropped'
        GROUP BY cl.class_code, c.course_name, i.first_name, i.last_name, cl.max_students
        ORDER BY utilization_pct DESC
    """)
    return app.response_class(to_json(d), mimetype='application/json')

@app.route('/api/q12')  # Score distribution
def api_q12():
    d = qry("""
        SELECT assessment_type, COUNT(*) AS total_grades,
               ROUND(AVG(score),2) AS avg_score,
               ROUND(STDDEV(score),2) AS std_dev,
               PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY score) AS p25,
               PERCENTILE_CONT(0.50) WITHIN GROUP (ORDER BY score) AS median,
               PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY score) AS p75
        FROM grades GROUP BY assessment_type ORDER BY avg_score DESC
    """)
    return app.response_class(to_json(d), mimetype='application/json')

@app.route('/api/q13')  # Instructor workload
def api_q13():
    d = qry("""
        SELECT i.instructor_id,
               i.first_name||' '||i.last_name AS instructor_name,
               i.specialization,
               COUNT(DISTINCT cl.class_id) AS total_classes,
               COUNT(DISTINCT e.student_id) AS total_students,
               SUM(cr.duration_hours) AS total_teaching_hours
        FROM instructors i
        JOIN classes cl ON i.instructor_id=cl.instructor_id
        JOIN courses cr ON cl.course_id=cr.course_id
        LEFT JOIN enrollments e ON cl.class_id=e.class_id AND e.status!='Dropped'
        GROUP BY i.instructor_id, i.first_name, i.last_name, i.specialization
        ORDER BY total_teaching_hours DESC
    """)
    return app.response_class(to_json(d), mimetype='application/json')

@app.route('/api/q14')  # At-risk students
def api_q14():
    d = qry("""
        WITH risk AS (
            SELECT s.student_id, s.first_name||' '||s.last_name AS student_name,
                   s.email, c.course_name,
                   ROUND(COUNT(CASE WHEN a.status='Present' THEN 1 END)*100.0
                         /NULLIF(COUNT(a.attendance_id),0),2) AS attendance_rate,
                   ROUND(AVG(g.score),2) AS avg_score
            FROM students s
            JOIN enrollments e ON s.student_id=e.student_id
            JOIN classes cl ON e.class_id=cl.class_id
            JOIN courses c ON cl.course_id=c.course_id
            LEFT JOIN attendance a ON e.enrollment_id=a.enrollment_id
            LEFT JOIN grades g ON e.enrollment_id=g.enrollment_id
            GROUP BY s.student_id, s.first_name, s.last_name, s.email, c.course_name
        )
        SELECT * FROM risk WHERE attendance_rate<70 OR avg_score<55
        ORDER BY avg_score ASC NULLS LAST, attendance_rate ASC
    """)
    return app.response_class(to_json(d), mimetype='application/json')

@app.route('/api/q15')  # Cumulative GPA
def api_q15():
    d = qry("""
        WITH es AS (
            SELECT e.student_id, s.first_name||' '||s.last_name AS student_name,
                   e.enrollment_date, c.course_name,
                   ROUND(SUM(g.score*g.weight)/NULLIF(SUM(g.weight),0),2) AS course_score
            FROM enrollments e
            JOIN students s ON e.student_id=s.student_id
            JOIN classes cl ON e.class_id=cl.class_id
            JOIN courses c ON cl.course_id=c.course_id
            JOIN grades g ON e.enrollment_id=g.enrollment_id
            GROUP BY e.student_id, s.first_name, s.last_name, e.enrollment_date, c.course_name
        )
        SELECT student_id, student_name, course_name, course_score,
               ROUND(AVG(course_score) OVER (
                   PARTITION BY student_id ORDER BY enrollment_date
                   ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW),2) AS cumulative_avg,
               ROW_NUMBER() OVER (PARTITION BY student_id ORDER BY enrollment_date) AS course_seq
        FROM es ORDER BY student_id, course_seq LIMIT 60
    """)
    return app.response_class(to_json(d), mimetype='application/json')

@app.route('/api/q16')  # Semester comparison
def api_q16():
    d = qry("""
        SELECT cl.semester, cl.academic_year,
               cl.semester||'/'||cl.academic_year AS label,
               COUNT(DISTINCT e.student_id) AS total_students,
               COUNT(DISTINCT cl.class_id) AS total_classes,
               ROUND(AVG(g.score),2) AS avg_score,
               COUNT(CASE WHEN g.score>=80 THEN 1 END) AS excellent_scores,
               COUNT(CASE WHEN g.score<50 THEN 1 END) AS failing_scores
        FROM classes cl
        JOIN enrollments e ON cl.class_id=e.class_id
        JOIN grades g ON e.enrollment_id=g.enrollment_id
        GROUP BY cl.semester, cl.academic_year
        ORDER BY cl.academic_year, cl.semester
    """)
    return app.response_class(to_json(d), mimetype='application/json')

@app.route('/api/q17')  # Course popularity by category
def api_q17():
    d = qry("""
        SELECT c.category, c.course_code, c.course_name, c.level,
               COUNT(e.enrollment_id) AS enrollment_count,
               RANK() OVER (PARTITION BY c.category ORDER BY COUNT(e.enrollment_id) DESC) AS rank_in_category,
               ROUND(COUNT(e.enrollment_id)*100.0
                     /SUM(COUNT(e.enrollment_id)) OVER (PARTITION BY c.category),2) AS pct_of_category
        FROM courses c
        JOIN classes cl ON c.course_id=cl.course_id
        JOIN enrollments e ON cl.class_id=e.class_id
        GROUP BY c.category, c.course_code, c.course_name, c.level
        ORDER BY c.category, rank_in_category
    """)
    return app.response_class(to_json(d), mimetype='application/json')


if __name__ == '__main__':
    print("="*55)
    print(" Learning Data System - T3H Web Demo")
    print(" URL: http://localhost:5000")
    print("="*55)
    app.run(debug=True, port=5000, host='0.0.0.0')
