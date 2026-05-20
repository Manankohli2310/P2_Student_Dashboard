import streamlit as st
import pandas as pd
import plotly.express as px
from database import run_query

# ======================================================
# PAGE CONFIG
# ======================================================

st.set_page_config(
    page_title="Student Management Dashboard",
    page_icon="🎓",
    layout="wide"
)

# ======================================================
# CUSTOM CSS
# ======================================================

st.markdown("""
<style>

.main {
    background-color: #f5f7fa;
}

div[data-testid="metric-container"] {
    background-color: white;
    border: 1px solid #e6e6e6;
    padding: 15px;
    border-radius: 15px;
    box-shadow: 0px 2px 8px rgba(0,0,0,0.08);
}

h1, h2, h3 {
    color: #1f2937;
}

</style>
""", unsafe_allow_html=True)

# ======================================================
# SIDEBAR
# ======================================================

st.sidebar.title("🎓 Navigation")

page = st.sidebar.radio(
    "Go To",
    [
        "Dashboard",
        "Student Analytics",
        "Attendance Analytics",
        "Top Performers"
    ]
)

# ======================================================
# FILTERS
# ======================================================

st.sidebar.subheader("🔍 Filters")

selected_class = st.sidebar.selectbox(
    "Select Class",
    ["All", "10A", "10B", "10C"]
)

selected_gender = st.sidebar.selectbox(
    "Select Gender",
    ["All", "Male", "Female"]
)

# ======================================================
# DYNAMIC FILTERS
# ======================================================

filter_conditions = []

if selected_class != "All":
    filter_conditions.append(
        f"s.class = '{selected_class}'"
    )

if selected_gender != "All":
    filter_conditions.append(
        f"s.gender = '{selected_gender}'"
    )

where_clause = ""

if filter_conditions:
    where_clause = "WHERE " + " AND ".join(filter_conditions)

# ======================================================
# DASHBOARD PAGE
# ======================================================

if page == "Dashboard":

    st.title("📊 Student Management Dashboard")

    # ==================================================
    # METRICS
    # ==================================================

    total_students_query = f"""
        SELECT COUNT(*) AS count
        FROM students s
        {where_clause}
    """

    total_students = run_query(
        total_students_query
    )

    average_marks_query = f"""
        SELECT ROUND(AVG(m.marks),2) AS avg
        FROM students s
        JOIN marks m
        ON s.student_id = m.student_id
        {where_clause}
    """

    average_marks = run_query(
        average_marks_query
    )

    pass_percentage_query = f"""
        SELECT ROUND(
            100.0 * COUNT(*) FILTER (
                WHERE average_marks >= 50
            ) / COUNT(*),
            2
        ) AS pass_percent
        FROM (
            SELECT s.student_id,
            AVG(m.marks) AS average_marks
            FROM students s
            JOIN marks m
            ON s.student_id = m.student_id
            {where_clause}
            GROUP BY s.student_id
        ) subquery
    """

    pass_percentage = run_query(
        pass_percentage_query
    )

    topper_query = f"""
        SELECT s.name,
        ROUND(AVG(m.marks),2) AS avg_marks
        FROM students s
        JOIN marks m
        ON s.student_id = m.student_id
        {where_clause}
        GROUP BY s.name
        ORDER BY avg_marks DESC
        LIMIT 1
    """

    topper = run_query(
        topper_query
    )

    # ==================================================
    # METRIC CARDS
    # ==================================================

    col1, col2, col3, col4 = st.columns(4)

    col1.metric(
        "👨‍🎓 Total Students",
        total_students['count'][0]
    )

    col2.metric(
        "📚 Average Marks",
        average_marks['avg'][0]
    )

    col3.metric(
        "✅ Pass Percentage",
        f"{pass_percentage['pass_percent'][0]}%"
    )

    col4.metric(
        "🏆 Top Performer",
        topper['name'][0]
    )

    st.markdown("---")

