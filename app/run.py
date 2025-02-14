"""
Creating a blueprint file to
break up the main.py file
"""

from flask import Blueprint, render_template, redirect, url_for, session
from functools import wraps
import pandas as pd
from app.flask_to_gcs import GcsConnection
from app.credentials import gcp_service_accnt

app_blueprint = Blueprint(
    "app_blueprint", __name__, template_folder="/templates", static_url_path="static"
)

guest_config = pd.read_csv("app/guest_list_config.csv")
gcs_connection = GcsConnection(
    service_accnt=gcp_service_accnt, gcs_bucket="website-responses"
)


def login_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if "logged_in" in session:
            return f(*args, **kwargs)
        else:
            return redirect(url_for("login"))

    return wrap


@app_blueprint.route("/home")
@login_required
def root() -> str:
    data = {}
    data["page_title"] = "Home"

    with open("app/markdown_pages/splash_page.md", "r") as f:
        text = f.read()
        data["html"] = text

    return render_template("index.html", data=data)


@app_blueprint.route("/our_story")
@login_required
def our_story() -> str:
    data = {}
    data["page_title"] = "Our Story"

    with open("app/templates/our_story.html", "r") as f:
        text = f.read()
        data["html"] = text

    return render_template("index.html", data=data)


@app_blueprint.route("/things_to_do")
@login_required
def things_to_do() -> str:
    data = {}
    data["page_title"] = "Things To Do"

    with open("app/templates/things_to_do.html", "r") as f:
        text = f.read()
        data["html"] = text

    return render_template("index.html", data=data)


@app_blueprint.route("/wedding_weekend")
@login_required
def wedding_weekend() -> str:
    data = {}
    data["page_title"] = "The Wedding Weekend"

    with open("app/templates/wedding_weekend.html", "r") as f:
        text = f.read()
        data["html"] = text

    return render_template("index.html", data=data)


@app_blueprint.route("/travel")
@login_required
def travel() -> str:
    data = {}
    data["page_title"] = "Travel"

    with open("app/templates/travel.html", "r") as f:
        text = f.read()
        data["html"] = text

    return render_template("index.html", data=data)


# @app_blueprint.route("/Registry")
# @login_required
# def registry() -> str:
#     data = {}
#     data["page_title"] = "Registry"

#     with open("app/markdown_pages/registry.html", "r") as f:
#         text = f.read()
#         data["html"] = text

#     temp = render_template("index.html", data=data)

#     return temp
