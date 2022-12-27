from flask import Flask, flash, redirect, render_template, request, session, Response
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
from cs50 import SQL
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

# Configure CS50 Library to use SQLite database
db = SQL("mttcalc.db")


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

    # Get username if user is loged in
    if session.get("user_id"):
        user_name = db.execute("SELECT username FROM users WHERE id == ?", session.get("user_id"))

    # Pass username to template to show welcome message if user is loged in
    return render_template("index.html", username=user_name)


