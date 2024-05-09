"""
Flask application for
running our wedding website
"""

from flask import Flask, render_template, redirect, url_for, request, session, flash
from functools import wraps
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import datetime
import os
import pandas as pd
import uuid
from app.flask_to_gcs import GcsConnection
from app.credentials import username, password, secret_key, gcp_service_accnt

app = Flask(__name__, static_url_path="/static/",
            template_folder="app/templates")
app.secret_key = secret_key

guest_config = pd.read_csv("app/guest_list_config.csv")
gcs_connection = GcsConnection(
    service_accnt=gcp_service_accnt, gcs_bucket="website-responses"
)


limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=["10000 per day", "500 per hour"],
    storage_uri="memory://",
)

# login required decorator


def login_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if "logged_in" in session:
            return f(*args, **kwargs)
        else:
            return redirect(url_for("login"))

    return wrap


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
            return redirect(url_for("root"))
    return render_template("login.html", error=error)


@app.route("/home")
@login_required
def root() -> str:
    data = {}
    data["page_title"] = "Home"

    with open("app/markdown_pages/splash_page.md", "r") as f:
        text = f.read()
        data["html"] = text

    return render_template("index.html", data=data)


@app.route("/our_story")
@login_required
def our_story() -> str:
    data = {}
    data["page_title"] = "Our Story"

    with open("app/templates/our_story.html", "r") as f:
        text = f.read()
        data["html"] = text

    return render_template("index.html", data=data)


@app.route("/things_to_do")
@login_required
def things_to_do() -> str:
    data = {}
    data["page_title"] = "Things To Do"

    with open("app/templates/things_to_do.html", "r") as f:
        text = f.read()
        data["html"] = text

    return render_template("index.html", data=data)


@app.route("/wedding_weekend")
@login_required
def wedding_weekend() -> str:
    data = {}
    data["page_title"] = "The Wedding Weekend"

    with open("app/templates/wedding_weekend.html", "r") as f:
        text = f.read()
        data["html"] = text

    return render_template("index.html", data=data)


@app.route("/travel")
@login_required
def travel() -> str:
    data = {}
    data["page_title"] = "Travel"

    with open("app/templates/travel.html", "r") as f:
        text = f.read()
        data["html"] = text

    return render_template("index.html", data=data)


@app.route("/RSVP", methods=["GET", "POST"])
@login_required
def rsvp(guest_df: pd.DataFrame = guest_config):
    data = {}
    data["page_title"] = "RSVP"

    temp = render_template("rsvp3.html", data=data)

    if request.method == "POST":
        session["invitee_name"] = request.form["invitename"]
        search_value = session["invitee_name"].lower()
        is_search_empty = guest_df.loc[
            guest_df["InviteeGroup"].str.lower().str.contains(search_value)
        ].empty

        if not is_search_empty and session["invitee_name"] != "":
            guest_slice = guest_df.loc[
                guest_df["InviteeGroup"].str.lower().str.contains(search_value), :
            ]

            session["names_list"] = guest_slice["InviteeGroup"].str.split(
                ", ").item()
            session["unknownplus"] = bool(guest_slice["UnknownPlusOne"].item())
            session["children"] = bool(guest_slice["FamilyInvited"].item())
            session["weddingparty"] = bool(guest_slice["WeddingParty"].item())

        return redirect(url_for("rsvpform"))

    return temp


