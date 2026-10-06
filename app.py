from flask import Flask, render_template, request, send_file
import pandas as pd
import os

app = Flask(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CSV_FILE = os.path.join(BASE_DIR, "Student_performance_data.csv")

df = pd.read_csv(CSV_FILE)


# =========================================================
# FEATURE 4 - GPA BASED GRADE CALCULATION
# =========================================================

def calculate_grade(gpa):
    if gpa >= 3.5:
        return "A"
    elif gpa >= 3.0:
        return "B"
    elif gpa >= 2.5:
        return "C"
    elif gpa >= 2.0:
        return "D"
    else:
        return "F"


df["Grade"] = df["GPA"].apply(calculate_grade)


# =========================================================
# FEATURE 5 - TOP 10 STUDENTS
# =========================================================

top10 = df.sort_values(
    by="GPA",
    ascending=False
).head(10)

top10_data = []

for _, row in top10.iterrows():
    top10_data.append({
        "StudentID": int(row["StudentID"]),
        "GPA": round(row["GPA"], 2),
        "Grade": row["Grade"]
    })


# =========================================================
# FEATURE 10 - GRADE WISE ANALYSIS
# =========================================================

grade_analysis = (
    df.groupby("Grade")
    .agg(
        Students=("StudentID", "count"),
        AverageGPA=("GPA", "mean")
    )
    .reset_index()
)

total_students = len(df)

grade_data = []

for _, row in grade_analysis.iterrows():
    percentage = (
        row["Students"] / total_students
    ) * 100

    grade_data.append({
        "Grade": row["Grade"],
        "Students": int(row["Students"]),
        "Percentage": round(percentage, 2),
        "AverageGPA": round(row["AverageGPA"], 2)
    })


# =========================================================
# FEATURE 9 - GRADE WISE STUDENT COUNT
# =========================================================

grade_students = {
    "A": len(df[df["Grade"] == "A"]),
    "B": len(df[df["Grade"] == "B"]),
    "C": len(df[df["Grade"] == "C"]),
    "D": len(df[df["Grade"] == "D"]),
    "F": len(df[df["Grade"] == "F"])
}


# =========================================================
# FEATURE 19 - STUDY TIME VS AVERAGE GPA
# =========================================================

study_analysis = (
    df.groupby("StudyTimeWeekly")
    .agg(
        Students=("StudentID", "count"),
        AverageGPA=("GPA", "mean")
    )
    .reset_index()
)

study_data = []

for _, row in study_analysis.iterrows():
    study_data.append({
        "StudyTimeWeekly": round(
            row["StudyTimeWeekly"], 2
        ),
        "Students": int(row["Students"]),
        "AverageGPA": round(
            row["AverageGPA"], 2
        )
    })


# =========================================================
# FEATURE 20 - ABSENCE ANALYSIS
# =========================================================

def absence_category(absences):
    if absences <= 5:
        return "0-5"
    elif absences <= 10:
        return "6-10"
    elif absences <= 15:
        return "11-15"
    elif absences <= 20:
        return "16-20"
    else:
        return "21+"


df["AbsenceRange"] = df["Absences"].apply(
    absence_category
)


absence_analysis = (
    df.groupby("AbsenceRange")
    .agg(
        Students=("StudentID", "count"),
        AverageGPA=("GPA", "mean")
    )
    .reset_index()
)


absence_order = [
    "0-5",
    "6-10",
    "11-15",
    "16-20",
    "21+"
]


absence_analysis["Order"] = (
    absence_analysis["AbsenceRange"].apply(
        lambda x: absence_order.index(x)
    )
)


absence_analysis = absence_analysis.sort_values(
    "Order"
)


absence_data = []

for _, row in absence_analysis.iterrows():
    absence_data.append({
        "AbsenceRange": row["AbsenceRange"],
        "Students": int(row["Students"]),
        "AverageGPA": round(
            row["AverageGPA"], 2
        )
    })
    # =========================================================
# FEATURE 21 - GENDER-WISE ANALYSIS
# =========================================================

gender_analysis = (
    df.groupby("Gender")
    .agg(
        Students=("StudentID", "count"),
        AverageGPA=("GPA", "mean")
    )
    .reset_index()
)

gender_data = []

for _, row in gender_analysis.iterrows():
    gender_data.append({
        "Gender": row["Gender"],
        "Students": int(row["Students"]),
        "AverageGPA": round(
            row["AverageGPA"], 2
        )
    })
    # =========================================================
# FEATURE 22 - PARENTAL SUPPORT ANALYSIS
# =========================================================

parental_support_analysis = (
    df.groupby("ParentalSupport")
    .agg(
        Students=("StudentID", "count"),
        AverageGPA=("GPA", "mean")
    )
    .reset_index()
)

parental_support_data = []

for _, row in parental_support_analysis.iterrows():
    parental_support_data.append({
        "ParentalSupport": row["ParentalSupport"],
        "Students": int(row["Students"]),
        "AverageGPA": round(
            row["AverageGPA"], 2
        )
    })


# =========================================================
# FEATURE 1 - DASHBOARD
# =========================================================

@app.route("/")
def dashboard():

    highest_gpa = df["GPA"].max()

    topper = df.loc[
        df["GPA"].idxmax()
    ]["StudentID"]

    average_gpa = df["GPA"].mean()

    students = df.to_dict(
        orient="records"
    )

    return render_template(
        "dashboard.html",
        students=students,
        total_students=total_students,
        average_gpa=round(
            average_gpa, 2
        ),
        highest_gpa=round(
            highest_gpa, 2
        ),
        topper=int(topper),
        top10=top10_data,
        grade_analysis=grade_data,
        grade_students=grade_students,
        study_data=study_data,
        absence_data=absence_data,
        gender_data=gender_data,
        parental_support_data=parental_support_data

    )


# =========================================================
# FEATURE 2 & 3 - STUDENT SEARCH / STUDENT REPORT
# =========================================================

@app.route("/student")
def student():

    student_id = request.args.get(
        "id",
        ""
    )

    if student_id == "":
        return render_template(
            "student.html",
            student=None
        )

    try:
        student_id = int(student_id)

    except ValueError:
        return render_template(
            "student.html",
            student=None
        )

    result = df[
        df["StudentID"] == student_id
    ]

    if result.empty:
        return render_template(
            "student.html",
            student=None
        )

    student_data = result.iloc[0].to_dict()

    return render_template(
        "student.html",
        student=student_data
    )


# =========================================================
# START FLASK APPLICATION
# =========================================================
# =========================================================
# FEATURE 23 - DOWNLOAD REPORT AS CSV
# =========================================================

@app.route("/download-report")
def download_report():

    report_file = os.path.join(
        BASE_DIR,
        "Student_Data_Analysis_Report.csv"
    )

    df.to_csv(
        report_file,
        index=False
    )

    return send_file(
        report_file,
        as_attachment=True,
        download_name="Student_Data_Analysis_Report.csv",
        mimetype="text/csv"
    )
if __name__ == "__main__":
    app.run(debug=True)