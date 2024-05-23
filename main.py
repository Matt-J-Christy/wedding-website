"""
Flask application for
running our wedding website
"""

from flask import Flask, render_template, redirect, url_for, request, session, flash
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import os
from app.credentials import username, password, secret_key
from app.run import app_blueprint


app = Flask(__name__, static_url_path="/static/",
            template_folder="app/templates")
app.secret_key = secret_key
app.register_blueprint(app_blueprint)


limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=["10000 per day", "500 per hour"],
    storage_uri="memory://",
)


# define login page
@app.route("/", methods=["GET", "POST"])
@limiter.limit("5/second", override_defaults=True)
def login():
    error = None
    if request.method == "POST":
        if request.form["username"] != username or request.form["password"] != password:
            error = "Invalid Credentials. Please try again."
        else:
            session["logged_in"] = True
            flash("You were logged in.")
            return redirect(url_for("app_blueprint.root"))
    return render_template("login.html", error=error)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
