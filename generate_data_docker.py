"""
generate_data_docker.py
Phiên bản không cần tương tác – dùng cho Docker / CI
Đọc thông tin kết nối từ biến môi trường:
  DB_HOST, DB_NAME, DB_USER, DB_PASS, DB_PORT
  DATA_PRESET = 't3h' (mặc định) | 'generic'
"""
import os, sys, random, time
from datetime import date, timedelta

try:
    import psycopg2
    from psycopg2.extras import execute_values
except ImportError:
    print("[ERROR] psycopg2 chưa được cài. Chạy: pip install psycopg2-binary")
    sys.exit(1)

# ─── Cấu hình kết nối từ env ─────────────────────────────────────────────────
DB = {
    "host":     os.environ.get("DB_HOST",     "localhost"),
    "dbname":   os.environ.get("DB_NAME",     "learning_data_system"),
    "user":     os.environ.get("DB_USER",     "postgres"),
    "password": os.environ.get("DB_PASS",     "postgres123"),
    "port":     int(os.environ.get("DB_PORT", 5432)),
}
PRESET = os.environ.get("DATA_PRESET", "t3h").lower()

random.seed(2026)

# ─── Pool dữ liệu tiếng Việt ─────────────────────────────────────────────────
HO      = ['Nguyễn','Trần','Lê','Phạm','Hoàng','Huỳnh','Phan','Vũ','Võ','Đặng',
           'Bùi','Đỗ','Hồ','Ngô','Dương','Lý','Trịnh','Đinh','Mai','Trương',
           'Lưu','Tô','Thái','Cao','Tạ','Hà','Triệu','Quách','Đoàn','Thạch']
ĐỆM_NAM = ['Văn','Hữu','Đức','Minh','Quốc','Thành','Xuân','Ngọc','Hùng','Thanh','Hoàng','Anh']
ĐỆM_NỮ  = ['Thị','Ngọc','Thanh','Phương','Hoài','Minh','Thuỳ','Kim','Diệu','Mỹ','Như','Bảo']
TÊN_NAM = ['Minh','Hùng','Đức','Tuấn','Khoa','Phong','Long','Bảo','Nam','Hải',
           'Khôi','Thiện','Trung','Nhật','Duy','Tú','Quân','Phúc','Khải','Khánh']
TÊN_NỮ  = ['Lan','Hương','Mai','Thảo','Linh','Ngọc','Vy','Trang','Yến','Hà',
           'Chi','Thu','Nhung','Loan','Thư','Nhi','Trúc','Diễm','Hiền','Hạnh']
QUẬN_HCM = ['Quận 1','Quận 3','Quận 5','Quận 7','Quận 10','Quận 12',
            'Quận Bình Thạnh','Quận Gò Vấp','Quận Tân Bình','Quận Tân Phú',
            'Quận Phú Nhuận','Quận Bình Tân','TP. Thủ Đức','Huyện Bình Chánh']
T3H_BRANCHES = [
    'Chi nhánh Q.1 - 47 Điện Biên Phủ',
    'Chi nhánh Bình Thạnh - 228 Đinh Tiên Hoàng',
    'Chi nhánh Q.12 - 32 Nguyễn Văn Quá',
    'Chi nhánh Gò Vấp - 55 Phan Văn Trị',
    'Chi nhánh Tân Bình - 12 Cộng Hòa',
    'Chi nhánh Thủ Đức - 100 Kha Vạn Cân',
]

STATUS_STUDENT = ['Active']*82 + ['Inactive']*5 + ['Graduated']*10 + ['Suspended']*3

def vn_phone():
    p = random.choice(['090','091','093','096','097','032','033','034','035','038','070','079'])
    return p + ''.join(str(random.randint(0,9)) for _ in range(7))

def strip_vn(s):
    m = {'ă':'a','â':'a','đ':'d','ê':'e','ô':'o','ơ':'o','ư':'u',
         'á':'a','à':'a','ả':'a','ã':'a','ạ':'a','ắ':'a','ặ':'a',
         'ầ':'a','ậ':'a','é':'e','è':'e','ẹ':'e','ế':'e','ề':'e','ệ':'e',
         'í':'i','ì':'i','ị':'i','ú':'u','ù':'u','ụ':'u','ứ':'u','ừ':'u','ự':'u',
         'ó':'o','ò':'o','ọ':'o','ố':'o','ồ':'o','ộ':'o','ớ':'o','ợ':'o',
         'ý':'y','ỳ':'y','ỵ':'y','Đ':'D'}
    return ''.join(m.get(c, c) for c in s).lower()

