"""
Generate realistic Vietnamese sample data and insert directly into PostgreSQL.
Requirements: pip install psycopg2-binary
"""
import random
import os
import getpass
try:
    import psycopg2
    from psycopg2.extras import execute_values
except ImportError:
    print("Error: psycopg2 is not installed.")
    print("Please run: pip install psycopg2-binary")
    exit(1)

random.seed(42)

# Vietnamese name pools
ho = ['Nguyễn', 'Trần', 'Lê', 'Phạm', 'Hoàng', 'Huỳnh', 'Phan', 'Vũ', 'Võ', 'Đặng',
      'Bùi', 'Đỗ', 'Hồ', 'Ngô', 'Dương', 'Lý', 'Trịnh', 'Đinh', 'Mai', 'Trương']
dem_nam = ['Văn', 'Hữu', 'Đức', 'Minh', 'Quốc', 'Thành', 'Xuân', 'Ngọc', 'Hùng', 'Thanh']
dem_nu = ['Thị', 'Ngọc', 'Thanh', 'Phương', 'Hoài', 'Minh', 'Thuỳ', 'Kim', 'Diệu', 'Mỹ']
ten_nam = ['Minh', 'Hùng', 'Đức', 'Tuấn', 'Khoa', 'Phong', 'Long', 'Bảo', 'Nam', 'Hải']
ten_nu = ['Lan', 'Hương', 'Mai', 'Thảo', 'Linh', 'Ngọc', 'Vy', 'Trang', 'Yến', 'Hà']

quan_hcm = ['Quận 1', 'Quận 3', 'Quận 4', 'Quận 5', 'Quận 6', 'Quận 7', 'Quận 8',
            'Quận 10', 'Quận 11', 'Quận 12', 'Quận Bình Thạnh', 'Quận Gò Vấp',
            'Quận Tân Bình', 'Quận Tân Phú', 'Quận Phú Nhuận', 'Quận Bình Tân',
            'TP. Thủ Đức', 'Huyện Nhà Bè', 'Huyện Bình Chánh']

statuses_student = ['Active'] * 85 + ['Inactive'] * 5 + ['Graduated'] * 8 + ['Suspended'] * 2

def vn_phone():
    prefixes = ['090', '091', '092', '093', '094', '096', '097', '098', '099', '032', '033']
    return random.choice(prefixes) + ''.join([str(random.randint(0,9)) for _ in range(7)])

def strip_vn(s):
    replacements = {
        'ă':'a','â':'a','đ':'d','ê':'e','ô':'o','ơ':'o','ư':'u',
        'á':'a','à':'a','ả':'a','ã':'a','ạ':'a','é':'e','è':'e','ẹ':'e','ẻ':'e','ẽ':'e',
        'í':'i','ì':'i','ỉ':'i','ĩ':'i','ị':'i','ú':'u','ù':'u','ủ':'u','ũ':'u','ụ':'u',
        'ó':'o','ò':'o','ỏ':'o','õ':'o','ọ':'o','ắ':'a','ằ':'a','ẳ':'a','ẵ':'a','ặ':'a',
        'ấ':'a','ầ':'a','ẩ':'a','ẫ':'a','ậ':'a','ế':'e','ề':'e','ể':'e','ễ':'e','ệ':'e',
        'ố':'o','ồ':'o','ổ':'o','ỗ':'o','ộ':'o','ớ':'o','ờ':'o','ở':'o','ỡ':'o','ợ':'o',
        'ứ':'u','ừ':'u','ử':'u','ữ':'u','ự':'u','Đ':'D','ý':'y','ỳ':'y','ỷ':'y','ỹ':'y','ỵ':'y'
    }
    result = s.lower()
    for k, v in replacements.items():
        result = result.replace(k, v)
    return result

