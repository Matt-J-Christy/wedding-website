from flask import Blueprint, render_template, redirect, url_for, session
from functools import wraps
import os
import math

pp_blueprint = Blueprint(
    "pp_blueprint", __name__, template_folder="/templates", static_url_path="static"
)


def full_path(direct):
    return [os.path.join(direct, filename) for filename in os.listdir(direct)]


wp_photo_list = full_path('static/welcomeparty')
bp_photo_list = full_path('static/bridalparty')
bg_photo_list = full_path('static/bridegroom')
fam_photo_list = full_path('static/family')
ce_photo_list = full_path('static/ceremony')
re_photo_list = full_path('static/reception')


def login_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if "logged_in" in session:
            return f(*args, **kwargs)
        else:
            return redirect(url_for("login"))

    return wrap


@pp_blueprint.route("/welcome_party")
@login_required
def welcome_party() -> str:
    data = {}
    data["page_title"] = "Welcome Party"

    len_li = len(wp_photo_list)
    len_want = math.ceil(len_li/3)

    chunks = [wp_photo_list[i:i + len_want]
              for i in range(0, len(wp_photo_list), len_want)]

    temp = render_template(
        "photo_gallery.html",
        data=data,
        chunks=chunks
    )

    return temp


@pp_blueprint.route("/bridalparty")
@login_required
def bridalparty() -> str:
    data = {}
    data["page_title"] = "Bridal Party"

    len_li = len(bp_photo_list)
    len_want = math.ceil(len_li/3)

    chunks = [bp_photo_list[i:i + len_want]
              for i in range(0, len(bp_photo_list), len_want)]

    temp = render_template(
        "photo_gallery.html",
        data=data,
        chunks=chunks
    )

    return temp


@pp_blueprint.route("/bridegroom")
@login_required
def bridegroom() -> str:
    data = {}
    data["page_title"] = "Bride & Groom"

    len_li = len(bg_photo_list)
    len_want = math.ceil(len_li/3)

    chunks = [bg_photo_list[i:i + len_want]
              for i in range(0, len(bg_photo_list), len_want)]

    temp = render_template(
        "photo_gallery.html",
        data=data,
        chunks=chunks
    )

    return temp


@pp_blueprint.route("/family")
@login_required
def family() -> str:
    data = {}
    data["page_title"] = "Family"

    len_li = len(fam_photo_list)
    len_want = math.ceil(len_li/3)

    chunks = [fam_photo_list[i:i + len_want]
              for i in range(0, len(fam_photo_list), len_want)]

    temp = render_template(
        "photo_gallery.html",
        data=data,
        chunks=chunks
    )

    return temp


@pp_blueprint.route("/ceremony")
@login_required
def ceremony() -> str:
    data = {}
    data["page_title"] = "Ceremony"

    len_li = len(ce_photo_list)
    len_want = math.ceil(len_li/3)

    chunks = [ce_photo_list[i:i + len_want]
              for i in range(0, len(ce_photo_list), len_want)]

    temp = render_template(
        "photo_gallery.html",
        data=data,
        chunks=chunks
    )

    return temp


@pp_blueprint.route("/reception")
@login_required
def reception() -> str:
    data = {}
    data["page_title"] = "Reception"

    len_li = len(re_photo_list)
    len_want = math.ceil(len_li/3)

    chunks = [re_photo_list[i:i + len_want]
              for i in range(0, len(re_photo_list), len_want)]

    temp = render_template(
        "photo_gallery.html",
        data=data,
        chunks=chunks
    )

    return temp
