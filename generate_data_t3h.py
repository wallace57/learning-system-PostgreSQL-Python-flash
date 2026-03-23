"""
Script tạo dữ liệu mẫu bám theo thực tế Trung tâm Tin học T3H
Website: https://t3h.com.vn/
Yêu cầu: pip install psycopg2-binary
"""
import random
import os
import getpass
from datetime import date, timedelta

try:
    import psycopg2
    from psycopg2.extras import execute_values
except ImportError:
    print("Lỗi: chưa cài psycopg2. Chạy: pip install psycopg2-binary")
    exit(1)

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

QUẬN_HCM = ['Quận 1','Quận 3','Quận 4','Quận 5','Quận 6','Quận 7','Quận 8',
            'Quận 10','Quận 11','Quận 12','Quận Bình Thạnh','Quận Gò Vấp',
            'Quận Tân Bình','Quận Tân Phú','Quận Phú Nhuận','Quận Bình Tân',
            'TP. Thủ Đức','Huyện Nhà Bè','Huyện Bình Chánh','Huyện Củ Chi']

# Chi nhánh T3H thực tế
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
    prefixes = ['090','091','092','093','094','096','097','098','032','033','034','035','036','037','038','039','056','058','070','079']
    return random.choice(prefixes) + ''.join([str(random.randint(0,9)) for _ in range(7)])

def strip_vn(s):
    m = {'ă':'a','â':'a','đ':'d','ê':'e','ô':'o','ơ':'o','ư':'u',
         'á':'a','à':'a','ả':'a','ã':'a','ạ':'a','ắ':'a','ặ':'a','ầ':'a','ậ':'a',
         'é':'e','è':'e','ẹ':'e','ế':'e','ề':'e','ệ':'e',
         'í':'i','ì':'i','ị':'i','ú':'u','ù':'u','ụ':'u','ứ':'u','ừ':'u','ự':'u',
         'ó':'o','ò':'o','ọ':'o','ố':'o','ồ':'o','ộ':'o','ớ':'o','ợ':'o',
         'ý':'y','ỳ':'y','ỵ':'y','Đ':'D'}
    return ''.join(m.get(c,c) for c in s).lower()


