"""
Creating a blueprint file to
for the RSVP pages
"""

from flask import Blueprint, render_template, redirect, url_for, request, session
from functools import wraps
import datetime
import pandas as pd
import uuid
from app.flask_to_gcs import GcsConnection
from app.credentials import gcp_service_accnt

rsvp_blueprint = Blueprint(
    "rsvp_blueprint", __name__, template_folder="/templates", static_url_path="static"
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


@rsvp_blueprint.route("/RSVP", methods=["GET", "POST"])
@login_required
def rsvp(guest_df: pd.DataFrame = guest_config):
    data = {}
    data["page_title"] = "RSVP"

    temp = render_template("rsvp3.html", data=data)

    if request.method == "POST":
        session["invitee_name"] = request.form["invitename"]
        search_value = session["invitee_name"].strip().lower()
        is_search_empty = guest_df.loc[
            guest_df["InviteeGroup"].apply(
                lambda names: any(
                    [search_value == x.strip().lower()
                     for x in list(names.split(","))]
                )
            )
        ].empty

        if not is_search_empty and session["invitee_name"] != "":
            guest_slice = guest_df.loc[
                guest_df["InviteeGroup"].apply(
                    lambda names: any(
                        [
                            search_value == x.strip().lower()
                            for x in list(names.split(","))
                        ]
                    )
                )
            ]

            session["names_list"] = guest_slice["InviteeGroup"].str.split(
                ", ").item()
            session["unknownplus"] = bool(guest_slice["UnknownPlusOne"].item())
            session["children"] = bool(guest_slice["FamilyInvited"].item())
            session["weddingparty"] = bool(guest_slice["WeddingParty"].item())

        return redirect(url_for("rsvp_blueprint.rsvpform"))

    return temp


@rsvp_blueprint.route("/RSVPForm", methods=["GET", "POST"])
@login_required
def rsvpform(guest_df: pd.DataFrame = guest_config):
    """
    Notes:
    Dropdown and button select responses left blank
    will break the ETL logic. Free text return blank
    if it is not filled out. So dinner and attendance
    must be filled out.

    Try-Except logic can handle missing data
    """
    data = dict(page_title="RSVPForm")
    search_value = session["invitee_name"].strip().lower()
    is_search_empty = guest_df.loc[
        guest_df["InviteeGroup"].apply(
            lambda names: any(
                [search_value == x.strip().lower()
                 for x in list(names.split(","))]
            )
        )
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
                diet_list.append(request.form["dietary_" + idx])
                songs.append(request.form["song_" + idx])

                # making RSVP and dinner choice handle missing data
                try:
                    rsvp_list.append(request.form["response_" + idx])
                except KeyError:
                    rsvp_list.append("Response missing")

                try:
                    dinner_list.append(request.form["dinnerchoice_" + idx])
                except KeyError:
                    dinner_list.append("Response missing")

                # handling wedding party event specific stuff
                if session["weddingparty"]:
                    try:
                        thurs_attendance.append(request.form["thurs_" + idx])
                    except KeyError:
                        thurs_attendance.append("Response missing")
                else:
                    thurs_attendance.append("Not invited")

            row = pd.DataFrame(
                dict(
                    guest_name=guest_names,
                    rsvp_result=rsvp_list,
                    dinner_option=dinner_list,
                    dietary_restriction=diet_list,
                    song_request=songs,
                    thursday_attendance=thurs_attendance,
                )
            )

            rsvp_results = pd.concat([rsvp_results, row], ignore_index=True)

        # handle missing plus one

        if session["unknownplus"] or is_search_empty or session["invitee_name"] == "":
            if session["weddingparty"]:
                try:
                    thurs_response = request.form["thurs_unk"]
                except KeyError:
                    thurs_response = "Response missing"
            else:
                thurs_response = "Not invited"

            try:
                rsvp_resp = request.form["response_unk"]
            except KeyError:
                rsvp_resp = "Response Missing"

            try:
                dinner = request.form["dinnerchoice_unk"]
            except KeyError:
                dinner = "Response Missing"

            row = pd.DataFrame(
                dict(
                    guest_name=request.form["unknown"],
                    rsvp_result=rsvp_resp,
                    dinner_option=dinner,
                    dietary_restriction=request.form["dietary_unk"],
                    song_request=request.form["song_unk"],
                    thursday_attendance=thurs_response,
                ),
                index=[0],
            )

            rsvp_results = pd.concat([rsvp_results, row], ignore_index=True)

        # handle kids

        if session["children"] and\
                session["invitee_name"] != "" and\
                not is_search_empty:
            names_list = []
            rsvp_list = []
            dinner_list = []
            diet_list = []
            songs = ["NA"] * 3
            thurs_attendance = ["Not invited"] * 3

            for i in range(3):
                idx = str(i + 1)
                names_list.append(request.form["child_" + idx])
                diet_list.append(request.form["dietary_child_" + idx])

                try:
                    rsvp_list.append(request.form["response_child_" + idx])
                except KeyError:
                    rsvp_list.append("Response missing")

                try:
                    dinner_list.append(
                        request.form["dinnerchoice_child_" + idx])
                except KeyError:
                    dinner_list.append("Response missing")

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

        return redirect(url_for("rsvp_blueprint.thankyou"))

    return temp


@rsvp_blueprint.route("/thankyou")
@login_required
def thankyou() -> str:
    data = {}
    data["page_title"] = "ThankYou"

    with open("app/markdown_pages/thank_you.html", "r") as f:
        text = f.read()
        data["html"] = text

    temp = render_template("index.html", data=data)

    return temp
