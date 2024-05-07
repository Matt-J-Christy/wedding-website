"""
Flask application for
running our wedding website
"""

from flask import Flask, render_template, redirect, url_for, request, session, flash
from functools import wraps
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from app.credentials import username, password, secret_key  # , gcp_service_accnt
import markdown
import os
import pandas as pd
# from app.flask_to_gcs import GcsConnection

app = Flask(__name__,
            static_url_path='/static/',
            template_folder='app/templates'
            )

app.guest_config = pd.read_csv('app/guest_list_config.csv')  # type: ignore
app.secret_key = secret_key
# app.gcs_connection = GcsConnection(
# service_accnt=gcp_service_accnt, gcs_bucket='website-responses') # type: ignore


test_data = {"InviteeGroup": ["Cynthia Pizzano, Sandy",
                              "Donna Rhodes, Jimmy Rhodes, Sydney Rhodes",
                              "Alexis Rhodes",
                              "Lindy, Tom"],
             "UnknownPlusOne": [0,
                                0,
                                1,
                                0],
             "FamilyInvited": [0,
                               0,
                               0,
                               1],
             "WeddingParty": [1,
                              0,
                              1,
                              0]}

df = pd.DataFrame(data=test_data)

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
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            return redirect(url_for('login'))
    return wrap


# define login page
@app.route('/', methods=['GET', 'POST'])
@limiter.limit("5/second", override_defaults=True)
def login():
    error = None
    if request.method == 'POST':
        if request.form['username'] != username or request.form['password'] != password:
            error = 'Invalid Credentials. Please try again.'
        else:
            session['logged_in'] = True
            flash('You were logged in.')
            return redirect(url_for('root'))
    return render_template('login.html', error=error)


@app.route("/home")
@login_required
def root() -> str:
    data = {}
    data["page_title"] = "Home"

    with open('app/markdown_pages/splash_page.md', 'r') as f:
        text = f.read()
        data["html"] = markdown.markdown(text)

    return render_template('index.html', data=data)


@app.route('/our_story')
@login_required
def our_story() -> str:
    data = {}
    data["page_title"] = "Our Story"

    with open('app/templates/our_story.html', 'r') as f:
        text = f.read()
        data["html"] = markdown.markdown(text)

    return render_template('index.html', data=data)


@app.route('/things_to_do')
@login_required
def things_to_do() -> str:
    data = {}
    data["page_title"] = "Things To Do"

    with open('app/templates/things_to_do.html', 'r') as f:
        text = f.read()
        data["html"] = markdown.markdown(text)

    return render_template('index.html', data=data)


@app.route('/wedding_weekend')
@login_required
def wedding_weekend() -> str:
    data = {}
    data["page_title"] = "The Wedding Weekend"

    with open('app/templates/wedding_weekend.html', 'r') as f:
        text = f.read()
        data["html"] = markdown.markdown(text)

    return render_template('index.html', data=data)


@app.route('/travel')
@login_required
def travel() -> str:
    data = {}
    data["page_title"] = "Travel"

    with open('app/templates/travel.html', 'r') as f:
        text = f.read()
        data["html"] = markdown.markdown(text)

    return render_template('index.html', data=data)


@app.route('/RSVP', methods=['GET', 'POST'])
@login_required
def rsvp():
    data = {}
    data["page_title"] = "RSVP"

    temp = render_template('rsvp3.html', data=data)

    if (request.method == 'POST'):
        session["invitee_name"] = request.form['invitename']
        if not df.loc[df.InviteeGroup.str.contains(request.form['invitename'])].empty:
            session["names_list"] = df.loc[df.InviteeGroup.str.contains(
                request.form['invitename'])].InviteeGroup.str.split(", ").item()
            session["unknownplus"] = bool(df.loc[df.InviteeGroup.str.contains(
                request.form['invitename'])].UnknownPlusOne.item())
            session["children"] = bool(df.loc[df.InviteeGroup.str.contains(
                request.form['invitename'])].FamilyInvited.item())
            session["weddingparty"] = bool(df.loc[df.InviteeGroup.str.contains(
                request.form['invitename'])].WeddingParty.item())
        return redirect(url_for('rsvpform'))

    return temp


@app.route('/RSVPForm', methods=['GET', 'POST'])
@login_required
def rsvpform():
    data = {}
    data["page_title"] = "RSVPForm"
    if not df.loc[df.InviteeGroup.str.contains(session["invitee_name"])].empty:
        temp = render_template('rsvp4.html', data=data,
                               names=session["names_list"],
                               unknownplus=session["unknownplus"],
                               children=session["children"],
                               weddingparty=session["weddingparty"])
    else:
        with open('app/markdown_pages/error_rsvp.html', 'r') as f:
            text = f.read()
            data["html"] = markdown.markdown(text)

        temp = render_template('index.html', data=data)

    if (request.method == 'POST'):
        return redirect(url_for('thankyou'))

    return temp


@app.route('/thankyou')
@login_required
def thankyou() -> str:
    data = {}
    data["page_title"] = "ThankYou"

    with open('app/markdown_pages/thank_you.html', 'r') as f:
        text = f.read()
        data["html"] = markdown.markdown(text)

    temp = render_template('index.html', data=data)

    return temp


@app.route('/Registry')
@login_required
def registry() -> str:
    data = {}
    data["page_title"] = "Registry"

    with open('app/markdown_pages/registry.html', 'r') as f:
        text = f.read()
        data["html"] = markdown.markdown(text)

    temp = render_template('index.html', data=data)

    return temp


"""
writing data to GCS

app.gcs_connection.write_to_gcs(rsvp=pd.DataFrame({
    'GuestName': 'test buddy',
    'RSVP': 'attending',
    'Meal': 'Short Rib',
    "PlusOneName": 'Ole Muppet Feet'
}, index=[0]))
"""


if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
