"""
Flask application for
running our wedding website
"""

from flask import Flask, render_template, redirect, url_for, request, session, flash
from functools import wraps
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from app.credentials import username, password, secret_key
import markdown
import os

app = Flask(__name__,
            static_url_path='/static/',
            template_folder='app/templates'
            )

app.secret_key = secret_key

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
@app.route('/login', methods=['GET', 'POST'])
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


@app.route("/")
@login_required
def root() -> str:
    data = {}
    data["page_title"] = "Splash Page"

    with open('app/markdown_pages/splash_page.md', 'r') as f:
        text = f.read()
        data["html"] = markdown.markdown(text)

    return render_template('index.html', data=data)


@app.route('/our_story')
@login_required
def our_story() -> str:
    data = {}
    data["page_title"] = "Our Story"

    # with open('app/markdown_pages/our_story.md', 'r') as f:
    #     text = f.read()
    #     data['html'] = markdown.markdown(text)

    # serve blank pages that aren't done
    data["html"] = ""

    return render_template('index.html', data=data)


@app.route('/things_to_do')
@login_required
def things_to_do() -> str:
    data = {}
    data["page_title"] = "Things to do"

    # with open('app/markdown_pages/things_to_do.md', 'r') as f:
    #     text = f.read()
    #     data["html"] = markdown.markdown(text)

    # serve blank pages that aren't done
    data['html'] = ""

    return render_template('index.html', data=data)


@app.route('/wedding_weekend')
@login_required
def wedding_weekend() -> str:
    data = {}
    data["page_title"] = "The Wedding Weekend"

    # with open('app/markdown_pages/wedding_weekend.md', 'r') as f:
    #     text = f.read()
    #     data["html"] = markdown.markdown(text)

    # serve blank pages that aren't done
    data['html'] = ""

    return render_template('index.html', data=data)


if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
