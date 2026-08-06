"""Olivia Portal website (Flask).

Run from the OliviaPortal folder:
    pip install -r requirements.txt
    python web/app.py

Then open http://127.0.0.1:5001
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
    flash,
    jsonify
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
from map.weather import find_weather,get_countries # noqa: E402

app = Flask(__name__)
app.secret_key = "olivia-portal-dev-only-change-me-v2"
app.config["MAX_CONTENT_LENGTH"] = 25 * 1024 * 1024  # 25 MB uploads
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
@app.route("/text_to_speech", methods=["POST"])
@login_required
def text_to_speech():
    selected_file = request.form.get("selected_file")
    # Add your Text-to-Speech logic here
    flash(f"Processing Text to Speech for file: {selected_file}")
    return redirect(url_for("transfer"))


@app.route("/compare_pdf", methods=["POST"])
@login_required
def compare_pdf():
    selected_file = request.form.get("selected_file")
    # Add your PDF comparison logic here
    flash(f"Comparing PDF file: {selected_file}")
    return redirect(url_for("transfer"))


@app.route("/find_value", methods=["POST"])
@login_required
def find_value():
    selected_file = request.form.get("selected_file")
    search_key = request.form.get("search_key")
    # Add your search logic here (e.g., searching for key inside the file)
    flash(f"Searching for key '{search_key}' in file: {selected_file}")
    return redirect(url_for("transfer"))

@app.route("/map")
@login_required
def map():
    message = session.get("message")
    selected_country = session.get("country")
    countries = get_countries()

    # Example: Retrieve lat/lng for the selected country/city
    # Replace this lookup logic with your actual helper function or API
    selected_lat = session.get("lat", 20)  # Default fallback lat
    selected_lng = session.get("lng", 0)  # Default fallback lng

    # If a country was selected, set a default zoom level closer in
    zoom_level = 5 if selected_country else 2

    return render_template(
        "map.html",
        message=message,
        selected_country=selected_country,
        selected_lat=selected_lat,
        selected_lng=selected_lng,
        zoom_level=zoom_level,
        countries=countries
    )
@app.route("/selected_city", methods=["POST"])
@login_required
def selected_city():
    city = request.json.get("country") if request.is_json else request.form.get("country")
    print(find_weather(city))
    weather_info, lat, lng = find_weather(city)
    return jsonify({
        "status": "success",
        "message": weather_info,
        "country": city,
        "lat": lat,
        "lng": lng
    })



@app.route("/charts/<path:filename>")
@login_required
def chart_file(filename):
    CHARTS_DIR.mkdir(parents=True, exist_ok=True)
    return send_from_directory(CHARTS_DIR, filename)


@app.route("/tools")
@login_required
def tools():
    from tools.to_pdf import DEFAULT_PDF_STYLE, normalize_pdf_style

    pdf_style = normalize_pdf_style(session.get("tools_pdf_style"))
    if session.get("tools_pdf_preview"):
        session["tools_pdf_style"] = pdf_style

    return render_template(
        "tools.html",
        username=session["username"],
        message=session.pop("tools_message", None),
        error=session.pop("tools_error", None),
        result_file=session.get("tools_file"),
        result_kind=session.get("tools_kind"),
        pdf_text=session.get("tools_pdf_text"),
        pdf_style=pdf_style,
        pdf_preview=bool(session.get("tools_pdf_preview")),
        default_pdf_style=DEFAULT_PDF_STYLE,
    )


@app.route("/tools/text-media", methods=["POST"])
@login_required
def tools_text_media():
    from tools.text_media import text_to_speech as make_speech
    from tools.text_media import text_to_video as make_video

    text = request.form.get("text", "")
    output_type = request.form.get("output_type", "speech")
    try:
        if output_type == "video":
            path = make_video(text)
            session["tools_kind"] = "video"
            session["tools_message"] = "Video created. Play it below or download."
        else:
            path = make_speech(text)
            session["tools_kind"] = "audio"
            session["tools_message"] = "Speech created. Play it below or download."
        session["tools_file"] = path.name
        session.pop("tools_pdf_text", None)
        session.pop("tools_pdf_preview", None)
        session.pop("tools_pdf_style", None)
    except Exception as exc:
        session["tools_error"] = str(exc)
    return redirect(url_for("tools"))


@app.route("/tools/bg-remove", methods=["POST"])
@login_required
def tools_bg_remove():
    from tools.bg_remove import remove_background

    upload = request.files.get("image")
    if not upload or not upload.filename:
        session["tools_error"] = "Please choose an image to upload."
        return redirect(url_for("tools"))
    try:
        path = remove_background(upload.read())
        session["tools_file"] = path.name
        session["tools_kind"] = "image"
        session["tools_message"] = "Background removed. Preview below or download the PNG."
        session.pop("tools_pdf_text", None)
        session.pop("tools_pdf_preview", None)
        session.pop("tools_pdf_style", None)
    except Exception as exc:
        session["tools_error"] = str(exc)
    return redirect(url_for("tools"))


@app.route("/tools/pdf", methods=["POST"])
@login_required
def tools_pdf():
    from tools.pdf_convert import pdf_to_speech, pdf_to_text
    from tools.to_pdf import DEFAULT_PDF_STYLE, text_to_pdf

    upload = request.files.get("pdf")
    output_type = request.form.get("output_type", "text")
    if not upload or not upload.filename:
        session["tools_error"] = "Please choose a PDF to upload."
        return redirect(url_for("tools"))
    try:
        data = upload.read()
        if output_type == "speech":
            path = pdf_to_speech(data)
            session["tools_file"] = path.name
            session["tools_kind"] = "audio"
            session["tools_message"] = "PDF converted to speech. Play it below or download."
            session.pop("tools_pdf_text", None)
            session.pop("tools_pdf_preview", None)
            session.pop("tools_pdf_style", None)
        else:
            text = pdf_to_text(data)
            style = dict(DEFAULT_PDF_STYLE)
            style["title"] = "Extracted from PDF"
            path = text_to_pdf(text, style=style)
            session["tools_file"] = path.name
            session["tools_kind"] = "pdf"
            session["tools_pdf_text"] = text
            session["tools_pdf_style"] = style
            session["tools_pdf_preview"] = True
            session["tools_message"] = (
                "PDF text extracted. Preview below — edit text or style, then update."
            )
    except Exception as exc:
        session["tools_error"] = str(exc)
    return redirect(url_for("tools"))


@app.route("/tools/to-pdf", methods=["POST"])
@login_required
def tools_to_pdf():
    from tools.to_pdf import resolve_text_input, style_from_form, text_to_pdf

    typed = request.form.get("text", "")
    output_type = request.form.get("output_type", "view")
    text_upload = request.files.get("text_file")
    audio_upload = request.files.get("audio_file")
    style = style_from_form(request.form)

    text_bytes = None
    text_name = ""
    if text_upload and text_upload.filename:
        text_bytes = text_upload.read()
        text_name = text_upload.filename

    audio_bytes = None
    audio_name = ""
    if audio_upload and audio_upload.filename:
        audio_bytes = audio_upload.read()
        audio_name = audio_upload.filename

    try:
        text = resolve_text_input(
            typed_text=typed,
            text_file=text_bytes,
            text_filename=text_name,
            audio_file=audio_bytes,
            audio_filename=audio_name,
        )
        path = text_to_pdf(text, style=style)
        session["tools_file"] = path.name
        session["tools_kind"] = "pdf"
        session["tools_pdf_style"] = style
        if output_type == "view":
            session["tools_pdf_text"] = text
            session["tools_pdf_preview"] = True
            session["tools_message"] = "PDF preview ready. Edit text or style, then update preview."
        else:
            session.pop("tools_pdf_text", None)
            session.pop("tools_pdf_preview", None)
            session["tools_message"] = "PDF exported. Preview below or download."
    except Exception as exc:
        session["tools_error"] = str(exc)
    return redirect(url_for("tools"))


@app.route("/tools/to-pdf/update", methods=["POST"])
@login_required
def tools_to_pdf_update():
    from tools.to_pdf import style_from_form, text_to_pdf

    text = request.form.get("text", "")
    style = style_from_form(request.form)
    try:
        path = text_to_pdf(text, style=style)
        session["tools_file"] = path.name
        session["tools_kind"] = "pdf"
        session["tools_pdf_text"] = text.strip()
        session["tools_pdf_style"] = style
        session["tools_pdf_preview"] = True
        session["tools_message"] = "PDF preview updated."
    except Exception as exc:
        session["tools_error"] = str(exc)
    return redirect(url_for("tools"))


@app.route("/tools/files/<path:filename>")
@login_required
def tools_file(filename):
    from tools.paths import TOOLS_DIR, ensure_tools_dir

    ensure_tools_dir()
    as_attachment = request.args.get("download") == "1"
    return send_from_directory(TOOLS_DIR, filename, as_attachment=as_attachment)


if __name__ == "__main__":
    # Port 5001 avoids macOS AirPlay Receiver, which already uses 5000.
    app.run(debug=True, port=5001)