@app.route("/RSVPForm", methods=["GET", "POST"])
@login_required
def rsvpform(guest_df: pd.DataFrame = guest_config):
    data = {}
    data["page_title"] = "RSVPForm"
    search_value = session["invitee_name"].lower()
    is_search_empty = guest_df.loc[
        guest_df["InviteeGroup"].str.lower().str.contains(search_value)
    ].empty

    if not is_search_empty and session["invitee_name"] != "":
        temp = render_template(
            "rsvp4.html",
            data=data,
            names=session["names_list"],
            unknownplus=session["unknownplus"],
            children=session["children"],
            weddingparty=session["weddingparty"],
        )
    else:
        with open("app/markdown_pages/error_rsvp.html", "r") as f:
            text = f.read()
            data["html"] = text

        temp = render_template("index.html", data=data)

    if request.method == "POST":
        guest_names = []
        rsvp_list = []
        dinner_list = []
        diet_list = []
        songs = []
        thurs_attendance = []

        rsvp_results = pd.DataFrame(
            columns=[
                "guest_name",
                "rsvp_result",
                "dinner_option",
                "dietary_restriction",
                "song_request",
                "thursday_attendance",
            ],
            dtype=str,
        )

        if not is_search_empty and session["invitee_name"] != "":
            guest_names = session["names_list"]

            for i in range(len(session["names_list"])):
                idx = str(i + 1)
                rsvp_list.append(request.form["response_" + idx])
                dinner_list.append(request.form["dinnerchoice_" + idx])
                diet_list.append(request.form["dietary_" + idx])
                songs.append(request.form["song_" + idx])

                if session["weddingparty"]:
                    try:
                        thurs_attendance.append(request.form["thurs_" + idx])
                    except KeyError:
                        thurs_attendance.append("Response missing")
                else:
                    thurs_attendance.append("Not invited")

            rsvp_results["guest_name"] = guest_names
            rsvp_results["rsvp_result"] = rsvp_list
            rsvp_results["dinner_option"] = dinner_list
            rsvp_results["dietary_restriction"] = diet_list
            rsvp_results["song_request"] = songs
            rsvp_results["thursday_attendance"] = thurs_attendance

        # handle missing plus one

        if session["unknownplus"] or is_search_empty or session["invitee_name"] == "":
            if session["weddingparty"]:
                try:
                    thurs_response = request.form["thurs_unk"]
                except KeyError:
                    thurs_response = "Response missing"
            else:
                thurs_response = "Not invited"

            row = pd.DataFrame(
                dict(
                    # TODO: update this naming
                    guest_name=request.form["unknown"],
                    rsvp_result=request.form["response_unk"],
                    dinner_option=request.form["dinnerchoice_unk"],
                    dietary_restriction=request.form["dietary_unk"],
                    song_request=request.form["song_unk"],
                    thursday_attendance=thurs_response,
                ),
                index=[0],
            )

            rsvp_results = pd.concat([rsvp_results, row], ignore_index=True)

        # handle kids

        if session["children"] and session["invitee_name"] != "":
            names_list = []
            rsvp_list = []
            dinner_list = []
            diet_list = []
            songs = ["NA"] * 3
            thurs_attendance = ["Not invited"] * 3

            print(thurs_attendance)

            for i in range(3):
                idx = str(i + 1)
                names_list.append(request.form["child_" + idx])
                rsvp_list.append(request.form["response_child_" + idx])
                dinner_list.append(request.form["dinnerchoice_child_" + idx])
                diet_list.append(request.form["dietary_child_" + idx])

            print(names_list)

            kid_rsvp = pd.DataFrame(
                dict(
                    guest_name=names_list,
                    rsvp_result=rsvp_list,
                    dinner_option=dinner_list,
                    dietary_restriction=diet_list,
                    song_request=songs,
                    thursday_attendance=thurs_attendance,
                )
            )

            rsvp_results = pd.concat(
                [rsvp_results, kid_rsvp], ignore_index=True)

        # write the session id before
        rsvp_results["session_id"] = str(uuid.uuid4())
        rsvp_results["timestamp"] = datetime.datetime.now()
        print(rsvp_results)

        gcs_connection.write_to_gcs(rsvp=rsvp_results)

        return redirect(url_for("thankyou"))

    return temp


@app.route("/thankyou")
@login_required
def thankyou() -> str:
    data = {}
    data["page_title"] = "ThankYou"

    with open("app/markdown_pages/thank_you.html", "r") as f:
        text = f.read()
        data["html"] = text

    temp = render_template("index.html", data=data)

    return temp


@app.route("/Registry")
@login_required
def registry() -> str:
    data = {}
    data["page_title"] = "Registry"

    with open("app/markdown_pages/registry.html", "r") as f:
        text = f.read()
        data["html"] = text

    temp = render_template("index.html", data=data)

    return temp


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
