from faker import Faker
import random
import psycopg2

print("Starting fake data generation...")

fake = Faker()

# ==========================================
# DATABASE CONNECTION
# ==========================================

try:

    print("Connecting to Neon database...")

    conn = psycopg2.connect(
        host="ep-red-math-aosf0yly-pooler.c-2.ap-southeast-1.aws.neon.tech",
        database="neondb",
        user="neondb_owner",
        password="npg_HsRIUF51zWMD",
        port="5432",
        sslmode="require",
        connect_timeout=10
    )

    print("Database connected successfully!")

    cur = conn.cursor()

except Exception as e:

    print("Connection failed!")
    print(e)

    exit()

# ==========================================
# DATA SETUP
# ==========================================

subjects = [
    "Math",
    "Science",
    "English",
    "Computer",
    "History"
]

classes = [
    "10A",
    "10B",
    "10C"
]

# ==========================================
# GENERATE DATA
# ==========================================

try:

    total_students = 500

    for i in range(total_students):

        # Progress tracker
        if (i + 1) % 50 == 0:
            print(f"{i+1} students inserted...")

        name = fake.name()

        student_class = random.choice(classes)

        gender = random.choice(
            ["Male", "Female"]
        )

        age = random.randint(15, 18)

        # ==================================
        # INSERT STUDENT
        # ==================================

        cur.execute("""
            INSERT INTO students(
                name,
                class,
                gender,
                age
            )
            VALUES (%s, %s, %s, %s)
            RETURNING student_id
        """, (
            name,
            student_class,
            gender,
            age
        ))

        student_id = cur.fetchone()[0]

        # ==================================
        # INSERT MARKS
        # ==================================

        for subject in subjects:

            marks = random.randint(35, 100)

            cur.execute("""
                INSERT INTO marks(
                    student_id,
                    subject,
                    marks
                )
                VALUES (%s, %s, %s)
            """, (
                student_id,
                subject,
                marks
            ))

        # ==================================
        # INSERT ATTENDANCE
        # ==================================

        attendance = round(
            random.uniform(60, 100),
            2
        )

        cur.execute("""
            INSERT INTO attendance(
                student_id,
                attendance_percentage
            )
            VALUES (%s, %s)
        """, (
            student_id,
            attendance
        ))

        # ==================================
        # COMMIT EVERY 100 RECORDS
        # ==================================

        if (i + 1) % 100 == 0:
            conn.commit()
            print("Changes committed to database.")

    # Final commit
    conn.commit()

    print("Fake data inserted successfully!")

except Exception as e:

    print("Error while inserting data:")
    print(e)

finally:

    cur.close()
    conn.close()

    print("Database connection closed.")