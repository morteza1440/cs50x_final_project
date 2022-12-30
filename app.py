import os


from flask import Flask, flash, redirect, url_for, render_template, send_file, request, session, Response
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
from cs50 import SQL
from helpers import get_absorbances, calc_mtt, login_required
from tempfile import mkdtemp
from shutil import rmtree
from datetime import datetime


# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Custom filter
# TODO

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure database
db = SQL("sqlite:///mttcalc.db")


@app.after_request
def after_request(response: Response) -> Response:
    """ Ensure responses aren't cached """

    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/")
def index():
    """ Show the main page of MTTCalc web app """

    return render_template("index.html")


@app.route("/mttcalc", methods=["GET", "POST"])
def mttcalc():
    """ Show forms to user and process submited data """

    if request.method == "GET":
        # Set number of groups and repeats
        num_groups = request.args.get("num_groups")
        num_groups = num_groups.strip() if num_groups else None

        num_repeats = request.args.get("num_repeats")
        num_repeats = num_repeats.strip() if num_repeats else None

        # Check validity of number of groups and number of repeats
        if not num_groups or not num_groups.isdigit() or not 0 < int(num_groups) < 21:
            flash("Invalid number of groups.")
            redirect(url_for("index"))

        if not num_repeats or not num_repeats.isdigit() or not 1 < int(num_repeats) < 11:
            flash("Invalid number of repeats.")
            redirect(url_for("index"))

        # Show form of MTTCalc
        return render_template("mttcalc.html", num_groups=int(num_groups), num_repeats=int(num_repeats))

    # If method == POST
    form = request.form

    name = form.get("name")
    if not name or name.strip() == "":
        flash("Please enter name of the test.", "bg-danger")
        return redirect(url_for("mttcalc", num_groups=form.get("num_groups"), num_repeats=form.get("num_repeats")))

    # Store submitted data in dataframe and set flash if failed
    absorbances = get_absorbances(form)
    if type(absorbances) is type(None):
        return redirect(url_for("mttcalc", num_groups=form.get("num_groups"), num_repeats=form.get("num_repeats")))

    # Create temporary directory to save mttcalc files in it
    out_dir = mkdtemp()
    if not "out_dir" in session or session["out_dir"] == "":
        session["out_dir"] = out_dir
    else:
        # Remove previous tempdir
        rmtree(session["out_dir"], ignore_errors=True)
        session["out_dir"] = out_dir

    # Save absorbances.csv to file
    abs_path = os.path.join(out_dir, "absorbances.csv")
    absorbances.to_csv(abs_path, index=False)

    # Generate MTTCalc output files and set flash if failed
    if not calc_mtt(form, abs_path, out_dir):
        redirect(url_for("mttcalc", num_groups=form.get("num_groups"), num_repeats=form.get("num_repeats")))

    # Save data to database if user is loged in
    if session.get("user_id"):
        db.execute("INSERT INTO history (user_id, name, num_groups, num_repeats, name_groups, _values, timestamp) VALUES (?, ?, ?, ?, ?, ?, ?)",
                   session.get("user_id"), name.strip(), int(form.get("num_groups")), int(form.get("num_repeats")),
                   str(list(absorbances.columns)).replace(" ", ""), str([list(absorbances[c].values) for c in list(absorbances)]).replace(" ", ""),
                   datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

    # Redirect to download page
    flash("Task was done successfuly.")
    return redirect(url_for("download"))


@app.route("/download")
def download():
    """ Render download page or send file"""

    # Store name of files exist inside the out_dir
    files = os.listdir(session["out_dir"])
    file_name = request.args.get("file_name")

    # Render download template if file_name parameter doesn't exist
    if not file_name or file_name.strip() == "":
        return render_template("download.html", files=files)

    # If file_name parameter exists
    file_name = file_name.strip()

    # If file exists send file
    if file_name in files:
        return send_file(os.path.join(session["out_dir"], file_name), as_attachment=True)

    # If file doesn't exist redirect to download page with not found message
    flash("File not found.")
    return redirect(url_for("download"))


@app.route("/register", methods=["GET", "POST"])
def register():
    """ Register user """

    if request.method == "GET":
        return render_template("register.html")

    # POST
    username, password, confirmation =\
        request.form.get("username"), request.form.get("password"), request.form.get("confirmation")

    # Check inputs
    if not username or not password or not confirmation or\
            username == "" or password == "" or confirmation == "":
        flash("Please fill all the fields.", "bg-danger")
        return redirect(url_for("register"))

    # Check password and confirmation
    if not password == confirmation:
        flash("Password must match the confirmation!", "bg-danger")
        return redirect(url_for("register"))

    try:
        # Insert user into the database
        db.execute("INSERT INTO users (username, hash) VALUES(?, ?)", username, generate_password_hash(password))
    except ValueError as e:
        if not str(e).find("UNIQUE constraint failed:") == -1:
            flash("The username has already been taken", "bg-danger")
            return redirect(url_for("register"))

    flash("Registered successfully!")
    return redirect(url_for("login"))


@app.route("/login", methods=["GET", "POST"])
def login():
    """ Log user in """

    # Forget any user_id
    flash_messages = session.get("_flashes")
    session.clear()
    if flash_messages:
        session["_flashes"] = flash_messages

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "GET":
        return render_template("login.html")

    # if request.method == "POST"

    # Ensure username was submitted
    if not request.form.get("username"):
        flash("username must be provided.", "bg-danger")
        return render_template("login.html"), 403

    # Ensure password was submitted
    elif not request.form.get("password"):
        flash("password must be provided.", "bg-danger")
        return render_template("login.html"), 403

    # Query database for username
    rows = db.execute("SELECT * FROM users WHERE username == ?", request.form.get("username"))

    # Ensure username exists and password is correct
    if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
        flash("Invalid username and/or password!", "bg-danger")
        return render_template("login.html"), 403

    # Remember which user has logged in
    session["user_id"] = rows[0]["id"]

    # Redirect user to index page
    flash("Logged in successfully!")
    return redirect("/")


@app.route("/logout")
def logout():
    """ Log user out """

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    flash("Logged out successfully!")
    return redirect("/")


@login_required
@app.route("/history")
def history():
    """ Show history to loged in user """

    # Read history of user from database
    history = db.execute("SELECT * FROM history WHERE user_id == ?", session["user_id"])

    return render_template("history.html", history=history)