def main():
    print("="*60)
    print("Learning Data System - Direct Database Generator")
    print("="*60)
    
    # Get database credentials
    db_name = input("Database name [learning_data_system]: ") or "learning_data_system"
    db_user = input("Username [postgres]: ") or "postgres"
    db_pass = getpass.getpass(f"Password for {db_user}: ")
    
    try:
        print("\nConnecting to database...")
        conn = psycopg2.connect(host="localhost", dbname=db_name, user=db_user, password=db_pass)
        cursor = conn.cursor()
        print("Connected successfully!")
    except Exception as e:
        print(f"Failed to connect: {e}")
        return

    # Clear existing data
    print("\nEmptying existing tables...")
    cursor.execute("""
        TRUNCATE grades, attendance, enrollments, classes, 
                 instructors, courses, students RESTART IDENTITY CASCADE;
    """)
    conn.commit()

    # ============================
    # STUDENTS
    # ============================
    print("Generating students...")
    students = []
    for i in range(1, 201):
        gender = random.choice(['Nam', 'Nữ'])
        surname = random.choice(ho)
        if gender == 'Nam':
            middle = random.choice(dem_nam)
            first = random.choice(ten_nam)
        else:
            middle = random.choice(dem_nu)
            first = random.choice(ten_nu)

        email = f"{strip_vn(first)}.{strip_vn(surname)[:3]}{i:03d}@email.com"
        phone = vn_phone()
        dob = f"{random.randint(1998, 2004)}-{random.randint(1, 12):02d}-{random.randint(1, 28):02d}"
        addr = f"{random.choice(quan_hcm)}, TP.HCM"
        enroll_date = f"{random.choice(['2024-09', '2024-10', '2024-11', '2025-01'])}-{random.randint(1, 28):02d}"
        status = random.choice(statuses_student)
        
        students.append((first, f"{surname} {middle}", email, phone, dob, gender, addr, enroll_date, status))

    execute_values(cursor, """
        INSERT INTO students (first_name, last_name, email, phone, date_of_birth, gender, address, enrolled_date, status)
        VALUES %s
    """, students)

    # ============================
    # COURSES
    # ============================
    print("Generating courses...")
    courses = [
        ('PY101', 'Lập trình Python cơ bản', 'Khóa học nền tảng về ngôn ngữ lập trình Python', 3, 45, 'Programming', 'Beginner', 3500000, 'Active'),
        ('DS201', 'Khoa học dữ liệu', 'Phân tích dữ liệu với Python và các thư viện', 4, 60, 'Data Science', 'Intermediate', 5500000, 'Active'),
        ('WD101', 'Phát triển Web Frontend', 'HTML, CSS, JavaScript cho người mới bắt đầu', 3, 45, 'Web Development', 'Beginner', 4000000, 'Active'),
        ('WD201', 'Phát triển Web Backend', 'Node.js, Express, và RESTful APIs', 4, 60, 'Web Development', 'Intermediate', 5000000, 'Active'),
        ('DB101', 'Quản trị cơ sở dữ liệu', 'SQL, PostgreSQL, và thiết kế database', 3, 45, 'Database', 'Beginner', 3500000, 'Active'),
        ('ML301', 'Machine Learning nâng cao', 'Thuật toán ML và ứng dụng thực tế', 5, 75, 'Data Science', 'Advanced', 7000000, 'Active'),
        ('PY201', 'Lập trình Python nâng cao', 'OOP, Design Patterns, và Python nâng cao', 4, 60, 'Programming', 'Intermediate', 4500000, 'Active'),
        ('AI301', 'Trí tuệ nhân tạo', 'Deep Learning và Neural Networks', 5, 75, 'Data Science', 'Advanced', 7500000, 'Active'),
        ('MB101', 'Lập trình Mobile', 'React Native cho ứng dụng di động', 3, 45, 'Mobile', 'Beginner', 4000000, 'Active'),
        ('CY201', 'An ninh mạng', 'Security fundamentals và ethical hacking', 4, 60, 'Security', 'Intermediate', 5500000, 'Active')
    ]
    execute_values(cursor, """
        INSERT INTO courses (course_code, course_name, description, credits, duration_hours, category, level, tuition_fee, status)
        VALUES %s
    """, courses)

    # ============================
    # INSTRUCTORS
    # ============================
    print("Generating instructors...")
    instructors = []
    specs = ['Python & Data Science', 'Web Development', 'Database & SQL', 'Machine Learning',
             'Mobile Development', 'Cybersecurity', 'AI & Deep Learning', 'Full Stack Development',
             'Python & Automation', 'Data Engineering', 'Cloud Computing', 'DevOps',
             'Software Engineering', 'UX/UI Design', 'Blockchain']
             
    for idx in range(1, 16):
        g = random.choice(['Nam', 'Nữ'])
        sn = random.choice(ho)
        md = random.choice(dem_nam) if g == 'Nam' else random.choice(dem_nu)
        fn = random.choice(ten_nam) if g == 'Nam' else random.choice(ten_nu)
        
        email = f"{strip_vn(fn)}.gv{idx:02d}@academy.vn"
        phone = vn_phone()
        spec = specs[idx - 1]
        hire = f"{random.randint(2015, 2022)}-{random.randint(1, 12):02d}-{random.randint(1, 28):02d}"
        qual = random.choice(['Thạc sĩ CNTT', 'Tiến sĩ CNTT', 'Thạc sĩ Khoa học dữ liệu'])
        instructors.append((fn, f"{sn} {md}", email, phone, spec, hire, qual, random.randint(3, 15), 'Active'))

    execute_values(cursor, """
        INSERT INTO instructors (first_name, last_name, email, phone, specialization, hire_date, qualification, experience_years, status)
        VALUES %s
    """, instructors)

    # ============================
    # CLASSES
    # ============================
    print("Generating classes...")
    semesters = [
        ('HK1', '2024-2025', '2024-09-15', '2024-12-15', 'Completed'),
        ('HK2', '2024-2025', '2025-01-15', '2025-04-15', 'Active'),
        ('HK3', '2024-2025', '2025-05-15', '2025-08-15', 'Active'),
    ]
    course_codes = ['PY101','DS201','WD101','WD201','DB101','ML301','PY201','AI301','MB101','CY201']
    
    classes = []
    classes_info = [] # store meta for later
    class_id = 0
    
    for sem_idx, (sem, ay, sd, ed, st) in enumerate(semesters):
        for cid in range(1, 11):
            class_id += 1
            iid = ((class_id - 1) % 15) + 1
            code = f"{course_codes[cid-1]}-{sem}"
            sch = f"T{random.randint(2,5)}-T{random.randint(4,7)} 18:00-20:30"
            rm = f"{random.choice(['A','B','C'])}{random.randint(101,305)}"
            mx = random.choice([25, 30, 35, 40])
            
            classes.append((code, cid, iid, sem, ay, sch, rm, mx, sd, ed, st))
            classes_info.append((class_id, sem_idx, cid))

    execute_values(cursor, """
        INSERT INTO classes (class_code, course_id, instructor_id, semester, academic_year, schedule, room, max_students, start_date, end_date, status)
        VALUES %s
    """, classes)

    # ============================
    # ENROLLMENTS, ATTENDANCE, GRADES
    # ============================
    print("Generating enrollments, attendance, and grades...")
    enroll_records = []
    att_records = []
    grade_records = []
    
    enrollment_id = 0
    used_pairs = set()
    
    session_dates_pool = [
        [f"2024-{m:02d}-{d:02d}" for m in [9,10,11,12] for d in [2,5,9,12,16,19,23,26]],
        [f"2025-{m:02d}-{d:02d}" for m in [1,2,3,4] for d in [6,10,13,17,20,24,27]],
        [f"2025-{m:02d}-{d:02d}" for m in [5,6,7,8] for d in [5,9,12,16,19,23,26]],
    ]
    
    for cinfo in classes_info:
        cid_val, sem_idx, course_id = cinfo
        num_students = random.randint(18, 30)
        pool = list(range(1, 201))
        random.shuffle(pool)
        
        for sid in pool[:num_students]:
            if (sid, cid_val) in used_pairs: continue
            used_pairs.add((sid, cid_val))
            enrollment_id += 1
            
            sem_data = semesters[sem_idx]
            base_month = ['2024-09', '2025-01', '2025-05'][sem_idx]
            e_date = f"{base_month}-{random.randint(1,14):02d}"
            
            st_choice = random.choices(['Completed', 'Dropped'], weights=[92, 8])[0] if sem_data[4] == 'Completed' else random.choices(['Enrolled', 'Dropped'], weights=[95, 5])[0]
            c_date = sem_data[3] if st_choice == 'Completed' else None
            
            enroll_records.append((sid, cid_val, e_date, st_choice, c_date))
            
            # Attendance
            num_sessions = random.randint(2, 4) if st_choice == 'Dropped' else random.randint(4, 8)
            dates = session_dates_pool[sem_idx]
            chosen = sorted(random.sample(dates, min(num_sessions, len(dates))))
            
            for sd in chosen:
                att_st = random.choice(['Present']*75 + ['Absent']*15 + ['Late']*7 + ['Excused']*3)
                remark = None
                if att_st == 'Absent' and random.random() < 0.2: remark = 'Nghỉ có phép'
                elif att_st == 'Excused': remark = 'Có giấy xin phép'
                att_records.append((enrollment_id, sd, att_st, remark))
                
            # Grades
            if st_choice == 'Dropped':
                if random.random() < 0.3:
                    grade_records.append((enrollment_id, 'Midterm', round(random.uniform(20, 65), 2), 0.30, e_date, None))
                continue
                
            configs = [('Midterm', 0.30), ('Final', 0.40), ('Project', 0.30)] if cid_val % 3 == 0 else [('Midterm', 0.30), ('Final', 0.40), ('Assignment', 0.30)]
            base_score = max(20, min(98, random.gauss(72, 15)))
            
            sy = int(sem_data[2][:4])
            sm = int(sem_data[2][5:7])
            
            for atype, weight in configs:
                score = round(max(0, min(100, base_score + random.uniform(-10, 10))), 2)
                gm = sm + (1 if atype == 'Midterm' else 3 if atype == 'Final' else 2)
                gy = sy + (1 if gm > 12 else 0)
                gm = gm - 12 if gm > 12 else gm
                
                remark = None
                if score >= 90 and random.random() < 0.5: remark = 'Xuất sắc'
                elif score < 50: remark = 'Không đạt' if random.random() < 0.5 else 'Cần cải thiện'
                
                grade_records.append((enrollment_id, atype, score, weight, f"{gy}-{gm:02d}-{random.randint(1,28):02d}", remark))

    execute_values(cursor, "INSERT INTO enrollments (student_id, class_id, enrollment_date, status, completion_date) VALUES %s", enroll_records)
    execute_values(cursor, "INSERT INTO attendance (enrollment_id, session_date, status, remarks) VALUES %s", att_records)
    execute_values(cursor, "INSERT INTO grades (enrollment_id, assessment_type, score, weight, graded_date, remarks) VALUES %s", grade_records)

    conn.commit()
    cursor.close()
    conn.close()

    print(f"\nSuccess! Directly inserted into the database:")
    print(f"- Students: 200")
    print(f"- Courses: 10")
    print(f"- Instructors: 15")
    print(f"- Classes: 30")
    print(f"- Enrollments: {len(enroll_records)}")
    print(f"- Attendance: {len(att_records)}")
    print(f"- Grades: {len(grade_records)}")
    print(f"Total Rows: {200+10+15+30+len(enroll_records)+len(att_records)+len(grade_records)}")
    print("="*60)

if __name__ == "__main__":
    main()
