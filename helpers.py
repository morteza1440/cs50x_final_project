from cs50 import SQL
from flask import session


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


def get_username():
    """ Return username from db """

    if session.get("user_id"):
        user_name = db.execute("SELECT username FROM users WHERE id == ?", session.get("user_id"))