def wait_for_db(max_retries=20, delay=3):
    """Chờ PostgreSQL sẵn sàng."""
    for attempt in range(1, max_retries + 1):
        try:
            conn = psycopg2.connect(**DB)
            conn.close()
            print(f"[OK] Kết nối database thành công (lần {attempt})")
            return True
        except psycopg2.OperationalError as e:
            print(f"[WAIT] Chờ database... ({attempt}/{max_retries}) – {e}")
            time.sleep(delay)
    print("[ERROR] Không thể kết nối database sau nhiều lần thử.")
    return False

def log(msg):
    print(f"  ► {msg}", flush=True)

# ─── Courses theo preset ──────────────────────────────────────────────────────
T3H_COURSES = [
    ('VOF101','Tin học văn phòng Word & Excel',   'Microsoft Word, Excel căn bản cho công việc',        2,30,'Office',         'Beginner',    1_200_000,'Active'),
    ('EXL201','Excel nâng cao & Power BI',         'Excel nâng cao, Dashboard, Power BI cơ bản',         3,45,'Office',         'Intermediate',2_500_000,'Active'),
    ('KTM101','Kế toán máy tính (MISA)',           'Kế toán thực hành trên phần mềm MISA SME',           3,45,'Accounting',     'Beginner',    2_800_000,'Active'),
    ('KTM201','Kế toán Excel nâng cao',            'Lập báo cáo tài chính và phân tích với Excel',       3,45,'Accounting',     'Intermediate',2_500_000,'Active'),
    ('WBF101','Lập trình Web Frontend',            'HTML5, CSS3, Bootstrap, JavaScript căn bản',         3,45,'Web Development','Beginner',    3_500_000,'Active'),
    ('WBF201','React.js & TypeScript',             'React Hooks, Redux, TypeScript, REST API',           4,60,'Web Development','Intermediate',5_000_000,'Active'),
    ('WBB201','Lập trình Web Backend Node.js',    'Node.js, Express, MongoDB, RESTful APIs',            4,60,'Web Development','Intermediate',5_000_000,'Active'),
    ('PY101', 'Lập trình Python căn bản',          'Python syntax, OOP, xử lý file, thư viện cơ bản',   3,45,'Programming',    'Beginner',    3_000_000,'Active'),
    ('DS201', 'Data Science với Python',           'Pandas, NumPy, Matplotlib, Scikit-learn',            4,60,'Data Science',   'Intermediate',5_500_000,'Active'),
    ('ML301', 'Machine Learning ứng dụng',         'Supervised/Unsupervised Learning, đánh giá mô hình', 5,75,'Data Science',   'Advanced',    7_000_000,'Active'),
    ('AI301', 'Deep Learning & AI',                'Neural Networks, CNN, RNN, NLP cơ bản',              5,75,'Data Science',   'Advanced',    7_500_000,'Active'),
    ('GDO101','Photoshop & Illustrator',           'Thiết kế đồ họa căn bản, chỉnh sửa hình ảnh',       3,45,'Design',         'Beginner',    3_000_000,'Active'),
    ('CAD101','AutoCAD 2D & 3D',                   'Vẽ kỹ thuật 2D/3D bằng AutoCAD',                    3,45,'Engineering',    'Beginner',    3_200_000,'Active'),
    ('MB101', 'Lập trình Mobile React Native',     'React Native, Expo, kết nối API, publish app',      3,45,'Mobile',         'Intermediate',4_500_000,'Active'),
    ('DB201', 'SQL & Quản trị CSDL',               'SQL nâng cao, PostgreSQL, thiết kế database',        3,45,'Database',       'Intermediate',3_500_000,'Active'),
    ('CY201', 'An ninh mạng & Ethical Hacking',    'Bảo mật hệ thống, kiểm thử xâm nhập cơ bản',       4,60,'Security',       'Intermediate',5_500_000,'Active'),
]

