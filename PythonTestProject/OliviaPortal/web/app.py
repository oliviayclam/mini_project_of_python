"""Olivia Portal website (Flask).

Run from the OliviaPortal folder:
    pip install -r requirements.txt
    python web/app.py

Then open http://127.0.0.1:5000
Login: olivia / 1234
"""

import random
import sys
from pathlib import Path
import os
from flask import (
    Flask,
    redirect,
    render_template,
    request,
    send_from_directory,
    session,
    url_for,
    flash
)
from werkzeug.utils import secure_filename

# Allow importing auth + bi from the parent OliviaPortal folder
ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from auth import check_login  # noqa: E402
from bi.charts import CHARTS_DIR, create_category_chart  # noqa: E402
from bi.load_data import load_rows  # noqa: E402
from bi.report import export_report  # noqa: E402
from bi.summary import category_totals, overall_stats  # noqa: E402
from games.digit_guessing import generate_num, no_duplicates,get_digits,num_of_bulls_cows  # noqa: E402
from data_transfer.upload_file import upload_file,allowed_file # noqa: E402

app = Flask(__name__)
app.secret_key = "olivia-portal-dev-only-change-me-v2"
# Set the upload path to: project_folder/data/uploaded_file
# os.path.join(BASE_DIR, 'data', 'uploaded_file'): Dynamically constructs the path across Windows, macOS, or Linux without hardcoding slash directions (/ vs \).
# BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# UPLOAD_FOLDER = os.path.join(BASE_DIR, 'data', 'uploaded_file')

# app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# os.makedirs(..., exist_ok=True): Automatically creates the parent data folder and the nested uploaded_file subfolder at the same time if they don't already exist.
# os.makedirs(UPLOAD_FOLDER, exist_ok=True)




def login_required(view):
    from functools import wraps

    @wraps(view)
    def wrapped(*args, **kwargs):
        if not session.get("username"):
            return redirect(url_for("login"))
        return view(*args, **kwargs)

    return wrapped


@app.route("/")
def home():
    print("CURRENT USER IN SESSION:", session.get("username"))
    if not session.get("username"):
        return redirect(url_for("login"))
    return render_template("home.html", username=session["username"])


@app.route("/login", methods=["GET", "POST"])

def login():
    error = None
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        if check_login(username, password):
            session["username"] = username
            return redirect(url_for("home"))
        error = "Wrong username or password."
    return render_template("login.html", error=error)


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


def _ensure_guess_secret():
    if "guess_secret" not in session:
        session["guess_secret"] = random.randint(1, 20)
        session["guess_attempts"] = 0

def _ensure_digit_guess_secret():
    if "digits_guess_secret" not in session:
        session["digits_guess_secret"] = random.randint(1000, 9999)
        session["digits_guess_attempts"] = 10


@app.route("/games")
@login_required
def games():
    _ensure_guess_secret()
    return render_template(
        "games.html",
        username=session["username"],
        guess_message=session.pop("guess_message", None),
        guess_hint=session.pop("guess_hint", None),
        rps_message=session.pop("rps_message", None),
        rps_wins=session.get("rps_wins", 0),
        rps_losses=session.get("rps_losses", 0),
        rps_ties=session.get("rps_ties", 0),
        digits_guess_message=session.pop("digits_guess_message", None),
        digits_guess_hint=session.pop("digits_guess_hint", None),
    )


@app.route("/games/guess", methods=["POST"])
@login_required
def games_guess():
    _ensure_guess_secret()
    try:
        guess = int(request.form.get("guess", ""))
    except ValueError:
        session["guess_hint"] = "Please enter a whole number."
        return redirect(url_for("games"))

    session["guess_attempts"] = session.get("guess_attempts", 0) + 1
    secret = session["guess_secret"]
    if guess < secret:
        session["guess_hint"] = "Too low!"
    elif guess > secret:
        session["guess_hint"] = "Too high!"
    else:
        session["guess_message"] = f"Correct in {session['guess_attempts']} attempt(s)!"
        session.pop("guess_secret", None)
        session["guess_attempts"] = 0
    return redirect(url_for("games"))


@app.route("/games/guess/reset", methods=["POST"])
@login_required
def games_guess_reset():
    session.pop("guess_secret", None)
    session["guess_attempts"] = 0
    session["guess_message"] = "New number ready. Guess again!"
    return redirect(url_for("games"))


@app.route("/games/digit_guess/reset", methods=["POST"])
@login_required
def digit_games_guess_reset():
    session.pop("digits_guess_secret", None)
    session["digits_guess_attempts"] = 0
    session["digits_guess_message"] = "New number ready. Guess again!"
    return redirect(url_for("games"))