# ==================================================
# MODERN SUBJECT ANALYSIS CHART
# ==================================================

    st.subheader("📊 Subject-wise Average Marks")

    subject_query = f"""
        SELECT m.subject,
        ROUND(AVG(m.marks),2) AS average_marks
        FROM students s
        JOIN marks m
        ON s.student_id = m.student_id
        {where_clause}
        GROUP BY m.subject
        ORDER BY average_marks DESC
    """

    subject_data = run_query(subject_query)

    # ==================================================
    # MODERN BAR CHART
    # ==================================================

    fig1 = px.bar(
        subject_data,
        x="subject",
        y="average_marks",
        text="average_marks",
        color="average_marks",

        # AMAZING COLOR THEME
        color_continuous_scale=[
            "#00C6FF",
            "#0072FF",
            "#6A5ACD",
            "#8A2BE2"
        ],

        title="📚 Subject Performance Dashboard"
    )

    # ==================================================
    # BAR STYLING
    # ==================================================

    fig1.update_traces(

        # Rounded Style Feel
        marker_line_color="rgba(255,255,255,0.2)",
        marker_line_width=1.5,

        # Text
        textposition="outside",
        textfont=dict(
            size=16,
            family="Arial Black"
        ),

        # Hover Effect
        hovertemplate=
        "<b>📘 Subject:</b> %{x}<br>" +
        "<b>📊 Avg Marks:</b> %{y}<br>" +
        "<extra></extra>"
    )

    # ==================================================
    # LAYOUT STYLING
    # ==================================================

    fig1.update_layout(
         # REMOVE COLOR SCALE
        coloraxis_showscale=False,
        # HEIGHT
        height=550,

    )

    # ==================================================
    # DISPLAY
    # ==================================================

    st.plotly_chart(
        fig1,
        use_container_width=True
    )
    # ==================================================
    # PASS FAIL ANALYSIS
    # ==================================================

    st.subheader("🎯 Pass vs Fail Distribution")

    pass_fail_query = f"""
        SELECT
        CASE
            WHEN AVG(m.marks) >= 50 THEN 'Pass'
            ELSE 'Fail'
        END AS result,
        COUNT(*) AS total
        FROM students s
        JOIN marks m
        ON s.student_id = m.student_id
        {where_clause}
        GROUP BY s.student_id
    """

    pass_fail = run_query(
        pass_fail_query
    )

    pass_fail_summary = (
        pass_fail
        .groupby("result")
        .sum()
        .reset_index()
    )

    fig2 = px.pie(
        pass_fail_summary,
        names="result",
        values="total",
        title="Pass vs Fail Ratio"
    )

    st.plotly_chart(
        fig2,
        use_container_width=True
    )

    # ==================================================
    # TOP 10 STUDENTS
    # ==================================================

    st.subheader("🏆 Top 10 Students")

    top_students_query = f"""
        SELECT s.name,
        s.class,
        ROUND(AVG(m.marks),2) AS average_marks
        FROM students s
        JOIN marks m
        ON s.student_id = m.student_id
        {where_clause}
        GROUP BY s.name, s.class
        ORDER BY average_marks DESC
        LIMIT 10
    """

    top_students = run_query(
        top_students_query
    )

    st.dataframe(
        top_students,
        use_container_width=True
    )

    fig3 = px.bar(
        top_students,
        x="name",
        y="average_marks",
        color="class",
        text_auto=True,
        title="Top 10 Students Performance"
    )

    st.plotly_chart(
        fig3,
        use_container_width=True
    )

    # ==================================================
    # ATTENDANCE DISTRIBUTION
    # ==================================================

    st.subheader("📈 Attendance Distribution")

    attendance_query = f"""
        SELECT s.name,
        s.class,
        a.attendance_percentage
        FROM students s
        JOIN attendance a
        ON s.student_id = a.student_id
        {where_clause}
    """

    attendance_data = run_query(
        attendance_query
    )

    fig4 = px.histogram(
        attendance_data,
        x="attendance_percentage",
        nbins=20,
        title="Attendance Distribution"
    )

    st.plotly_chart(
        fig4,
        use_container_width=True
    )