GENERIC_COURSES = [
    ('PY101','Lập trình Python cơ bản',    'Khóa học nền tảng Python',             3,45,'Programming',  'Beginner',    3_500_000,'Active'),
    ('DS201','Khoa học dữ liệu',           'Phân tích dữ liệu với Python',         4,60,'Data Science', 'Intermediate',5_500_000,'Active'),
    ('WD101','Phát triển Web Frontend',    'HTML, CSS, JavaScript',                3,45,'Web Dev',      'Beginner',    4_000_000,'Active'),
    ('WD201','Phát triển Web Backend',     'Node.js, Express, RESTful APIs',       4,60,'Web Dev',      'Intermediate',5_000_000,'Active'),
    ('DB101','Quản trị cơ sở dữ liệu',    'SQL, PostgreSQL, thiết kế database',   3,45,'Database',     'Beginner',    3_500_000,'Active'),
    ('ML301','Machine Learning nâng cao',  'Thuật toán ML và ứng dụng',            5,75,'Data Science', 'Advanced',    7_000_000,'Active'),
    ('PY201','Lập trình Python nâng cao',  'OOP, Design Patterns',                 4,60,'Programming',  'Intermediate',4_500_000,'Active'),
    ('AI301','Trí tuệ nhân tạo',           'Deep Learning và Neural Networks',     5,75,'Data Science', 'Advanced',    7_500_000,'Active'),
    ('MB101','Lập trình Mobile',           'React Native cho mobile',              3,45,'Mobile',       'Beginner',    4_000_000,'Active'),
    ('CY201','An ninh mạng',               'Security fundamentals',                4,60,'Security',     'Intermediate',5_500_000,'Active'),
]

INSTRUCTOR_SPECS_T3H = [
    ('Tin học văn phòng & Office',    'Thạc sĩ Công nghệ thông tin',    8),
    ('Microsoft Excel & Power BI',    'Thạc sĩ Hệ thống thông tin',    10),
    ('Kế toán & MISA',                'Thạc sĩ Kế toán',               12),
    ('Kế toán Excel & Tài chính',     'Thạc sĩ Tài chính',              7),
    ('Web Frontend - HTML/CSS/JS',    'Kỹ sư CNTT',                     5),
    ('React.js & Frontend nâng cao',  'Thạc sĩ Kỹ thuật phần mềm',     6),
    ('Node.js & Backend Development', 'Kỹ sư CNTT',                     7),
    ('Python Programming',            'Thạc sĩ Khoa học máy tính',      9),
    ('Data Science & Analytics',      'Tiến sĩ Khoa học dữ liệu',      11),
    ('Machine Learning',              'Tiến sĩ Học máy',                14),
    ('Deep Learning & AI',            'Tiến sĩ Trí tuệ nhân tạo',      13),
    ('Thiết kế đồ họa',               'Cử nhân Mỹ thuật ứng dụng',      9),
    ('AutoCAD & Kỹ thuật cơ khí',     'Kỹ sư cơ khí',                  15),
    ('Mobile Development',            'Kỹ sư CNTT',                     5),
    ('Database & SQL',                'Thạc sĩ Hệ thống thông tin',     8),
    ('Cybersecurity',                 'Thạc sĩ An ninh mạng',           7),
    ('Python & Data Engineering',     'Thạc sĩ Kỹ thuật phần mềm',     6),
    ('Full Stack Development',        'Kỹ sư CNTT',                     8),
    ('Tin học văn phòng nâng cao',    'Thạc sĩ Công nghệ thông tin',   11),
    ('Cloud & DevOps',                'Kỹ sư Hệ thống',                 9),
]

INSTRUCTOR_SPECS_GENERIC = [
    ('Python & Data Science',  'Thạc sĩ CNTT',              8),
    ('Web Development',        'Kỹ sư CNTT',                 6),
    ('Database & SQL',         'Thạc sĩ Hệ thống thông tin',9),
    ('Machine Learning',       'Tiến sĩ CNTT',              14),
    ('Mobile Development',     'Kỹ sư CNTT',                 5),
    ('Cybersecurity',          'Thạc sĩ An ninh mạng',       7),
    ('AI & Deep Learning',     'Tiến sĩ AI',                13),
    ('Full Stack Development', 'Kỹ sư CNTT',                 8),
    ('Python & Automation',    'Thạc sĩ CNTT',               9),
    ('Data Engineering',       'Thạc sĩ Khoa học dữ liệu',  10),
    ('Cloud Computing',        'Kỹ sư Hệ thống',             6),
    ('DevOps',                 'Kỹ sư CNTT',                  5),
    ('Software Engineering',   'Tiến sĩ CNTT',               12),
    ('UX/UI Design',           'Cử nhân Thiết kế',            7),
    ('Blockchain',             'Thạc sĩ CNTT',                4),
]


