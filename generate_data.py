from faker import Faker
import random
import psycopg2

fake = Faker()

conn = psycopg2.connect(
    host="ep-red-math-aosf0yly-pooler.c-2.ap-southeast-1.aws.neon.tech",
    database="neondb",
    user="neondb_owner",
    password="npg_HsRIUF51zWMD",
    port="5432"
)

cur = conn.cursor()

subjects = ["Math", "Science", "English", "Computer", "History"]

classes = ["10A", "10B", "10C"]

# Generate 500 students
for i in range(500):

    name = fake.name()
    student_class = random.choice(classes)
    gender = random.choice(["Male", "Female"])
    age = random.randint(15, 18)

    # Insert student
    cur.execute("""
        INSERT INTO students(name, class, gender, age)
        VALUES (%s, %s, %s, %s)
        RETURNING student_id
    """, (name, student_class, gender, age))

    student_id = cur.fetchone()[0]

    # Insert marks
    for subject in subjects:

        marks = random.randint(0, 100)

        cur.execute("""
            INSERT INTO marks(student_id, subject, marks)
            VALUES (%s, %s, %s)
        """, (student_id, subject, marks))

    # Insert attendance
    attendance = round(random.uniform(60, 100), 2)

    cur.execute("""
        INSERT INTO attendance(student_id, attendance_percentage)
        VALUES (%s, %s)
    """, (student_id, attendance))

conn.commit()

cur.close()
conn.close()

print("Fake data inserted successfully!")