# ======================================================
# STUDENT ANALYTICS PAGE
# ======================================================

elif page == "Student Analytics":

    st.title("👨‍🎓 Student Analytics")

    search_student = st.text_input(
        "🔍 Search Student Name"
    )

    student_query = f"""
        SELECT s.name,
        s.class,
        s.gender,
        s.age,
        ROUND(AVG(m.marks),2) AS average_marks
        FROM students s
        JOIN marks m
        ON s.student_id = m.student_id
        {where_clause}
        GROUP BY s.name, s.class, s.gender, s.age
        ORDER BY average_marks DESC
    """

    students_df = run_query(
        student_query
    )

    if search_student:

        students_df = students_df[
            students_df['name'].str.contains(
                search_student,
                case=False
            )
        ]

    st.dataframe(
        students_df,
        use_container_width=True
    )

    # ==================================================
    # DOWNLOAD BUTTON
    # ==================================================

    csv = students_df.to_csv(index=False)

    st.download_button(
        label="⬇ Download Student Report",
        data=csv,
        file_name="student_report.csv",
        mime="text/csv"
    )

# ======================================================
# ATTENDANCE ANALYTICS PAGE
# ======================================================

elif page == "Attendance Analytics":

    st.title("📈 Attendance Analytics")

    attendance_query = f"""
        SELECT s.name,
        s.class,
        a.attendance_percentage
        FROM students s
        JOIN attendance a
        ON s.student_id = a.student_id
        {where_clause}
    """

    attendance_data = run_query(
        attendance_query
    )

    st.dataframe(
        attendance_data,
        use_container_width=True
    )

    # ==================================================
    # HISTOGRAM
    # ==================================================

    fig5 = px.histogram(
        attendance_data,
        x="attendance_percentage",
        nbins=20,
        title="Attendance Distribution Histogram"
    )

    st.plotly_chart(
        fig5,
        use_container_width=True
    )

    # ==================================================
    # BOX PLOT
    # ==================================================

    fig6 = px.box(
        attendance_data,
        y="attendance_percentage",
        title="Attendance Spread Analysis"
    )

    st.plotly_chart(
        fig6,
        use_container_width=True
    )

# ======================================================
# TOP PERFORMERS PAGE
# ======================================================

elif page == "Top Performers":

    st.title("🏆 Top Performers")

    topper_query = f"""
        SELECT s.name,
        s.class,
        ROUND(AVG(m.marks),2) AS average_marks
        FROM students s
        JOIN marks m
        ON s.student_id = m.student_id
        {where_clause}
        GROUP BY s.name, s.class
        ORDER BY average_marks DESC
        LIMIT 20
    """

    topper_df = run_query(
        topper_query
    )

    st.dataframe(
        topper_df,
        use_container_width=True
    )

    # ==================================================
    # TOPPER BAR CHART
    # ==================================================

    fig7 = px.bar(
        topper_df,
        x="name",
        y="average_marks",
        color="class",
        text_auto=True,
        title="Top 20 Students"
    )

    st.plotly_chart(
        fig7,
        use_container_width=True
    )

    # ==================================================
    # SCATTER PLOT
    # ==================================================

    fig8 = px.scatter(
        topper_df,
        x="name",
        y="average_marks",
        color="class",
        size="average_marks",
        title="Top Students Scatter Plot"
    )

    st.plotly_chart(
        fig8,
        use_container_width=True
    )

    # ==================================================
    # DOWNLOAD BUTTON
    # ==================================================

    csv = topper_df.to_csv(index=False)

    st.download_button(
        label="⬇ Download Topper Report",
        data=csv,
        file_name="top_performers.csv",
        mime="text/csv"
    )