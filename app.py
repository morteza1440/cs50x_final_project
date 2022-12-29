import os


from flask import Flask, flash, redirect, render_template, request, session, Response
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
from helpers import MTTCalcDB, get_absorbances
from tempfile import mkdtemp
from mttcalc import calc_viabilities
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
db = MTTCalcDB("mttcalc.db")


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

    # Pass username to template to show welcome message if user is loged in
    return render_template("index.html", username=db.get_username())


@app.route("/mttcalc", methods=["GET", "POST"])
def mttcalc():
    """ Show forms to user and process submited data """

    if request.method == "GET":
        render_template("mttcalc.html")

    # If method == POST

    # Store submitted data in dataframe
    absorbances = get_absorbances(request.form)

    # Create temporary directory to save mttcalc files
    temp_path = mkdtemp()
    if not "temp_path" in session or session["temp_path"] == "":
        session["temp_path"] = temp_path
    else:
        session["temp_path"] = temp_path

    absorbances.to_csv(os.path.join(temp_path, "absorbances.csv"), index=False)

