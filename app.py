from flask import Flask, flash, redirect, render_template, request, session, Response
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
from helpers import MTTCalcDB
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


def mttcalc():
    """ Show forms to user and process submited data """

    if request.method == "GET":
        render_template("mttcalc.html")

    # If method == POST
    num_groups = request.form.get("num_groups")
    num_repeats = request.form.get("num_repeats")
    data = {}

    # Load data in a dic
    for g in range(num_groups):
        group = []
        blank = []

        # Acumulate absorbances of each group and its blank
        for r in range(num_repeats):
            group.append(request.form.get(f"g{g}_r{r}"))
            blank.append(request.form.get(f"b{g}_r{r}"))

        # Add acumulated group and blank to data
        data[request.form.get(f"g{g}")] = group
        data[f"b{g}"] = blank

    
