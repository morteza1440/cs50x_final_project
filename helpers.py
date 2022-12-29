from flask import flash, redirect
from cs50 import SQL
from flask import session
from pandas import DataFrame
import inflect


p = inflect.engine()


class MTTCalcDB(SQL):

    def __init__(self, path: str):
        super(MTTCalcDB, self).__init__(f"sqlite:///{path}")

    def get_username(self):
        """ Return username of loged in user """

        # If user is loged in, return username
        if session.get("user_id"):
            return self.execute("SELECT username FROM users WHERE id == ?", session.get("user_id"))

        # If user is not loged in, return None
        return None


def get_viabilities(form: dict) -> DataFrame:
    """ Return a dataframe initilized by submitted form data """

    num_groups: str = form.get("num_groups")
    num_groups = num_groups.strip() if num_groups else None
    if not num_groups or not num_groups.isdigit() or 1 > int(num_groups) > 100:
        flash("Number of groups should be an integer between 0 and 101.")
        return None

    num_repeats: str = form.get("num_repeats")
    num_repeats = num_repeats.strip() if num_repeats else None
    if not num_repeats or not num_repeats.isdigit() or 1 > int(num_repeats) > 100:
        flash("Number of repeats should be an integer between 0 and 101.")
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
            if not viability or not viability.replace(".", "1").isdigit():
                flash(f"Invalid value for {p.ordianl(r + 1)} repeat of group {g + 1}.")

            blank: str = form.get(f"b{g}_r{r}")
            blank = blank.strip() if blank else None
            if not blank or not blank.replace(".", "1").isdigit():
                flash(f"Invalid value for {p.ordianl(r + 1)} repeat of group {g + 1} blank.")

            group.append(float(viability))
            blanks.append(float(blank))

        # Store group name
        name_group: str = form.get(f"g{g}")
        if not name_group or name_group == "":
            flash(f"Enter name for group {g + 1}.")

        # Add acumulated group and blank to data
        data[name_group.strip()] = group
        data[f"b{g}"] = blanks

    return DataFrame(data)