def gen_dates(start_str, weeks=12, per_week=2):
    s = date.fromisoformat(start_str)
    days_set = set()
    for w in range(weeks):
        for _ in range(per_week):
            d = s + timedelta(days=w * 7 + random.choice([0, 2, 4]))
            days_set.add(str(d))
    return sorted(days_set)


def run():
    print("=" * 60)
    print(" Learning Data System – Docker Data Generator")
    print(f" Preset: {PRESET.upper()} | DB: {DB['dbname']}@{DB['host']}:{DB['port']}")
    print("=" * 60)

    if not wait_for_db():
        sys.exit(1)

    conn = psycopg2.connect(**DB)
    cur  = conn.cursor()

    # ── Xóa dữ liệu cũ ────────────────────────────────────────────────────────
    print("\n[1/6] Xóa dữ liệu cũ...")
    cur.execute("""
        TRUNCATE grades, attendance, enrollments, classes,
                 instructors, courses, students RESTART IDENTITY CASCADE;
    """)
    conn.commit()

    is_t3h       = (PRESET == "t3h")
    courses_data = T3H_COURSES if is_t3h else GENERIC_COURSES
    instr_specs  = INSTRUCTOR_SPECS_T3H if is_t3h else INSTRUCTOR_SPECS_GENERIC
    n_students   = 300 if is_t3h else 200
    n_semesters  = 5   if is_t3h else 3
    num_courses  = len(courses_data)

    # ── STUDENTS ───────────────────────────────────────────────────────────────
    print(f"\n[2/6] Tạo {n_students} học viên...")
    students = []
    used_emails = set()
    for i in range(1, n_students + 1):
        gender = random.choice(['Nam', 'Nữ'])
        ho_i   = random.choice(HO)
        if gender == 'Nam':
            dem, first = random.choice(ĐỆM_NAM), random.choice(TÊN_NAM)
        else:
            dem, first = random.choice(ĐỆM_NỮ),  random.choice(TÊN_NỮ)

        base = f"{strip_vn(first)}.{strip_vn(ho_i)[:3]}{i:03d}"
        dom  = random.choice(['gmail.com','yahoo.com','outlook.com','email.com'])
        email = f"{base}@{dom}"
        while email in used_emails:
            email = f"{base}{random.randint(1,9)}@{dom}"
        used_emails.add(email)

        dob = f"{random.randint(1995,2005)}-{random.randint(1,12):02d}-{random.randint(1,28):02d}"
        if is_t3h:
            addr = f"{random.choice(T3H_BRANCHES)} | {random.choice(QUẬN_HCM)}, TP.HCM"
        else:
            addr = f"{random.choice(QUẬN_HCM)}, TP.HCM"

        em = random.choice(['2023-06','2023-09','2024-01','2024-03','2024-06','2024-09','2025-01','2025-03'])
        enroll_d = f"{em}-{random.randint(1,28):02d}"
        students.append((first, f"{ho_i} {dem}", email, vn_phone(), dob,
                         gender, addr, enroll_d, random.choice(STATUS_STUDENT)))

    execute_values(cur, """
        INSERT INTO students
            (first_name,last_name,email,phone,date_of_birth,gender,address,enrolled_date,status)
        VALUES %s
    """, students)
    log(f"{n_students} học viên ✓")

    # ── COURSES ────────────────────────────────────────────────────────────────
    print(f"\n[3/6] Tạo {num_courses} khóa học ({PRESET.upper()})...")
    execute_values(cur, """
        INSERT INTO courses
            (course_code,course_name,description,credits,duration_hours,
             category,level,tuition_fee,status)
        VALUES %s
    """, courses_data)
    log(f"{num_courses} khóa học ✓")

    # ── INSTRUCTORS ────────────────────────────────────────────────────────────
    n_instructors = len(instr_specs)
    print(f"\n[4/6] Tạo {n_instructors} giảng viên...")
    instructors = []
    used_gv = set()
    for idx, (spec, qual, exp) in enumerate(instr_specs, 1):
        g     = random.choice(['Nam', 'Nữ'])
        ho_i  = random.choice(HO)
        first = random.choice(TÊN_NAM if g == 'Nam' else TÊN_NỮ)
        dem   = random.choice(ĐỆM_NAM if g == 'Nam' else ĐỆM_NỮ)
        email = f"{strip_vn(first)}.gv{idx:02d}@t3h.edu.vn"
        while email in used_gv:
            email = f"{strip_vn(first)}.gv{idx:02d}x@t3h.edu.vn"
        used_gv.add(email)
        hire = f"{random.randint(2010,2023)}-{random.randint(1,12):02d}-{random.randint(1,28):02d}"
        status = random.choices(['Active', 'On Leave'], weights=[92, 8])[0]
        instructors.append((first, f"{ho_i} {dem}", email, vn_phone(),
                             spec, hire, qual, exp, status))

    execute_values(cur, """
        INSERT INTO instructors
            (first_name,last_name,email,phone,specialization,hire_date,
             qualification,experience_years,status)
        VALUES %s
    """, instructors)
    log(f"{n_instructors} giảng viên ✓")

    # ── CLASSES ────────────────────────────────────────────────────────────────
    semesters_t3h = [
        ('HK2','2023-2024','2024-01-08','2024-04-08','Completed'),
        ('HK3','2023-2024','2024-05-06','2024-08-06','Completed'),
        ('HK1','2024-2025','2024-09-09','2024-12-09','Completed'),
        ('HK2','2024-2025','2025-01-06','2025-04-06','Active'),
        ('HK3','2024-2025','2025-05-05','2025-08-05','Active'),
    ]
    semesters_gen = [
        ('HK1','2024-2025','2024-09-15','2024-12-15','Completed'),
        ('HK2','2024-2025','2025-01-15','2025-04-15','Active'),
        ('HK3','2024-2025','2025-05-15','2025-08-15','Active'),
    ]
    semesters = semesters_t3h if is_t3h else semesters_gen

    schedules = ['T2-T4 18:00-20:30','T3-T5 18:00-20:30','T6-CN 08:00-11:00',
                 'T7-CN 13:00-16:00','T2-T4 08:00-10:30','T3-T5 13:00-15:30']
    rooms = ['A101','A201','A202','B101','B201','B202','Lab1','Lab2','Lab3','C101']

    classes      = []
    classes_meta = []  # (class_id, sem_idx, course_id_1based)
    cls_id = 0
    for sem_idx, (sem, ay, sd, ed, st) in enumerate(semesters):
        for cid in range(1, num_courses + 1):
            cls_id += 1
            iid  = ((cls_id - 1) % n_instructors) + 1
            code = f"T3H-C{cid:02d}-{sem}-{ay[-4:]}"
            mx   = random.choice([20, 25, 30, 35])
            classes.append((code, cid, iid, sem, ay,
                             random.choice(schedules), random.choice(rooms), mx, sd, ed, st))
            classes_meta.append((cls_id, sem_idx, cid))

    print(f"\n[5/6] Tạo {len(classes)} lớp học ({len(semesters)} học kỳ × {num_courses} khóa)...")
    execute_values(cur, """
        INSERT INTO classes
            (class_code,course_id,instructor_id,semester,academic_year,
             schedule,room,max_students,start_date,end_date,status)
        VALUES %s
    """, classes)
    log(f"{len(classes)} lớp học ✓")

    # ── ENROLLMENTS / ATTENDANCE / GRADES ─────────────────────────────────────
    print(f"\n[6/6] Tạo đăng ký, điểm danh, điểm số...")
    session_pools = [gen_dates(s[2]) for s in semesters]

    enroll_rows, att_rows, grade_rows = [], [], []
    used_pairs  = set()
    eid = 0

    for cls_id_val, sem_idx, cid in classes_meta:
        sem_info = semesters[sem_idx]
        is_done  = sem_info[4] == 'Completed'
        n_stu    = random.randint(15, 28)
        pool     = list(range(1, n_students + 1))
        random.shuffle(pool)

        for sid in pool[:n_stu]:
            if (sid, cls_id_val) in used_pairs:
                continue
            used_pairs.add((sid, cls_id_val))
            eid += 1

            base_m = sem_info[2][:7]
            e_date = f"{base_m}-{random.randint(1,14):02d}"

            if is_done:
                e_status = random.choices(['Completed','Dropped','Withdrawn'], weights=[88,8,4])[0]
            else:
                e_status = random.choices(['Enrolled','Dropped'], weights=[95,5])[0]
            c_date = sem_info[3] if e_status == 'Completed' else None

            enroll_rows.append((sid, cls_id_val, e_date, e_status, c_date))

            # Attendance
            n_sess  = random.randint(3,7) if e_status == 'Dropped' else random.randint(10, 20)
            pool_d  = session_pools[sem_idx]
            chosen  = sorted(random.sample(pool_d, min(n_sess, len(pool_d))))
            for sess_d in chosen:
                att_st = random.choices(['Present','Absent','Late','Excused'],
                                        weights=[72,16,8,4])[0]
                remark = None
                if att_st == 'Absent' and random.random() < 0.25:
                    remark = random.choice(['Bận việc gia đình','Nghỉ có phép','Ốm'])
                elif att_st == 'Excused':
                    remark = 'Có giấy xin phép'
                att_rows.append((eid, sess_d, att_st, remark))

            if e_status == 'Dropped':
                if random.random() < 0.4:
                    sc = round(random.uniform(15, 60), 2)
                    grade_rows.append((eid, 'Midterm', sc, 0.30,
                                       f"{base_m}-{random.randint(15,28):02d}", None))
                continue

            # Grade configs theo nhóm khóa học
            if cid in [1, 2, 3, 4]:      # Office / KTM
                configs = [('Midterm',0.30),('Final',0.40),('Assignment',0.30)]
            elif cid in [10, 11]:         # ML / AI
                configs = [('Midterm',0.20),('Final',0.40),('Project',0.30),('Participation',0.10)]
            elif cid in [9, 15, 16]:      # DS / DB / CY
                configs = [('Midterm',0.25),('Final',0.40),('Project',0.25),('Quiz',0.10)]
            else:
                configs = [('Midterm',0.30),('Final',0.40),('Project',0.30)]

            base_sc = max(20, min(98, random.gauss(72, 13)))
            sy = int(sem_info[2][:4])
            sm = int(sem_info[2][5:7])

            for atype, w in configs:
                sc    = round(max(0, min(100, base_sc + random.uniform(-12, 12))), 2)
                off   = {'Midterm':1,'Final':3,'Project':2,'Assignment':2,'Quiz':1,'Participation':0}
                gm    = sm + off.get(atype, 1)
                gy    = sy + (1 if gm > 12 else 0)
                gm    = gm - 12 if gm > 12 else gm
                g_dt  = f"{gy}-{gm:02d}-{random.randint(1,28):02d}"
                remark = None
                if sc >= 90 and random.random() < 0.5:
                    remark = random.choice(['Xuất sắc','Rất tốt'])
                elif sc < 50:
                    remark = random.choice(['Không đạt','Cần cải thiện'])
                grade_rows.append((eid, atype, sc, w, g_dt, remark))

    log(f"Đang insert {len(enroll_rows):,} đăng ký...")
    execute_values(cur, """
        INSERT INTO enrollments (student_id,class_id,enrollment_date,status,completion_date)
        VALUES %s
    """, enroll_rows)

    log(f"Đang insert {len(att_rows):,} điểm danh...")
    execute_values(cur, """
        INSERT INTO attendance (enrollment_id,session_date,status,remarks)
        VALUES %s
    """, att_rows)

    log(f"Đang insert {len(grade_rows):,} điểm số...")
    execute_values(cur, """
        INSERT INTO grades (enrollment_id,assessment_type,score,weight,graded_date,remarks)
        VALUES %s
    """, grade_rows)

    conn.commit()
    cur.close()
    conn.close()

    total = n_students + num_courses + n_instructors + len(classes) \
            + len(enroll_rows) + len(att_rows) + len(grade_rows)

    print("\n" + "=" * 60)
    print(" ✓  Hoàn thành! Thống kê dữ liệu đã nạp:")
    print("=" * 60)
    print(f"   Học viên       : {n_students}")
    print(f"   Khóa học       : {num_courses}  [{PRESET.upper()}]")
    print(f"   Giảng viên     : {n_instructors}")
    print(f"   Lớp học        : {len(classes)}")
    print(f"   Đăng ký        : {len(enroll_rows):,}")
    print(f"   Điểm danh      : {len(att_rows):,}")
    print(f"   Bảng điểm      : {len(grade_rows):,}")
    print(f"   ─────────────────────────────────────")
    print(f"   TỔNG CỘNG      : {total:,} bản ghi")
    print("=" * 60)


if __name__ == "__main__":
    run()