@app.route("/games/rps", methods=["POST"])
@login_required
def games_rps():
    beats = {"rock": "scissors", "paper": "rock", "scissors": "paper"}
    move = request.form.get("move", "")
    if move not in beats:
        session["rps_message"] = "Invalid move."
        return redirect(url_for("games"))

    computer = random.choice(list(beats))
    if move == computer:
        session["rps_ties"] = session.get("rps_ties", 0) + 1
        session["rps_message"] = f"Computer chose {computer}. Tie!"
    elif beats[move] == computer:
        session["rps_wins"] = session.get("rps_wins", 0) + 1
        session["rps_message"] = f"Computer chose {computer}. You win!"
    else:
        session["rps_losses"] = session.get("rps_losses", 0) + 1
        session["rps_message"] = f"Computer chose {computer}. Computer wins!"
    return redirect(url_for("games"))


@app.route("/digit-guess", methods=["POST"])
def digit_guess():
    _ensure_digit_guess_secret()

    digit_secret = session["digits_guess_secret"]
    print(digit_secret)
    digit_guess = request.form.get("digit_guess", "").strip()

    # Track remaining attempts in the session (default to 10 if not set)
    attempts = session.get("digits_guess_attempts", 10)

    # 1. Validate Input (Use if / elif / else so invalid inputs stop processing!)
    if not digit_guess.isdigit() or len(digit_guess) != 4:
        session["digits_guess_message"] = "Please enter a valid 4-digit number."

    elif not no_duplicates(digit_guess):
        print("no_duplicates(digit_guess)")
        print(no_duplicates(digit_guess))

        session["digits_guess_message"] = "Number should not have repeated digits. Try again."

    else:
        # 2. Input is valid -> Process guess & decrement attempts
        attempts -= 1
        session["digits_guess_attempts"] = attempts

        bulls, cows = num_of_bulls_cows(digit_secret, digit_guess)

        # 3. Check Win / Loss / Next Attempt conditions
        if bulls == 4:
            session["digits_guess_message"] = "You guessed right!"
            session.pop("digits_guess_secret", None)  # Reset secret for next game
            session.pop("digits_guess_attempts", None)

        elif attempts <= 0:
            session["digits_guess_hint"] = f"You ran out of tries. The number was {digit_secret}."
            session.pop("digits_guess_secret", None)
            session.pop("digits_guess_attempts", None)

        else:
            session["digits_guess_hint"] = f"{bulls} bulls, {cows} cows. ({attempts} tries left)"

    return redirect(url_for("games"))


@app.route("/bi")
@login_required
def bi():
    rows = load_rows()
    count, total, average = overall_stats(rows)
    totals = category_totals(rows)
    chart_name = None
    report_name = None
    message = None

    action = request.args.get("action")
    if action == "chart":
        path = create_category_chart()
        chart_name = path.name
        message = "Chart created."
    elif action == "export":
        path = export_report()
        report_name = path.name
        message = f"Report exported: {report_name}"

    return render_template(
        "bi.html",
        username=session["username"],
        rows=rows[:15],
        count=count,
        total=total,
        average=average,
        totals=totals,
        chart_name=chart_name,
        message=message,
    )


@app.route("/transfer", methods=["POST","GET"])
@login_required
def transfer():
    path = upload_file()
    # If GET request, render page as normal
    if request.method == "GET":
        # Retrieve all files currently saved in data/uploaded_file
        files_list = []
        if os.path.exists(path):
            # Filter out hidden system files (like .DS_Store)
            files_list = [
                f for f in os.listdir(path)
                if not f.startswith('.')
            ]
        return render_template(
            "transfer.html",
            username=session["username"],
            files = files_list
        )
    else:
        # Check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part selected')
            return redirect(request.url)

        file = request.files['file']

        # If user submits without selecting a file
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)

        # Validate and save file
        # Never trust user - supplied filenames directly! Always use secure_filename()
        # to prevent path traversal vulnerabilities
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_path = os.path.join(path, filename)
            file.save(file_path)

            flash(f'File "{filename}" uploaded successfully!')
            return redirect(url_for('transfer'))
        else:
            flash('File type not allowed')
            return redirect(request.url)

@app.route("/charts/<path:filename>")
@login_required
def chart_file(filename):
    CHARTS_DIR.mkdir(parents=True, exist_ok=True)
    return send_from_directory(CHARTS_DIR, filename)


if __name__ == "__main__":
    app.run(debug=True)
