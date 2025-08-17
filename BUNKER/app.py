from flask import Flask, request, render_template
import math
from datetime import datetime
import os

app = Flask(__name__)

# -----------------------------
# Academic Calendar Settings
# -----------------------------
SEMESTER_TOTAL_CLASSES = 510  # from your academic calculation

# Day-wise timetable (example: Mon has 6 periods)
TIMETABLE = {
    "Monday": 6,
    "Tuesday": 6,
    "Wednesday": 6,
    "Thursday": 5,   # LIBRARY
    "Friday": 5,     # SPORTS
    "Saturday": 6, 
    "Sunday": 0      # holiday
}

# -----------------------------
# Routes
# -----------------------------
@app.route("/")
def home():
    return render_template("form.html")

@app.route("/select_date", methods=["POST"])
def select_date():
    try:
        present = int(request.form.get("present", 0))
        absent = int(request.form.get("absent", 0))
    except ValueError:
        present, absent = 0, 0
    return render_template("date.html", present=present, absent=absent)

@app.route("/bunk_option", methods=["POST"])
def bunk_option():
    present = int(request.form.get("present", 0))
    absent = int(request.form.get("absent", 0))
    date = request.form.get("date", "")
    option = request.form.get("option", "")

    weekday = datetime.strptime(date, "%Y-%m-%d").strftime("%A") if date else ""
    if option == "whole":
        bunk_k = TIMETABLE.get(weekday, 0)
        return compute_and_render_result(date, present, absent, bunk_k)
    else:
        periods = TIMETABLE.get(weekday, 0)
        return render_template("period.html", date=date, present=present, absent=absent, periods=periods)

@app.route("/result", methods=["POST"])
def show_periods_or_result():
    present = int(request.form.get("present", 0))
    absent = int(request.form.get("absent", 0))
    date = request.form.get("date", "")
    selected_periods = request.form.getlist("periods")
    bunk_k = len(selected_periods)
    return compute_and_render_result(date, present, absent, bunk_k)

# -----------------------------
# Core Logic
# -----------------------------
def compute_and_render_result(date, present, absent, bunk_k):
    total_done = present + absent + bunk_k
    total_classes = SEMESTER_TOTAL_CLASSES
    remaining = total_classes - total_done

    final_present = present + remaining  # if attend all left
    final_percent = (final_present / total_classes) * 100

    required_present = math.ceil(0.75 * total_classes)
    safe_bunks = final_present - required_present
    allowed = final_percent >= 75

    return render_template(
        "result.html",
        date=date,
        total_classes=total_classes,
        present=present,
        absent=absent + bunk_k,
        final_percent=float(final_percent),
        allowed=allowed,
        safe_bunks=safe_bunks
    )

# -----------------------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