def main():
    print("="*60)
    print(" Learning Data System – Dữ liệu mẫu T3H")
    print(" Trung tâm Tin học T3H | t3h.com.vn")
    print("="*60)

    db_name = input("Tên database [learning_data_system]: ").strip() or "learning_data_system"
    db_user = input("Username [postgres]: ").strip() or "postgres"
    db_pass = getpass.getpass(f"Mật khẩu của {db_user}: ")

    try:
        print("\nĐang kết nối database...")
        conn = psycopg2.connect(host="localhost", dbname=db_name, user=db_user, password=db_pass)
        cur  = conn.cursor()
        print("Kết nối thành công!")
    except Exception as e:
        print(f"Không thể kết nối: {e}")
        return

    # Xóa dữ liệu cũ
    print("\nXóa dữ liệu cũ...")
    cur.execute("""
        TRUNCATE grades, attendance, enrollments, classes,
                 instructors, courses, students RESTART IDENTITY CASCADE;
    """)
    conn.commit()

    # ──────────────────────────────────────────────────────────────
    # 1. STUDENTS  (300 học viên)
    # ──────────────────────────────────────────────────────────────
    print("Tạo học viên...")
    students = []
    used_emails = set()
    for i in range(1, 301):
        gender  = random.choice(['Nam','Nữ'])
        ho_i    = random.choice(HO)
        if gender == 'Nam':
            dem   = random.choice(ĐỆM_NAM)
            first = random.choice(TÊN_NAM)
        else:
            dem   = random.choice(ĐỆM_NỮ)
            first = random.choice(TÊN_NỮ)

        base_email = f"{strip_vn(first)}.{strip_vn(ho_i)[:3]}{i:03d}"
        domain     = random.choice(['gmail.com','yahoo.com','outlook.com','email.com','t3h.edu.vn'])
        email = f"{base_email}@{domain}"
        while email in used_emails:
            email = f"{base_email}{random.randint(1,99)}@{domain}"
        used_emails.add(email)

        dob = f"{random.randint(1995,2005)}-{random.randint(1,12):02d}-{random.randint(1,28):02d}"
        branch = random.choice(T3H_BRANCHES)
        addr   = f"{random.choice(QUẬN_HCM)}, TP.HCM"
        enroll_m = random.choice(['2023-06','2023-09','2024-01','2024-03','2024-06','2024-09','2025-01','2025-03'])
        enroll_d = f"{enroll_m}-{random.randint(1,28):02d}"
        status = random.choice(STATUS_STUDENT)

        students.append((first, f"{ho_i} {dem}", email, vn_phone(), dob,
                         gender, f"{branch} | {addr}", enroll_d, status))

    execute_values(cur, """
        INSERT INTO students
            (first_name,last_name,email,phone,date_of_birth,gender,address,enrolled_date,status)
        VALUES %s
    """, students)

    # ──────────────────────────────────────────────────────────────
    # 2. COURSES  (khóa học T3H thực tế)
    # ──────────────────────────────────────────────────────────────
    print("Tạo khóa học T3H...")
    courses = [
        # code         tên                                       mô tả                                        tc  giờ  category                   level          phí
        ('VOF101', 'Tin học văn phòng Word & Excel',     'Microsoft Word, Excel căn bản cho công việc',     2,  30,  'Office',                  'Beginner',     1_200_000, 'Active'),
        ('EXL201', 'Excel nâng cao & Power BI',          'Excel nâng cao, Dashboard, Power BI cơ bản',      3,  45,  'Office',                  'Intermediate', 2_500_000, 'Active'),
        ('KTM101', 'Kế toán máy tính (MISA)',            'Kế toán thực hành trên phần mềm MISA SME',        3,  45,  'Accounting',              'Beginner',     2_800_000, 'Active'),
        ('KTM201', 'Kế toán Excel nâng cao',             'Lập báo cáo tài chính và phân tích với Excel',    3,  45,  'Accounting',              'Intermediate', 2_500_000, 'Active'),
        ('WBF101', 'Lập trình Web Frontend',             'HTML5, CSS3, Bootstrap, JavaScript căn bản',      3,  45,  'Web Development',         'Beginner',     3_500_000, 'Active'),
        ('WBF201', 'React.js & TypeScript',              'React Hooks, Redux, TypeScript, REST API',         4,  60,  'Web Development',         'Intermediate', 5_000_000, 'Active'),
        ('WBB201', 'Lập trình Web Backend Node.js',     'Node.js, Express, MongoDB, RESTful APIs',          4,  60,  'Web Development',         'Intermediate', 5_000_000, 'Active'),
        ('PY101', 'Lập trình Python căn bản',            'Python syntax, OOP, xử lý file, thư viện cơ bản', 3,  45,  'Programming',             'Beginner',     3_000_000, 'Active'),
        ('DS201', 'Data Science với Python',             'Pandas, NumPy, Matplotlib, Seaborn, Scikit-learn', 4,  60,  'Data Science',            'Intermediate', 5_500_000, 'Active'),
        ('ML301', 'Machine Learning ứng dụng',           'Supervised/Unsupervised Learning, đánh giá mô hình',5, 75,  'Data Science',            'Advanced',     7_000_000, 'Active'),
        ('AI301', 'Deep Learning & AI',                  'Neural Networks, CNN, RNN, NLP cơ bản',            5,  75,  'Data Science',            'Advanced',     7_500_000, 'Active'),
        ('GDO101', 'Photoshop & Illustrator',            'Thiết kế đồ họa căn bản, chỉnh sửa hình ảnh',     3,  45,  'Design',                  'Beginner',     3_000_000, 'Active'),
        ('CAD101', 'AutoCAD 2D & 3D',                    'Vẽ kỹ thuật 2D/3D bằng AutoCAD',                  3,  45,  'Engineering',             'Beginner',     3_200_000, 'Active'),
        ('MB101', 'Lập trình Mobile React Native',       'React Native, Expo, kết nối API, publish app',    3,  45,  'Mobile',                  'Intermediate', 4_500_000, 'Active'),
        ('DB201', 'SQL & Quản trị CSDL',                 'SQL nâng cao, PostgreSQL, thiết kế database',      3,  45,  'Database',                'Intermediate', 3_500_000, 'Active'),
        ('CY201', 'An ninh mạng & Ethical Hacking',      'Bảo mật hệ thống, kiểm thử xâm nhập cơ bản',     4,  60,  'Security',                'Intermediate', 5_500_000, 'Active'),
    ]
    execute_values(cur, """
        INSERT INTO courses
            (course_code,course_name,description,credits,duration_hours,category,level,tuition_fee,status)
        VALUES %s
    """, courses)

    # ──────────────────────────────────────────────────────────────
    # 3. INSTRUCTORS  (20 giảng viên)
    # ──────────────────────────────────────────────────────────────
    print("Tạo giảng viên...")
    # Dữ liệu giảng viên được thiết kế thực tế theo chuyên môn
    instructor_specs = [
        ('Tin học văn phòng & Office',    'Thạc sĩ Công nghệ thông tin',    8),
        ('Microsoft Excel & Power BI',    'Thạc sĩ Hệ thống thông tin',     10),
        ('Kế toán & MISA',                'Thạc sĩ Kế toán',                12),
        ('Kế toán Excel & Tài chính',     'Thạc sĩ Tài chính',              7),
        ('Web Frontend - HTML/CSS/JS',    'Kỹ sư CNTT',                     5),
        ('React.js & Frontend nâng cao',  'Thạc sĩ Kỹ thuật phần mềm',     6),
        ('Node.js & Backend Development', 'Kỹ sư CNTT',                     7),
        ('Python Programming',            'Thạc sĩ Khoa học máy tính',      9),
        ('Data Science & Analytics',      'Tiến sĩ Khoa học dữ liệu',       11),
        ('Machine Learning',              'Tiến sĩ Học máy',                14),
        ('Deep Learning & AI',            'Tiến sĩ Trí tuệ nhân tạo',       13),
        ('Thiết kế đồ họa',               'Cử nhân Mỹ thuật ứng dụng',      9),
        ('AutoCAD & Kỹ thuật cơ khí',     'Kỹ sư cơ khí',                   15),
        ('Mobile Development',            'Kỹ sư CNTT',                     5),
        ('Database & SQL',                'Thạc sĩ Hệ thống thông tin',     8),
        ('Cybersecurity',                 'Thạc sĩ An ninh mạng',           7),
        ('Python & Data Engineering',     'Thạc sĩ Kỹ thuật phần mềm',     6),
        ('Full Stack Development',        'Kỹ sư CNTT',                     8),
        ('Tin học văn phòng nâng cao',    'Thạc sĩ Công nghệ thông tin',    11),
        ('Cloud & DevOps',                'Kỹ sư Hệ thống',                 9),
    ]

    instructors = []
    used_gv_emails = set()
    for idx, (spec, qual, exp) in enumerate(instructor_specs, 1):
        g     = random.choice(['Nam','Nữ'])
        ho_i  = random.choice(HO)
        first = random.choice(TÊN_NAM if g == 'Nam' else TÊN_NỮ)
        dem   = random.choice(ĐỆM_NAM if g == 'Nam' else ĐỆM_NỮ)
        email = f"{strip_vn(first)}.gv{idx:02d}@t3h.edu.vn"
        while email in used_gv_emails:
            email = f"{strip_vn(first)}.gv{idx:02d}x@t3h.edu.vn"
        used_gv_emails.add(email)

        hire = f"{random.randint(2010,2023)}-{random.randint(1,12):02d}-{random.randint(1,28):02d}"
        status = random.choices(['Active','On Leave'], weights=[92,8])[0]
        instructors.append((first, f"{ho_i} {dem}", email, vn_phone(), spec, hire, qual, exp, status))

    execute_values(cur, """
        INSERT INTO instructors
            (first_name,last_name,email,phone,specialization,hire_date,qualification,experience_years,status)
        VALUES %s
    """, instructors)

    # ──────────────────────────────────────────────────────────────
    # 4. CLASSES  (4 học kỳ × 16 khóa học = 64 lớp)
    # ──────────────────────────────────────────────────────────────
    print("Tạo lớp học...")
    semesters = [
        ('HK2', '2023-2024', '2024-01-08', '2024-04-08', 'Completed'),
        ('HK3', '2023-2024', '2024-05-06', '2024-08-06', 'Completed'),
        ('HK1', '2024-2025', '2024-09-09', '2024-12-09', 'Completed'),
        ('HK2', '2024-2025', '2025-01-06', '2025-04-06', 'Active'),
        ('HK3', '2024-2025', '2025-05-05', '2025-08-05', 'Active'),
    ]
    num_courses = 16
    # Map course_id 1..16 → instructor_id 1..16 (thêm một số overlap)
    course_instructor_map = {
        1:1, 2:2, 3:3, 4:4, 5:5, 6:6, 7:7, 8:8, 9:9, 10:10,
        11:11, 12:12, 13:13, 14:14, 15:15, 16:16
    }
    schedules = [
        'T2-T4 08:00-10:30', 'T2-T4 13:00-15:30', 'T2-T4 18:00-20:30',
        'T3-T5 08:00-10:30', 'T3-T5 13:00-15:30', 'T3-T5 18:00-20:30',
        'T6-CN 08:00-10:30', 'T6-CN 13:00-15:30', 'T7-CN 08:00-11:00',
        'T7-CN 13:00-16:00',
    ]
    rooms = ['A101','A102','A201','A202','A203','B101','B102','B201','B202','B203',
             'C101','C102','Lab1','Lab2','Lab3']

    classes = []
    classes_meta = []  # (class_id, sem_idx, course_id_1based)
    cls_id = 0
    for sem_idx, (sem, ay, sd, ed, st) in enumerate(semesters):
        for cid in range(1, num_courses + 1):
            cls_id += 1
            iid  = course_instructor_map.get(cid, ((cid-1)%20)+1)
            code = f"T3H-{cid:02d}-{sem}-{ay[-4:]}"
            sch  = random.choice(schedules)
            rm   = random.choice(rooms)
            mx   = random.choice([20, 25, 30, 35])
            classes.append((code, cid, iid, sem, ay, sch, rm, mx, sd, ed, st))
            classes_meta.append((cls_id, sem_idx, cid))

    execute_values(cur, """
        INSERT INTO classes
            (class_code,course_id,instructor_id,semester,academic_year,
             schedule,room,max_students,start_date,end_date,status)
        VALUES %s
    """, classes)

    # ──────────────────────────────────────────────────────────────
    # 5. ENROLLMENTS, ATTENDANCE, GRADES
    # ──────────────────────────────────────────────────────────────
    print("Tạo đăng ký, điểm danh, điểm số...")

    # Session dates pool theo học kỳ (2 buổi/tuần × ~12 tuần = ~24 buổi)
    def gen_dates(start_str, weeks=12, per_week=2):
        s = date.fromisoformat(start_str)
        dates = []
        for w in range(weeks):
            for _ in range(per_week):
                d = s + timedelta(days=w*7 + random.choice([0,2,4]))
                dates.append(str(d))
        return sorted(set(dates))

    session_pools = [gen_dates(s[2]) for s in semesters]

    enroll_rows = []
    att_rows    = []
    grade_rows  = []
    used_pairs  = set()
    eid = 0

    for cls_id_val, sem_idx, cid in classes_meta:
        sem_info = semesters[sem_idx]
        is_done  = sem_info[4] == 'Completed'
        n_stu    = random.randint(15, 28)
        pool     = list(range(1, 301))
        random.shuffle(pool)

        for sid in pool[:n_stu]:
            if (sid, cls_id_val) in used_pairs:
                continue
            used_pairs.add((sid, cls_id_val))
            eid += 1

            base_m = sem_info[2][:7]  # YYYY-MM
            e_date = f"{base_m}-{random.randint(1,14):02d}"

            if is_done:
                e_status = random.choices(['Completed','Dropped','Withdrawn'], weights=[88,8,4])[0]
            else:
                e_status = random.choices(['Enrolled','Dropped'], weights=[95,5])[0]
            c_date = sem_info[3] if e_status == 'Completed' else None

            enroll_rows.append((sid, cls_id_val, e_date, e_status, c_date))

            # Attendance
            n_sessions = random.randint(3,7) if e_status == 'Dropped' else random.randint(10, 20)
            pool_dates = session_pools[sem_idx]
            chosen = sorted(random.sample(pool_dates, min(n_sessions, len(pool_dates))))

            for sess_d in chosen:
                att_st = random.choices(
                    ['Present','Absent','Late','Excused'],
                    weights=[72, 16, 8, 4])[0]
                remark = None
                if att_st == 'Absent' and random.random() < 0.25:
                    remark = random.choice(['Bận việc gia đình','Nghỉ có phép','Ốm'])
                elif att_st == 'Excused':
                    remark = random.choice(['Có giấy xin phép','Việc đột xuất'])
                elif att_st == 'Late':
                    remark = random.choice(['Kẹt xe','Trễ 15 phút',None])
                att_rows.append((eid, sess_d, att_st, remark))

            if e_status == 'Dropped':
                if random.random() < 0.4:
                    sc = round(random.uniform(15, 60), 2)
                    grade_rows.append((eid, 'Midterm', sc, 0.30,
                                       f"{base_m}-{random.randint(15,28):02d}", None))
                continue

            # Điểm – dựa trên loại khóa học
            base_score = max(20, min(98, random.gauss(72, 13)))
            sy  = int(sem_info[2][:4])
            sm  = int(sem_info[2][5:7])

            # Cấu hình điểm theo khóa học
            if cid in [1,2,3,4]:        # Office/KTM → không có Project
                configs = [('Midterm',0.30),('Final',0.40),('Assignment',0.30)]
            elif cid in [10,11]:        # ML/AI → nhiều Project
                configs = [('Midterm',0.20),('Final',0.40),('Project',0.30),('Participation',0.10)]
            elif cid in [9,15,16]:      # DS/DB/CY → Quiz thêm
                configs = [('Midterm',0.25),('Final',0.40),('Project',0.25),('Quiz',0.10)]
            else:
                configs = [('Midterm',0.30),('Final',0.40),('Project',0.30)]

            for atype, w in configs:
                sc  = round(max(0, min(100, base_score + random.uniform(-12, 12))), 2)
                off = {'Midterm':1,'Final':3,'Project':2,'Assignment':2,'Quiz':1,'Participation':0}
                gm  = sm + off.get(atype, 1)
                gy  = sy + (1 if gm > 12 else 0)
                gm  = gm - 12 if gm > 12 else gm
                g_date = f"{gy}-{gm:02d}-{random.randint(1,28):02d}"

                remark = None
                if sc >= 90 and random.random() < 0.5:
                    remark = random.choice(['Xuất sắc','Rất tốt','Làm bài cẩn thận'])
                elif sc < 50:
                    remark = random.choice(['Không đạt','Cần cải thiện','Làm lại bài'])

                grade_rows.append((eid, atype, sc, w, g_date, remark))

    print(f"  Đang insert {len(enroll_rows):,} đăng ký...")
    execute_values(cur, """
        INSERT INTO enrollments (student_id,class_id,enrollment_date,status,completion_date)
        VALUES %s
    """, enroll_rows)

    print(f"  Đang insert {len(att_rows):,} điểm danh...")
    execute_values(cur, """
        INSERT INTO attendance (enrollment_id,session_date,status,remarks)
        VALUES %s
    """, att_rows)

    print(f"  Đang insert {len(grade_rows):,} điểm số...")
    execute_values(cur, """
        INSERT INTO grades (enrollment_id,assessment_type,score,weight,graded_date,remarks)
        VALUES %s
    """, grade_rows)

    conn.commit()
    cur.close()
    conn.close()

    total = 300 + 16 + 20 + len(classes) + len(enroll_rows) + len(att_rows) + len(grade_rows)
    print("\n" + "="*60)
    print(" ✓  Hoàn thành! Dữ liệu T3H đã được nạp vào database:")
    print("="*60)
    print(f"   Học viên       : 300 (đa dạng chi nhánh T3H)")
    print(f"   Khóa học       : 16 (theo catalog T3H thực tế)")
    print(f"   Giảng viên     : 20")
    print(f"   Lớp học        : {len(classes)} (5 học kỳ × 16 khóa)")
    print(f"   Đăng ký        : {len(enroll_rows):,}")
    print(f"   Điểm danh      : {len(att_rows):,}")
    print(f"   Bảng điểm      : {len(grade_rows):,}")
    print(f"   ─────────────────────────────────────")
    print(f"   TỔNG CỘNG      : {total:,} bản ghi")
    print("="*60)
    print("\nChạy web demo:")
    print("  cd web && pip install -r requirements.txt && python app.py")

if __name__ == "__main__":
    main()
