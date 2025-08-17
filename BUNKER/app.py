from flask import Flask, request, render_template_string
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
    "Friday": 5,    #  SPORTS
    "Saturday": 6, 
    "Sunday": 0     # holiday
}

# -----------------------------
# HTML Templates
FORM_HTML = """
<!DOCTYPE html>
<html>
<head>
  <title>Bunk Planner</title>
</head>
<body>
  <h2>Attendance Planner</h2>
  <form method="post" action="/select_date">
    Present: <input type="number" name="present" required><br>
    Absent: <input type="number" name="absent" required><br>
    <button type="submit">Next</button>
  </form>
</body>
</html>
"""

DATE_HTML = """
<!DOCTYPE html>
<html>
<head>
  <title>Select Date</title>
</head>
<body>
  <h2>Select Date to Bunk</h2>
  <form method="post" action="/bunk_option">
    <input type="hidden" name="present" value="{{ present }}">
    <input type="hidden" name="absent" value="{{ absent }}">
    <label for="date">Pick a date:</label>
    <input type="date" name="date" required><br><br>
    <input type="radio" name="option" value="whole" required> Whole Day<br>
    <input type="radio" name="option" value="period"> Specific Periods<br>
    <button type="submit">Next</button>
  </form>
</body>
</html>
"""

PERIOD_HTML = """
<!DOCTYPE html>
<html>
<head>
  <title>Select Periods</title>
</head>
<body>
  <h2>Select Periods to Bunk on {{ date }}</h2>
  <form method="post" action="/result">
    <input type="hidden" name="present" value="{{ present }}">
    <input type="hidden" name="absent" value="{{ absent }}">
    <input type="hidden" name="date" value="{{ date }}">
    {% for i in range(1, periods+1) %}
      <input type="checkbox" name="periods" value="{{ i }}"> Period {{ i }}<br>
    {% endfor %}
    <button type="submit">Calculate</button>
  </form>
</body>
</html>
"""

RESULT_HTML = """
<!DOCTYPE html>
<html>
<head>
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Attendance Result</title>
  <style>
    body {
      font-family: Arial, sans-serif;
      padding: 15px;
      background: #f9f9f9;
    }
    h2 {
      text-align: center;
      color: #333;
    }
    .result-container {
      max-width: 400px;
      margin: 0 auto;
      background: #fff;
      padding: 20px;
      border-radius: 8px;
      box-shadow: 0 0 10px rgba(0,0,0,0.1);
    }
    p {
      line-height: 1.4;
      color: #555;
      margin: 8px 0;
    }
    .allowed {
      color: green;
      font-weight: bold;
    }
    .not-allowed {
      color: red;
      font-weight: bold;
    }
    .note {
      font-size: 0.9em;
      color: gray;
      margin-top: 10px;
    }
    @media (max-width: 500px) {
      body {
        padding: 10px;
      }
      .result-container {
        padding: 15px;
      }
    }
  </style>
</head>
<body>
  <h2>Attendance Calculation Result</h2>
  <div class="result-container">
    <p><strong>Date Selected:</strong> {{ date }}</p>
    <p><strong>Total Classes in Semester:</strong> {{ total_classes }}</p>
    <p><strong>Present:</strong> {{ present }}</p>
    <p><strong>Absent:</strong> {{ absent }}</p>
    <p><strong>Final Percentage:</strong> {{ "%.2f"|format(final_percent) }}%</p>
    <p><strong>Safe Bunks Left:</strong> {{ safe_bunks }}</p>

    {% if allowed %}
      <p class="allowed">Yes ✅ you can still reach 75%.</p>
    {% else %}
      <p class="not-allowed">No ❌ you cannot reach 75%.</p>
    {% endif %}

    <p class="note">
      Note: Calculated percentage may differ slightly (±0.5%) due to rounding in semester totals.
    </p>
  </div>
</body>
</html>
"""

# -----------------------------
# Routes
# -----------------------------
@app.route("/")
def home():
    return render_template_string(FORM_HTML)

@app.route("/select_date", methods=["POST"])
def select_date():
    present = int(request.form["present"])
    absent = int(request.form["absent"])
    return render_template_string(DATE_HTML, present=present, absent=absent)

@app.route("/bunk_option", methods=["POST"])
def bunk_option():
    present = int(request.form["present"])
    absent = int(request.form["absent"])
    date = request.form["date"]
    option = request.form["option"]

    if option == "whole":
        weekday = datetime.strptime(date, "%Y-%m-%d").strftime("%A")
        bunk_k = TIMETABLE.get(weekday, 0)
        return compute_and_render_result(date, present, absent, bunk_k)
    else:
        weekday = datetime.strptime(date, "%Y-%m-%d").strftime("%A")
        periods = TIMETABLE.get(weekday, 0)
        return render_template_string(PERIOD_HTML, date=date, present=present, absent=absent, periods=periods)

@app.route("/result", methods=["POST"])
def show_periods_or_result():
    present = int(request.form["present"])
    absent = int(request.form["absent"])
    date = request.form["date"]
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

    return render_template_string(
        RESULT_HTML,
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
    app.run(host="0.0.0.0", port=port, debug=True)
