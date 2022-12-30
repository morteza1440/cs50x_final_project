from flask import flash, redirect
from flask import session
from pandas import DataFrame
from mttcalc import calc_viabilities, draw_barchart, draw_boxplot, Anova
from functools import wraps


import inflect
import os


p = inflect.engine()


def get_absorbances(form: dict) -> DataFrame:
    """ Return a dataframe initilized by submitted form data """

    num_groups: str = form.get("num_groups")
    num_groups = num_groups.strip() if num_groups else None
    if not num_groups or not num_groups.isdigit() or 1 > int(num_groups) > 20:
        flash("Number of groups should be an integer between 0 and 21.", "bg-danger")
        return None

    num_repeats: str = form.get("num_repeats")
    num_repeats = num_repeats.strip() if num_repeats else None
    if not num_repeats or not num_repeats.isdigit() or 2 > int(num_repeats) > 10:
        flash("Number of repeats should be an integer between 1 and 11.", "bg-danger")
        return None

    # Load data in a dic
    data = {}

    for g in range(int(num_groups)):
        group = []
        blanks = []

        # Acumulate absorbances of each group and its blanks
        for r in range(int(num_repeats)):
            viability: str = form.get(f"g{g}_r{r}")
            viability = viability.strip() if viability else None
            if not viability or not viability.replace(".", "1").isdigit() or len(viability) > 10:
                flash(f"Invalid value for {p.ordinal(r + 1)} repeat of group {g + 1}.", "bg-danger")
                return None

            blank: str = form.get(f"b{g}_r{r}")
            blank = blank.strip() if blank else None
            if not blank or not blank.replace(".", "1").isdigit() or len(blank) > 10:
                flash(f"Invalid value for {p.ordinal(r + 1)} repeat of group {g + 1} blank.", "bg-danger")
                return None

            group.append(float(viability))
            blanks.append(float(blank))

        # Store group name
        name_group: str = form.get(f"g{g}")
        if not name_group or name_group == "":
            flash(f"Enter name for group {g + 1}.", "bg-danger")
            return None

        # Add acumulated group and blank to data
        data[name_group.strip()] = group
        data[f"b{g}"] = blanks

    return DataFrame(data)


def calc_mtt(form: dict, abs_path: str, out_dir: str):
    """
        Perform MTTCalc one passed absorbances.csv file
        and save output files inside out_dir
    """

    # Calculate viabilites.csv from absorbances.csv
    viabilities = calc_viabilities(abs_path, out_dir)
    if not viabilities:
        flash("Can not calculate viabilities. Check your data and try again.", "bg-danger")
        return False

    # Generate bc.png
    if form.get("bc"):
        angle: str = form.get("angle")
        angle = float(angle) if angle and angle.strip().replace(".", "1").isdigit() else None

        draw_barchart(os.path.join(out_dir, "viabilities.csv"), os.path.join(out_dir, "barchart.png"),
                      title=form.get("bc_t"), xlabel=form.get("bc_x"), ylabel=form.get("bc_y"), angle=angle)

    # Generate pb.png
    if form.get("bp"):
        draw_boxplot(viabilities, os.path.join(out_dir, "boxplot.png"))

    try:
        anova = Anova(viabilities, out_dir)
    except ValueError:
        # Exit if out_dir is not valid
        flash("Internal server error. Try again later.", "bg-danger")
        return False

    # Check anova assumptions and generate out.dat
    if form.get("ca"):
        anova.check_assumptions()

    # One-Way ANOVA Test. Append to out.dat
    anova.test()

    # Pairwise multiple comparison, as anova post hoc. Append to out.dat
    if form.get("mc"):
        anova.perform_tukey()

    return True


def login_required(f):
    """
    Decorate routes to require login.

    https://flask.palletsprojects.com/en/1.1.x/patterns/viewdecorators/
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function